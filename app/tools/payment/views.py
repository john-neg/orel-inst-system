from dataclasses import dataclass

from flask import render_template, request, flash, redirect, url_for
from flask.views import View
from flask_login import login_required

from config import PermissionsConfig
from . import payment_bp as bp
from .forms import (
    create_payment_form,
    DeleteForm,
    DocumentsForm,
    create_increase_form,
    RatesForm,
    create_rate_values_form,
    create_pension_duty_form,
    create_global_coefficient_form,
    create_addons_form,
    create_addons_values_form,
    create_single_addons_form,
)
from .func import get_paginated_data, make_slug
from ...auth.func import permission_required
from ...core.db.database import db
from ...core.db.payment_models import (
    PaymentRates,
    PaymentAddons,
    PaymentSingleAddons,
    PaymentGlobalCoefficient,
    PaymentPensionDutyCoefficient,
    PaymentDocuments,
    PaymentIncrease,
    PaymentRatesValues,
    PaymentAddonsValues,
)


@bp.route("/payment", methods=["GET", "POST"])
async def payment_tool():
    rate_items: list = PaymentRates.get_all()
    addon_items: list = PaymentAddons.get_all()
    single_items: list = PaymentSingleAddons.get_all()
    pension_duty_items: list = PaymentPensionDutyCoefficient.get_all()
    global_coeff: list = PaymentGlobalCoefficient.get_all()
    payment_types: dict[str, str] = {
        "salary": "Расчет зарплаты",
        "pension": "Расчет пенсии",
    }

    form = create_payment_form(
        rate_items=rate_items,
        addon_items=addon_items,
        single_items=single_items,
        pension_duty_items=pension_duty_items,
    )

    if request.method == "POST" and form.validate_on_submit():
        payment_data = {}
        for payment_type in payment_types:
            payment_data[f"{payment_type}_data"] = {}
            payment_data[f"{payment_type}_total"] = 0

        # Информация об окладах
        for item in rate_items:
            item_value_id = int(request.form.get(item.slug))
            value_data = item.get_value_data(item_value_id)
            item_rate_data = {
                "name": item.payment_name,
                "value": value_data.value,
                "value_name": value_data.name,
                "description": value_data.description,
                "document": value_data.document.name,
            }
            if item.increase:
                item_rate_data["increase"] = item.increase
            for payment_type in payment_types:
                if getattr(item, payment_type):
                    payment_data[f"{payment_type}_data"][item.slug] = item_rate_data
                    payment_data[f"{payment_type}_total"] += value_data.value

        # Информация о надбавках с множественным выбором
        if addon_items:
            for item in addon_items:
                item_value_id = int(request.form.get(item.slug))
                value_data = item.get_value_data(item_value_id)
                if value_data:
                    for payment_type in payment_types:
                        if getattr(item, payment_type):
                            value = sum(
                                [
                                    round(
                                        payment_data[f"{payment_type}_data"]
                                        .get(rate.slug)
                                        .get("value")
                                        * value_data.value,
                                        ndigits=2,
                                    )
                                    for rate in item.rates
                                ]
                            )
                            if value:
                                payment_data[f"{payment_type}_data"][item.slug] = {
                                    "name": f"{item.payment_name} ({value_data.value:.0%})",
                                    "value": value,
                                    "value_name": value_data.name,
                                    "description": value_data.description,
                                    "document": value_data.document.name,
                                }
                                payment_data[f"{payment_type}_total"] += value

        # Информация о надбавках с одиночным выбором
        if single_items:
            for item in single_items:
                if request.form.get(item.slug):
                    # Сохраняем выбранное значение в форме
                    form[item.slug].object_data = True
                    for payment_type in payment_types:
                        if getattr(item, payment_type):
                            value = sum(
                                [
                                    round(
                                        payment_data[f"{payment_type}_data"]
                                        .get(rate.slug)
                                        .get("value")
                                        * item.value,
                                        ndigits=2,
                                    )
                                    for rate in item.rates
                                ]
                            )
                            payment_data[f"{payment_type}_data"][item.slug] = {
                                "name": f"{item.payment_name} ({item.value:.0%})",
                                "value": value,
                                "description": item.description,
                                "document": item.document.name,
                            }
                            payment_data[f"{payment_type}_total"] += value
                else:
                    form[item.slug].object_data = False

        # Информация о пенсионном коэффициенте
        if request.form.get("pension_duty_years"):
            item_value_id = int(request.form.get("pension_duty_years"))
            value_data = PaymentPensionDutyCoefficient.get(item_value_id)
            value = round(
                payment_data["pension_total"] * (value_data.value - 1), ndigits=2
            )
            payment_data["pension_data"]["pension_duty_years"] = {
                "name": f"{form.pension_duty_years.label.text} ({value_data.value:.0%})",
                "value": value,
                "value_name": value_data.name,
                "document": value_data.document.name,
            }
            payment_data["pension_total"] += value

        # Информация о глобальных коэффициентах
        if global_coeff:
            for item in PaymentGlobalCoefficient.get_all():
                for payment_type in payment_types:
                    if getattr(item, payment_type):
                        # Костыль для округления НДФЛ
                        if item.slug == "coeff_ndfl":
                            value = round(
                                payment_data[f"{payment_type}_total"]
                                * (float(item.value) - 1)
                            )
                        else:
                            value = round(
                                payment_data[f"{payment_type}_total"]
                                * (float(item.value) - 1),
                                ndigits=2,
                            )
                        payment_data[f"{payment_type}_data"][item.slug] = {
                            "name": f"{item.payment_name}",
                            "value": value,
                            "description": item.description,
                            "document": item.document.name,
                        }
                        payment_data[f"{payment_type}_total"] += value

        # Округляем итоговые значения
        for payment_type in payment_types:
            payment_data[f"{payment_type}_total"] = round(
                payment_data.get(f"{payment_type}_total"), ndigits=2
            )

        return render_template(
            "tools/payment/payment.html",
            active="tools",
            form=form,
            payment_data=payment_data,
            rate_items=rate_items,
            payment_types=payment_types,
        )
    return render_template(
        "tools/payment/payment.html",
        active="tools",
        form=form,
        rate_items=rate_items,
    )


@dataclass
class PaymentGetView(View):
    """View класс для просмотра списка записей."""

    template_name: str
    title: str
    payment_class: db.Model
    methods = ["GET", "POST"]

    @permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self):
        paginated_data = get_paginated_data(self.payment_class.query)
        return render_template(
            self.template_name,
            title=self.title,
            paginated_data=paginated_data,
        )


bp.add_url_rule(
    "/payment/documents",
    view_func=PaymentGetView.as_view(
        "documents_get",
        title="Нормативные документы",
        template_name="tools/payment/documents.html",
        payment_class=PaymentDocuments,
    ),
)

bp.add_url_rule(
    "/payment/rates",
    view_func=PaymentGetView.as_view(
        "rates_get",
        title="Базовые оклады",
        template_name="tools/payment/rates.html",
        payment_class=PaymentRates,
    ),
)

bp.add_url_rule(
    "/payment/addons",
    view_func=PaymentGetView.as_view(
        "addons_get",
        title="Надбавки с множественными значениями",
        template_name="tools/payment/addons.html",
        payment_class=PaymentAddons,
    ),
)

bp.add_url_rule(
    "/payment/single_addons",
    view_func=PaymentGetView.as_view(
        "single_addons_get",
        title="Фиксированные надбавки",
        template_name="tools/payment/single_addons.html",
        payment_class=PaymentSingleAddons,
    ),
)

bp.add_url_rule(
    "/payment/increase",
    view_func=PaymentGetView.as_view(
        "increase_get",
        title="Индексация",
        template_name="tools/payment/increase.html",
        payment_class=PaymentIncrease,
    ),
)

bp.add_url_rule(
    "/payment/pension_duty",
    view_func=PaymentGetView.as_view(
        "pension_duty_get",
        title="Пенсионный коэффициент",
        template_name="tools/payment/pension_duty.html",
        payment_class=PaymentPensionDutyCoefficient,
    ),
)

bp.add_url_rule(
    "/payment/global_coefficient",
    view_func=PaymentGetView.as_view(
        "global_coefficient_get",
        title="Глобальные коэффициенты",
        template_name="tools/payment/global_coefficient.html",
        payment_class=PaymentGlobalCoefficient,
    ),
)


@bp.route("/payment/documents/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def documents_add():
    form = DocumentsForm()
    if request.method == "POST" and form.validate_on_submit():
        PaymentDocuments.create(name=request.form.get("name"))
        flash("Документ успешно добавлен", category="success")
        return redirect(url_for(".documents_get"))
    return render_template(
        "tools/payment/documents_edit.html",
        title=f"Добавить документ",
        form=form,
    )


@bp.route("/payment/documents/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def documents_edit(id_):
    document = PaymentDocuments.get(id_)
    form = DocumentsForm(obj=document)
    if request.method == "POST" and form.validate_on_submit():
        PaymentDocuments.update(
            id_,
            name=request.form.get("name"),
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".documents_get"))

    return render_template(
        "tools/payment/documents_edit.html",
        title=f"Изменить документ #{id_}",
        form=form,
    )


@bp.route("/payment/rates/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def rates_add():
    form = RatesForm()
    if request.method == "POST" and form.validate_on_submit():
        PaymentRates.create(
            name=request.form.get("name"),
            slug=make_slug(request.form.get("name"), prefix="rate_"),
            payment_name=request.form.get("payment_name"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
        )
        flash(
            "Оклад успешно добавлен (не забудьте добавить значения)", category="success"
        )
        return redirect(url_for(".rates_get"))
    return render_template(
        "tools/payment/rates_edit.html",
        title=f"Добавить оклад",
        form=form,
    )


@bp.route("/payment/rates/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def rates_edit(id_):
    rate = PaymentRates.get(id_)
    form = RatesForm(obj=rate)
    if request.method == "POST" and form.validate_on_submit():
        PaymentRates.update(
            id_,
            name=request.form.get("name"),
            slug=make_slug(request.form.get("name"), prefix="rate_"),
            payment_name=request.form.get("payment_name"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".rates_get"))
    return render_template(
        "tools/payment/rates_edit.html",
        title=f"Изменить оклад #{id_}",
        form=form,
        rate=rate,
    )


@bp.route("/payment/rates/<int:id_>/values", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def rates_values_get(id_):
    rate = PaymentRates.get(id_)
    paginated_data = get_paginated_data(PaymentRatesValues.query.filter_by(rate_id=id_))
    return render_template(
        "tools/payment/rates_values.html",
        title=f'Значения оклада "{rate.name}"',
        paginated_data=paginated_data,
        rate=rate,
        rate_id=id_,
    )


@bp.route("/payment/rates/<int:id_>/values/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def rates_values_add(id_):
    rate_items = PaymentRates.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_rate_values_form(
        rate_items=rate_items, document_items=document_items, rate_id=id_
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentRatesValues.create(
            name=request.form.get("name"),
            value=request.form.get("value"),
            description=request.form.get("description"),
            rate_id=request.form.get("rate_id"),
            document_id=request.form.get("document_id"),
        )
        flash("Значение оклада успешно добавлено", category="success")
        return redirect(url_for(".rates_values_get", id_=request.form.get("rate_id")))
    return render_template(
        "tools/payment/rates_values_edit.html",
        title=f"Добавить значение оклада",
        form=form,
    )


@bp.route("/payment/rates/<int:id_>/values/<int:value_id>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def rates_values_edit(id_, value_id):
    value = PaymentRatesValues.get(value_id)
    rate_items = PaymentRates.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_rate_values_form(
        obj=value,
        rate_items=rate_items,
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentRatesValues.update(
            value_id,
            name=request.form.get("name"),
            value=request.form.get("value"),
            description=request.form.get("description"),
            rate_id=request.form.get("rate_id"),
            document_id=request.form.get("document_id"),
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".rates_values_get", id_=request.form.get("rate_id")))
    return render_template(
        "tools/payment/rates_values_edit.html",
        title=f"Изменить значение оклада #{id_}",
        form=form,
        value=value,
    )


@bp.route("/payment/addons/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def addons_add():
    rate_items = PaymentRates.get_all()
    form = create_addons_form(rate_items=rate_items)
    if request.method == "POST" and form.validate_on_submit():
        PaymentAddons.create(
            name=request.form.get("name"),
            slug=make_slug(request.form.get("name"), prefix="addon_"),
            payment_name=request.form.get("payment_name"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
            rates=[rate for rate in rate_items if request.form.get(rate.slug)],
        )
        flash("Оклад успешно добавлен", category="success")
        return redirect(url_for(".addons_get"))
    return render_template(
        "tools/payment/addons_edit.html",
        title=f"Добавить надбавку с множественным выбором",
        form=form,
    )


@bp.route("/payment/addons/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def addons_edit(id_):
    addon = PaymentAddons.get(id_)
    rate_items = PaymentRates.get_all()
    form = create_addons_form(obj=addon, rate_items=rate_items)
    for rate in addon.rates:
        if rate in rate_items:
            form.__getattribute__(rate.slug).data = True
    if request.method == "POST" and form.validate_on_submit():
        PaymentAddons.update(
            id_,
            name=request.form.get("name"),
            slug=make_slug(request.form.get("name"), prefix="addon_"),
            payment_name=request.form.get("payment_name"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
            rates=[rate for rate in rate_items if request.form.get(rate.slug)],
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".addons_get"))
    return render_template(
        "tools/payment/addons_edit.html",
        title=f"Изменить надбавку #{id_}",
        form=form,
        addon=addon,
    )


@bp.route("/payment/addons/<int:id_>/values", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def addons_values_get(id_):
    addon = PaymentAddons.get(id_)
    paginated_data = get_paginated_data(
        PaymentAddonsValues.query.filter_by(addon_id=id_)
    )
    return render_template(
        "tools/payment/addons_values.html",
        title=f'Значения надбавки "{addon.name}"',
        paginated_data=paginated_data,
        addon=addon,
        addon_id=id_,
    )


@bp.route("/payment/addons/<int:id_>/values/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def addons_values_add(id_):
    addons_items = PaymentAddons.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_addons_values_form(
        addons_items=addons_items,
        document_items=document_items,
        addon_id=id_,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentAddonsValues.create(
            name=request.form.get("name"),
            value=request.form.get("value"),
            description=request.form.get("description"),
            addon_id=request.form.get("addon_id"),
            document_id=request.form.get("document_id"),
        )
        flash("Значение надбавки успешно добавлено", category="success")
        return redirect(url_for(".addons_values_get", id_=request.form.get("addon_id")))
    return render_template(
        "tools/payment/addons_values_edit.html",
        title=f"Добавить значение надбавки",
        form=form,
    )


@bp.route("/payment/addons/<int:id_>/values/<int:value_id>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def addons_values_edit(value_id):
    value = PaymentAddonsValues.get(value_id)
    addons_items = PaymentAddons.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_addons_values_form(
        obj=value,
        addons_items=addons_items,
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentAddonsValues.update(
            value_id,
            name=request.form.get("name"),
            value=request.form.get("value"),
            description=request.form.get("description"),
            addon_id=request.form.get("addon_id"),
            document_id=request.form.get("document_id"),
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".addons_values_get", id_=request.form.get("addon_id")))
    return render_template(
        "tools/payment/addons_values_edit.html",
        title=f"Изменить значения надбавки",
        form=form,
        value=value,
    )


@bp.route("/payment/single_addons/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def single_addons_add():
    rate_items = PaymentRates.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_single_addons_form(
        rate_items=rate_items,
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentSingleAddons.create(
            slug=make_slug(request.form.get("name"), prefix="single_"),
            name=request.form.get("name"),
            value=request.form.get("value"),
            payment_name=request.form.get("payment_name"),
            description=request.form.get("description"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
            default_state=True if request.form.get("default_state") else False,
            document_id=request.form.get("document_id"),
            rates=[rate for rate in rate_items if request.form.get(rate.slug)],
        )
        flash("Фиксированную надбавка успешно добавлена", category="success")
        return redirect(url_for(".single_addons_get"))
    return render_template(
        "tools/payment/single_addons_edit.html",
        title=f"Добавить фиксированную надбавку",
        form=form,
    )


@bp.route("/payment/single_addons/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def single_addons_edit(id_):
    addon = PaymentSingleAddons.get(id_)
    rate_items = PaymentRates.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_single_addons_form(
        obj=addon,
        rate_items=rate_items,
        document_items=document_items,
    )
    for rate in addon.rates:
        if rate in rate_items:
            form.__getattribute__(rate.slug).data = True
    if request.method == "POST" and form.validate_on_submit():
        PaymentSingleAddons.update(
            id_,
            slug=make_slug(request.form.get("name"), prefix="single_"),
            name=request.form.get("name"),
            value=request.form.get("value"),
            payment_name=request.form.get("payment_name"),
            description=request.form.get("description"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
            default_state=True if request.form.get("default_state") else False,
            document_id=request.form.get("document_id"),
            rates=[rate for rate in rate_items if request.form.get(rate.slug)],
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".single_addons_get"))
    return render_template(
        "tools/payment/single_addons_edit.html",
        title=f"Изменить фиксированную надбавку #{id_}",
        form=form,
        addon=addon,
    )


@bp.route("/payment/increase/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def increase_add():
    rate_items = PaymentRates.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_increase_form(
        rate_items=rate_items,
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentIncrease.create(
            name=request.form.get("name"),
            value=request.form.get("value"),
            document_id=request.form.get("document_id"),
            rates=[rate for rate in rate_items if request.form.get(rate.slug)],
        )
        flash("Индексация успешно добавлена", category="success")
        return redirect(url_for(".increase_get"))
    return render_template(
        "tools/payment/increase_edit.html",
        title=f"Добавить индексацию",
        form=form,
    )


@bp.route("/payment/increase/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def increase_edit(id_):
    increase = PaymentIncrease.get(id_)
    rate_items = PaymentRates.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_increase_form(
        obj=increase,
        rate_items=rate_items,
        document_items=document_items,
    )
    for rate in increase.rates:
        if rate in rate_items:
            form.__getattribute__(rate.slug).data = True
    if request.method == "POST" and form.validate_on_submit():
        PaymentIncrease.update(
            id_,
            name=request.form.get("name"),
            value=request.form.get("value"),
            document_id=request.form.get("document_id"),
            rates=[rate for rate in rate_items if request.form.get(rate.slug)],
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".increase_get"))
    return render_template(
        "tools/payment/increase_edit.html",
        title=f"Изменить индексацию #{id_}",
        form=form,
        increase=increase,
    )


@bp.route("/payment/pension_duty/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def pension_duty_add():
    document_items = PaymentDocuments.get_all()
    form = create_pension_duty_form(
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentPensionDutyCoefficient.create(
            name=request.form.get("name"),
            value=request.form.get("value"),
            document_id=request.form.get("document_id"),
        )
        flash("Пенсионный коэффициент успешно добавлен", category="success")
        return redirect(url_for(".pension_duty_get"))
    return render_template(
        "tools/payment/pension_duty_edit.html",
        title=f"Добавить пенсионный коэффициент",
        form=form,
    )


@bp.route("/payment/pension_duty/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def pension_duty_edit(id_):
    pension_duty = PaymentPensionDutyCoefficient.get(id_)
    document_items = PaymentDocuments.get_all()
    form = create_pension_duty_form(
        obj=pension_duty,
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentPensionDutyCoefficient.update(
            id_,
            name=request.form.get("name"),
            value=request.form.get("value"),
            document_id=request.form.get("document_id"),
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".pension_duty_get"))
    return render_template(
        "tools/payment/pension_duty_edit.html",
        title=f"Изменить пенсионный коэффициент #{id_}",
        form=form,
        pension_duty=pension_duty,
    )


@bp.route("/payment/global_coefficient/add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def global_coefficient_add():
    document_items = PaymentDocuments.get_all()
    form = create_global_coefficient_form(
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentGlobalCoefficient.create(
            name=request.form.get("name"),
            slug=make_slug(request.form.get("name"), prefix="coeff_"),
            value=request.form.get("value"),
            payment_name=request.form.get("payment_name"),
            description=request.form.get("description"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
            document_id=request.form.get("document_id"),
        )
        flash("Глобальный коэффициент успешно добавлен", category="success")
        return redirect(url_for(".global_coefficient_get"))
    return render_template(
        "tools/payment/global_coefficient_edit.html",
        title=f"Добавить глобальный коэффициент",
        form=form,
    )


@bp.route("/payment/global_coefficient/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def global_coefficient_edit(id_):
    global_coefficient = PaymentGlobalCoefficient.get(id_)
    document_items = PaymentDocuments.get_all()
    form = create_global_coefficient_form(
        obj=global_coefficient,
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentGlobalCoefficient.update(
            id_,
            name=request.form.get("name"),
            slug=make_slug(request.form.get("name"), prefix="coeff_"),
            value=request.form.get("value"),
            payment_name=request.form.get("payment_name"),
            description=request.form.get("description"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
            document_id=request.form.get("document_id"),
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for(".global_coefficient_get"))
    return render_template(
        "tools/payment/global_coefficient_edit.html",
        title=f"Изменить глобальный коэффициент #{id_}",
        form=form,
        global_coefficient=global_coefficient,
    )


@dataclass
class PaymentDeleteView(View):
    """View класс для удаления записей."""

    template_name: str
    title: str
    payment_slug: str
    payment_class: db.Model
    methods = ["GET", "POST"]

    @permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self, del_id, **kwargs):
        data = self.payment_class.get(del_id)
        form = DeleteForm()
        if request.method == "POST" and form.validate_on_submit():
            message = self.payment_class.delete(del_id)
            flash(message, category="success")
            return redirect(url_for(f".{self.payment_slug}_get", **kwargs))
        return render_template(
            self.template_name,
            title=f"{self.title} #{del_id}",
            form=form,
            data=data,
            back_link=url_for(f".{self.payment_slug}_get", **kwargs),
        )


bp.add_url_rule(
    "/payment/documents/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "documents_delete",
        title="Удалить документ",
        template_name="tools/payment/data_delete.html",
        payment_slug="documents",
        payment_class=PaymentDocuments,
    ),
)

bp.add_url_rule(
    "/payment/rates/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "rates_delete",
        title="Удалить оклад",
        template_name="tools/payment/data_delete.html",
        payment_slug="rates",
        payment_class=PaymentRates,
    ),
)

bp.add_url_rule(
    "/payment/rates/<int:id_>/values/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "rates_values_delete",
        title="Удалить значение оклада",
        template_name="tools/payment/data_delete.html",
        payment_slug="rates_values",
        payment_class=PaymentRatesValues,
    ),
)

bp.add_url_rule(
    "/payment/addons/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "addons_delete",
        title="Удалить надбавку",
        template_name="tools/payment/data_delete.html",
        payment_slug="addons",
        payment_class=PaymentAddons,
    ),
)

bp.add_url_rule(
    "/payment/addons/<int:id_>/values/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "addons_values_delete",
        title="Удалить значение надбавки",
        template_name="tools/payment/data_delete.html",
        payment_slug="addons_values",
        payment_class=PaymentAddonsValues,
    ),
)

bp.add_url_rule(
    "/payment/single_addons/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "single_addons_delete",
        title="Удалить надбавку",
        template_name="tools/payment/data_delete.html",
        payment_slug="single_addons",
        payment_class=PaymentSingleAddons,
    ),
)

bp.add_url_rule(
    "/payment/increase/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "increase_delete",
        title="Удалить индексацию",
        template_name="tools/payment/data_delete.html",
        payment_slug="increase",
        payment_class=PaymentIncrease,
    ),
)

bp.add_url_rule(
    "/payment/pension_duty/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "pension_duty_delete",
        title="Удалить пенсионный коэффициент",
        template_name="tools/payment/data_delete.html",
        payment_slug="pension_duty",
        payment_class=PaymentPensionDutyCoefficient,
    ),
)

bp.add_url_rule(
    "/payment/global_coefficient/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "global_coefficient_delete",
        title="Удалить глобальный коэффициент",
        template_name="tools/payment/data_delete.html",
        payment_slug="global_coefficient",
        payment_class=PaymentGlobalCoefficient,
    ),
)


@bp.route("/payment/data", methods=["GET"])
@permission_required(PermissionsConfig.PAYMENTS_DATA_EDIT_PERMISSION)
@login_required
async def payment_data():
    data = {
        "Нормативные документы": url_for(".documents_get"),
        "Базовые оклады": url_for(".rates_get"),
        "Надбавки с множественным выбором": url_for(".addons_get"),
        "Фиксированные надбавки": url_for(".single_addons_get"),
        "Пенсионные коэффициенты": url_for(".pension_duty_get"),
        "Индексация": url_for(".increase_get"),
        "Глобальные коэффициенты": url_for(".global_coefficient_get"),
    }
    return render_template(
        "tools/payment/data_edit.html",
        title="Редактировать информацию",
        data=data,
    )

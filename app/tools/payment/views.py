from dataclasses import dataclass

from flask import render_template, request, flash, redirect, url_for
from flask.views import View
from flask_login import login_required, current_user

from app import db
from app.common.func.app_core import get_paginated_data, make_slug
from app.db.payment_models import (
    PaymentRate,
    PaymentAddons,
    PaymentSingleAddon,
    PaymentGlobalCoefficient,
    PaymentPensionDutyCoefficient,
    PaymentDocuments,
    PaymentIncrease, PaymentRateValues,
)
from config import FlaskConfig
from . import payment_bp as bp
from .forms import (
    create_payment_form,
    DeleteForm,
    DocumentsForm,
    create_increase_form,
    RatesForm, create_rate_values_form, create_pension_duty_form,
)


@bp.route("/payment", methods=["GET", "POST"])
async def payment_tool():
    rate_items: list = PaymentRate.get_all()
    addon_items: list = PaymentAddons.get_all()
    single_items: list = PaymentSingleAddon.get_all()
    pension_duty_items: list = PaymentPensionDutyCoefficient.get_all()
    payment_types: list[str] = ["salary", "pension"]

    form = create_payment_form(
        rate_items=rate_items,
        addon_items=addon_items,
        single_items=single_items,
        pension_duty_items=pension_duty_items,
    )

    if request.method == "POST" and form.validate_on_submit():
        payment_data: dict = {
            "salary_data": {},
            "salary_total": 0,
            "pension_data": {},
            "pension_total": 0,
        }

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
                                for rate in item.rate
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
                                for rate in item.rate
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
        item_value_id = int(request.form.get("pension_duty_years"))
        value_data = PaymentPensionDutyCoefficient.get(item_value_id)
        value = round(payment_data["pension_total"] * (value_data.value - 1), ndigits=2)
        payment_data["pension_data"]["pension_duty_years"] = {
            "name": f"{form.pension_duty_years.label.text} ({value_data.value:.0%})",
            "value": value,
            "value_name": value_data.name,
            "document": value_data.document.name,
        }
        payment_data["pension_total"] += value

        # Информация о глобальных коэффициентах
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
        payment_data["salary_total"] = round(payment_data["salary_total"], ndigits=2)
        payment_data["pension_total"] = round(payment_data["pension_total"], ndigits=2)

        return render_template(
            "tools/payment/payment.html", active="tools", form=form, payment_data=payment_data
        )
    return render_template("tools/payment/payment.html", active="tools", form=form)


@login_required
@bp.route("/payment/data", methods=["GET"])
async def payment_data():
    return render_template(
        "tools/payment/data_edit.html", title="Редактировать информацию"
    )


@dataclass
class PaymentGetView(View):
    """View класс для просмотра списка записей."""

    template_name: str
    title: str
    payment_class: db.Model
    methods = ["GET", "POST"]

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
        payment_class=PaymentRate,
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


@login_required
@bp.route("/payment/documents/add", methods=["GET", "POST"])
async def documents_add():
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
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


@login_required
@bp.route("/payment/documents/<int:id_>", methods=["GET", "POST"])
async def documents_edit(id_):
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
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


@login_required
@bp.route("/payment/rates/add", methods=["GET", "POST"])
async def rates_add():
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
    form = RatesForm()
    if request.method == "POST" and form.validate_on_submit():
        PaymentRate.create(
            name=request.form.get("name"),
            slug=make_slug(request.form.get("name"), prefix="rate_"),
            payment_name=request.form.get("payment_name"),
            salary=True if request.form.get("salary") else False,
            pension=True if request.form.get("pension") else False,
        )
        flash("Оклад успешно добавлен", category="success")
        return redirect(url_for(".rates_get"))
    return render_template(
        "tools/payment/rates_edit.html",
        title=f"Добавить оклад",
        form=form,
    )


@login_required
@bp.route("/payment/rates/<int:id_>", methods=["GET", "POST"])
async def rates_edit(id_):
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
    rate = PaymentRate.get(id_)
    form = RatesForm(obj=rate)
    if request.method == "POST" and form.validate_on_submit():
        PaymentRate.update(
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


@login_required
@bp.route("/payment/rates/<int:id_>/values", methods=["GET", "POST"])
async def rates_values_get(id_):
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
    rate = PaymentRate.get(id_)
    paginated_data = get_paginated_data(
        PaymentRateValues.query.filter_by(rate_id=id_)
    )
    return render_template(
        "tools/payment/rates_values.html",
        title=f'Значения оклада "{rate.name}"',
        paginated_data=paginated_data,
        rate=rate,
        rate_id=id_,
    )


@login_required
@bp.route("/payment/rates/<int:id_>/values/add", methods=["GET", "POST"])
async def rates_values_add(id_):
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
    rate_items = PaymentRate.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_rate_values_form(
        rate_items=rate_items,
        document_items=document_items,
        rate_id=id_
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentRateValues.create(
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
        title=f"Добавить значение оклада",
        form=form,
    )


@login_required
@bp.route("/payment/rates/<int:id_>/values/<int:value_id>", methods=["GET", "POST"])
async def rates_values_edit(id_, value_id):
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
    value = PaymentRateValues.get(value_id)
    rate_items = PaymentRate.get_all()
    document_items = PaymentDocuments.get_all()
    form = create_rate_values_form(
        obj=value,
        rate_items=rate_items,
        document_items=document_items,
    )
    if request.method == "POST" and form.validate_on_submit():
        PaymentRateValues.update(
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


@login_required
@bp.route("/payment/increase/add", methods=["GET", "POST"])
async def increase_add():
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
    rate_items = PaymentRate.get_all()
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


@login_required
@bp.route("/payment/increase/<int:id_>", methods=["GET", "POST"])
async def increase_edit(id_):
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
    increase = PaymentIncrease.get(id_)
    rate_items = PaymentRate.get_all()
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


@login_required
@bp.route("/payment/pension_duty/add", methods=["GET", "POST"])
async def pension_duty_add():
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
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
        flash("Данные сохранены", category="success")
        return redirect(url_for(".pension_duty_get"))
    return render_template(
        "tools/payment/pension_duty_edit.html",
        title=f"Добавить пенсионный коэффициент",
        form=form,
    )


@login_required
@bp.route("/payment/pension_duty/<int:id_>", methods=["GET", "POST"])
async def pension_duty_edit(id_):
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for(".payment_tool"))
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


@dataclass
class PaymentDeleteView(View):
    """View класс для удаления записей."""

    template_name: str
    title: str
    payment_slug: str
    payment_class: db.Model
    methods = ["GET", "POST"]

    @login_required
    async def dispatch_request(self, del_id, **kwargs):
        if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
            return redirect(url_for(".payment_tool"))
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
        payment_class=PaymentRate,
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
    "/payment/rates/<int:id_>/values/delete/<int:del_id>",
    view_func=PaymentDeleteView.as_view(
        "rates_values_delete",
        title="Удалить значение оклада",
        template_name="tools/payment/data_delete.html",
        payment_slug="rates_values",
        payment_class=PaymentRateValues
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

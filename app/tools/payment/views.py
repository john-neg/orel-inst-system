from flask import render_template, request, flash, redirect, url_for

from app.db.payment_models import (
    PaymentRate,
    PaymentAddons,
    PaymentSingleAddon,
    PaymentGlobalCoefficient,
    PaymentPensionDutyCoefficient, PaymentDocuments,
)

from . import payment_bp as bp
from .forms import create_payment_form, DocumentsEditForm, DeleteForm, DocumentsAddForm
from ...common.func.app_core import get_paginated_data


@bp.route("/payment", methods=["GET", "POST"])
async def payment_tool():
    rate_items: list = PaymentRate.get_all()
    addon_items: list = PaymentAddons.get_all()
    single_items: list = PaymentSingleAddon.get_all()
    payment_types: list[str] = ["salary", "pension"]

    form = create_payment_form(
        rate_items=rate_items,
        addon_items=addon_items,
        single_items=single_items,
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
            "tools/payment.html", active="tools", form=form, payment_data=payment_data
        )
    return render_template("tools/payment.html", active="tools", form=form)


@bp.route("/payment/data", methods=["GET"])
async def payment_data():
    return render_template(
        "tools/payment_data_edit.html",
        title="Редактировать информацию"
    )


@bp.route("/payment/documents", methods=["GET"])
async def documents_get():
    paginated_data = get_paginated_data(PaymentDocuments.query)
    return render_template(
        "tools/payment_documents.html",
        title="Нормативные документы",
        paginated_data=paginated_data,
    )


@bp.route("/payment/documents/add", methods=["GET", "POST"])
async def documents_add():
    form = DocumentsAddForm()
    if request.method == "POST" and form.validate_on_submit():
        PaymentDocuments.create(name=request.form.get('name'))
        flash("Документ успешно добавлен", category="success")
        return redirect(url_for("tools.payment.documents_get"))
    return render_template(
        "tools/payment_documents_edit.html",
        title=f"Добавить документ",
        form=form,
    )


@bp.route("/payment/documents/edit/<int:document_id>", methods=["GET", "POST"])
async def documents_edit(document_id):
    document = PaymentDocuments.get(document_id)
    form = DocumentsEditForm(obj=document)

    if request.method == "POST" and form.validate_on_submit():
        PaymentDocuments.update(
            document_id,
            name=request.form.get('name'),
        )
        flash("Данные обновлены", category="success")
        return redirect(url_for("tools.payment.documents_get"))

    return render_template(
        "tools/payment_documents_edit.html",
        title=f"Изменить документ #{document_id}",
        form=form,
    )


@bp.route("/payment/documents/delete/<int:document_id>", methods=["GET", "POST"])
async def documents_delete(document_id):
    document = PaymentDocuments.get(document_id)
    form = DeleteForm()
    if request.method == "POST" and form.validate_on_submit():
        message = PaymentDocuments.delete(document_id)
        flash(message, category="success")
        return redirect(url_for("tools.payment.documents_get"))
    return render_template(
        "tools/payment_data_delete.html",
        title=f"Удалить документ #{document_id}",
        form=form,
        document=document,
    )
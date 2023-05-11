from flask import render_template, request

from app.db.payment_models import (
    PaymentRate,
    PaymentAddons,
    PaymentSingleAddon,
    PaymentGlobalCoefficient,
    PaymentPensionDutyCoefficient,
)

from . import payment_bp as bp
from .forms import create_payment_form


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
        value_data = PaymentPensionDutyCoefficient.get_item(item_value_id)
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

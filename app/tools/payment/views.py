from flask import render_template, request

from app.db.payment_models import (
    PaymentRate,
    PaymentAddons,
    PaymentSingleAddon,
    PaymentGlobalCoefficient,
)

from app.tools.payment import payment_bp as bp
from app.tools.payment.forms import create_payment_form


@bp.route("/payment", methods=["GET", "POST"])
async def payment():
    rate_items = PaymentRate.get_all()
    addon_items = PaymentAddons.get_all()
    single_items = PaymentSingleAddon.get_all()

    form = create_payment_form(
        rate_items=rate_items,
        addon_items=addon_items,
        single_items=single_items,
    )

    if request.method == "POST":
        payment_data = {
            "salary_data": {},
            "salary_total": 0,
            "pension_data": {},
            "pension_total": 0,
        }

        for item in rate_items:
            value = int(request.form.get(item.slug))
            if item.salary:
                payment_data["salary_data"][item.slug] = {
                    "name": item.payment_name,
                    "value": value,
                    "description": item.description,
                }
                if item.increase:
                    payment_data["salary_data"][item.slug]["increase"] = item.increase
                payment_data["salary_total"] += value
            if item.pension:
                payment_data["pension_data"][item.slug] = {
                    "name": item.payment_name,
                    "value": int(request.form.get(item.slug)),
                    "description": item.description,
                }
                if item.increase:
                    payment_data["pension_data"][item.slug]["increase"] = item.increase
                payment_data["pension_total"] += value

        for item in addon_items:
            addon_coeff = float(request.form.get(item.slug))
            if item.salary:
                value = sum(
                    [
                        round(
                            payment_data["salary_data"].get(rate.slug).get("value")
                            * addon_coeff
                            + 0.1
                        )
                        for rate in item.rate
                    ]
                )
                if value:
                    payment_data["salary_data"][item.slug] = {
                        "name": f"{item.payment_name} ({int(addon_coeff * 100)}%)",
                        "value": value,
                        "description": item.description,
                    }
                    payment_data["salary_total"] += value
            if item.pension:
                value = sum(
                    [
                        round(
                            payment_data["pension_data"].get(rate.slug).get("value")
                            * addon_coeff
                            + 0.1
                        )
                        for rate in item.rate
                    ]
                )
                if value:
                    payment_data["pension_data"][item.slug] = {
                        "name": f"{item.payment_name} ({int(addon_coeff * 100)}%)",
                        "value": value,
                        "description": item.description,
                    }
                    payment_data["pension_total"] += value

        for item in single_items:
            if request.form.get(item.slug):
                if item.salary:
                    value = sum(
                        [
                            round(
                                payment_data["salary_data"].get(rate.slug).get("value")
                                * item.value
                                + 0.1
                            )
                            for rate in item.rate
                        ]
                    )
                    payment_data["salary_data"][item.slug] = {
                        "name": f"{item.payment_name} ({int(item.value * 100)}%)",
                        "value": value,
                        "description": item.description,
                    }
                    payment_data["salary_total"] += value
                if item.pension:
                    value = sum(
                        [
                            round(
                                payment_data["pension_data"].get(rate.slug).get("value")
                                * item.value
                                + 0.1
                            )
                            for rate in item.rate
                        ]
                    )
                    payment_data["pension_data"][item.slug] = {
                        "name": f"{item.payment_name} ({int(item.value * 100)}%)",
                        "value": value,
                        "description": item.description,
                    }
                    payment_data["pension_total"] += value

        duty_coeff = float(request.form.get("pension_duty_years"))
        value = round(payment_data["pension_total"] * (duty_coeff - 1))
        payment_data["pension_data"]["pension_duty_years"] = {
            "name": f"{form.pension_duty_years.label.text} ({int(duty_coeff * 100)}%)",
            "value": value,
        }
        payment_data["pension_total"] += value

        for item in PaymentGlobalCoefficient.get_all():
            if item.salary:
                value = round(payment_data["salary_total"] * (float(item.value) - 1))
                payment_data["salary_data"][item.slug] = {
                    "name": f"{item.payment_name}",
                    "value": value,
                    "description": item.description,
                }
                payment_data["salary_total"] += value
            if item.pension:
                value = round(payment_data["pension_total"] * (float(item.value) - 1))
                payment_data["pension_data"][item.slug] = {
                    "name": f"{item.payment_name}",
                    "value": value,
                    "description": item.description,
                }
                payment_data["pension_total"] += value
        return render_template(
            "tools/payment.html", active="tools", form=form, payment_data=payment_data
        )
    return render_template("tools/payment.html", active="tools", form=form)

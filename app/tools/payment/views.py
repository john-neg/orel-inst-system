import json
import os

from flask import render_template, request

from app.common.func.app_core import read_json_file
#
from app.tools.payment import payment_bp as bp
from app.tools.payment.forms import PaymentForm
from config import BASEDIR

PAYMENT_FILE_DIR = os.path.join(BASEDIR, "app", "tools", "payment", )
rates_data = read_json_file(os.path.join(PAYMENT_FILE_DIR, "rates_data.json"))


@bp.route("/payment", methods=["GET", "POST"])
async def payment():
    form = PaymentForm()
    position = request.form.get("base_position")
    years_of_duty =  request.form.get("years_of_duty")
    police_rank = request.form.get("police_rank")


    #     temperature = request.form.get("temperature")
    #     top_k = request.form.get("top_k")
    #     top_p = request.form.get("top_p")
    #     repetition_penalty = request.form.get("repetition_penalty")
    #     num_return_sequences = request.form.get("num_return_sequences")
    #     text, text_all = {}, []
    #     status = await rewriter("", get_code=True)
    #
    #     if request.method == "POST":
    #         source_text = request.form.get("rewriter_text").rstrip().split('\r\n')
    #         for paragraph in source_text:
    #             if paragraph:
    #                 response = await rewriter(
    #                         paragraph,
    #                         temperature=float(temperature),
    #                         top_k=int(top_k),
    #                         top_p=float(top_p),
    #                         repetition_penalty=float(repetition_penalty),
    #                         num_return_sequences=int(num_return_sequences),
    #                     )
    #                 if response.get('prediction_best'):
    #                     text = await combine_dict(
    #                         text,
    #                         response.get('prediction_best')
    #                     )
    #                     text_all.append(response.get('predictions_all'))
    #                 elif response.get('origin'):
    #                     del response['origin']
    #                     text = await combine_dict(
    #                         text,
    #                         response
    #                     )
    #                 else:
    #                     error = {'ERROR': 'Произошла ошибка на удаленном сервере'}
    #                     text = await combine_dict(
    #                         text,
    #                         error
    #                     )
    #
    return render_template(
        "tools/payment.html",
        active="tools",
        form=form
    )

from flask import render_template, request

from . import bp
from .forms import RewriterForm
from .func import rewriter, combine_dict


@bp.route("/rewriter", methods=["GET", "POST"])
async def field_edit():
    form = RewriterForm()
    temperature = request.form.get("temperature")
    top_k = request.form.get("top_k")
    top_p = request.form.get("top_p")
    repetition_penalty = request.form.get("repetition_penalty")
    num_return_sequences = request.form.get("num_return_sequences")
    text, text_all = {}, []
    status = await rewriter("", get_code=True)

    if request.method == "POST":
        source_text = request.form.get("rewriter_text").rstrip().split('\r\n')
        for paragraph in source_text:
            if paragraph:
                response = await rewriter(
                        paragraph,
                        temperature=float(temperature),
                        top_k=int(top_k),
                        top_p=float(top_p),
                        repetition_penalty=float(repetition_penalty),
                        num_return_sequences=int(num_return_sequences),
                    )
                text = await combine_dict(
                    text,
                    response.get('prediction_best')
                )
                text_all.append(response.get('predictions_all'))

    return render_template(
        "tools/rewriter.html",
        active="tools",
        form=form,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        num_return_sequences=num_return_sequences,
        text=text,
        text_all=text_all,
        status=status,
    )

from flask import render_template, request

from . import bp
from .forms import RewriterForm
from .func import rewriter, combine_dict


@bp.route("/rewriter", methods=["GET", "POST"])
async def field_edit():
    form = RewriterForm()
    text = {}
    status = await rewriter("", get_code=True)

    if request.method == "POST":
        source_text = request.form.get("rewriter_text").rstrip().split('\r\n')
        for paragraph in source_text:
            if paragraph:
                text = await combine_dict(
                    text,
                    await rewriter(paragraph)
                )

    return render_template(
        "tools/rewriter.html",
        active="tools",
        form=form,
        text=text,
        status=status,
    )
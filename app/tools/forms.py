from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    TextAreaField,
)


class RewriterForm(FlaskForm):
    rewriter_text = TextAreaField("Введите текст")
    do_rewrite = SubmitField("Rewrite")

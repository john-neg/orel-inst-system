from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    TextAreaField, FloatField, IntegerField,
)
from wtforms.validators import DataRequired, NumberRange


class RewriterForm(FlaskForm):
    rewriter_text = TextAreaField("Введите текст")
    temperature = FloatField(
        "Температура текста",
        default=0.95,
        validators=[DataRequired(), NumberRange(min=0.1, max=1)]
    )
    top_k = IntegerField(
        "top_k",
        default=40,
        validators=[DataRequired(), NumberRange(min=1, max=100)]
    )
    top_p = FloatField(
        "top_p",
        default=0.95,
        validators=[DataRequired(), NumberRange(min=0.1, max=1)]
    )
    repetition_penalty = FloatField(
        "Штраф за повтор",
        default=3,
        validators=[DataRequired(), NumberRange(min=0.1, max=5)]
    )
    num_return_sequences = IntegerField(
        "Кол-во примеров для выбора",
        default=7,
        validators=[DataRequired(), NumberRange(min=1, max=15)]
    )
    do_rewrite = SubmitField("Rewrite")

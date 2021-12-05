from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired


class ChoosePlan(FlaskForm):
    edu_spec = SelectField("Специальность:", coerce=str, validators=[DataRequired()])
    edu_plan = SelectField(
        "План:", coerce=str, validators=[DataRequired()], validate_choice=False
    )

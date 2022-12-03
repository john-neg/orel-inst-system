import logging
import operator
import os

from flask import render_template, request, redirect, url_for, flash

from app.tools import bp
from app.tools.forms import RewriterForm
from app.tools.func import rewriter


@bp.route("/rewriter", methods=["GET", "POST"])
async def field_edit():
    form = RewriterForm()
    text = ""

    if request.method == "POST":
        source_text = request.form.get("rewriter_text")
        text = await rewriter(source_text)

    return render_template(
        "tools/rewriter.html",
        active="tools",
        form=form,
        text=text,
    )


    #     parameter = request.form.get("program_fields")
    #     if request.form.get("fields_data"):
    #         return redirect(
    #             url_for("programs.field_edit", wp_id=program_id, parameter=parameter)
    #         )
    #     if request.form.get("field_update") and form.validate_on_submit():
    #         load_data = request.form.get("field_edit")
    #         kwargs = {parameter: load_data}
    #         try:
    #             await edit_work_programs_data(program_id, **kwargs)
    #             flash("Данные обновлены", category="success")
    #         except ApeksWrongParameterException:
    #             if parameter == "department_data":
    #                 parameter1 = Apeks.MM_WORK_PROGRAMS.get("date_department")
    #                 d = (
    #                     load_data.split("\r\n")[0]
    #                     .replace("Дата заседания кафедры:", "")
    #                     .replace(" ", "")
    #                 )
    #                 d = datetime.strptime(d, "%d.%m.%Y")
    #                 p1_data = date.isoformat(d)
    #                 parameter2 = Apeks.MM_WORK_PROGRAMS.get("document_department")
    #                 p2_data = (
    #                     load_data.split("\r\n")[1]
    #                     .replace("Протокол №", "")
    #                     .replace(" ", "")
    #                 )
    #                 kwargs = {parameter1: p1_data, parameter2: p2_data}
    #                 await edit_work_programs_data(program_id, **kwargs)
    #                 flash("Данные обновлены", category="success")
    #             else:
    #                 flash(f"Передан неверный параметр: {parameter}", category="danger")

    # work_program_data = await get_work_programs_data(
    #     id=program_id, fields=db_fields, sections=db_sections
    # )
    # try:
    #     form.field_edit.data = work_program_get_parameter_info(
    #         work_program_data[program_id], parameter
    #     )
    # except ApeksWrongParameterException:
    #     form.field_edit.data = (
    #         f"ApeksWrongParameterException {work_program_data[program_id]}"
    #     )
    #     flash(f"Передан неверный параметр: {parameter}", category="danger")
    # except ApeksParameterNonExistException:
    #     await work_program_add_parameter(program_id, parameter)
    #     form.field_edit.data = ""

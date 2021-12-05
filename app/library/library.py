from flask import render_template
from flask_login import login_required
from app.library import bp


@bp.route("/library")
@login_required
def library():
    return render_template("library/library.html", active="library")

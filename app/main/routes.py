from flask import render_template, redirect, url_for
from app.main import bp

@bp.route("/")
def index():
    return redirect(url_for("blockly.editor"))

@bp.route("/about")
def about():
    return render_template("about.html")



from flask import Blueprint, render_template

attack = Blueprint("attack", __name__)

@attack.route("/attack")
def playground():
    return render_template("attack.html")
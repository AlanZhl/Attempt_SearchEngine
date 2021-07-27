from flask import Blueprint, render_template, request
from app.utils import checkExistence
from app.models import db, Users

users = Blueprint("users", __name__)


@users.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]

        # post-check on the request form
        errors = checkExistence(name, email)
        if role == "":
            errors.append("Role of the user must be specified.")
        
        if len(errors) > 0:
            return render_template("register.html", errors=errors)
        else:
            newUser = Users(name=name, role=role, email=email, password=password)
            db.session.add(newUser)
            db.session.commit()
            db.session.close()
            return render_template("register.html")
    else:
        return render_template("register.html")
from flask import Blueprint, render_template, request
from app.utils import checkByEmail, checkByName, checkExistence
from app.models import db, Users


users = Blueprint("users", __name__)


@users.route("/register", methods=["POST", "GET"])
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


@users.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        mode = request.form["mode"]
        identity = request.form["identity"]
        password = request.form["password"]

        errors = []
        if mode == "name":
            errors.extend(checkByName(identity, password))
        else:
            errors.extend(checkByEmail(identity, password))

        if len(errors) > 0:
            return render_template("login.html", errors=errors)
        user = Users.query.filter_by(name=identity).first() if mode == "name" else Users.query.filter_by(email=identity).first()
        return render_template("job_search.html", name=user.name)
    else:
        return render_template("login.html")
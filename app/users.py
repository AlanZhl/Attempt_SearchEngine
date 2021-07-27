from flask import Blueprint, render_template, request

users = Blueprint("users", __name__)


@users.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]

        errors = []
        if role == "":
            errors.append("Role of the user must be specified.")
        if len(password) < 8 or len(password) > 20:
            errors.append("Length of your password must be within 8 and 20 characters.")
        
        if len(errors) > 0:
            return render_template("register.html", errors=errors)
        else:
            return render_template("register.html")
    else:
        return render_template("register.html")
from app.models import Users


# used for name and email checks in a registration process
def checkExistence(name, email):
    exist_name = Users.query.filter_by(name=name).first()
    exist_email = Users.query.filter_by(email=email).first()
    errors = []
    if exist_name:
        errors.append("Your user name has been used. Pls use a new name.")
    if exist_email:
        errors.append("Your email has been registered. Pls try a new one.")
    return errors
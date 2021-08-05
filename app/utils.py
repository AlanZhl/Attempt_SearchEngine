from passlib.hash import bcrypt_sha256
from datetime import date, timedelta

from app.models import Users, JobPost, MyError


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


# used for name and password checks when trying to login in with username
def checkByName(name, password):
    user = Users.query.filter_by(name=name).first()
    errors = []
    if user is None:
        errors.append("No such user exists, pls check your inputs.")
    elif not bcrypt_sha256.verify(str(password), user.password):
        errors.append("Password does not match the given user. Pls try again.")
    return errors


# used for email and password checks when trying to login in with email
def checkByEmail(email, password):
    user = Users.query.filter_by(email=email).first()
    errors = []
    if user is None:
        errors.append("No user with this email exists, pls check your inputs.")
    elif not bcrypt_sha256.verify(str(password), user.password):
        errors.append("Password does not match the given user. Pls try again.")
    return errors


# turn a MySQL record object into a displayable post
def create_post(record):
    post = {}
    post["post_id"] = record.post_id
    post["title"] = record.title
    post["link"] = "https://" + record.link
    post["company"] = record.company
    post["salary_min"] = record.salary_min
    post["salary_max"] = record.salary_max
    post["salary"] = "not given" if record.salary_max == 0 \
                    else " - ".join(["$" + str(record.salary_min), "$" + str(record.salary_max)])
    post["date"] = record.date

    return post


# filter from a list of displayable results (format shown in function "create_post")
def filter_results(results, kw, val):
    filtered_results = []
    if kw == "date":
        val_num = int(val)
        if val_num == 1000:
            filtered_results = results
        else:
            today = date.today()
            for post in results:
                delta = today - post["date"]
                if delta.days <= val_num:
                    filtered_results.append(post)
    elif kw == "salary":
        if val == "None":
            for post in results:
                if post["salary"] == "not given": 
                    filtered_results.append(post)
        elif val == "all":
            filtered_results = results
        else:
            category, thres_str = val.split("_")
            thres = int(thres_str)
            if category == "min":
                for post in results:
                    if post["salary_min"] >= thres:
                        filtered_results.append(post)
            else:
                for post in results:
                    if post["salary_max"] >= thres:
                        filtered_results.append(post)
    else:
        MyError.display("JobFilter Error" + MyError.UI_REQUEST_UNKNOWN + "unknown keyword sent by UI.")
        return results

    return filtered_results


# sort a list of displayable results
def sort_results(results, kw, val):
    print(kw, val)
    return results
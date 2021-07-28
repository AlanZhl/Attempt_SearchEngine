from flask import Blueprint
from flask.templating import render_template


jobs = Blueprint("jobs", __name__)


@jobs.route("/", methods=["POST", "GET"])
def job_searching():
    return render_template("job_search.html")
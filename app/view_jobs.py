from datetime import datetime
import elasticsearch
from elasticsearch import helpers
from flask import Blueprint, request, session, make_response
from flask.templating import render_template
from werkzeug.utils import redirect

from app.models import db, es, JobPost, Permissions, Users, MyError
from app.common import permission_check
from .utils import create_post, filter_results, sort_results, genESPost


query = {
    "_source": ['post_id'],
    "size": 200,
    "query": {
        "multi_match": {
            "query": "software",
            "type": "best_fields",
            "fields": ["title", "description"],
            "tie_breaker": 0.3
        }
    }
}    # return 200 results a time in real practice


jobs = Blueprint("jobs", __name__)


@jobs.route("/", methods=["POST", "GET"])
def job_searching():
    posts = session.get("search_results")
    if request.method == "POST":
        info = request.form
        print(info)
        keys = info.keys()
        # case 0: show the favored posts of the user
        if "show_favors" in keys:
            return redirect("/job_favors")
        # case 1: receiving request from the search bar
        elif "keyword" in keys:
            query["query"]["multi_match"]["query"] = info["keyword"]
            response = es.search(index="index_jobposts", body=query)["hits"]["hits"]
            idx = 0
            id_dict = {}    # order of the results sorted by the scores
            for record in response:
                id_dict[record["_source"]["post_id"]] = idx
                idx += 1
            
            search_results = JobPost.query.filter(JobPost.post_id.in_(id_dict.keys()))
            displays = [None] * idx
            for record in search_results:
                displays[id_dict[record.post_id]] = create_post(record)    # reorder the search results as how they were returned from ES
            session["search_results"] = displays    # TODO: store the search results temporarily at the server
            return render_template("job_search.html", name=session.get("user_name"), posts=displays)
        # case 2: favor / unfavor a job post (stored in cookies)
        if "favor" in keys or "unfavor" in keys:
            id_str = request.cookies.get("favored_posts")
            resp = make_response(render_template("job_search.html", name=session.get("user_name"), posts=posts))
            if posts:
                if "favor" in keys:
                    val = int(info.get("favor"))
                    id = str(posts[val-1]["post_id"])
                    if not id_str:
                        resp.set_cookie("favored_posts", id, max_age=2592000)
                    else:
                        id_lst = id_str.split("_")
                        if id not in id_lst:
                            id_lst.append(id)
                            resp.set_cookie("favored_posts", "_".join(id_lst), max_age=2592000)
                else:
                    val = int(info.get("unfavor"))
                    if id_str:
                        id = str(posts[val-1]["post_id"])
                        id_lst = id_str.split("_")
                        if id in id_lst:
                            id_lst.remove(id)
                            resp.set_cookie("favored_posts", "_".join(id_lst), max_age=2592000)
            return resp
        # case 3: receiving response from the filters or sorters
        else:
            operated_results = posts
            if operated_results:
                for key, val in request.form.items():    # different filters and sorters can add up
                    operation, kw = key.split("_")
                    if operation == "filter":
                        operated_results = filter_results(operated_results, kw, val)    # non-destructive
                    else:
                        operated_results = sort_results(operated_results, kw, val)    # !! destructive
            return render_template("job_search.html", name=session.get("user_name"), posts=operated_results)
    else:
        return render_template("job_search.html", name=session.get("user_name"), posts=posts)


@jobs.route("/job_manage", methods=["POST", "GET"])
@permission_check(Permissions.JOB_MANAGE)
def job_managing():
    # pre-process to generate all the jobs posted by the company
    raw_posts = JobPost.query.filter_by(company=session.get("user_name")).all()
    posts = []
    for post in raw_posts:
        posts.append(create_post(post))

    if request.method == "POST":
        try:
            request_contents = request.form
            # case 1: jump to the creation page
            if "create" in request_contents.keys():
                return redirect("/job_create")
            # case 2: delete a job post (from both MySQL and ES)
            elif "delete" in request_contents.keys():
                idx = int(request_contents["delete"]) - 1
                post = posts.pop(idx)
                # step 1) delete from mySQL
                post_mysql = JobPost.query.filter_by(post_id=post["post_id"]).first()
                db.session.delete(post_mysql)
                db.session.commit()
                db.session.close()
                # step 2) delete from ES
                delete_query = {
                    "query": {
                        "match_phrase": {
                            "post_id": post["post_id"]
                        }
                    }
                }
                es.delete_by_query(index="index_jobposts", body=delete_query)
            # case 3: filter / sort the job posts
            else:
                operated_posts = posts
                for key, val in request_contents.items():
                    operation, kw = key.split("_")
                    if operation == "filter":
                        operated_posts = filter_results(operated_posts, kw, val)
                    else:
                        operated_posts = sort_results(operated_posts, kw, val)
                return render_template("job_manage.html", name=session.get("user_name"), posts=operated_posts)
        except Exception as e:
            print(e)
    return render_template("job_manage.html", name=session.get("user_name"), posts=posts)


@jobs.route("/job_create", methods=["POST", "GET"])
@permission_check(Permissions.JOB_CREATE)
def create_jobpost():
    if request.method == "POST":
        try:
            # post creation for MySQL
            raw_content = request.form
            post = {}
            post["title"] = raw_content["title"]
            post["company"] = session.get("user_name")
            post["salary"] = " - ".join(["$" + str(raw_content["salary_min"]), "$" + str(raw_content["salary_max"])])
            post["date"] = "Today"
            post["snippet"] = raw_content["description"]
            db.session.add(JobPost(title=post["title"], link=None, company=post["company"], \
                salary=post["salary"], date=post["date"], description=post["snippet"]))
            db.session.commit()
            db.session.close()

            # post creation for ES
            id = JobPost.query.filter_by(title=post["title"], company=post["company"]).first().post_id
            es_post = [genESPost(post, id)]
            helpers.bulk(es, es_post)
            return redirect("/job_manage")
        except Exception as e:
            MyError.display("Post Creation Error", MyError.MYSQL_CREATE_FAIL, "fail to create a new job post")
            print(e)
            return render_template("job_create.html", errors=["Sorry, job creation failed due to server error."])
    return render_template("job_create.html")


@jobs.route("/job_favors", methods=["POST", "GET"])
def show_favors():
    id_str = request.cookies.get("favored_posts")
    print(id_str)
    posts = []
    if id_str:
        id_lst = []
        id_str_lst = id_str.split("_")
        for id in id_str_lst:
            id_lst.append(int(id))
        raw_posts = JobPost.query.filter(JobPost.post_id.in_(id_lst))
        for post in raw_posts:
            posts.append(create_post(post))
    return render_template("job_favors.html", name=session.get("user_name"), posts=posts)
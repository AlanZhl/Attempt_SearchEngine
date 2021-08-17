from app.view_users import register
import elasticsearch
from elasticsearch import helpers
from flask import Blueprint, request, session, make_response
from flask.templating import render_template
from werkzeug.utils import redirect

from app.models import db, es, Users, JobPost, Permissions, MyError
from app.common import permission_check
from .config import Config
from .utils import create_post, get_post_MySQL, filter_results, sort_results, genESPost, \
                split_keyword, transfer_history_2dict, transfer_history_2str, get_hotspots



jobs = Blueprint("jobs", __name__)


@jobs.route("/", methods=["POST", "GET"])
def job_searching():
    posts = session.get("search_results")
    if posts == None: posts = []    # ensure var "posts" is a list (iterable)
    role = 0
    if session.get("user_id"):
        role = Users.query.filter_by(user_id=session["user_id"]).first().role_id

    if request.method == "POST":
        info = request.form
        keys = info.keys()

        # case 1: log out / show favors for a current user
        if "logout" in keys or "show_favors" in keys:
            if "logout" in keys:
                # when attempting to logout, the session and cookies of the former user would be cleared!
                if session.get("user_id"): session.clear()
                resp = make_response(redirect("/login"))
                resp.delete_cookie("favored_posts")
                resp.delete_cookie("search_history")
                return resp
            else:
                return redirect("/job_favors")

        # case 2: log in / register for a tourist
        elif "login" in keys or "register" in keys:
            if "login" in keys:
                return redirect("/login")
            else:
                return redirect("/register")

        # case 3: redirect to "job_manage.html"/"user_manage.html"
        elif "manage_posts" in keys or "manage_users" in keys:
            if "manage_posts" in keys:
                return redirect("/job_manage")
            else:
                return redirect("/user_manage")

        # case 4: receiving request from the search bar
        elif "keyword" in keys:
            # step 1) record the resulting post ids from es
            query = Config.QUERY.copy()
            query["query"]["multi_match"]["query"] = info["keyword"]
            response = es.search(index="index_jobposts", body=query)["hits"]["hits"]
            # step 2) retrieve the records from MySQL and rearrange them according to the order in id_dict (match scores)
            # TODO: store the search results temporarily at the server
            session["search_results"] = get_post_MySQL(response)
            # step 3) record the search history and render the resulting page
            words = split_keyword(es, info["keyword"])
            history = transfer_history_2dict(request.cookies.get("search_history"))
            for word in words:
                if history.get(word):
                    history[word] += 1
                else:
                    history[word] = 1
            resp = make_response(render_template("job_search.html", \
                name=session.get("user_name"), posts=session["search_results"], role=role))
            resp.set_cookie("search_history", transfer_history_2str(history), max_age=2592000)
            return resp

        # case 5: favor / unfavor a job post (stored in cookies)
        elif "favor" in keys or "unfavor" in keys:
            id_str = request.cookies.get("favored_posts")
            resp = make_response(render_template("job_search.html", \
                name=session.get("user_name"), posts=posts, role=role))
            if posts != []:
                # "favored_posts" are splitted with "_"
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

        # case 6: receiving response from the filters or sorters
        else:
            operated_results = posts
            if operated_results != []:
                for key, val in request.form.items():    # different filters and sorters can add up
                    operation, kw = key.split("_")
                    if operation == "filter":
                        operated_results = filter_results(operated_results, kw, val)    # non-destructive
                    else:
                        operated_results = sort_results(operated_results, kw, val)    # !! destructive
            return render_template("job_search.html", \
                name=session.get("user_name"), posts=operated_results, role=role)
    # get request processing (recommendation)
    else:
        recommend_posts = []
        favored_list = []
        history_str = request.cookies.get("search_history")
        favors = request.cookies.get("favored_posts")
        if favors:
            favored_str_list = favors.split("_")
            for id in favored_str_list:
                favored_list.append(int(id))
        if history_str:
            history_str, hotspots = get_hotspots(history_str)    # this function would change the order of history_str as well
            recommend_query = Config.QUERY.copy()
            recommend_query["size"] = 100
            recommend_query["query"]["multi_match"]["query"] = ", ".join(hotspots)
            response = es.search(index="index_jobposts", body=recommend_query)["hits"]["hits"]
            filtered_response = []
            cnt = 0    # show 10 recommended posts a time at most
            for record in response:
                if record["_source"]["post_id"] not in favored_list:
                    cnt += 1
                    filtered_response.append(record)
                if cnt == 10:
                    break
            recommend_posts = get_post_MySQL(filtered_response)
        return render_template("job_search.html", \
            name=session.get("user_name"), posts=recommend_posts, role=role)


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
            keys = request_contents.keys()

            # case 1: jump to the creation page
            if "create" in keys:
                return redirect("/job_create")

            # case 2: return to main page ("job_search.html")
            elif "return" in keys:
                return redirect("/")

            # case 3: delete a job post (from both MySQL and ES)
            elif "delete" in keys:
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

            # case 4: filter / sort the job posts
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
            raw_content = request.form
            keys = raw_content.keys()
            
            # case 1: cancel job creation
            if "cancel" in keys:
                return redirect("/job_manage")

            # case 2: submit a job creation form
            else:
                # post creation for MySQL
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
@permission_check(Permissions.JOB_FAVOR)
def show_favors():
    # preprocessing: find all the favored job posts
    id_str = request.cookies.get("favored_posts")
    id_str_lst = []    # id_str_lst and posts would be used throughout the function
    posts = []
    if id_str:
        id_str_lst = id_str.split("_")
        id_lst = []
        for id in id_str_lst:
            id_lst.append(int(id))
        raw_posts = JobPost.query.filter(JobPost.post_id.in_(id_lst))
        for post in raw_posts:
            posts.append(create_post(post))
    
    if request.method == "POST":
        request_content = request.form
        keys = request_content.keys()

        # case 1: return to main page (job_search.html)
        if "return" in keys:
            return redirect("/")

        # case 2: remove a favored post from the favored list
        elif "unfavor" in keys:
            try:
                if id_str:
                    idx = int(request_content.get("unfavor")) - 1
                    post = posts.pop(idx)
                    id = str(post["post_id"])
                    resp = make_response(render_template("job_favors.html", name=session.get("user_name"), posts=posts))
                    print("outside")
                    if id in id_str_lst:
                        print("inside")
                        id_str_lst.remove(id)
                        resp.set_cookie("favored_posts", "_".join(id_str_lst), max_age=2592000)
                    return resp
            except Exception as e:
                print(e)

        # case 3: sort the favored posts
        else:
            for key, val in request_content.items():
                operation, kw = key.split("_")
                if operation == "sort":
                    posts = sort_results(posts, kw, val)

    return render_template("job_favors.html", name=session.get("user_name"), posts=posts)
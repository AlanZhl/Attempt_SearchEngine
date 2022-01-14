from elasticsearch import helpers
from flask import Blueprint, request, session, make_response
from flask.templating import render_template
from werkzeug.utils import redirect
import redis
from time import time

from app.models import db, es, redis_pool, Users, JobPost, Permissions, MyError
from app.common import permission_check
from .config import Config
from .utils import create_post, gen_recommendations, get_post_MySQL, filter_results, \
                    sort_results, genESPost, split_keyword, transfer_history_2dict, \
                    transfer_history_2str, get_hotspots, update_all_history



jobs = Blueprint("jobs", __name__)


@jobs.route("/", methods=["POST", "GET"])
def job_searching():
    # preprocessing: record the latest search / recommendation results (as "posts") and the user role
    posts = session.get("search_results")
    if posts == None: posts = []    # ensure var "posts" is a list (iterable)

    role = 0
    if session.get("user_id"):
        role = Users.query.filter_by(user_id=session["user_id"]).first().role_id

    # process with "post" requests
    if request.method == "POST":
        info = request.form
        keys = info.keys()

        # case 1: log out / show favors for a current user
        if "logout" in keys or "show_favors" in keys:
            if "logout" in keys:
                if session.get("user_id"): session.clear()
                resp = make_response(redirect("/"))
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
            filtered_kw = info["keyword"]
            query = Config.QUERY.copy()
            query["query"]["multi_match"]["query"] = filtered_kw
            response = es.search(index="index_jobposts", body=query)["hits"]["hits"]
            # step 2) retrieve the records from MySQL and rearrange them according to the order in id_dict (match scores)
            session["search_results"] = get_post_MySQL(response)
            resp = make_response(render_template("job_search.html", \
                name=session.get("user_name"), posts=session["search_results"], role=role))
            if session["search_results"] != []:    # avoid recording null searches
                # step 3) record the search history and render the resulting page
                words = split_keyword(es, filtered_kw)
                history = transfer_history_2dict(session.get("search_history"))
                for word in words:
                    if history.get(word):
                        history[word] += 1
                    else:
                        history[word] = 1
                if session.get("user_id"):
                    session["search_history"] = transfer_history_2str(history)
                    db.session.query(Users).filter_by(user_id=session["user_id"]).update({"search_history" : session["search_history"]})
                    db.session.commit()
                    db.session.close()
                # step 4) record the search to redis for shared search histories as well
                redis_instance = redis.Redis(connection_pool=redis_pool, decode_responses=True)
                all_history = redis_instance.get("search_history_all")
                new_history = update_all_history(all_history, words)
                if new_history:
                    redis_instance.set("search_history_all", new_history)
            return resp

        # case 5: favor / unfavor a job post (stored in cookies)
        elif "favor" in keys or "unfavor" in keys:
            resp = make_response(render_template("job_search.html", \
                name=session.get("user_name"), posts=posts, role=role))
            if posts != [] and session.get("user_id"):
                # "favored_posts" are splitted with "&"
                if "favor" in keys:
                    val = int(info.get("favor"))
                    user = Users.query.filter_by(user_id=session["user_id"]).first()
                    post = JobPost.query.filter_by(post_id=posts[val-1]["post_id"]).first()
                    user.favors.append(post)
                    db.session.commit()
                else:
                    val = int(info.get("unfavor"))
                    user = Users.query.filter_by(user_id=session["user_id"]).first()
                    post = JobPost.query.filter_by(post_id=posts[val-1]["post_id"]).first()
                    for favor in user.favors:
                        if favor == post:
                            user.favors.remove(post)
                            break
                    db.session.commit()
            return resp

        # case 6: receiving response from the filters or sorters
        else:
            operated_results = posts
            if operated_results != []:
                for key, val in request.form.items():    # different filters and sorters can add up
                    operation, kw = key.split("_")
                    start_time = time()
                    if operation == "filter":
                        operated_results = filter_results(operated_results, kw, val)    # non-destructive
                        print("Filter time (dev version): ", time() - start_time)
                    else:
                        operated_results = sort_results(operated_results, kw, val)    # !! destructive
                        print("Sort time (dev version): ", time() - start_time)
            return render_template("job_search.html", \
                name=session.get("user_name"), posts=operated_results, role=role)
    
    # get request processing (recommendation)
    else:
        recommend_posts = []
        favored_list = []
        history_str = None
        if session.get("user_id"):
            user = Users.query.filter_by(user_id=session["user_id"]).first()
            history_str = user.search_history
            for post in user.favors:
                favored_list.append(post.post_id)
        
        # case 1: local search history found: use the 3 most frequently used keywords for recommendation
        if history_str:
            history_str_new, hotspots = get_hotspots(history_str)    # this function would change the order of history_str as well
            recommend_posts = gen_recommendations(es, hotspots, favored_list)
            resp = make_response(render_template("job_search.html", \
                name=session.get("user_name"), posts=recommend_posts, role=role))
            session["search_history"] = history_str_new
            db.session.query(Users).filter_by(user_id=session["user_id"]).update({"search_history" : history_str_new})
            db.session.commit()
            db.session.close()
            session["search_results"] = recommend_posts
            return resp
        else:
            redis_instance = redis.Redis(connection_pool=redis_pool)
            history_all = redis_instance.get("search_history_all")
            # case 2: search history for all users found: use the latest three keywords to generate recommendation
            if history_all:
                history_lst = history_all.decode("utf-8").split("&")
                latest_words = history_lst[-1:-4:-1]
                recommend_posts = gen_recommendations(es, latest_words, [])
            # case 3: use the latest 10 posts for recommendation
            else:
                posts = JobPost.query.order_by(JobPost.post_id.desc())[0:10]
                for post in posts:
                    recommend_posts.append(create_post(post))
            session["search_results"] = recommend_posts
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
    user = Users.query.filter_by(user_id=session["user_id"]).first()
    posts = user.favors
    
    if request.method == "POST":
        request_content = request.form
        keys = request_content.keys()

        # case 1: return to main page (job_search.html)
        if "return" in keys:
            return redirect("/")

        # case 2: remove a favored post from the favored list
        elif "unfavor" in keys:
            try:
                idx = int(request_content.get("unfavor")) - 1
                post = posts.pop(idx)    # post content displayed at frontend
                resp = make_response(render_template("job_favors.html", name=session.get("user_name"), posts=posts))
                user = Users.query.filter_by(user_id=session["user_id"]).first()
                for favor in user.favors:
                    if favor == post:
                        user.favors.remove(post)
                        break
                db.session.commit()
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
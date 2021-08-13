from datetime import datetime
import elasticsearch
from elasticsearch import helpers
from flask import Blueprint, request, session
from flask.templating import render_template
from werkzeug.utils import redirect

from app.models import db, es, JobPost, Permissions, Users, MyError
from app.common import permission_check
from .utils import create_post, filter_results, sort_results, genESPost


# temporary sample data
sample_data = [
    {
        "title": "Sofrware Engineer", 
        "link": "https://sg.indeed.com/pagead/clk?mo=r&ad=-6NYlbfkN0AuWpd06JaTHFjvTB_5q6-0gBNCyrzTNez_CNw5GfFr-Uvaof5dLYkpXw27dWLYNm-xa2NTOhaWsJIcFGY_PviZ18DfiyayAnH2x4AQ-DXLnPuw41TvRlXrUJVBLV3RxCukWhyi27D9SKPicRKdGvisheEPs2OXimYc59LWcHe4aMiedoH8Fhs4mKK30vCW5Ov5n94vVtNitjdJLSrFDr9TOHJiWKB0bEOkiibfWXaLbhxpxontuwzvgpsYX6ktEvaBY4bwCGhOms9BMJjPrnt7zo964QIiEAioF1O00mo4mFObxKwnOmJEr9cn-j-JkBlbuBO7L22xvkmSu5ypGROq_uae_fR_sZLxGytpJh8a9rByaANZ4TPYuJwE0AxPr0Lo3ZoKyGsWDNoEPYLaiEsgAzE2agvbC48T-1WK65vUmIBpxvq7n_sxs6TPOWZVou29BqqsJt1dHpXnXXQFF7sN4iNunqylGFJYGyeRg4fT6eLogJtC8KZqfW1EY4oXlKHsuAQZeqCM-PIhrmv0rYe-jOYFcJ4rL_CZsu55T_X304OFuzsZsmuDVq3Xovh928r5wB_FC1_TmkuHn5092DcMnqnKbX3f4DoKagFRUIn0CdzGZDXOgtAo-SLcROBx6EmZ6kbZjsvesYMHjNVc5YnD_f8p8oz9q-eNi1BMikbAzvUsqrlDwMKXcT_WS3Y4at-RQx_aKtgAgPe8jXEJsm0DH7GhpJI7y8f11owZdH4vl5QAaVJIGUL-ytiQBS-st7g=&p=0&fvj=0&vjs=3",
        "company": "SOFTENGER (SINGAPORE) PTE. LTD.",
        "salary": "$5000 - $6500 a month",
        "date": "2021-07-31"
    },
    {
        "title": "[EIPIC] Finance Executive", 
        "link": "https://sg.indeed.com/pagead/clk?mo=r&ad=-6NYlbfkN0AuWpd06JaTHFjvTB_5q6-0gBNCyrzTNez_CNw5GfFr-Uvaof5dLYkpQptHyIobf6wgmBdiqDP19eQfjBdkjP-eFEFNCevFTa36BnNQhcTk35iZlzBtnzuQ5xzVCsqGiEkrCEROfIb4oaoi0UStZrC6hN56Ieg2DFZ8rAfbGovtylZHntBJB1ZzVaKbd_vNxmm9g8XQ06EDSQsxxl4iwFNhJeIR2z6IeF3bO8626Mt47OHDzqI_jDGon2mFybJNpLByVeSg5ZydvwvE97_ZgeUEsQ6kxoILug_lWqlBeSzHTdKveI8ytiCGAu8t6wFc2IXXdvo9ECXhI10tpB3cE1Tutx5jH-IrlA98Fhfi7qe2qHqZTLRX6zp5vqIqdpcc0xTNg5JPCiQP4IcCpSBDlNeWTjOzRGrKbiaYTZArjRo8lob5V90yfC1u5c1lbTXhSUz6nFchfqN243nxQrI6_Zx61JoTUgewRhXDeCysf2DHVSpIJWi6hnQtQOyvCe5x-rl_O5narKrV6HPMD4mXwaeXYg2LEkKcmgu9GBWFLjSeeiE3nBX7nuMIIoiTyTOtOhE7NXRYqiZhujke9OVKSlI3VzkxlnRMdn7LdIBuov3GJFU49BX7K_k6lpC_cg-kMve3Uqj8D9rUwgahMF2AYTtFJ73auSWE0HefQw32IjX6SwW8jmi0jHJ67fuKev6jwGUII2-Gp1Oz3p4pcjEBvDzaXsLhBocS1o9kaxznhXmVtShnwoUNQcSlN1uiJpfDL25mWLLGFsr49TPRalzEog_PClS2CDAHF3wGfutzmP08VKkhml6i_EWy1zIRkOaYyY8=&p=1&fvj=0&vjs=3",
        "company": "THYE HUA KWAN MORAL CHARITIES LIMITED",
        "salary": "$2510 - $3030 a month",
        "date": "2021-07-31"
    },
    {
        "title": "Sofrware Engineer", 
        "link": "https://sg.indeed.com/rc/clk?jk=254952268b4e141e&fccid=8975b9f5b98c2e9d&vjs=3",
        "company": "A2000 Solutions Pte Ltd",
        "salary": "not given",
        "date": "2021-08-01"
    }
]

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
    if request.method == "POST":
        info = request.form
        keys = info.keys()
        # case 1: receiving request from the search bar
        if "keyword" in keys:
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
        # case 2: receiving response from the filters or sorters
        else:
            operated_results = session.get("search_results")
            if operated_results:
                for key, val in request.form.items():    # different filters and sorters can add up
                    operation, kw = key.split("_")
                    if operation == "filter":
                        operated_results = filter_results(operated_results, kw, val)
                    else:
                        operated_results = sort_results(operated_results, kw, val)
            return render_template("job_search.html", name=session.get("user_name"), posts=operated_results)
    else:
        return render_template("job_search.html", name=session.get("user_name"), posts=sample_data)


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
            print(request.form)    # just for test
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
        except Exception as e:
            print(e)
    return render_template("job_manage.html", name=session.get("user_name"), posts=posts)


# TODO: test the integrated process
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
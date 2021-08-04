from app.models.jobs import JobPost
from flask import Blueprint, request, session
from flask.templating import render_template

from app.models import es
from .utils import create_post


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
        if "keyword" in keys:
            query["query"]["multi_match"]["query"] = info["keyword"]
            response = es.search(index="index_jobposts", body=query)["hits"]["hits"]
            idx = 0
            id_dict = {}    # order of the results sorted by the scores
            for record in response:
                id_dict[record["_source"]["post_id"]] = idx
                idx += 1
            
            search_results = JobPost.query.filter(JobPost.post_id.in_(id_dict.keys()))
            displays = [None] * (idx + 1)
            # reorder the search results as how they were returned from ES
            for record in search_results:
                displays[id_dict[record.post_id]] = create_post(record)
            # TODO: store the search results temporarily at the server
            session["search_results"] = displays
        return render_template("job_search.html", name=session.get("user_name"), posts=session.get("search_results"))
    else:
        return render_template("job_search.html", name=session.get("user_name"), posts=sample_data)
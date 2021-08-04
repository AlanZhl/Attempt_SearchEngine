from app import create_app, db, es
from app.models import JobPost


app = create_app()

# test the return value of a query in elasticsearch
query = {
    "_source": ['post_id'],
    "size": 30,
    "query": {
        "multi_match": {
            "query": "software",
            "fields": ["title", "description"]
        }
    }
}    # return 300 results a time in real practice


# es query test
def test_ES_query():
    response = es.search(index="index_jobposts", body=query)["hits"]["hits"]
    print(len(response))
    id_lst = [record["_source"]["post_id"] for record in response]
    print(id_lst)


# mysql query test
def test_MySQL_query():
    posts = JobPost.query.filter(JobPost.post_id.in_([16, 17]))
    for post in posts:
        print(post.salary_min, post.salary_max, post.date)
        print(type(post.salary_min), type(post.date))



if __name__ == "__main__":
    # test_ES_query()
    test_MySQL_query()
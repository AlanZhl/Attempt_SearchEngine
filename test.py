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


def test_ES_create(id, title, company, description):
    create_es_test(es)
    body = {
        "post_id": id,
        "title": title,
        "company": company,
        "description": description
    }
    es.create(index="test_jobposts", id=123, body=body)


# mysql query test
def test_MySQL_query():
    posts = JobPost.query.filter(JobPost.post_id.in_([16, 17]))
    for post in posts:
        print(post.salary_min, post.salary_max, post.date)
        print(type(post.salary_min), type(post.date))


# create an ES index identical to the one used in the project
def create_es_test(es):
    mappings = {
        "mappings": {
            "properties": {
                "post_id": {
                    "type": "long",
                    "index": True
                },
                "title": {
                    "type": "text",
                    "index": True,
                    "analyzer": "default"
                },
                "company": {
                    "type": "text",
                    "index": True
                },
                "description": {
                    "type": "text",
                    "index": True,
                    "analyzer": "default"
                }
            }
        },
        "settings": {
            "number_of_replicas": 2,
            "number_of_shards": 5
        }
    }
    if not es.indices.exists(index="test_jobposts"):
        es.indices.create(index="test_jobposts", body=mappings)



if __name__ == "__main__":
    test_ES_create(123, "software engineer_for test", "test_company", "test description.")
    # test_MySQL_query()
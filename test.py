import redis

from app import create_app, db, es
from app.models import JobPost, redis_pool
from elasticsearch import client


app = create_app()

# test the return value of a query in elasticsearch
query = {
    "_source": ['post_id'],
    "size": 15,
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
    for item in response:
        print(item)
    #print(len(response))
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


def test_ES_analyze(kw):
    body = {
        "text": kw
    }
    es_client = client.IndicesClient(es)
    response = es_client.analyze(index="index_jobposts", body=body)
    for item in response["tokens"]:
        print(item)


# mysql query test
def test_MySQL_query():
    # posts = JobPost.query.filter(JobPost.post_id.in_([16, 17]))
    # for post in posts:
    #     print(post.salary_min, post.salary_max, post.date)
    #     print(type(post.salary_min), type(post.date))

    posts = JobPost.query.order_by(JobPost.post_id.desc())[0:10]
    for post in posts:
        print(post.post_id, post.title)


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


def test_redis_hashtable():
    r = redis.Redis(connection_pool=redis_pool)
    # r.hset("test_history", mapping={"software": 5, "java": 1, "python": 2})
    # print("creation succeeds!")
    # all_history = r.hgetall("test_history")
    # print(all_history, type(all_history))
    # r.hincrby("test_history", "software", 1)
    # print(r.hgetall("test_history"))
    key_lst = r.keys("session_*")
    print(key_lst)
    if key_lst:
        r.delete(*key_lst)
    print(r.keys("session_*"))


def test_redis_string():
    r = redis.Redis(connection_pool=redis_pool)
    r.set("test_history", "java_python_test_测试")
    retrieve = r.get("test_history")
    if retrieve:
        retrieve = retrieve.decode("utf-8")
    print(retrieve, type(retrieve))


if __name__ == "__main__":
    #test_ES_create(123, "software engineer_for test", "test_company", "test description.")
    test_MySQL_query()
    # test_ES_analyze("software, engineer, java, Java")
    # test_redis_string()
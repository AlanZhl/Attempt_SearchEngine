from app import create_app, db, es


app = create_app()

# test the return value of a query in elasticsearch
query = {
    "_source": ['post_id'],
    "size": 20,
    "query": {
        "match": {
            "title": "software"
        }
    }
}    # return 300 results a time in real practice
response = es.search(index="index_jobposts", body=query)["hits"]["hits"]
print(len(response))
for record in response:
    print(record)
    print()
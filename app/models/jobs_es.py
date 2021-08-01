def create_es(es):
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
    if not es.indices.exists(index="index_jobposts"):
        es.indices.create(index="index_jobposts", body=mappings)
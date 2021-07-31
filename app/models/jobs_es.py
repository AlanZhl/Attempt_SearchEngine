def create_es(es):
    mappings = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "index": True,
                    "analyzer": "default"
                },
                "link": {
                    "type": "text",
                    "index": True
                },
                "company": {
                    "type": "text",
                    "index": True
                },
                "salary_min": {
                    "type": "long",
                    "index": True
                },
                "salary_max": {
                    "type": "long",
                    "index": True
                },
                "date": {
                    "type": "date",
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
    es.indices.create(index="index_jobposts", body=mappings)
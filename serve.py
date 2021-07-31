from app import create_app, db, es
from app.jobscrawler import init_jobposts

app = create_app()

if __name__ == "__main__":
    init_jobposts(db, es, "software")
    app.run(debug = False, port = 9001)
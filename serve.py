from app import create_app, db
from app.jobscrawler import init_jobposts

app = create_app()

if __name__ == "__main__":
    init_jobposts(db, "software")
    app.run(debug = False, port = 9001)
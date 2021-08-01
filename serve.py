from app import create_app, db, es
# from app.jobscrawler import update_jobposts
from threads import ScrawlerThread


app = create_app()

if __name__ == "__main__":
    mission1 = ScrawlerThread(keyword="software", driver="chrome")
    mission2 = ScrawlerThread(keyword="IT", driver="firefox")

    mission1.start()
    mission2.start()
    # update_jobposts(db, es, "software", "opera")
    app.run(debug = False, port = 9001)
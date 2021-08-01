import threading
from app import db, es
from app.jobscrawler import update_jobposts


class ScrawlerThread(threading.Thread):
    def __init__(self, keyword, driver, pageStart=0, date=1):
        threading.Thread.__init__(self)
        self.db = db
        self.es = es
        self.keyword = keyword
        self.driver = driver
        self.pageStart = pageStart
        self.date = date


    def run(self):
        update_jobposts(self.db, self.es, self.keyword, self.driver, self.pageStart, self.date)

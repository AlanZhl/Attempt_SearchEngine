from . import db
from datetime import date, timedelta


class JobPost(db.Model):
    __tablename__ = "job_posts"
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True)
    link = db.Column(db.Text, nullable=True)
    company = db.Column(db.String(100), index=True)
    salary_min = db.Column(db.Integer, index=True)
    salary_max = db.Column(db.Integer, index=True)
    date = db.Column(db.Date, index=True)
    description = db.Column(db.Text)


    def __init__(self, title, link, company, salary, date, description):
        self.title = title
        self.link = link
        self.company = company
        self.salary_min, self.salary_max = JobPost.getSalary(salary)
        self.date = JobPost.getDate(date)
        self.description = description


    def __eq__(self, other):
        return self.post_id == other.post_id


    @staticmethod
    def getSalary(salary):
        # if no salary is provided
        if salary == "": return 0, 0

        words = salary.split(" ")
        divisor = 1 
        if "year" in words:
            divisor = 12
        elif "week" in words:
            divisor = 0.25
        
        lowest = 0
        highest = 0
        try:
            for word in words:
                if word.find("$") != -1:
                    if lowest == 0:
                        lowest = int("".join(word[1:].split(",")))
                    else:
                        highest = int("".join(word[1:].split(",")))
        except Exception as e:
            print("Parsing error: posiion: Jobpost.getSalary")
            print(e)
        return int(lowest // divisor), int(highest // divisor)


    @staticmethod
    def getDate(dateString):
        # if is posted today
        if dateString in ["今天", "刚刚发布", "Today", "Just posted"]:
            return date.today()
        else:
            # if is posted more than 1 month ago
            if "+" in dateString: return date.today() - timedelta(days=31)
            
            # default: posted within a month (30 days)
            num = ""
            for ch in dateString:
                ascii = ord(ch)
                if ascii >= 48 and ascii <= 57:
                    num += ch
                else:
                    break
            return date.today() - timedelta(days=int(num))


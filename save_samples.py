from datetime import date
from csv import DictReader, DictWriter

from app import db, es
from app.models import JobPost
from app.jobscrawler import create_jobposts_MySQL, create_jobposts_ES


# save samples collected from job scrawler
def save_samples():
    samples = JobPost.query.all()
    headers = ["post_id", "title", "link", "company", "salary", "date", "description"]
    posts = []
    for record in samples:
        posts.append(transfer_mysql_2dict(record))
    with open("samples.csv", "w", newline="", encoding="utf-8") as f:
        f_csv = DictWriter(f, fieldnames=headers)
        f_csv.writeheader()
        f_csv.writerows(posts)


def load_samples():
    with open("samples.csv", "r", newline="", encoding="utf-8") as f:
        f_csv = DictReader(f)
        posts = []
        for row in f_csv:
            posts.append(row)
        create_jobposts_MySQL(db, posts)
        create_jobposts_ES(es, posts)


# turn a MySQL record object into savable dict
def transfer_mysql_2dict(record):
    post = {}
    post["post_id"] = record.post_id
    post["title"] = record.title
    post["link"] = "https://" + record.link if record.link else None
    post["company"] = record.company
    salary_min = record.salary_min if record.salary_min > 0 else record.salary_max
    salary_max = record.salary_max if record.salary_max > 0 else record.salary_min
    if salary_min == 0 and salary_max == 0:
        post["salary"] = ""
    else:
        post["salary"] = " - ".join(["$"+str(salary_min), "$"+str(salary_max)])
    date_diff = (date.today() - record.date).days
    if date_diff == 0:
        post["date"] = "today"
    else:
        post["date"] = str(date_diff) + " days ago"
    post["description"] = record.description
    print(post)

    return post
from operator import pos
from app.models.jobs import JobPost
from selenium import webdriver
from selenium.webdriver.opera.options import Options
import urllib
from bs4 import BeautifulSoup
import re
import time
import random
import elasticsearch.helpers

from app.models import MyError
from .utils import genESPost, checkESPost


driver_path = r"C:\Users\72337\Desktop\test\browser_drivers"
# upon any update of "required field", add the respective processing method in \
# "getElement", "create_jobposts_MySQL", "create_jobposts_ES" and "getESPost" as well
required_fields = ["title", "link", "company", "salary", "date", "snippet"]


# default browser: Chrome
def init_driver(name):
    if name == "chrome":
        driver = webdriver.Chrome(driver_path + "/chromedriver/chromedriver.exe")
    elif name == "edge":
        driver = webdriver.Edge(driver_path + "/edgedriver/msedgedriver.exe")
    elif name == "firefox":
        driver = webdriver.Firefox(driver_path + "/geckodriver")
    elif name == "opera":    # there's still some problems with opera
        options = Options()
        driver = webdriver.Opera(options=options, executable_path=driver_path + "/operadriver/operadriver.exe")
    else:
        driver = webdriver.Chrome(driver_path + "/chromedriver/chromedriver.exe")

    return driver


def update_jobposts(db, es, keyword, driver_name, pageStart=0, date=1):
    driver = init_driver(driver_name)

    pageStart *= 10

    for page in range(pageStart, pageStart + 250, 10): # 25 pages at a time (needs modification!)
        web_content = get_webcontent(driver, keyword, date, page)
        time.sleep(random.randint(400, 600) / 1000)
        if web_content == None:
            break
        posts = extract_info(web_content)
        create_jobposts_MySQL(db, posts)
        create_jobposts_ES(es, posts)


# get all the contents in one page
def get_webcontent(driver, keyword, date, page):
    args = {"q": keyword, "fromage": date, "start": page}
    url = ('https://sg.indeed.com/jobs?' + urllib.parse.urlencode(args))
    driver.get(url)
    contents = driver.find_element_by_id("mosaic-provider-jobcards")
    contents_html = contents.get_attribute("innerHTML")
    job_soup = BeautifulSoup(contents_html, "html.parser")
    return job_soup


# grab all the post information the content of one page
def extract_info(content):
    job_cards = content.find_all("a", class_=re.compile("^tapItem"))

    posts = []
    for card in job_cards:
        post = {}
        succeed = True
        for field in required_fields:
            post[field] = getElement(card, field)
            if post[field] == None: succeed = False
        if succeed and \
            JobPost.query.filter_by(title=post["title"], company=post["company"]).first() is None:
            posts.append(post)
    return posts


# grab information from a specific field
def getElement(card, field):
    if field == "title":
        return getTitle(card)
    elif field == "link":
        return getLink(card)
    elif field == "company":
        return getCompany(card)
    elif field == "salary":
        return getSalary(card)
    elif field == "date":
        return getDate(card)
    elif field == "snippet":
        return getSnippet(card)


# toolbox for getTitle()
def getTitle(card):
    try:
        fieldBlock = card.find("td", class_="resultContent")
        field = fieldBlock.find("h2", class_=re.compile("^jobTitle")).find_all("span")[-1]
        fieldText = field.text.strip()
    except Exception as e:
        MyError.display("Scrawler Error", MyError.WEB_SOURCE_NULL, "failed to collect title from Indeed.")
        print(e)
        fieldText = None
    return fieldText

def getLink(card):
    try:
        link = card["href"]
        link = "sg.indeed.com" + link
    except Exception as e:
        MyError.display("Scrawler Error", MyError.WEB_SOURCE_NULL, "failed to collect weblink from Indeed.")
        print(e)
        link = None
    return link

def getCompany(card):
    try:
        fieldBlock = card.find("td", class_="resultContent")
        field = fieldBlock.find("span", class_="companyName")
        fieldText = field.text.strip()
    except Exception as e:
        MyError.display("Scrawler Error", MyError.WEB_SOURCE_NULL, "failed to collect company from Indeed.")
        print(e)
        fieldText = None
    return fieldText

def getSalary(card):
    fieldContainer = card.find("div", class_=re.compile("salary-snippet-container"))
    # can tolerate without specified salaries!
    if fieldContainer is None:
        return ""
    fieldBlock = fieldContainer.find("span", class_="salary-snippet")
    fieldText = fieldBlock.text.strip()
    return fieldText

def getDate(card):
    try:
        fieldContainer = card.find("table", class_="jobCardShelfContainer")
        fieldBlock = fieldContainer.find("span", class_="date")
        fieldText = fieldBlock.text.strip()
    except Exception as e:
        MyError.display("Scrawler Error", MyError.WEB_SOURCE_NULL, "failed to collect date from Indeed.")
        print(e)
        fieldText = None
    return fieldText

def getSnippet(card):
    try:
        fieldContainer = card.find("table", class_="jobCardShelfContainer")
        fieldBlock = fieldContainer.find("div", class_="job-snippet")
        fieldText = ""
        for text in fieldBlock.find_all("li"):
            fieldText += text.text.strip()
    except Exception as e:
        MyError.display("Scrawler Error", MyError.WEB_SOURCE_NULL, "failed to collect description from Indeed.")
        print(e)
        fieldText = None
    return fieldText


# (testing version) create a new job post with the extracted information
def create_jobposts_MySQL(db, posts):
    try:
        for post in posts:
            post_record = JobPost(title=post["title"], link=post["link"], company=post["company"], \
                salary=post["salary"], date=post["date"], description=post["snippet"])
            db.session.add(post_record)
        db.session.commit()
    except Exception as e:
        MyError.display("Scrawler Error" + MyError.MYSQL_CREATE_FAIL + "fail to create a page of posts in MySQL.")
        print(e)
        db.session.rollback()
    
    db.session.close()


def create_jobposts_ES(es, posts):
    try:
        es_posts = []
        for post in posts:
            id = JobPost.query.filter_by(title=post["title"], company=post["company"]).first().post_id
            if not checkESPost(es, id):
                es_post = genESPost(post, id)
                es_posts.append(es_post)
        elasticsearch.helpers.bulk(es, es_posts)
    except Exception as e:
        MyError.display("Scrawler Error" + MyError.ES_CREATE_FAIL + "fail to create a page of posts in ES.")
        print(e)

import selenium
from selenium import webdriver
from app import db


driver_path = r"browser_drivers"
required_fields = ["title", "link", "company", "salary", "date", "snippet"]


# default browser: Chrome
def init_driver():
    driver = webdriver.Chrome(driver_path + "/Chromedriver/chromedriver.exe")
    return driver


def init_jobposts(keyword, date=31):
    driver = init_driver()
    pages = count_pages(driver, keyword, date)

    for page in range(1, pages + 1):
        web_content = get_webcontent(driver, keyword, date, page)
        if web_content == None:
            break
        posts = extract_info(web_content)
        create_jobposts(posts)


# get the number of posts from the first page
def count_pages(driver, keyword, date):
    return


# get all the contents in one page
def get_webcontent(driver, keyword, date, page):
    return


# grab all the post information the content of one page
def extract_info(content):
    return 


# create a new job post with the extracted information
def create_jobposts(posts):
    return
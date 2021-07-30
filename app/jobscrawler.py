from selenium import webdriver
import urllib
from bs4 import BeautifulSoup
import re
import time


driver_path = r"C:\Users\72337\Desktop\project\repo\searchEngine\Attempt_SearchEngine\app\browser_drivers"
# upon any update of "required field", add the respective processing method in "getElement" as well
required_fields = ["title", "link", "company", "salary", "date", "snippet"]


# default browser: Chrome
def init_driver():
    driver = webdriver.Chrome(driver_path + "/Chromedriver/chromedriver.exe")
    return driver


def init_jobposts(db, keyword, date=31):
    driver = init_driver()
    # pages = count_pages(driver, keyword, date)

    for page in range(1, 2): # 1001
        web_content = get_webcontent(driver, keyword, date, page)
        # print(web_content)
        if web_content == None:
            break
        posts = extract_info(web_content)
        create_jobposts(db, posts)


# TODO: get the number of posts from the first page
# def count_pages(driver, keyword, date):
#     return


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
        # print(card)
        for field in required_fields:
            post[field] = getElement(card, field)
        print(post)
        print()
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
    fieldBlock = card.find("td", class_="resultContent")
    field = fieldBlock.find("h2", class_=re.compile("^jobTitle")).find_all("span")[-1]
    fieldText = field.text.strip()
    return fieldText

def getLink(card):
    link = card["href"]
    link = "sg.indeed.com" + link
    return link

def getCompany(card):
    fieldBlock = card.find("td", class_="resultContent")
    field = fieldBlock.find("span", class_="companyName")
    fieldText = field.text.strip()
    return fieldText

def getSalary(card):
    fieldContainer = card.find("div", class_=re.compile("salary-snippet-container"))
    if fieldContainer is None:
        return ""
    fieldBlock = fieldContainer.find("span", class_="salary-snippet")
    fieldText = fieldBlock.text.strip()
    return fieldText

def getDate(card):
    fieldContainer = card.find("table", class_="jobCardShelfContainer")
    fieldBlock = fieldContainer.find("span", class_="date")
    fieldText = fieldBlock.text.strip()
    return fieldText

def getSnippet(card):
    fieldContainer = card.find("table", class_="jobCardShelfContainer")
    fieldBlock = fieldContainer.find("div", class_="job-snippet")
    fieldText = ""
    for text in fieldBlock.find_all("li"):
        fieldText += text.text.strip()
    return fieldText


# (testing version) create a new job post with the extracted information
def create_jobposts(db, posts):
    return
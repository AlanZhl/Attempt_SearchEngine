import selenium
from selenium import webdriver
from app import db


driver_path = r"browser_drivers"
required_fields = ["title", "link", "company", "salary", "date", "snippet"]


# default browser: Chrome
def init_driver():
    driver = webdriver.Chrome(driver_path + "/Chromedriver/chromedriver.exe")
    return driver


def init_jobposts():
    driver = init_driver()

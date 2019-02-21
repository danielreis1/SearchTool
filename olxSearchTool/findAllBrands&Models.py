import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_all_models_for_brand():
    return


def startBrowser():
    start_url = "https://google.com"
    options = Options()
    #options.headless = True
    # TODO change this paths to command line input or environment variable, and create script to initialize that
    #  variable
    profile_path = "/root/.mozilla/firefox/yy1okn6z.default"
    profile = webdriver.FirefoxProfile(profile_path)
    firefox_binary_path = "/usr/bin/firefox"
    firefox_binary = FirefoxBinary(firefox_binary_path)
    browser = webdriver.Firefox(options=options, firefox_profile=profile, firefox_binary=firefox_binary)
    browser.get(start_url)
    return browser


browser = startBrowser()
url = 'https://www.olx.pt/carros-motos-e-barcos/carros/'
browser.get(url)

# press button for all brands to appear on dropdown menu
element = browser.find_element_by_css_selector("div#subSelect378")
print(element.text)
element = element.find_element_by_xpath("//a")
print(element.text)
'''
element.click()

wait = WebDriverWait(browser, 10)
wait.until(element)

soup = BeautifulSoup(browser.page_source, "html.parser")
tags = soup.find_all("a")
print(tags)
brands = []
for tag in tags:
    brands += [tag['data-code']]
print(brands)
'''
input("press key to quit")
browser.quit()

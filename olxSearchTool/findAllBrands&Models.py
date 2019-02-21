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

def press_dropdown_menu_button():
    # press button for all brands to appear on dropdown menu and wait for it to appear
    element = browser.find_element_by_css_selector("div[class='filter-item rel category-item']")
    element = element.find_element_by_css_selector("a")
    element.click()
    #wait = WebDriverWait(browser, 10)
    #wait.until(EC.presence_of_all_elements_located(By.CSS_SELECTOR, "div[class='filter-item rel category-item']"))


def select_brand_from_dropdown_menu(brand):
    press_dropdown_menu_button()
    click_brand(brand)


def click_brand(brand):
    browser.find_element_by_css_selector("a[data-code=" + brand + "]").click()


def get_all_brands():
    brands_models_dict = {}
    # get all brands
    soup = BeautifulSoup(browser.page_source, "html.parser")
    tags = soup.find_all("a", {"data-name": "search[category_id]"})
    brands = []
    for tag in tags:
        brands += [tag['data-code']]
    #print(brands)
    for i in brands:
        brands_models_dict[i] = []
    return brands_models_dict


def get_models(brand): #TODO
    # get models from 1 brand
    return


def get_all_models_from_all_brands(brands_dict):
    # get all models from all brands
    return


browser = startBrowser()
url = 'https://www.olx.pt/carros-motos-e-barcos/carros/'
browser.get(url)

press_dropdown_menu_button()
brands = get_all_brands()
print(brands)
#press_dropdown_menu_button()
click_brand("abarth")
get_models("abarth")


input("press key to quit")
browser.quit()

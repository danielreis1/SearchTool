import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def start_browser():
    start_url = "https://google.com"
    options = Options()
    # options.headless = True
    # TODO change this paths to command line input or environment variable, and create script to initialize that
    #  variable
    profile_path = "/root/.mozilla/firefox/yy1okn6z.default"
    profile = webdriver.FirefoxProfile(profile_path)
    firefox_binary_path = "/usr/bin/firefox"
    firefox_binary = FirefoxBinary(firefox_binary_path)
    browser = webdriver.Firefox(options=options, firefox_profile=profile, firefox_binary=firefox_binary)
    browser.get(start_url)
    return browser


def click_brands():
    # press button for all brands to appear on dropdown menu and wait for it to appear
    element = browser.find_element_by_css_selector("div[class='filter-item rel category-item']")
    element = element.find_element_by_css_selector("a")
    element.click()
    # wait = WebDriverWait(browser, 10)
    # wait.until(EC.presence_of_all_elements_located(By.CSS_SELECTOR, "div[class='filter-item rel category-item']"))


def select_brand_from_dropdown_menu(brand):
    click_brands()
    click_brand(brand)


def click_brand(brand):
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-code=" + brand + "]")))
    element.click()


def get_all_brands():
    brands_models_dict = {}
    click_brands()
    soup = BeautifulSoup(browser.page_source, "html.parser")
    tags = soup.find_all("a", {"data-name": "search[category_id]"})
    brands = []
    for tag in tags:
        brands += [tag['data-code']]
    # print(brands)
    for i in brands:
        brands_models_dict[i] = []
    return brands_models_dict


def get_models(brand, brand_model_dict):
    # get models from 1 brand
    click_models()
    soup = BeautifulSoup(browser.page_source, "html.parser")
    # TODO test this
    tags = soup.find_all("label", {"data-name": "search[filter_enum_modelo][]"})
    print
    print(tags)
    print
    models = []
    for tag in tags:
        model = tag.span
        models += [model]
    brand_model_dict[brand] = models
    print(brand_model_dict[brand])
    return brand_model_dict


def click_model(brand, model):
    # TODO test
    click_brands()
    click_brand(brand)
    click_models()
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[value=" + model + "]")))
    element.click()


def click_models():
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[id=param_modelo]')))
    soup = BeautifulSoup(browser.page_source, "html.parser")
    tag = soup.find("li", {"id": "param_modelo"})
    element = element.find_element_by_css_selector("a")
    element.click()


def get_all_models_from_all_brands(brands_dict):
    # get all models from all brands
    return


browser = start_browser()
url = 'https://www.olx.pt/carros-motos-e-barcos/carros/'
browser.get(url)

brands_model_dict = get_all_brands()
print(brands_model_dict)
click_brand("abarth")
get_models("abarth", brands_model_dict)

# browser.quit()

from bs4 import BeautifulSoup
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle


def start_browser():
    start_url = "https://google.com"
    options = Options()
    options.headless = True
    # TODO change this paths to command line input or environment variable, and create script to initialize that
    #  variable
    profile_path = "/root/.mozilla/firefox/yy1okn6z.default"
    profile = webdriver.FirefoxProfile(profile_path)
    firefox_binary_path = "/usr/bin/firefox"
    firefox_binary = FirefoxBinary(firefox_binary_path)
    browser = webdriver.Firefox(options=options, firefox_profile=profile, firefox_binary=firefox_binary)
    browser.get(start_url)
    return browser


def click_brands(browser):
    # press button for all brands to appear on dropdown menu and wait for it to appear
    element = browser.find_element_by_css_selector("div[class='filter-item rel category-item']")
    element = element.find_element_by_css_selector("a")
    element.click()


def select_brand_from_dropdown_menu(brand, browser):
    click_brands(browser)
    click_brand(brand, browser)


def click_brand(brand, browser):
    wait = WebDriverWait(browser, 15)
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-code=" + brand + "]")))
    element.click()


def get_all_brands(browser, url):
    brands_models_dict = {}
    browser.get(url)
    click_brands(browser)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    tags = soup.find_all("a", {"data-name": "search[category_id]"})
    brands = []
    for tag in tags:
        brands += [tag['data-code']]
    # print(brands)
    for i in brands:
        brands_models_dict[i] = []
    return brands_models_dict


def get_models(brand, brand_model_dict, browser):
    # get models from 1 brand
    try:
        click_models(browser)
    except TimeoutException as t:
        error = "get_models click_models timed out, didnt get " + brand
        error += "\n\t" + t.msg
        error = u''.join(error).encode('utf-8').strip()
        log_to_error_file(error)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    tags = soup.find_all("label", {"data-name": "search[filter_enum_modelo][]"})
    models = {}
    for tag in tags:
        model = tag.span.text.lower().replace(" ", "-")
        # print(model)
        models[model] = []
    brand_model_dict[brand] = models
    print(brand)
    print(brand_model_dict[brand])
    return brand_model_dict


def click_model(brand, model, browser):
    # must be tested, not required, can "click model" through url get with the correct url
    click_brands(browser)
    click_brand(brand, browser)
    click_models(browser)
    wait = WebDriverWait(browser, 15)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[value=" + model + "]")))
    element.click()


def click_models(browser):
    wait = WebDriverWait(browser, 15)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[id=param_modelo]')))
    element = element.find_element_by_css_selector("a")
    element.click()


def get_all_models_from_all_brands(browser):
    url = 'https://www.olx.pt/carros-motos-e-barcos/carros/'
    brands_model_dict = get_all_brands(browser, url)

    for key in brands_model_dict:
        browser.get(url)
        print(key)
        select_brand_from_dropdown_menu(key, browser)
        get_models(key, brands_model_dict, browser)

    return brands_model_dict


def save_brands_and_models(brands_model_dict):
    file = 'textFiles/brands_and_models'
    file_txt = 'textFiles/brands_and_models_in_text_format'
    f_pickle = open(file, "wb")
    pickle.dump(brands_model_dict, f_pickle)
    f_pickle.close()
    f_txt = open(file_txt, 'w+')

    for brand in brands_model_dict:
        brand_to_write = u''.join(brand).encode('utf-8').strip()
        f_txt.write(brand_to_write + "\n")
        for model in list(brands_model_dict[brand].keys()):
            model_to_write = u''.join(model).encode('utf-8').strip()
            f_txt.write("\t" + model_to_write + "\n")
        f_txt.write("--------------------------\n")

    f_txt.close()


def load_brands_and_models():
    file = 'textFiles/brands_and_models'
    f_pickle = open(file, "r")
    return pickle.load(f_pickle)


def log_to_error_file(error):
    file_txt = 'textFiles/last_execution_errors_log'
    write_to_file_replace(file_txt, error)


def write_to_file_replace(file_txt, text):
    f_txt = open(file_txt, 'w+')
    text_to_write = u''.join(text).encode('utf-8').strip()
    f_txt.write(text_to_write + '\n')
    f_txt.close()


def create_data_struct():
    browser = start_browser()
    brands_model_dict = get_all_models_from_all_brands(browser)
    browser.quit()
    save_brands_and_models(brands_model_dict)
    return brands_model_dict


if __name__ == "__main__":
    brands_model_dict = {}
    if len(sys.argv) > 1:
        print("arguments found")
        if "-h" in sys.argv:
            print
            print("no args to use what we have")
            print("-remake to get all from olx")

        if "-remake" not in sys.argv:
            try:
                brands_model_dict = load_brands_and_models()
            except (OSError, IOError) as e:
                brands_model_dict = create_data_struct()
        else:
            print("remaking")
            brands_model_dict = create_data_struct()

    else:
        print("args not found")
        try:
            brands_model_dict = load_brands_and_models()
        except (OSError, IOError) as e:
            brands_model_dict = create_data_struct()

    print(brands_model_dict)

    '''
    # test writing and reading to text file
    brands_model_dict = {"abarth": {"model_a": ["1", "2"], "model_a2": ["3", "4"]}, "volks": {"model_b": ["5", "6"], "model_b2": ["7", "8"]}}
    print(brands_model_dict)
    save_brands_and_models(brands_model_dict)
    
    brands_model_dict = load_brands_and_models()
    print(brands_model_dict)
    '''

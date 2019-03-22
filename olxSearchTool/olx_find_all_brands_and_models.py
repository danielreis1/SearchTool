from bs4 import BeautifulSoup
import sys
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle


def start_browser(headless=True):
    start_url = "https://google.com"
    options = Options()
    options.headless = headless
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
    wait = WebDriverWait(browser, 10)
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
        brand = tag['data-code']
        if "nao-list" in brand:
            continue
        brands += [brand]
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
        # error = u''.join(error).encode('utf-8').strip()
        log_to_error_file(error)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    tags = soup.find_all("label", {"data-name": "search[filter_enum_modelo][]"})
    models = {}
    for tag in tags:
        model = tag.span.text.lower().replace(" ", "-")
        # print(model)
        models[model] = {}
    brand_model_dict[brand] = models
    print(brand)
    print(brand_model_dict[brand])
    return brand_model_dict


def click_model(brand, model, browser):
    # must be tested, not required, can "click model" through url get with the correct url
    click_brands(browser)
    click_brand(brand, browser)
    click_models(browser)
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[value=" + model + "]")))
    element.click()


def click_models(browser):
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[id=param_modelo]')))
    element = element.find_element_by_css_selector("a")
    element.click()


def get_all_models_from_all_brands(browser):
    url = 'https://www.olx.pt/carros-motos-e-barcos/carros/'
    brand_models_olx = get_all_brands(browser, url)

    for key in brand_models_olx:
        browser.get(url)
        print(key)
        select_brand_from_dropdown_menu(key, browser)
        get_models(key, brand_models_olx, browser)

    return brand_models_olx


def save_brands_and_models(brand_models_olx):
    file = 'textFiles/brands_and_models_olx'
    f_pickle = open(file, "wb")
    pickle.dump(brand_models_olx, f_pickle)
    f_pickle.close()


def load_brands_and_models(filename):
    file = 'textFiles/' + filename
    f_pickle = open(file, "rb")
    return pickle.load(f_pickle)


def pickle_load():
    return load_brands_and_models('brands_and_models_olx')


def log_to_error_file(error):
    file = 'last_execution_errors_log_olx'
    log_error_to_file(file, error)


def log_error_to_file(file, error):
    file_txt = 'textFiles/' + file
    write_to_file_replace(file_txt, error)


def write_to_file_replace(file_txt, text):
    f_txt_temp = file_txt + "temp"
    try:  # file may not exist to be removed
        os.remove(file_txt)
    except Exception as e:
        print(e)
    f_txt = open(f_txt_temp, 'wb')
    text_to_write = u''.join(text + '\n').encode('utf-8').strip()
    f_txt.write(text_to_write)
    f_txt.close()
    os.replace(f_txt_temp, file_txt)


def create_data_struct():
    browser = start_browser()
    brand_models_olx = get_all_models_from_all_brands(browser)
    browser.quit()
    save_brands_and_models(brand_models_olx)
    return brand_models_olx


if __name__ == "__main__":
    brand_models_olx = {}
    if len(sys.argv) > 1:
        print("arguments found")
        if "-h" in sys.argv:
            print
            print("no args to use what we have")
            print("-remake to get all from olx")
            exit(0)
        if "-remake" not in sys.argv:
            try:
                brand_models_olx = load_brands_and_models('brands_and_models_olx')
            except (OSError, IOError) as e:
                brand_models_olx = create_data_struct()
        else:
            print("remaking")
            brand_models_olx = create_data_struct()

    else:
        print("args not found")
        try:
            brand_models_olx = load_brands_and_models('brands_and_models_olx')
        except (OSError, IOError) as e:
            brand_models_olx = create_data_struct()

    print(brand_models_olx)

    # TODO find a way to fit datsun brand (no models)

    # TODO olx average

    # TODO refactor what is below
"""

def get_car_links_from_a_given_olx_page(url):
    """
"""
    :param url: input url already has info on brand and model
    :return: all cars for a given brand
    """
"""
    # TODO this checks 1st page only, check all pages

    # r = requests.get('https://www.olx.pt/carros-motos-e-barcos/carros/abarth/?search[filter_enum_modelo][0]=500&search[description]=1')
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        # no olx todos os links na pagina que vai ate ao carro tem /anuncio/ , e' so' preciso procurar em todos esses links
        matched_lines = [line for line in r.text.split('\"') if "/anuncio/" in line]
        for cnt, line in enumerate(matched_lines):
            new_line = line.split("html")
            new_line = new_line[0] + "html"
            matched_lines[cnt] = new_line

        links_to_cars = list(set(matched_lines))
        # print("number cars " + str(len(links_to_cars)))

        # TODO use this to see if page changed from last time?
        # TODO if a given brand has many pages of cars, check last page for number of cars? yes
        # TODO default esta ordenado por mais recente no olx, o primeiro carro vai para a primeira pagina
        # TODO after checking new car exists and identifying it check if it exists in persistent list
        return links_to_cars


def get_features_olx(soup):
    price = soup.find_all('div', {"class": "price-label"})
    price = ''.join(price[0].find_all(text=True))
    price = price.replace("€", "")
    price = price.replace(".", "")
    price = price.strip()

    price = int(price)
    print(str(price))

    used = soup.find('th', string="Condição").parent.a.text.strip()
    if used.lower() == "usado":
        used = True
    else:
        used = False
    print(used)

    km = soup.find('th', string="Quilómetros").parent.strong.text.strip().replace(".", "")
    print(km)
    km = int(km)

    fuel_type = soup.find('th', string="Combustível").parent.a.text.strip()
    print(fuel_type)

    year = soup.find('th', string="Ano").parent.strong.text.strip()
    print(year)
    year = int(year)

    model = soup.find('th', string="Modelo").parent.a.text.strip()
    print(model)

    name_feature = {"price": price, "used": used, "km": km, "fuel_type": fuel_type, "year": year, "model": model}
    return name_feature

"""

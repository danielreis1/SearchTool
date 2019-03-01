from bs4 import BeautifulSoup
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle
import olx_find_all_brands_and_models


def get_all_brands(browser):
    brands_models_standv = {}
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[data-key="make"]')))
    element = element.find_elements_by_css_selector("option")
    for ele_value in element:
        brand = ele_value.get_attribute("value")
        print(brand)
        if brand == "":
            continue
        elif "nao-list" in brand:
            continue
        brands_models_standv[brand] = {}
    return brands_models_standv


def get_all_models_by_brand(browser, brand, brands_models_standv):

    click_brand(browser, brand)
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[data-key="model"]')))
    element = element.find_elements_by_css_selector("option")
    models = {}
    for ele_value in element:
        model = ele_value.get_attribute("value")
        print(model)
        if model == "":
            continue
        elif "nao-list" in model:
            continue
        models[model] = {}
    brands_models_standv[brand] = models


def get_all_brands_and_models():
    browser = olx_find_all_brands_and_models.start_browser()  # headless=False)
    browser.get("https://www.standvirtual.com/")

    brands_models_standv = get_all_brands(browser)
    for brand in brands_models_standv:
        get_all_models_by_brand(browser, brand, brands_models_standv)
    browser.quit()
    return brands_models_standv


def pickle_save(brands_models_standv):
    file = 'textFiles/brands_and_models_standv'
    f_pickle = open(file, "wb")
    pickle.dump(brands_models_standv, f_pickle)
    f_pickle.close()


def pickle_load():
    return olx_find_all_brands_and_models.load_brands_and_models("brands_and_models_standv")


def click_brand(browser, brand):
    """
    doesnt really click brand, just simulates it TODO
    :return: simulates click on brand
    """
    url = "https://www.standvirtual.com/carros/" + "/" + brand + "/?search[filter_enum_damaged]=0&search[new_used]=all"
    browser.get(url)


def click_model(browser, brand, model):
    """
    same as click brand, should be used before get_all_car_pages functions
    :param browser:
    :param model:
    :return:
    """
    url = "https://www.standvirtual.com/carros/" + "/" + brand + "/" + model + "/?search[filter_enum_damaged]=0" \
                                                                               "&search[brand_program_id][0]=&search[" \
                                                                               "country]= "
    browser.get(url)


def get_all_car_pages(browser):
    """
    TODO change this to get all cars from all pages, not just the first page
    :param browser: browser should already contain url
    :param brand:
    :param model:
    :return: list of car pages
    """
    # TODO this needs to be tested
    car_pages = []
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article[role="link"]')))
    for page in element:
        car_page = page.get_attribute("data-href")
        print(car_page)
        car_pages += [car_page]
    return car_pages


def get_cars(browser, brand, model):
    # TODO this function is the one that will be used by car_search after import,
    #   abstracts click_model then get_all_car_pages
    url = ""
    browser.get(url)
    click_model(browser, brand, model)
    get_all_car_pages(browser)
    pass


if __name__ == "__main__":
    brands_models_standv = {}
    if len(sys.argv) > 1:
        print("arguments found")
        if "-h" in sys.argv:
            print
            print("no args to use what we have")
            print("-remake to get all from standvirtual")
            exit(0)
        if "-remake" not in sys.argv:
            try:
                brands_models_standv = pickle_load()
            except (OSError, IOError) as e:
                brands_models_standv = get_all_brands_and_models()
                pickle_save(brands_models_standv)
        else:
            print("remaking")
            brands_models_standv = get_all_brands_and_models()
            pickle_save(brands_models_standv)
    else:
        print("no args")
        try:
            brands_models_standv = pickle_load()
        except (OSError, IOError) as e:
            brands_models_standv = get_all_brands_and_models()
            pickle_save(brands_models_standv)

        print(brands_models_standv)

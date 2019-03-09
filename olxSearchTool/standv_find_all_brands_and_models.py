import requests
from bs4 import BeautifulSoup
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle
import olx_find_all_brands_and_models
from car_links_struct import *


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


def get_model_soup(brand, model):
    """
    doesnt use the browser
    :param brand:
    :param model:
    :return:
    """
    url = "https://www.standvirtual.com/carros/" + brand + "/" + model + "/?search[filter_enum_damaged]=0" \
                                                                         "&search[brand_program_id][0]=&search[" \
                                                                         "country]= "
    # print(url)
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        return soup


def get_max_car_pages(soup):
    max_page_num = 0
    dic = {}
    page_nums = soup.find_all('li', {"class": ""})
    for num_container in page_nums:
        num_container = num_container.find("a")
        if num_container is not None:
            num_container = num_container.find("span", {"id": False})
            if num_container is not None:
                try:
                    num_container = int(num_container.text)
                    # print(num_container)
                    if num_container > max_page_num:
                        max_page_num = num_container
                except ValueError:
                    # print("error converting")
                    continue
    return max_page_num


def get_all_car_pages(max_page_num, brand, model):
    standv_cars = []
    links = []
    if max_page_num == 0:
        url = "https://www.standvirtual.com/carros/" + brand + "/" + model + "/?search[filter_enum_damaged]=0&search[" \
                                                                             "brand_program_id][0]=&search[country]="
        aux_get_all_car_pages(brand, model, links, 0, url)
    else:
        links = aux_get_all_car_pages(brand, model)
        for i in range(1, max_page_num + 1):
            aux_get_all_car_pages(brand, model, links, i)
    standv_struct = CarLinksStruct(brand, model, links, max_page_num)
    return standv_struct


def aux_get_all_car_pages(brand, model, links, i, url=None):
    # print(i)
    if url is None:
        url = "https://www.standvirtual.com/carros/" + brand + "/" + model + "/?search%5Bfilter_enum_damaged%5D=0&page="
        url += str(i)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    car_links = soup.find_all('article', {"role": "link"})
    for link in car_links:
        link = link['data-href']
        # print(link)
        if link not in links:
            links += [link]
    # print(len(links))
    return links


def get_cars(brand, model):
    """

    :param brand:
    :param model:
    :return: returns list with keys: (brand and model)
    and values: (a list of CarLinkFeature -> gives all the links for given features for a brand and model)
    """
    # this is to be used in import car_search.py

    soup = get_model_soup(brand, model)
    max_pages = get_max_car_pages(soup)
    car_pages = get_all_car_pages(max_pages, brand, model)
    return associate_feats_to_carlink(car_pages)


def associate_feats_to_carlink(standv_struct):
    """
    :param standv_struct: brand, model associated with all its links
    :return: returns list with keys: (brand and model)
    and values: (a list of CarLinkFeature -> gives all the links for given features for a brand and model)
    """

    brand = standv_struct.get_brand()
    model = standv_struct.get_model()
    brand_model_car_struct_list = CarLinkFeaturesList(brand, model)
    continue_loop = ContinueLoop()
    for link in standv_struct.get_links():
        # print(link)
        km, price, color, feats = get_features(link)
        print(feats)
        try:
            for car_link_feats_list in brand_model_car_struct_list.get_features_list():
                if car_link_feats_list.is_feats_equal(feats):
                    car_link_feats_list.add_car(price, km, link, color)
                    print("CarLinkFeatures added")
                    raise continue_loop
        except ContinueLoop:
            # print("exception")
            continue
        # print("car created")
        car_struct = CarLinkFeatures(feats)
        car_struct.add_car(price, km, link, color)
        brand_model_car_struct_list.add_features(car_struct)
    # for i in brand_model_car_struct_list.get_features_list():
    # print(i)
    return brand_model_car_struct_list


def get_features(url):
    """
    :param url: standvirtual's car url
    :return: features_dict, key: feature name, val: feat value and km and price
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    price = soup.find_all('span', {"class": "offer-price__number"})

    price = ''.join(price[0].find_all(text=True))
    price = price.replace("EUR", "")
    price = price.strip()
    price = price.replace(" ", "")

    price = int(price)
    # print(str(price))

    used = soup.find('span', string="Condição").parent.a.text.strip()
    if used.lower() == "usados":
        used = "usado"
    else:
        used = "novo"
    print(used)

    km = soup.find('span', string="Quilómetros").parent.div.text.strip().replace(" ", "")
    km = km.replace("km", "")
    print(km)
    km = int(km)

    fuel_type = soup.find('span', string="Combustível").parent.a.text.strip()
    print(fuel_type)

    year = soup.find('span', string="Ano de Registo").parent.div.text.strip()
    print(year)
    year = int(year)

    cv = soup.find('span', string="Potência").parent.div.text.strip()
    cv = cv.lower().replace("cv", "").replace(" ", "")
    # print(cv)
    cv = int(cv)

    segmento = soup.find('span', string="Segmento").parent.div.text.strip()
    segmento = segmento.lower()
    # print(segmento)

    color = soup.find('span', string="Cor").parent.a.text.strip()
    # print(color)
    try:
        caixa_mudancas = soup.find('span', string="Tipo de Caixa").parent.a.text.strip()
    except AttributeError:
        caixa_mudancas = "manual"
    # print(caixa_mudancas)

    try:
        traccao = soup.find('span', string="Tracção").parent.div.text.strip()
        traccao = traccao.replace("Tracção ", "")
    except AttributeError:
        traccao = "traseira"
    # print(traccao)

    try:
        version = soup.find('span', string="Versão").parent.div.text.strip()
    except AttributeError:
        version = ""
    # print(version)

    try:
        doors = soup.find('span', string="Nº de portas").parent.a.text.strip()
    except AttributeError:
        doors = 4
    # print(doors)
    feats = CarFeatures(used, fuel_type, year, cv, caixa_mudancas, traccao, segmento,
                        version, doors)
    return km, price, color, feats


if __name__ == "__main__":
    brands_models_standv = {}
    if len(sys.argv) > 1:
        print("arguments found")
        if "-h" in sys.argv:
            print()
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
        print()

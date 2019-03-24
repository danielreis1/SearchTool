import time

import requests
import os
from bs4 import BeautifulSoup
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle

import car_search
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
    file_temp = file + "temp"
    f_pickle = open(file_temp, "wb")
    pickle.dump(brands_models_standv, f_pickle)
    f_pickle.close()
    os.replace(file_temp, file)


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
    print("requests")
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


def load_car_links_struct(brand, model):
    filename = "carLinksStructs/standv" + "_" + brand + "_" + model
    return olx_find_all_brands_and_models.load_brands_and_models(filename)


def save_car_links_struct(standv_struct):
    brand = standv_struct.get_brand()
    model = standv_struct.get_model()
    file = 'textFiles/carLinksStructs/' + "standv" + "_" + brand + "_" + model
    file_temp = file + "temp"
    f_pickle = open(file_temp, "wb")
    pickle.dump(standv_struct, f_pickle)
    f_pickle.close()
    os.replace(file_temp, file)


def aux_update(update, links, url=None):
    """
    :param url:
    :type update: CarLinksStruct
    :param update:
    :param links: list
    :return:
    """
    max_page = update.get_max_pages()
    brand = update.get_brand()
    model = update.get_model()

    if url is not None:
        aux_aux_update(update, links, url)

    else:
        for i in range(1, max_page + 1):
            url = "https://www.standvirtual.com/carros/" + brand + "/" + model + "/?search%5Bfilter_enum_damaged%5D=0" \
                                                                                 "&page= "
            url += str(i)
            end = aux_aux_update(update, links, url)
            if end:
                break
            time.sleep(1)
    return links


def aux_aux_update(update, links, url):
    end = False
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    car_links = soup.find_all('article', {"role": "link"})
    for link in car_links:
        link = link['data-href']
        # TODO this links are not ordered, new car may be on first page, if all on first page are new go to 2nd page,
        #  and so on
        if link in update.get_links():
            end = True
            break
        else:
            links += [link]
    return end


def get_all_car_pages(max_page_num, brand, model, update=None):
    # it does get first page in both cases max page == 0 and != 0
    links = []
    if max_page_num == 0:
        url = "https://www.standvirtual.com/carros/" + brand + "/" + model + "/?search[filter_enum_damaged]=0&search[" \
                                                                             "brand_program_id][0]=&search[country]="
        if update is None:
            aux_get_all_car_pages(brand, model, links, url)
        else:
            aux_update(update, links, url)

    else:
        if update is None:
            for i in range(1, max_page_num + 1):
                aux_get_all_car_pages(brand, model, links, i)
                time.sleep(1)
        else:
            aux_update(update, links)
    if update is None:
        standv_struct = CarLinksStruct(brand, model, links, max_page_num)
        save_car_links_struct(standv_struct)
    else:
        # update has all links, but only the new ones are returned
        update.add_links(links)
        save_car_links_struct(update)
        standv_struct = CarLinksStruct(brand, model, links, max_page_num)
    return standv_struct


def aux_get_all_car_pages(brand, model, links, i, url=None):
    # print(i)
    if url is None:
        url = "https://www.standvirtual.com/carros/" + brand + "/" + model + "/?search%5Bfilter_enum_damaged%5D=0&page="
        url += str(i)
    print("requests")
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


def update_car_pages(car_pages):
    """

    :type car_pages: CarLinksStructr
    :param car_pages:
    :return:
    """
    max_pages = car_pages.get_max_pages()
    brand = car_pages.get_brand()
    model = car_pages.get_model()
    standv_struct = get_all_car_pages(max_pages, brand, model, car_pages)
    return standv_struct


def get_cars(brand, model, type_c):
    """

    :param brand:
    :param model:
    :return: returns list with keys: (brand and model)
    and values: (a list of CarLinkFeature -> gives all the links for given features for a brand and model)
    """
    # this is to be used in import car_search.py

    soup = get_model_soup(brand, model)
    try:
        car_pages = load_car_links_struct(brand, model)
        print("loaded car links struct")
        try:  # this is in case database (al_car_features_lists)doesnt exist and carLinksStructs data does
            car_search.pickle_load_cars(type_c, brand, model)
            car_pages = update_car_pages(car_pages)  # if datastruct exists, return info to update it
        except (OSError, IOError) as e:
            # if datastruct doesnt exist, return originally loaded car_pages and recreate datastruct, it will be
            # updated in next loop
            ret = associate_feats_to_carlink(car_pages, type_c)
            return ret
    except (OSError, IOError) as e:
        print("could not load car links struct")
        max_pages = get_max_car_pages(soup)
        car_pages = get_all_car_pages(max_pages, brand, model)
    ret = associate_feats_to_carlink(car_pages, type_c)
    return ret


def associate_feats_to_carlink(standv_struct, type_c):
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
        time.sleep(1)
        try:
            print(link)
            km, price, color, feats = get_features(link)
        except FailedURLException as e:
            print(e.get_url())
            continue
        # print("standv associate_feats_to_carlink")
        # print(feats)
        try:
            for car_link_feats in brand_model_car_struct_list.get_features_list():
                if car_link_feats.is_feats_equal(feats):
                    # cars = car_link_feats.get_cars()
                    car_link_feats.add_car(price, km, link, color)
                    print("Car added to existing car_link_feats list")
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
    print("associating feats to carlink done")
    return brand_model_car_struct_list


def get_features(url):
    """
    :param url: standvirtual's car url
    :return: features_dict, key: feature name, val: feat value and km and price
    """
    print("requests get_features standv")
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
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
        # print(used)

        km = soup.find('span', string="Quilómetros").parent.div.text.strip().replace(" ", "")
        km = km.replace("km", "")
        # print(km)
        km = int(km)

        fuel_type = soup.find('span', string="Combustível").parent.a.text.strip()
        # print(fuel_type)

        year = soup.find('span', string="Ano de Registo").parent.div.text.strip()
        # print(year)
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
    else:
        failed_to_load_url = FailedURLException(url)
        raise failed_to_load_url
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

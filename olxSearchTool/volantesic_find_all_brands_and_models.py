import requests
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

import olx_find_all_brands_and_models


# TODO put all brands and models into datastruct for comparison
# olx_find_all_brands_and_models.start_browser()

def get_all_brands():
    brand_models_volantesic = {}
    url = "https://volantesic.pt/marcas-carros/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    brand_names = soup.find_all('p', {"class": "brandSlideName"})
    for brand in brand_names:
        brand = brand.text.lower().replace(" ", "-")
        #print(brand)
        brand_models_volantesic[brand] = {}
    #print
    #print("number brands")
    #print(len(brand_models_volantesic))
    return brand_models_volantesic


def get_all_models_by_brand(brand, brand_models_volantesic):
    url = "https://volantesic.pt/marcas-carros/"
    url += brand + "/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    model_names = soup.find_all("p", {"class": "carBlockTitle"})
    models = {}
    for model in model_names:
        model = model.text.lower().replace(" ", "-")
        print(model)
        models[model] = {}
    print(models)
    brand_models_volantesic[brand] = models
    return brand_models_volantesic


def get_all_brands_and_models():
    brand_models_volantesic = get_all_brands()
    for brand in brand_models_volantesic.keys():
        get_all_models_by_brand(brand, brand_models_volantesic)
    return brand_models_volantesic


def pickle_save(brand_models_volantesic):
    file = 'textFiles/brands_and_models_volantesic'
    f_pickle = open(file, "wb")
    pickle.dump(brand_models_volantesic, f_pickle)
    f_pickle.close()


def pickle_load():
    return olx_find_all_brands_and_models.load_brands_and_models("brands_and_models_volantesic")


if __name__ == "__main__":
    brand_models_volantesic = {}
    if len(sys.argv) > 1:
        print("arguments found")
        if "-h" in sys.argv:
            print
            print("no args to use what we have")
            print("-remake to get all from olx")
            exit(0)
        if "-remake" not in sys.argv:
            try:
                brand_models_olx = pickle_load()
            except (OSError, IOError) as e:
                brand_models_volantesic = get_all_brands_and_models()
                pickle_save(brand_models_volantesic)
        else:
            print("remaking")
            brand_models_volantesic = get_all_brands_and_models()
            pickle_save(brand_models_volantesic)
    else:
        print("no args")
        brand_models_volantesic = pickle_load()

    print(brand_models_volantesic)

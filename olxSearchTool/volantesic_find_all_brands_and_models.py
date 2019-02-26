import requests
from bs4 import BeautifulSoup
import sys

import pickle
import olx_find_all_brands_and_models

def get_all_brands():
    brands_models_volantesic = {}
    url = "https://volantesic.pt/marcas-carros/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    brand_names = soup.find_all('p', {"class": "brandSlideName"})
    for brand in brand_names:
        brand = brand.text.lower().replace(" ", "-")
        #print(brand)
        brands_models_volantesic[brand] = {}
    #print
    #print("number brands")
    #print(len(brands_models_volantesic))
    return brands_models_volantesic


def get_all_models_by_brand(brand, brands_models_volantesic):
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
    brands_models_volantesic[brand] = models
    return brands_models_volantesic


def get_all_brands_and_models():
    brands_models_volantesic = get_all_brands()
    for brand in brands_models_volantesic.keys():
        get_all_models_by_brand(brand, brands_models_volantesic)
    return brands_models_volantesic


def pickle_save(brands_models_volantesic):
    file = 'textFiles/brands_and_models_volantesic'
    f_pickle = open(file, "wb")
    pickle.dump(brands_models_volantesic, f_pickle)
    f_pickle.close()


def pickle_load():
    return olx_find_all_brands_and_models.load_brands_and_models("brands_and_models_volantesic")


if __name__ == "__main__":
    brands_models_volantesic = {}
    if len(sys.argv) > 1:
        print("arguments found")
        if "-h" in sys.argv:
            print
            print("no args to use what we have")
            print("-remake to get all from olx")
            exit(0)
        if "-remake" not in sys.argv:
            try:
                brands_models_volantesic = pickle_load()
            except (OSError, IOError) as e:
                brands_models_volantesic = get_all_brands_and_models()
                pickle_save(brands_models_volantesic)
        else:
            print("remaking")
            brands_models_volantesic = get_all_brands_and_models()
            pickle_save(brands_models_volantesic)
    else:
        print("no args")
        brands_models_volantesic = pickle_load()

    print(brands_models_volantesic)

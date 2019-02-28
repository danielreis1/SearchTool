import requests
from bs4 import BeautifulSoup
import sys

import pickle
import olx_find_all_brands_and_models


def get_all_brands():
    # TODO - div -> data-key: make
    pass


def get_all_models_by_brand(brand, brands_models_standv):
    # TODO - div -> data-key: model
    pass


def get_all_brands_and_models():
    brands_models_standv = get_all_brands()
    for brand in brands_models_standv:
        get_all_models_by_brand(brand, brands_models_standv)
    return brands_models_standv


def pickle_save(brands_models_standv):
    file = 'textFiles/brands_and_models_standv'
    f_pickle = open(file, "wb")
    pickle.dump(brands_models_standv, f_pickle)
    f_pickle.close()


def pickle_load():
    return olx_find_all_brands_and_models.load_brands_and_models("brands_and_models_standv")


def click_brand(browser):
    # TODO
    pass


def click_model(browser):
    # TODO
    pass


def click_search_button(browser):
    # TODO
    pass


def get_all_car_pages(browser):
    # TODO
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
            # TODO
            browser = olx_find_all_brands_and_models.start_browser(headless=False)

    print(brands_models_standv)

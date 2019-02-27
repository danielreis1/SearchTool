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
import volantesic_find_all_brands_and_models


def log_errors(error):
    file = 'compare_errors'
    olx_find_all_brands_and_models.log_error_to_file(file, error)


def create_associations(comparison_src, comparison_target):
    # TODO surrond the following with 2 != try catches and create the brand_model dictionaries if required
    volante_brands_and_models = comparison_src.pickle_load()
    olx_brands_and_models = comparison_target.pickle_load()

    association_dict = {}  # key is olx, value is volantesic
    for brand in olx_brands_and_models:
        if brand in volante_brands_and_models.keys():
            for olx_model in olx_brands_and_models[brand]:
                olx_volante_models_dict = {}
                for volante_model in volante_brands_and_models[brand]:
                    olx_volante_models_dict[olx_model] += [volante_model]
                association_dict[brand] = olx_volante_models_dict

        else:
            error = "brand: " + brand + "\n" + "the brand does not exist in volantesic"
            log_errors(error)

        print("olx" + "\t\t" + "volantesic")
    return association_dict


def olx_volantsic_assoc():
    return create_associations(volantesic_find_all_brands_and_models, olx_find_all_brands_and_models)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("arguments found")
        if len(sys.argv) == 4:
            if "-d":
                print("-d brand model to delete association, must run again with no args to remake the association")
                pass

        elif "-h" in sys.argv:
            print("-h for help")
            print("-r to remake everything")
            print("-d brand model to delete association, must run again with no args to remake the association")

        elif "-r":
            print("-r to remake everything")
            dic = olx_volantsic_assoc()

    else:
        print("args not found")

        dic = olx_volantsic_assoc()
        # TODO display both volante and olx's models side by side in cmd line separate with \t

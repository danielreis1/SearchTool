import pickle
import sys

import requests
from bs4 import BeautifulSoup
import threading
import time

import os

import olx_find_all_brands_and_models
import compare_models
import standv_find_all_brands_and_models
import volantesic_find_all_brands_and_models


def get_source_dest_imports(source, dest):
    temp = []
    if source == "standv":
        temp += [standv_find_all_brands_and_models]
    elif source == "olx":
        temp += [olx_find_all_brands_and_models]
    if dest == "volantesic":
        temp += [volantesic_find_all_brands_and_models]
    return temp


def get_compare_dict(type_c):
    return compare_models.load_comparison_dic(type_c)


def pickle_save_all_car_feature_lists(all_car_features_lists, type_c, brand, model):
    file = 'textFiles/carFeaturesList/all_car_features_lists_' + type_c + "_" + brand + "_" + model
    file_temp = file + "temp"
    f_pickle = open(file_temp, "wb")
    pickle.dump(all_car_features_lists, f_pickle)
    os.rename(file_temp, file)
    f_pickle.close()


def pickle_load_cars(type_c, brand, model):
    file = 'textFiles/carFeaturesList/all_car_features_lists_' + type_c + "_" + brand + "_" + model
    f_pickle = open(file, "rb")
    return pickle.load(f_pickle)


def remake_by_brand_model(brand, model, output_list, browser, type_c, dest):
    t_list = source_import.get_cars(brand, model)
    for car_link_features in t_list:
        if dest not in car_link_features.get_searched_dests():
            dest_import.get_all_cars_dest_url(brand, model, car_link_features, type_c)
            dest_import.get_correct_estimate_prices(car_link_features, browser, dest)
            # dest_import.get_correct_estimate_prices(car_link_features, browser)
        time.sleep(1)
    pickle_save_all_car_feature_lists(t_list, type_c, brand, model)
    output_list += [t_list]


def detect_new_car_addition():
    # TODO detects when new car is added by checking the last page (max pages in car link feats)
    """
    :return:
    """
    pass


if __name__ == "__main__":

    if len(sys.argv) > 1:
        print("arguments found")
        if len(sys.argv) == 2:
            if "-h" in sys.argv:
                print("-h for help")
                print("-r to remake associations dict")
                print("no arguments to start where u left of")
            elif "-remake" in sys.argv:
                print("remake all")
            else:
                print("invalid args")
        elif len(sys.argv) == 4:
            if "-r" == sys.argv[1]:
                brand = sys.argv[2].lower()
                model = sys.argv[3].lower()

        else:
            print("invalid args")

    else:
        print("no arguments")
        time.sleep(1)
        sources = ["standv"]  # , "olx"]
        dests = ["volantesic"]
        browser = olx_find_all_brands_and_models.start_browser()
        try:
            for source in sources:
                for dest in dests:
                    type_comp = source + "_" + dest
                    source_import, dest_import = get_source_dest_imports(source, dest)
                    compare_dict = get_compare_dict(type_comp)
                    list_of_all_lists_of_car_link_feats = []

                    brands = ["abarth"]
                    for brand in brands:
                        models = ["500"]
                        for model in models:
                            brand = brand.lower()
                            model = model.lower()
                            print("next set of car_link_features")
                            lis = None
                            try:
                                lis = pickle_load_cars(type_comp, brand, model)
                                list_of_all_lists_of_car_link_feats += [lis]
                                print("successfully loaded")
                            except (OSError, IOError) as e:
                                print("could not load cars for brand: " + brand + " and model: " + model)
                                remake_by_brand_model(brand, model, list_of_all_lists_of_car_link_feats,
                                                      browser, type_comp, dest)
                            time.sleep(1)
                        time.sleep(1)
            browser.quit()
        except Exception as e:
            print(e)
            browser.quit()

# TODO the idea is to check standvirtual, then olx, all sources..., sequentialy and check if there is a new one and
#  add that new one to our structure and then compare to volantesic and all other destinations...,

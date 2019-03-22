import pickle
import random
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
from container_classes import SearchStatus, OutputTextContainer


def get_source_dest_imports(source, dest):
    temp = []
    if source == "standv":
        temp += [standv_find_all_brands_and_models]
    elif source == "olx":
        temp += [olx_find_all_brands_and_models]
    if dest == "volantesic":
        temp += [volantesic_find_all_brands_and_models]
    return temp


def get_type_comp_by_source_dest(source, dest):
    return source + "_" + dest


def get_source_and_dest_from_type_comp(type_c):
    """
    return independent strings source ([0]) and dest ([1]) in a list
    :param type_c:
    :return:
    """
    source = type_c.split("_")[0]
    dest = type_c.split("_")[1]
    return source, dest


def get_source_dest_imports_by_type_c(type_c):
    temp = []
    if type_c == "standv_volantesic":
        temp += [standv_find_all_brands_and_models]
        temp += [volantesic_find_all_brands_and_models]
    elif type_c == "olx_volantesic":
        temp += [olx_find_all_brands_and_models]
        temp += [volantesic_find_all_brands_and_models]
    return temp


def get_compare_dict(type_c):
    return compare_models.load_comparison_dic(type_c)


def pickle_save_all_car_feature_lists(all_car_features_lists, type_c, brand, model):
    file = 'textFiles/carFeaturesList/all_car_features_lists_' + type_c + "_" + brand + "_" + model
    file_temp = file + "temp"
    f_pickle = open(file_temp, "wb")
    pickle.dump(all_car_features_lists, f_pickle)
    f_pickle.close()
    os.replace(file_temp, file)


def pickle_load_cars(type_c, brand, model):
    file = 'textFiles/carFeaturesList/all_car_features_lists_' + type_c + "_" + brand + "_" + model
    f_pickle = open(file, "rb")
    return pickle.load(f_pickle)


def save_search_status(brand, model, type_comp):
    file = 'status'
    file_temp = file + "temp"

    stats = SearchStatus(brand, model, type_comp)
    f_pickle = open(file_temp, "wb")
    pickle.dump(stats, f_pickle)
    f_pickle.close()
    os.replace(file_temp, file)


def load_search_status():
    file_manual = 'status_manual.txt'
    # TODO try to load from file first if it fails, purposely or not load from previous state
    # file_auto is where previous state is
    file_auto = 'status'
    try:
        f_pickle = open(file_auto, "rb")
        return pickle.load(f_pickle)
    except (OSError, IOError) as e:
        return None


def remake_by_brand_model(brand, model, browser, type_c, output_list=None, dest_bool=False):
    """
    :param brand:
    :param model:
    :param browser:
    :param type_c:
    :param output_list:
    :param dest_bool: makes the search happen regardless if the destination has already been searched or not
    :return: changes output list (list of lists (brand and model)) and saves lists (brand and model)
    """

    source_import, dest_import = get_source_dest_imports_by_type_c(type_c)
    src, dest = get_source_and_dest_from_type_comp(type_c)
    t_list = source_import.get_cars(brand, model, type_c)  # gets new cars only (updates since last time)
    for car_link_features in t_list:
        if dest not in car_link_features.get_searched_dests() or dest_bool:  # different destination may get a higher
            # score
            dest_import.get_all_cars_dest_url(brand, model, car_link_features, type_c)
            dest_import.get_correct_estimate_prices(car_link_features, browser, dest)
            time.sleep(1)
    try:
        car_link_features_list = pickle_load_cars(type_c, brand, model)
        car_link_features_list.add_car_link_feats_list_to_existing_set(t_list)
        pickle_save_all_car_feature_lists(car_link_features_list, type_c, brand, model)
    except (OSError, IOError) as e:
        print("could not load cars for brand: " + brand + " and model: " + model)
        pickle_save_all_car_feature_lists(t_list, type_c, brand, model)

    save_prices(t_list, type_c)
    if output_list is not None:
        output_list += [t_list]


def update_cars(brand_model_list, type_c, browser):
    """
    will get all pages again
    will output good prices's links into file, but first check if they are already there
    :param browser:
    :param type_c:
    :type brand_model_list: CarLinkFeaturesList
    :param brand_model_list:
    :return:
    """
    # source_import, dest_import = get_source_dest_imports_by_type_c(type_c)
    brand = brand_model_list.get_brand()
    model = brand_model_list.get_model()
    l = []
    remake_by_brand_model(brand, model, browser, type_c, l, True)


def save_prices(car_link_feats_list, type_c):
    """
    purpose is to show prices for one given brand-model
    :param type_c:
    :type car_link_feats_list CarLinkFeaturesList
    :return:
    """
    text = ""
    for car_link_feats in car_link_feats_list:
        cars = car_link_feats.get_cars()
        feats = car_link_feats.get_feats()
        version = feats.get_version()
        dest_urls = car_link_feats.get_destination()[0]
        max_score = car_link_feats.get_max_score()
        dest_urls_text = ""
        for i in dest_urls:
            dest_urls_text += i
        for car in cars:
            print("car link")
            # if car.is_good_estimation():
            estimation = car.get_estimation()
            text += "-----\n" + "brand " + brand + " model " + model \
                    + "\ncar version: " + version \
                    + "\nprice difference: " + str(estimation) \
                    + "\nmax score: " + str(max_score) \
                    + "\nurl:\n" + car.get_link() \
                    + "\ndest_links:\n" + dest_urls_text \
                    + "\n"
    save_prices_to_file(type_c, text)


def save_prices_to_file(type_c, text):
    """
    :param type_c:
    :return:
    """
    filename = "estimates/" + type_c
    t = text
    try:
        obj = pickle_load_final_prices_obj(type_c)
        obj.add_text(t)
    except (OSError, IOError) as e:
        obj = OutputTextContainer(t)
        pickle_save_final_prices_obj(obj, type_c)

    t = obj.get_text()
    olx_find_all_brands_and_models.write_to_file_replace(filename, t)


def pickle_save_final_prices_obj(obj, type_c):
    file = 'final_text_output_' + type_c
    file_temp = file + "temp"
    f_pickle = open(file_temp, "wb")
    pickle.dump(obj, f_pickle)
    f_pickle.close()
    os.replace(file_temp, file)


def pickle_load_final_prices_obj(type_c):
    file = 'final_text_output_' + type_c
    f_pickle = open(file, "rb")
    return pickle.load(f_pickle)


def show_new_good_prices(dict_of_lists, browser):
    # TODO this could open all new stuff in browser
    """
    output all good price's links to file
    output format: \n brand, model, price, link + blank line to put "done" or "ok" or "wrong" or after checking the link \n
    :return:
    """
    for type_c in dict_of_lists:
        for list_of_brands_models_car_links in dict_of_lists[type_c]:
            pass


def parse_status():
    # TODO
    """
    purpose is to set status from text file, status should be according to status class in container_classes.py
    :return: status object
    """
    pass


def delete_database():
    # only data affected by this file
    mydir1 = "textFiles/carFeaturesList"
    mydir2 = "textFiles/carLinksStructs"
    mydir3 = "estimates"
    aux_delete_db(mydir1)
    aux_delete_db(mydir2)
    aux_delete_db(mydir3)


def aux_delete_db(mdir):
    filelist = [f for f in os.listdir(mdir)]
    for f in filelist:
        os.remove(os.path.join(mdir, f))


if __name__ == "__main__":

    if len(sys.argv) > 1:
        print("arguments found")
        if len(sys.argv) == 2:
            if "-h" in sys.argv:
                print("-h for help")
                print("-r to remake one car association")
                print("no arguments to start where u left of")
            elif "-r" in sys.argv:
                print("deleting all, run again to restart")
                delete_database()
                # everything will eventually remake itself
            elif "-status" in sys.argv:
                print("updating status")
                parse_status()
            else:
                print("invalid args")
        else:
            print("invalid args")

    else:
        print("no arguments")
        sources = ["standv"]  # , "olx"]
        dests = ["volantesic"]
        print("starting browser...")
        browser = olx_find_all_brands_and_models.start_browser()
        dict_of_list_for_all_sources_dests = {}
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
                                remake_by_brand_model(brand, model, browser, type_comp,
                                                      list_of_all_lists_of_car_link_feats)
                            time.sleep(5)  # model
                        time.sleep(5)  # brand
                    dict_of_list_for_all_sources_dests[type_comp] = list_of_all_lists_of_car_link_feats
        except Exception as e:
            print(e)
            browser.quit()
            exit()

        print("finished initial full search")
        search_start = True  # bool to know if it's the search's first iteration or not
        status = load_search_status()
        print("initial stats")
        print(status)
        time.sleep(3)

        try:
            while True:
                for type_comp in dict_of_list_for_all_sources_dests:
                    if search_start:
                        if status is not None:
                            if type_comp != status.get_type_c():
                                continue
                    # compare_dict = get_compare_dict(type_comp)
                    list_of_all_car_link_feats_for_source_dest = dict_of_list_for_all_sources_dests[type_comp]
                    for brand_and_model_list in list_of_all_car_link_feats_for_source_dest:
                        brand = brand_and_model_list.get_brand()
                        model = brand_and_model_list.get_model()
                        if search_start:
                            if status is not None:
                                if brand != status.get_brand() and model != status.get_model():
                                    continue
                        search_start = False
                        update_cars(brand_and_model_list, type_comp, browser)
                        save_search_status(brand, model, type_comp)
                        print("new stats")
                        print(status)
                        print("just saved new search results for brand: " + brand + " and model: " + model)
                        sleep = random.randint(10, 20)
                        print("next brand-model list, (sleep " + str(sleep) + "secs)")
                        time.sleep(sleep)
        except Exception as e:
            print(e)
            browser.quit()
            exit()
        browser.quit()

# the idea is to check standvirtual, then olx, all sources..., sequentialy and check if there is a new one and
#  add that new one to our structure and then compare to volantesic and all other destinations...,

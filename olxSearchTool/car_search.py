import requests
from bs4 import BeautifulSoup
import threading

import olx_find_all_brands_and_models
import compare_models
import standv_find_all_brands_and_models
import volantesic_find_all_brands_and_models
from car_links_struct import MaxScoreToLowForEvaluation


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


if __name__ == "__main__":
    sources = ["standv"]  # , "olx"]
    dests = ["volantesic"]
    """
    while True:
        for source in sources:
            for dest in dests:
                """

    source = "standv"
    dest = "volantesic"
    type_comp = source + "_" + dest
    source_import, dest_import = get_source_dest_imports(source, dest)
    compare_dict = get_compare_dict(type_comp)
    brand = "abarth"
    model = "500"
    lis = source_import.get_cars(brand, model)
    for car_link_features in lis:
        features = car_link_features.get_feats()
        buttons = dest_import.get_buttons_from_features(brand, model, features, type_comp)
        try:
            max_score, max_score_buttons = dest_import.filter_buttons(buttons)
            print("max_score " + str(max_score))
            print()
            print(str(len(max_score_buttons)))
        except MaxScoreToLowForEvaluation:
            print("no evaluation was possible, similarity score to low")
        # dest_import.get_correct_price(lis)

# TODO the idea is to check standvirtual, then olx, all sources..., sequentialy and check if there is a new one and
#  add that new one to our structure and then compare to volantesic, all destinations...,

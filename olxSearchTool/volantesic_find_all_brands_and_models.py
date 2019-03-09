import requests
from bs4 import BeautifulSoup
import sys

import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import olx_find_all_brands_and_models
import feats_mapper
from car_links_struct import MaxScoreToLowForEvaluation


def get_all_brands():
    brands_models_volantesic = {}
    url = "https://volantesic.pt/marcas-carros/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    brand_names = soup.find_all('p', {"class": "brandSlideName"})
    for brand in brand_names:
        brand = brand.text.lower().replace(" ", "-")
        # print(brand)
        brands_models_volantesic[brand] = {}
    # print
    # print("number brands")
    # print(len(brands_models_volantesic))
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


def get_dest_url(feats, brand, model):
    year = feats.year
    used = feats.used

    # closest year calculation
    preview_url = 'https://volantesic.pt/' + brand + '/' + model
    # print(preview_url)
    preview_r = requests.get(preview_url)
    soup = BeautifulSoup(preview_r.text, "html.parser")
    links = soup.find_all('p', {"class": "carBlockTitle"})

    # TODO this is not ok, there should be a better way to get year, fix with scores fix
    prev_year_interval = 100
    min_year = 100
    for link in links:
        test_year = link.strong.text
        # print(year)
        test_year = int(test_year)
        if test_year == year:
            feats.is_exact_year()
        year_interval = abs(year - test_year)
        if year_interval < prev_year_interval:
            min_year = test_year
        if year_interval == 0:
            break

    year = min_year

    dest_url = 'https://volantesic.pt/' + brand + '/' + model + '/' + str(year) + '/' + used
    # print(dest_url)
    return dest_url


def get_clean_feats(feats, type_c):
    """
    :param type_c:
    :param feats: src_feats
    :return: feats list for volantesic
    """
    clean_feats = {}
    feats_assoc = feats_mapper.pickle_load(type_c)
    src_feats_dict = feats.get_feats_dict()
    for feat_type in src_feats_dict:
        feat_val = src_feats_dict[feat_type]
        print(feat_type)
        print(feat_val)
        clean_feats[feat_type] = feats_assoc[feat_type][feat_val]

    print(clean_feats)
    return clean_feats


def get_all_seleccione_buttons(url):
    """
    :param url: ex: https://volantesic.pt/marcas-carros/jaguar/daimler/2008/usado/
    :return: all links attached to the selecione buttons
    """

    # this should be useful for olx maybe, but not used yet
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        # print(soup)

        links = soup.find_all("a", string="Selecione")
        links = [link['href'] for link in links]
        links = ["https://volantesic.pt" + link.replace("opcoes", "preco") for link in links]
        print(links)
        print(len(
            links))  # all selecciones appear ate' os escondidos (alguns estao escondidos pelo seleccao das opcoes


def get_all_seleccione_text_and_button(url):
    """
    :param url: ex: https://volantesic.pt/marcas-carros/jaguar/daimler/2008/usado/
    :return: all links attached to the selecione buttons
    """
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        # print(soup)

        seleccione_buttons = soup.find_all("a", string="Selecione")
        seleccione_text_association = {}
        for seleccione in seleccione_buttons:
            version = seleccione.parent.parent.parent.find("div", {"class": "versionsListControls"}).p.text
            features_text = seleccione.parent.p.text
            seleccione_text_association[seleccione] = [features_text, version]
            # print(seleccione_text_association)
        return seleccione_text_association


def get_buttons_from_features(brand, model, feats, type_c):
    """
    must give a score based on how precise the search is and show that score the score or similarity score is how
    much the car from the source is similar to the destination, the higher the better
    :param type_c:
    :param feats: CarFeatures object
    :return: returns list of all buttons associated with given feats and their score
    """

    buttons = {}  # key: button, val: score
    url = get_dest_url(feats, brand, model)
    r = requests.get(url)
    t_year = -1
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        t_year = soup.find('span', {"itemprop": "releaseDate"}).text
        print(t_year)
    else:
        print("error in request")

    t_year = int(t_year)
    sel_buttons = get_all_seleccione_text_and_button(url)
    caixa_mudancas, traction, segmento, fuel_type = get_clean_feats(feats, type_c)
    cv = int(feats.cv)
    str_cv = str(cv) + "cv"
    year = int(feats.year)
    doors = str(feats.doors) + "p"
    version = feats.version

    for sel in sel_buttons:
        select = sel_buttons[sel]
        score = 0
        text = select[0]
        t_version = select[1].strip().lower()

        text = text.strip().lower().split(" ")
        t_segmento = text[0]
        t_cv = text[1]
        int_t_cv = t_cv.strip().lower().replace("cv", "")
        int_t_cv = int(int_t_cv)
        t_doors = text[2]
        t_fuel_type = text[3]
        t_traction = text[4]
        t_caixa_mudancas = text[5]

        # TODO fix how the scores work later
        if caixa_mudancas in t_caixa_mudancas:
            score += 5
        if traction == t_traction:
            score += 5
        if segmento == t_segmento:
            score += 5
        if str_cv == t_cv:
            score += 10
        elif int_t_cv - 5 < cv < int_t_cv + 5:
            score += 5
        elif int_t_cv - 10 < cv < int_t_cv + 10:
            score += 1
        if doors == t_doors:
            score += 5
        if fuel_type == t_fuel_type:
            score += 5
        if version != "":
            if version == t_version:
                score += 30
            elif version in t_version:
                score += 15
            else:
                version_tokens = version.split(" ")
                for token in version_tokens:
                    if token in t_version:
                        score += 1
        if t_year == -1:
            print("t_year=-1 error")
            pass
        elif year == t_year:
            score += 5
        elif year - 2 < t_year < year + 2:
            score += 1

        buttons[sel] = score
    return buttons


def filter_buttons(buttons):
    """
    :param buttons: input buttons, alongside scores key: button, val: score
    :return: max_score, list with all buttons with max_score as key
    """
    max_score = 0
    max_score_buttons = []
    for i in buttons:
        if buttons[i] > max_score:
            max_score = buttons[i]
    # TODO fix max_score minimum value once more info is collected on the scores and how to make them better
    if max_score < 30:
        raise MaxScoreToLowForEvaluation
    for i in buttons:
        if buttons[i] == max_score:
            max_score_buttons += [i]

    return max_score, max_score_buttons


def get_car_estimated_price_volantesic(browser, car):
    """

    :param browser:
    :param car:
    :return: returns base value for a car
    """
    km = car.km
    browser.get(car.link)

    # press buy private
    browser.find_element_by_id("tabBuyPrivate").click()
    wait = WebDriverWait(browser, 10)

    # press the button to change km
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class=pricingMileageEdit]")))
    element.click()

    # input km number
    element = wait.until(EC.element_to_be_clickable((By.ID, 'TextBoxKM')))
    element.clear()
    element.send_keys(km)

    # press button to change km
    browser.find_element_by_css_selector("a[onclick*='VehiclePrice.SaveTexBoxKMPricing']").click()

    # get value to compare to
    element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[id*=drawSVG]')))  # wait for image to appear
    soup = BeautifulSoup(browser.page_source, "html.parser")
    base_value = soup.svg.find('tspan', string="Valor a Particular").parent
    base_value = base_value.find_all('tspan', text=True)

    # print(base_value)
    for i in base_value:
        if "€" in i.text:
            base_value = i.text.replace("€", "").replace(" ", "").strip()
    print(base_value)
    return base_value


def get_correct_estimate_price(car, type_c):
    # this is to be used in import car_search.py
    """
    uses get_car_estimated_price_volantesic to get correct prices
    :param type_c:
    :param car: output of get_cars from source
    :return: correct price is picked after inspecting
    all prices from all given buttons and picks the lowest, to get worst possible evaluation and see if worst
    possible is good, or returns None if there was no value worth returning (because the cars are not similar enough)
    """
    element = next(iter(car))
    brand = element.get_brand()
    model = element.get_model()
    buttons = get_buttons_from_features(brand, model, element, type_c)
    buttons_links = []
    try:
        max_score, max_score_buttons = filter_buttons(buttons)
    except MaxScoreToLowForEvaluation:
        print("no evaluation was possible, similarity score to low")
        return None
    for but in max_score_buttons:
        url = but['href']
        print(url)


def get_all_cars_estimate_price(cars, type_c):
    pass


def build_estimate_struct():
    pass


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
    print()


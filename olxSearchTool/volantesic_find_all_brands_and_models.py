import os

import requests
import unidecode
from bs4 import BeautifulSoup
import sys
import pickle
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import olx_find_all_brands_and_models
import feats_mapper
from car_links_struct import *
from container_classes import FeaturesContainer


def get_all_brands():
    brands_models_volantesic = {}
    url = "https://volantesic.pt/marcas-carros/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    brand_names = soup.find_all('p', {"class": "brandSlideName"})
    for brand in brand_names:
        brand = brand.text.lower().replace(" ", "-")
        # # print(brand)
        brands_models_volantesic[brand] = {}
    # # print
    # # print("number brands")
    # # print(len(brands_models_volantesic))
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
        # print(model)
        models[model] = {}
    # print(models)
    brands_models_volantesic[brand] = models
    return brands_models_volantesic


def get_all_brands_and_models():
    brands_models_volantesic = get_all_brands()
    for brand in brands_models_volantesic.keys():
        get_all_models_by_brand(brand, brands_models_volantesic)
    return brands_models_volantesic


def pickle_save(brands_models_volantesic):
    file = 'textFiles/brands_and_models_volantesic'
    file_temp = file + "temp"
    f_pickle = open(file, "wb")
    pickle.dump(brands_models_volantesic, f_pickle)
    f_pickle.close()
    os.replace(file_temp, file)


def get_dest_url(feats, brand, model):
    year = feats.year
    used = feats.used

    # closest year calculation
    preview_url = 'https://volantesic.pt/' + brand + '/' + model
    # # print(preview_url)
    # print("preview_url " + preview_url)
    preview_r = requests.get(preview_url)
    soup = BeautifulSoup(preview_r.text, "html.parser")
    links = soup.find_all('p', {"class": "carBlockTitle"})

    # TODO this is not ok, there should be a better way to get year, fix with scores fix
    prev_year_interval = 100
    min_year = 100
    for link in links:
        try:
            test_year = link.strong.text
        except AttributeError as e:  # NOVO element, it appears again, as a normal case, so, ignore is best solution
            # # print(e)
            continue
        # # print(year)
        test_year = int(test_year)
        year_interval = abs(year - test_year)
        if year_interval < prev_year_interval:
            min_year = test_year
        if year_interval == 0:
            break

    year = min_year

    dest_url = 'https://volantesic.pt/' + brand + '/' + model + '/' + str(year) + '/' + used
    # # print(dest_url)
    return dest_url


def get_clean_feats(feats, type_c):
    # TODO refactor to file imported by all destinations
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
        # # print(feat_type)
        # # print(feat_val)
        clean_feats[feat_type] = feats_assoc[feat_type][feat_val]

    # # print(clean_feats)
    return clean_feats


def get_all_seleccione_buttons(url):
    # not used maybe in olx
    """
    :param url: ex: https://volantesic.pt/marcas-carros/jaguar/daimler/2008/usado/
    :return: all links attached to the selecione buttons
    """

    # this should be useful for olx maybe, but not used yet
    # print("seleccione_buttons " + url)
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        # # print(soup)

        links = soup.find_all("a", string="Selecione")
        links = [link['href'] for link in links]
        links = ["https://volantesic.pt" + link.replace("opcoes", "preco") for link in links]
        # # print(links)
        # # print(len(
        #    links))  # all selecciones appear ate' os escondidos (alguns estao escondidos pelo seleccao das opcoes


def get_all_seleccione_text_and_button(url):
    """
    :param url: ex: https://volantesic.pt/marcas-carros/jaguar/daimler/2008/usado/
    :return: all links attached to the selecione buttons
    """
    # print("text_and_button " + url)
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        # # print(soup)

        seleccione_buttons = soup.find_all("a", string="Selecione")
        seleccione_text_association = {}
        for seleccione in seleccione_buttons:
            version = seleccione.parent.parent.parent.find("div", {"class": "versionsListControls"}).p
            # print(version)
            # print("version_txt")
            version = version.text
            features_text = seleccione.parent.p
            # print("feats_text")
            # print(features_text)
            features_text = features_text.text
            seleccione_text_association[seleccione] = [features_text, version]
            # # print(seleccione_text_association)
        return seleccione_text_association


def get_buttons_from_features(brand, model, feats, type_c):
    """
    must give a score based on how precise the search is and show that score, the score or similarity score is how
    much the car from the source is similar to the destination, the higher the better, has a minimum value
    :type feats: CarFeatures
    :param brand:
    :param model:
    :param type_c:
    :param feats: CarFeatures object
    :return: returns list of all buttons associated with given feats and their score
    """

    ## print("new set of buttons for different car features")
    buttons = {}  # key: button, val: score
    url = get_dest_url(feats, brand, model)
    # print("buttons_from_feat " + url)
    r = requests.get(url)
    t_year = -1
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        t_year = soup.find('span', {"itemprop": "releaseDate"})
        # print(t_year)
        t_year = t_year.text
        ## print("t_year: " + t_year)
    else:
        # print("error in request")
        exception = FailedURLException(url)
        raise exception
    t_year = int(t_year)

    feats_dict = get_clean_feats(feats, type_c)
    caixa_mudancas = feats_dict['tipo de caixa']
    traction = feats_dict['traccao']
    segmento = feats_dict['segmento']
    fuel_type = feats_dict['combustivel']
    cv = int(feats.cv)
    year = int(feats.year)
    doors = str(feats.doors) + "p"
    version = feats.version
    src_feats = FeaturesContainer(caixa_mudancas, traction, segmento, fuel_type, cv, year, doors, version)

    sel_buttons = get_all_seleccione_text_and_button(url)

    for sel in sel_buttons:
        # print()
        # print("next button")
        # print()
        select = sel_buttons[sel]
        text = select[0]

        t_version = select[1].strip().lower()

        text = text.strip().lower().split(" ")
        t_segmento = text[0]
        t_cv = text[1]
        t_int_cv = t_cv.strip().lower().replace("cv", "")
        t_int_cv = int(t_int_cv)
        t_doors = text[2]
        t_fuel_type = text[3]
        t_traction = text[4]
        t_caixa_mudancas = text[5]
        dest_feats = FeaturesContainer(t_caixa_mudancas, t_traction, t_segmento, t_fuel_type, t_int_cv, t_year, t_doors,
                                       t_version)

        score = set_score(src_feats, dest_feats)
        buttons[sel] = score
    return buttons


def set_score(src_feats, dest_feats):
    # TODO refactor this function to all dests imported file
    """
    purpose is to set score or add to other function also helping to set score from any destination
    also good to log all this information to later display it when presenting the chosen car
    :param dest_feats:
    :param src_feats:
    :return:
    """
    score = 0

    caixa_mudancas = src_feats.caixa_mudancas
    traction = src_feats.traction
    segmento = src_feats.segmento
    fuel_type = src_feats.fuel_type
    cv = src_feats.cv_int
    year = src_feats.year_int
    doors = src_feats.doors
    version = src_feats.version
    str_cv = str(cv) + "cv"

    t_caixa_mudancas = dest_feats.caixa_mudancas
    t_traction = dest_feats.traction
    t_segmento = dest_feats.segmento
    t_fuel_type = dest_feats.fuel_type
    t_int_cv = dest_feats.cv_int
    t_cv = str(t_int_cv)
    t_year = dest_feats.year_int
    t_doors = dest_feats.doors
    t_version = dest_feats.version
    '''
    # print("source \t dest" + "\n"
          + segmento + "\t" + t_segmento + "\n"
          + str(cv) + "\t" + str(t_cv) + "cv" + "\n"
          + doors + "\t" + t_doors + "\n"
          + fuel_type + "\t" + t_fuel_type + "\n"
          + traction + "\t" + t_traction + "\n"
          + caixa_mudancas + "\t" + t_caixa_mudancas + "\n"
          + str(year) + "\t" + str(t_year) + "\n"
          + version + "\t" + t_version)
    '''
    # scores might need some twerking
    if caixa_mudancas in t_caixa_mudancas:
        score += 3
    if traction == t_traction:
        score += 3
    if segmento == t_segmento:
        score += 3
    if str_cv == t_cv:
        score += 10
    elif t_int_cv - 5 < cv < t_int_cv + 5:
        score += 3
    elif t_int_cv - 10 < cv < t_int_cv + 10:
        score += 1
    if doors == t_doors:
        score += 3
    if fuel_type == t_fuel_type:
        score += 3
    if version != "":
        if version == t_version:
            score += 30
        elif version in t_version:
            score += 16
        else:
            scored = True
            version_tokens = version.split(" ")
            for i in range(len(version_tokens) - 1):
                v_tokens_aglomeration = version_tokens[i] + " " + version_tokens[i + 1]
                if v_tokens_aglomeration in t_version:
                    score += 16
                    scored = False
                    break
            if scored:
                for token in version_tokens:
                    if token in t_version:
                        score += 1
    if t_year == -1:
        # print("t_year=-1 error")
        pass
    elif year == t_year:
        score += 5
    elif year - 2 < t_year < year + 2:
        score += 1
    # print("score: " + str(score))
    return score


def filter_buttons(buttons):
    """
    from all the buttons chooses the buttons with the highest similarity score
    :param buttons: input buttons, alongside scores key: button, val: score
    :return: max_score, list with all buttons with max_score as key
    """
    max_score = 0
    max_score_buttons = []
    for i in buttons:
        if buttons[i] > max_score:
            max_score = buttons[i]
    # max_score minium value might need some twerking
    if max_score < 30:
        raise MaxScoreTooLowForEvaluation(max_score)
    for i in buttons:
        if buttons[i] == max_score:
            max_score_buttons += [i]

    return max_score, max_score_buttons


def get_car_estimated_price(browser, url, car):
    """

    :param browser:
    :param car: Car Object
    :return: returns base value for a car
    """
    km = car.km
    browser.get(url)

    # press buy private
    try:
        wait = WebDriverWait(browser, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, "tabBuyPrivate")))
        element.click()

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
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[id*=drawSVG]')))  # wait for svg image to appear
    except WebDriverException as e:
        base_value = -1
        return base_value
    try:
        soup = BeautifulSoup(browser.page_source, "html.parser")
        base_value = soup.svg.find('tspan', string="Valor a Particular").parent
        base_value = base_value.find_all('tspan', text=True)

        # # print("base_value")
        # # print(base_value)
        # print("base val tokens")
        for i in base_value:
            # print(i)
            txt = unidecode.unidecode(i.text)
            ## printx(txt)
            if "€" in txt:
                base_value = txt.replace("€", "")
                break
            elif "EUR" in txt:
                base_value = txt.replace("EUR", "")
        base_value = base_value.replace(" ", "").strip()
        ## print(base_value)
        base_value = int(base_value)
        print("base value")
        print(url)
        print(str(base_value))
    except AttributeError as e:
        base_value = -1
    return base_value


def get_correct_estimate_prices(car_link_features, browser, dest):
    # this is to be used in import car_search.py

    """
    purpose is to set the estimated_price in all Car objects in car_link_features
    :param dest: used to set already searched destination
    :type car_link_features: CarLinkFeatures
    :param browser:
    :param car_link_features: CarLinkFeatures object

    :return: correct price is picked after inspecting
    all prices from all given buttons and picks the lowest, to get worst possible evaluation and see if worst
    possible is good, or returns None if max_score is too low -> there was no value worth returning (because the cars
    are not similar enough)
    the above in :return is done for all cars with the same features and estimated_price is set in all of them
    """
    if car_link_features is None:
        # print("car link feats is none in get_correct_estimate_prices")
        return
    cars = car_link_features.get_cars()
    feats = car_link_features.get_feats()
    urls, max_score = feats.get_destination()
    for car in cars:
        for url in urls:
            estimated_price = get_car_estimated_price(browser, url, car)
            car.set_new_estimation(estimated_price, dest)  # set new estimated price if it is higher than the last
    car_link_features.add_searched_dest(dest)


def get_all_cars_dest_url(brand, model, car_link_feats, type_c):
    # this is to be used in import car_search.py

    """
    purpose is to get all urls associated to the seleccione buttons (all possible dest urls associated to a set of features)
    :type car_link_feats: CarLinkFeatures
    :param model:
    :param car_link_feats:
    :param type_c:
    :return urls, max_score

    """

    # print()
    features = car_link_feats.get_feats()
    try:
        buttons = get_buttons_from_features(brand, model, features, type_c)
    except FailedURLException as e:
        raise e
    max_score_buttons = []
    try:
        max_score, max_score_buttons = filter_buttons(buttons)
        # print()
        # print("max_score " + str(max_score))
        # # print("max_score buttons number: " + str(len(max_score_buttons)))
    except MaxScoreTooLowForEvaluation as e:
        # print()
        e.get_score_error_msg()
        return

    urls = []
    for but in max_score_buttons:
        url = 'https://volantesic.pt' + but['href']
        urls += [url]
    links = urls
    links = [link.replace("opcoes", "preco") for link in links]
    urls = links
    # print(urls)
    car_link_feats.set_destination(urls, max_score)
    return urls, max_score


def pickle_load():
    return olx_find_all_brands_and_models.load_brands_and_models("brands_and_models_volantesic")


if __name__ == "__main__":
    brands_models_volantesic = {}
    if len(sys.argv) > 1:
        # print("arguments found")
        if "-h" in sys.argv:
            # print
            # print("no args to use what we have")
            # print("-remake to get all from olx")
            exit(0)
        if "-remake" not in sys.argv:
            try:
                brands_models_volantesic = pickle_load()
            except (OSError, IOError) as e:
                brands_models_volantesic = get_all_brands_and_models()
                pickle_save(brands_models_volantesic)
        else:
            # print("remaking")
            brands_models_volantesic = get_all_brands_and_models()
            pickle_save(brands_models_volantesic)
    else:
        # print("no args")
        brands_models_volantesic = pickle_load()

    # print(brands_models_volantesic)
    # print()

import requests
from bs4 import BeautifulSoup
import threading

# import scapy
# import re
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import olx_find_all_brands_and_models
import volantesic_find_all_brands_and_models
import compare_models


# TODO this is required, because there is no reliable way of getting the model otherwise
# brand_model_dict = {"":[]}  1 brand - many models


def get_features_olx(soup):
    price = soup.find_all('div', {"class": "price-label"})
    price = ''.join(price[0].find_all(text=True))
    price = price.replace("€", "")
    price = price.replace(".", "")
    price = price.strip()

    price = int(price)
    print(str(price))

    used = soup.find('th', string="Condição").parent.a.text.strip()
    if used.lower() == "usado":
        used = True
    else:
        used = False
    print(used)

    km = soup.find('th', string="Quilómetros").parent.strong.text.strip().replace(".", "")
    print(km)
    km = int(km)

    fuel_type = soup.find('th', string="Combustível").parent.a.text.strip()
    print(fuel_type)

    year = soup.find('th', string="Ano").parent.strong.text.strip()
    print(year)
    year = int(year)

    model = soup.find('th', string="Modelo").parent.a.text.strip()
    print(model)

    name_feature = {"price": price, "used": used, "km": km, "fuel_type": fuel_type, "year": year, "model": model}
    return name_feature


def get_car_links_from_a_given_olx_page(url):
    """
    :param url: input url already has info on brand and model
    :return: all cars for a given brand
    """
    # TODO this checks 1st page only, check all pages

    # r = requests.get('https://www.olx.pt/carros-motos-e-barcos/carros/abarth/?search[filter_enum_modelo][0]=500&search[description]=1')
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        # no olx todos os links na pagina que vai ate ao carro tem /anuncio/ , e' so' preciso procurar em todos esses links
        matched_lines = [line for line in r.text.split('\"') if "/anuncio/" in line]
        for cnt, line in enumerate(matched_lines):
            new_line = line.split("html")
            new_line = new_line[0] + "html"
            matched_lines[cnt] = new_line

        links_to_cars = list(set(matched_lines))
        # print("number cars " + str(len(links_to_cars)))

        # TODO use this to see if page changed from last time?
        # TODO if a given brand has many pages of cars, check last page for number of cars? yes
        # TODO default esta ordenado por mais recente no olx, o primeiro carro vai para a primeira pagina
        # TODO after checking new car exists and identifying it check if it exists in persistent list
        return links_to_cars


def get_all_selecione_buttons_volantesic_for_olx(url):
    """
    # TODO this is what to do after getting all the parameters from olx, must get average from all prices in volantesic?
    getting all buttons is useless for standvirtual
    :param url: ex: https://volantesic.pt/marcas-carros/jaguar/daimler/2008/usado/
    :return: all links attached to the selecione buttons
    """
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        # print(soup)

        links = soup.find_all("a", string="Selecione")
        links = [link['href'] for link in links]
        links = ["https://volantesic.pt" + link.replace("opcoes", "preco") for link in links]
        print(links)
        print(len(
            links))  # aparecem todos os selecione ate' os escondidos (alguns estao escondidos pelo seleccao das opcoes

        # for link in links:
        link = links[0]


def get_features(url, soup):
    if "standvirtual" in url:
        elements_dict = get_features_standvirtual(soup)
    if "olx" in url:
        elements_dict = get_features_olx(soup)

    return elements_dict


def get_dest_url_in_volantesic(features_dict):
    brand = features_dict["brand"]  # set at the beggining manually in for loop (checks all brands)
    model = features_dict['model']
    year = features_dict['year']
    # print(str(year))
    used = features_dict['used']
    if used:
        used = "usado"
    else:
        used = "novo"

    # closest year calculation
    preview_url = 'https://volantesic.pt/' + brand + '/' + model
    # print(preview_url)
    preview_r = requests.get(preview_url)
    soup = BeautifulSoup(preview_r.text, "html.parser")
    links = soup.find_all('p', {"class": "carBlockTitle"})

    prev_year_interval = 100
    min_year = 100
    for link in links:
        test_year = link.strong.text
        # print(year)
        test_year = int(test_year)
        year_interval = abs(year - test_year)
        if year_interval < prev_year_interval:
            min_year = test_year
        if year_interval == 0:
            break

    year = min_year

    dest_url = 'https://volantesic.pt/' + brand + '/' + model + '/' + str(year) + '/' + used
    print(dest_url)
    return requests.get(dest_url)


def get_car_estimated_price_volantesic(browser, url):
    browser.get(url)

    # press buy private
    browser.find_element_by_id("tabBuyPrivate").click()
    wait = WebDriverWait(browser, 10)

    # press the button to change km
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class=pricingMileageEdit]")))
    element.click()

    # input km number
    element = wait.until(EC.element_to_be_clickable((By.ID, 'TextBoxKM')))
    element.clear()
    element.send_keys("100000")

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


def get_features_standvirtual(url):
    """
    :param url: standvirtual's car url
    :return: features_dict, key: feature name, val: feat value
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # standvirtual tem mto mais informacao, n e' preciso randomizar alguns campos na procura no bkk se for standvirtual
    price = soup.find_all('span', {"class": "offer-price__number"})
    price = ''.join(price[0].find_all(text=True))
    price = price.replace("EUR", "")
    price = price.strip()
    price = price.replace(" ", "")

    price = int(price)
    print(str(price))

    used = soup.find('span', string="Condição").parent.a.text.strip()
    if used.lower() == "usados":
        used = True
    else:
        used = False

    print(used)

    km = soup.find('span', string="Quilómetros").parent.div.text.strip().replace(" ", "")
    km = km.replace("km", "")
    print(km)
    km = int(km)

    fuel_type = soup.find('span', string="Combustível").parent.a.text.strip()
    print(fuel_type)

    year = soup.find('span', string="Ano de Registo").parent.div.text.strip()
    print(year)
    year = int(year)

    model = soup.find('span', string="Modelo").parent.a.text.strip()
    print(model)

    # TODO
    # Cilindrada
    # Cor
    # info de Caixa de mudancas
    # traccao
    # origem? - pais de origem

    name_feature = {"price": price, "used": used, "km": km, "fuel_type": fuel_type, "year": year, "model": model}
    return name_feature


def get_car_accurate_page_volantesic(features):
    # TODO
    """
    :param features: dictionary with key: parameter name, value: parameter ready for use by volantesic
    :return: link to webpage from where you get the price from
    """

    # v_url = get_dest_url_in_volantesic(features)
    v_url = "https://volantesic.pt/marcas-carros/alfa-romeo/giulietta/2011/usado/"


def get_car_links_standv():
    # TODO
    pass


def get_car_links_standv_to_compare_to_volantesic(comp_dic):
    # TODO
    pass


def get_compare_dict(type_c):
    compare_d = {}
    if type_c == "olx_volantesic":
        compare_d = compare_models.pickle_load_olx_volante()
    elif type_c == "standv_volantesic":
        compare_d = compare_models.pickle_load_standv_volante()
    else:
        print("type_c is wrong")
    return compare_d


type_comp = "standv"
compare_dict = get_compare_dict(type_comp)
# url = "https://volantesic.pt/abarth/500/2015/usado/comprar/preco/?ID=88279"
# browser = olx_find_all_brands_and_models.start_browser()
get_car_links_standv()  # these are the links from standv
get_car_links_standv_to_compare_to_volantesic(compare_dict)  # only those being compared to volantesic
standv_car_url = "https://www.standvirtual.com/anuncio/alfa-romeo-giulietta-1-6-jtdm-sport-nacional-ID8MqJJV.html" \
                 "#1881796c1f;promoted "
feature_dict = get_features_standvirtual(standv_car_url)
get_car_accurate_page_volantesic(feature_dict)

# get_car_estimated_price_volantesic(browser, url)
# input("press key to exit")
# browser.quit()

# TODO ignorar os que aparecem do standvirtual no olx e usar o proprio site do standvirtual para fazer os do standvirtual

# TODO olx average

# TODO os clicks no que for preciso deve de estar no ficheiro associado ao site em que isso aconteces

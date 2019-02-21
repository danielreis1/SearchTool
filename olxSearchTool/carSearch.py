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

# from pyvirtualdisplay import Display


# TODO this is required, because there is no reliable way of getting the model otherwise
# brand_model_dict = {"":[]}  1 brand - many models

def get_features_standvirtual(soup):
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

    # Cilindrada
    # Cor
    # info de Caixa de mudancas
    # traccao
    # origem? - pais de origem

    name_feature = {"price": price, "used": used, "km": km, "fuel_type": fuel_type, "year": year, "model": model}
    return name_feature


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


def get_features(url, soup):
    if "standvirtual" in url:
        elements_dict = get_features_standvirtual(soup)
    if "olx" in url:
        elements_dict = get_features_olx(soup)

    return elements_dict


def get_brand_and_model_from_url(url):
    brand_and_model = url.split("ID")[0]
    brand_and_model = brand_and_model.replace("-", " ")
    brand_and_model = brand_and_model.split('/anuncio/')[1]
    # print(brand_and_model)  # for google search
    return brand_and_model


def get_dest(features_dict, brand):
    brand_and_model = get_brand_and_model_from_url(url)
    brand = brand  # set at the beggining manually in for loop (checks all brands)
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


brandList = []  # all lists
brand = 'abarth'
'''
r = requests.get(
    'https://www.olx.pt/carros-motos-e-barcos/carros/abarth/?search[filter_enum_modelo][0]=500&search[description]=1')


if r.status_code == requests.codes.ok:
    # no olx todos os links na pagina que vai ate ao carro tem /anuncio/ , e' so' preciso procurar em todos esses links
    # print(r.text)
    # anuncio = "http[?]*/anuncio/"
    # link_list = [m for m in re.findall(anuncio, r.text)]
    # print(link_list)
    matched_lines = [line for line in r.text.split('\"') if "/anuncio/" in line]
    for cnt, line in enumerate(matched_lines):
        new_line = line.split("html")
        new_line = new_line[0] + "html"
        matched_lines[cnt] = new_line

    links_to_cars = list(set(matched_lines))  # remove duplicates
    # print(links_to_cars)
    print("number cars " + str(len(links_to_cars)))

    # TODO use this to see if page changed from last time?
    # TODO if a given brand has 20 pages of cars, check 1st and last page for number of cars? sim
    # TODO default esta ordenado por mais recente no olx, o primeiro carro vai para a primeira pagina
    # TODO after checking new car exists and identifying it check if it exists in persistent list
    # part 2
    # this for is just to test specific site

    url = links_to_cars[0]  # random, - between standvirtual or olx

    '''
'''
        for i in links_to_cars:
        if "standvirtual" in i:
            url = i
            break
            

    url_type = ""
    if "standvirtual" in url:
        url_type = "standvirtual"
    elif "olx" in url:
        url_type = "olx"

    print(url)

    # pode redereccionar para standvirtual ou olx
    r2 = requests.get(url)
    # get features: price, year, km, used or not, fuel
    if r2.status_code == requests.codes.ok:
        soup1 = BeautifulSoup(r2.text, "html.parser")
        # print(soup)
        features_dict = get_features(url, soup1)
        r3 = get_dest(features_dict, brand)
        '''
'''
if r3.status_code == requests.codes.ok:
    soup2 = BeautifulSoup(r3.text, "html.parser")
    #print(soup2)

    # TODO put this into a function and call after check if it is persistent
    links = soup2.find_all("a", string="Selecione")
    links = [link['href'] for link in links]
    links = ["https://volantesic.pt" + link.replace("opcoes", "preco") for link in links]
    print(links)
    print(len(links))  # aparecem todos os selecione ate' os escondidos,
    # TODO put in dict -> brand: {}, and make persistent

    # TODO olx ve todos e tira pelo preco mais baixo para ver se e' bom ou nao
    #for link in links:  # TODO get from persistent if exists, if not call get links func
    link = links[0]
    '''

url = "https://volantesic.pt/abarth/500/2015/usado/comprar/preco/?ID=88279"
link = "https://volantesic.pt/abarth/500/2015/usado/comprar/preco/?ID=88279"

# print(link)
# r = requests.get(link)
# soup = BeautifulSoup(r.text, "lxml")
# print(soup)
# svg_to_parse = soup.find("svg")
# print(svg_to_parse)
# svg = BeautifulSoup(svg_to_parse, "xml")
# precos = soup.find_all("svg")
# print(precos)


# display = Display(visible=0, size=(1366, 768))

options = Options()
options.headless = True
# TODO change this string to comand line input or environment variable, and create script to initialize that variable
profile = webdriver.FirefoxProfile("/root/.mozilla/firefox/yy1okn6z.default")
firefox_binary = FirefoxBinary("/usr/bin/firefox")
browser = webdriver.Firefox(options=options, firefox_profile=profile, firefox_binary=firefox_binary)
browser.get(url)

# press buy private
browser.find_element_by_id("tabBuyPrivate").click()
wait = WebDriverWait(browser, 10)
# press the button to change km
element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class=pricingMileageEdit]")))
browser.find_element_by_css_selector("a[class=pricingMileageEdit]").click()
# input km number
element = wait.until(EC.element_to_be_clickable((By.ID, 'TextBoxKM')))
element = browser.find_element_by_id("TextBoxKM")
element.clear()
element.send_keys("100000")
# press button to change km
browser.find_element_by_css_selector("a[onclick*='VehiclePrice.SaveTexBoxKMPricing']").click()

# get value to compare to
element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[id*=drawSVG]'))) # wait for image to appear
soup = BeautifulSoup(browser.page_source, "html.parser")
base_value = soup.svg.find('tspan', string="Valor a Particular").parent
base_value = base_value.find_all('tspan', text=True)
#print(base_value)
for i in base_value:
    if "€" in i.text:
        base_value = i.text.replace("€", "").replace(" ", "").strip()
print(base_value)

input("press key to exit")
browser.quit()

# TODO olx ve todos e tira pelo preco mais baixo para ver se e' bom ou nao

# TODO standvirtual permite uma pesquisa mais certeira

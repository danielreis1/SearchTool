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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("arguments found")
        if "-h" in sys.argv:
            print

    else:
        print("args not found")
        volante_brands_and_models = volantesic_find_all_brands_and_models.pickle_load()
        olx_brands_and_models = olx_find_all_brands_and_models.pickle_load()


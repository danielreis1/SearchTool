import os
import pickle
import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import olx_find_all_brands_and_models


def load_history_set():
    file = "estimates_history/hist"
    f_pickle = open(file, "rb")
    return pickle.load(f_pickle)


def save_history_set(obj):
    file = "estimates_history/hist"
    file_temp = file + "temp"
    f_pickle = open(file_temp, "wb")
    pickle.dump(obj, f_pickle)
    f_pickle.close()
    os.replace(file_temp, file)


def open_link_browser(link, browser, dest_links):
    wait = WebDriverWait(browser, 10)
    for i in dest_links:
        element = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "body")))
        element.send_keys(Keys.CONTROL + 't')
        windows = browser.window_handles
        browser.switch_to.window(windows[len(windows) - 1])
        browser.get(i)
        # time.sleep(2)

    element = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "body")))
    element.send_keys(Keys.CONTROL + 't')
    windows = browser.window_handles
    browser.switch_to.window(windows[len(windows) - 1])
    browser.get(link)


def log_error(link, hist):
    # print(link)
    links = hist.get_links()
    for src_link in links:
        print(src_link)
        if src_link == link:
            dest_links = links[src_link].copy()
            if hist.add_bad_link(src_link, dest_links):
                print("error logged")
            else:
                print("this error was already logged")
    # print(str(hist.get_bad_links()))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("arguments found")
        if len(sys.argv) > 1:
            pass
    else:
        print("no arguments")
        history_set = load_history_set()
        # print(str(history_set))
        print("starting browser...")
        browser = olx_find_all_brands_and_models.start_browser(headless=False)
        try:
            last_link = None
            last_hist = None
            while True:
                history_set = load_history_set()
                link_dict = {}
                hist_dict = {}
                dest_links = []
                cnt = 0
                for hist in history_set:
                    print("brand " + hist.get_brand() + " model " + hist.get_model())
                    print()
                    print("unread links:")
                    unread_links = hist.get_unread_links()
                    for link in unread_links:
                        print("counter " + str(cnt) + " associated to the following link:")
                        print("src")
                        print(link)
                        print("dest")
                        dest_links = unread_links[link]
                        for d in dest_links:
                            print(str(d))

                        link_dict[cnt] = link
                        hist_dict[cnt] = hist
                        cnt += 1
                print()
                num = input("type a number associated to the link you want above, and then press enter\n"
                            + "or type: -1 to report an error in the previously chosen url\n"
                            + "or type 'quit' to quit\n"
                            )
                num = num.lower().strip()
                if num == "quit":
                    browser.quit()
                    exit()
                try:
                    num = int(num)
                except ValueError:
                    print("try again, input a number")
                    time.sleep(3)
                    continue
                if num == -1:
                    if last_hist is None or last_link is None:
                        print("you must first pick a link, before saying it's bad or not!")
                        time.sleep(3)
                        continue
                    else:
                        log_error(last_link, last_hist)
                        time.sleep(3)
                        continue
                try:
                    chosen_link = link_dict[num]
                    chosen_hist = hist_dict[num]
                    # print("hist")
                    # print(str(chosen_hist.get_links()))
                except ValueError as e:
                    print("try another number, this one is not a valid pick")
                    continue
                if chosen_hist.read_link(chosen_link):
                    # print(str(chosen_hist.get_links()))
                    last_link = chosen_link
                    last_hist = chosen_hist
                    open_link_browser(chosen_link, browser, dest_links)
                else:
                    print("link already read")
                    time.sleep(3)
                save_history_set(history_set)
        except Exception as e:
            browser.quit()
            raise e

# the purpose is to have a way to show the user the links he already picked and the new ones he still has to
#  pick, and open them in browser

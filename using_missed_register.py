# NOTE : This version of the file is here for historical reasons and is no longer supported
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import datetime
import PySimpleGUI as psg
import yaml
import os

def ask_domain_config():
    domain = None
    domain = psg.popup_get_text("Enter the domain",default_text="https://")
    return domain


def ask_gecko_config():
    gecko_driver = psg.popup_get_file("Enter the path to geckodriver.exe", default_path=r"C:\geckodriver.exe",
                                      file_types=(("All files", "*.*"), ("Executables", "*.exe")))
    print(gecko_driver)
    return gecko_driver


def get_config(settings):
    config_file = "config.yaml"
    if os.path.exists(config_file):
        with open(config_file, 'r') as cf:
            ret = yaml.load(cf, Loader=yaml.FullLoader)
    else:
        ret = {}
        for setting, missing_handler in settings:
            ret[setting] = missing_handler()

        with open(config_file, 'w') as cf:
            yaml.dump(ret, cf)

    return ret


settings = get_config((("domain",ask_domain_config),("gecko",ask_gecko_config)))
print(settings)


now = datetime.datetime.now().date()
days = (now - datetime.date(2019,9,1)).days

driver = webdriver.Firefox(executable_path=settings["gecko"])
driver.get(settings["domain"] + "/MissedRegisters.aspx")
assert "Engage" in driver.title

while True:
    while "Missed Registers" not in driver.title:
        print("Waiting for page to load")
        time.sleep(1)

    try:
        dr = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "ctl00_PageContent_missedRegisterDetailsFilterBar_ctl00_btnFilter")))

    except TimeoutException:
        print("Loading text timeout!")
        exit()
    time.sleep(2) #TODO I need this delay, to ensure the rest of the page loads.. but its ugly

    # type in 00 to make 700
    dr = driver.find_element_by_id("ctl00_PageContent_missedRegisterDetailsFilterBar_dateRange_upDown_txtNumericValue")
    #dr.send_keys("0")
    dr.send_keys(Keys.BACKSPACE)
    dr.send_keys(str(days))
    go = driver.find_element_by_id("ctl00_PageContent_missedRegisterDetailsFilterBar_ctl00_btnFilter")
    go.click()
    time.sleep(1)  #TODO I need this delay to ensure the rest of the page loads.. but its ugly

    soup_level = BeautifulSoup(driver.page_source, "html.parser")
    classes = soup_level.find_all("tr",class_="hand")

    if len(classes) <= 0:
        print("No more classes")
        break

    for c in classes:
        t = settings["domain"] + c.attrs['data-href']
        print(t)
        driver.get(t)
        time.sleep(2)
        links = driver.find_elements_by_link_text("Mark as Present")

        if len(links) > 0:
            for l in links:
                l.click()
            save = driver.find_element_by_name("ctl00$PageContent$btnSaveGrid")
            save.click()
            time.sleep(2)

    driver.get(settings["domain"] + "/MissedRegisters.aspx")

driver.close()
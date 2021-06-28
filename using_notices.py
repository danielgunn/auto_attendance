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
                                      file_types=(("Executables", "*.exe"),("All Files","*.*")))
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

#driver = webdriver.Firefox()
driver = webdriver.Firefox(executable_path=settings["gecko"])

first_time = True

while True:
    driver.get(settings["domain"] + "/default.aspx")
    assert "Engage" in driver.title
    try:
        dr = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.ID, 'ctl00_PageContent_ctl07_pnlNotices')))

    except TimeoutException:
        print("Loading text timeout!")
        exit()

    time.sleep(3) #TODO I need this delay, to ensure the rest of the page loads.. but its ugly

    if not first_time:
        # TODO: we need to delete the notice
        selectBox = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'ctl00_PageContent_ctl07_rptrNotices_ctl00_ctl03')))
        print("selecting notice box")
        selectBox.click()
        time.sleep(1)

        deleteButt = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'ctl00_PageContent_ctl07_btnBatchDelete')))
        print("deleting notice...")
        deleteButt.click()
        time.sleep(1)

        print("confirming delete..")
        driver.switch_to.alert.accept()
        time.sleep(1)

    print("trying notice 0")
    try:
        noticeButt = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'ctl00_PageContent_ctl07_rptrNotices_ctl00_btnSubject')))
    except TimeoutException:
        print("notice 0 not found")
        exit()

    print("clicking notice")
    noticeButt.click()
    time.sleep(2)

    c = driver.find_elements_by_xpath('//a[contains(@href,"ClassAttendance.aspx?")]')
    c_href = c[0].get_attribute('href')
    print("found class link:",c_href)

    driver.get(c_href)
    dr = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, "pupilHoverImage")))
    mark_link = driver.find_elements_by_link_text("Mark as Present")
    for l in mark_link:
        l.click()

    save = driver.find_element_by_name("ctl00$PageContent$btnSaveGrid")
    save.click()
    time.sleep(2)

    first_time = False

driver.close()
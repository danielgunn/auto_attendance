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

#driver = webdriver.Firefox()
driver = webdriver.Firefox(executable_path=settings["gecko"])

num_weeks = 0
while True:
    driver.get(settings["domain"] + "/Timetable.aspx")
    assert "Engage" in driver.title
    try:
        dr = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "weeklyTT")))

    except TimeoutException:
        print("Loading text timeout!")
        exit()
    time.sleep(2) #TODO I need this delay, to ensure the rest of the page loads.. but its ugly

    for w in range(num_weeks):
        print("waiting...")
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "weeklyTT")))
        print("waiting to clicking...",w)
        backButt = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_PageContent_staffTTWidget_weekSelector_btnPrevWeek"]')))
        print("click",w)
        backButt.click()
        print("sleep")
        time.sleep(2)

    classes = driver.find_elements_by_xpath('//a[contains(@href,"ClassAttendance.aspx?")]')

    if len(classes) <= 0:
        print("No more classes")
        break

    class_links = []
    for c in classes:
        t = c.get_attribute('href')
        class_links.append(c.get_attribute('href'))

    for c in class_links:
        print(c)
        driver.get(c)
        dr = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "pupilHoverImage")))
        mark_link = driver.find_elements_by_link_text("Mark as Present")
        for l in mark_link:
            l.click()
        #    save = driver.find_element_by_name("ctl00$PageContent$btnSaveGrid")
        #    save.click()
        time.sleep(2)

    num_weeks += 1
    print("going back",num_weeks,"weeks")

driver.close()
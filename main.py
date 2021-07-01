from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
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

driver = webdriver.Firefox(executable_path=settings["gecko"])

first_time = True

try:
    while True:
        driver.get(settings["domain"] + "/default.aspx")
        assert "Engage" in driver.title
        dr = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.ID, 'ctl00_PageContent_ctl07_pnlNotices')))

        # I am using delays to ensure the rest of the page loads in time.. yes its a bit ugly
        # TODO: use a better system
        sleep(3)

        # We only delete previous notices after going through the loop once
        if not first_time:
            selectBox = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'ctl00_PageContent_ctl07_rptrNotices_ctl00_ctl03')))
            print("selecting notice box")
            selectBox.click()
            sleep(1)

            deleteButt = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'ctl00_PageContent_ctl07_btnBatchDelete')))
            print("deleting notice...")
            deleteButt.click()
            sleep(1)

            print("confirming delete..")
            driver.switch_to.alert.accept()
            sleep(1)

        # click notice 0 and open the corresponding link
        noticeButt = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'ctl00_PageContent_ctl07_rptrNotices_ctl00_btnSubject')))

        print("clicking notice")
        noticeButt.click()
        sleep(2)

        view_reg_link = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#notice-content > a:nth-child(3)")))
        c_href = view_reg_link.get_attribute('href')
        print("found class link:",c_href)

        # wait for students images to load and then mark all students present
        driver.get(c_href)
        sleep(1)

        print("Waiting for class page to load...")
        dr = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "pupilHoverImage")))
        sleep(1)

        print("Pressing Mark as Present...")
        mark_link = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.LINK_TEXT,'Mark as Present')))
        mark_link.click()
        sleep(1)

        print("Pressing Save Button...")
        save = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID,'ctl00_PageContent_btnSaveGrid')))
        save.click()
        sleep(1)

        first_time = False
#except TimeoutException as err:
#    print("Timed out..:", err)
finally:
    driver.close()
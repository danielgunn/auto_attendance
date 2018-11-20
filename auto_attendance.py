import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
driver = webdriver.Firefox()
driver.get("https://sis.rkcshz.cn/MissedRegisters.aspx")
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
    dr.send_keys("00")
    go = driver.find_element_by_id("ctl00_PageContent_missedRegisterDetailsFilterBar_ctl00_btnFilter")
    go.click()
    time.sleep(1)  #TODO I need this delay to ensure the rest of the page loads.. but its ugly

    soup_level = BeautifulSoup(driver.page_source, "html.parser")
    classes = soup_level.find_all("tr",class_="hand")
    if len(classes) == 0:
        print("No more classes")
        break

    for c in classes:
        driver.get("https://sis.rkcshz.cn" + c.attrs['data-href'])
        time.sleep(2)
        links = driver.find_elements_by_link_text("Mark as Present")
        for l in links:
            l.click()
        save = driver.find_element_by_name("ctl00$PageContent$btnSaveGrid")
        save.click()
        time.sleep(2)

    driver.get("https://sis.rkcshz.cn/MissedRegisters.aspx")

driver.close()
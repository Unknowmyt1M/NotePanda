from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
options.add_argument('--headless=new')
options.add_argument('--window-size=1280,1000')

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:3000')
    time.sleep(2)

    # 1. Click Batch 151
    for b in driver.find_elements(By.TAG_NAME, 'button'):
        if '151' in b.text or 'Drona JEE class 11th' in b.text:
            b.click()
            break
    time.sleep(1)

    # 2. Click Physics
    for el in driver.find_elements(By.XPATH, "//*[text()='Physics']"):
        el.click()
        break
    time.sleep(1)

    # 3. Click Work Energy Power
    for el in driver.find_elements(By.XPATH, "//*[text()='Work Energy Power']"):
        el.click()
        break
    time.sleep(1)

    driver.save_screenshot('notepanda_wep_distinct.png')
    print('Saved notepanda_wep_distinct.png successfully!')

    # 4. Search for Work Energy to see badge distinction
    search_input = driver.find_element(By.TAG_NAME, 'input')
    search_input.send_keys('Work Energy Power L - 09')
    time.sleep(1)
    driver.save_screenshot('notepanda_search_distinct.png')
    print('Saved notepanda_search_distinct.png successfully!')

finally:
    driver.quit()

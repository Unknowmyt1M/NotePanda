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
    search_input = driver.find_element(By.TAG_NAME, 'input')
    search_input.send_keys('Work Energy')
    time.sleep(1)
    
    # Click preview button
    preview_btn = driver.find_element(By.XPATH, "//button[contains(., 'Preview')]")
    preview_btn.click()
    time.sleep(2)
    driver.save_screenshot('notepanda_preview_modal.png')
    print('Saved notepanda_preview_modal.png successfully!')
finally:
    driver.quit()

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run():
    options = Options()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        url = "https://studypanda.study/missionjeet/151"
        driver.get(url)

        # 1. Content
        content_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Content')]")))
        content_btn.click()

        # 2. Physics
        physics_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Physics']")))
        physics_el.click()

        # 3. Work Energy Power
        wep_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Work Energy Power']")))
        wep_el.click()

        # 4. Handwritten Notes
        hn_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Handwritten Notes']")))
        hn_el.click()

        # 5. File item
        file_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'WORK POWER AND ENERGY')]")))
        print("Clicking file:", file_el.text)
        file_el.click()
        time.sleep(4)

        print("Window handles count:", len(driver.window_handles))
        print("Current URL:", driver.current_url)

        # Let's inspect the DOM
        with open("pdf_view_rendered.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        driver.save_screenshot("pdf_view.png")

        # Check for iframes or viewer
        for ifr in driver.find_elements(By.TAG_NAME, "iframe"):
            print("IFRAME:", ifr.get_attribute("src"))
        for emb in driver.find_elements(By.TAG_NAME, "embed"):
            print("EMBED:", emb.get_attribute("src"))
        for a in driver.find_elements(By.TAG_NAME, "a"):
            if "pdf" in (a.get_attribute("href") or "").lower():
                print("PDF LINK A:", a.get_attribute("href"), a.text)

    finally:
        driver.quit()

if __name__ == '__main__':
    run()

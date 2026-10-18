import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def verify_all_batches():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1600,1000")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("http://localhost:3000")
        time.sleep(3)
        driver.save_screenshot("screenshot_batch_151.png")
        print("Captured screenshot 151")
        
        # Click on all batches
        batch_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Drona')]")
        print(f"Found {len(batch_buttons)} batch buttons:")
        for b in batch_buttons:
            print(" - Button:", b.text.replace("\n", " "))

        for idx, btn in enumerate(batch_buttons):
            btn_text = btn.text.replace("\n", " ")
            btn.click()
            time.sleep(1.5)
            fname = f"screenshot_batch_tab_{idx+1}.png"
            driver.save_screenshot(fname)
            print(f"Saved {fname} for {btn_text}")

        # Search test
        search_input = driver.find_element(By.XPATH, "//input[@placeholder]")
        search_input.send_keys("Physics")
        time.sleep(1)
        driver.save_screenshot("screenshot_search_physics.png")
        print("Saved screenshot_search_physics.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    verify_all_batches()

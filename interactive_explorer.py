import json
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
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://studypanda.study/missionjeet/151"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(5)
        
        # Find 'Content' button
        buttons = driver.find_elements(By.TAG_NAME, "button")
        content_btn = None
        for b in buttons:
            if "Content" in b.text:
                content_btn = b
                break
        
        if not content_btn:
            print("Content button not found!")
            return
            
        print("Clicking 'Content' button...")
        content_btn.click()
        time.sleep(5)
        
        # Check rendered DOM after clicking Content
        print("\n--- DOM after clicking Content ---")
        with open("after_content_click.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("after_content_click.png")
        
        # Check all visible text/elements
        body = driver.find_element(By.TAG_NAME, "body")
        print("Body text snippet:")
        print(body.text[:1000].encode('ascii', errors='backslashreplace').decode())
        
        # Check buttons now
        new_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nTotal buttons after clicking Content: {len(new_buttons)}")
        for i, b in enumerate(new_buttons):
            print(f"Button {i}: '{b.text}'")

        # Collect performance logs
        logs = driver.get_log('performance')
        network_events = []
        for entry in logs:
            try:
                msg = json.loads(entry['message'])['message']
                if 'Network.' in msg.get('method', ''):
                    network_events.append(msg)
            except Exception:
                pass
                
        with open("network_events_content.json", "w", encoding="utf-8") as f:
            json.dump(network_events, f, indent=2)

    finally:
        driver.quit()

if __name__ == '__main__':
    run()

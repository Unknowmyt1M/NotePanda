import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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

        # 1. Click 'Content'
        print("Clicking 'Content'...")
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "Content" in b.text:
                b.click()
                break
        time.sleep(3)

        # 2. Click 'Physics'
        print("Looking for 'Physics' item...")
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Physics')]")
        print(f"Found {len(elements)} elements with 'Physics'")
        physics_el = None
        for el in elements:
            if el.tag_name in ['div', 'button', 'a', 'p', 'h3', 'h4', 'span']:
                # Find clickable container
                p = el
                while p and p.tag_name not in ['div', 'button', 'a']:
                    p = p.find_element(By.XPATH, "..")
                physics_el = p
                break
        
        if physics_el:
            print(f"Clicking Physics element: {physics_el.tag_name} with text: {physics_el.text[:40]}")
            physics_el.click()
            time.sleep(3)
        else:
            print("Physics element not found!")

        driver.save_screenshot("step2_physics.png")
        print("Current URL:", driver.current_url)

        # Print all visible items
        body = driver.find_element(By.TAG_NAME, "body")
        print("Body text after clicking Physics (first 1000 chars):")
        print(body.text[:1000].encode('ascii', errors='backslashreplace').decode())

        # 3. Click 'Work Energy Power'
        print("Looking for 'Work Energy Power'...")
        wep_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Work Energy Power')]")
        print(f"Found {len(wep_elements)} elements with 'Work Energy Power'")
        wep_el = None
        for el in wep_elements:
            p = el
            while p and p.tag_name not in ['div', 'button', 'a']:
                p = p.find_element(By.XPATH, "..")
            wep_el = p
            break
            
        if wep_el:
            print(f"Clicking Work Energy Power element: {wep_el.tag_name} with text: {wep_el.text[:40]}")
            wep_el.click()
            time.sleep(3)
            
        driver.save_screenshot("step3_wep.png")
        print("Current URL:", driver.current_url)
        body = driver.find_element(By.TAG_NAME, "body")
        print("Body text after clicking WEP (first 1000 chars):")
        print(body.text[:1000].encode('ascii', errors='backslashreplace').decode())

        # 4. Click 'Handwritten Notes'
        print("Looking for 'Handwritten Notes'...")
        hn_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Handwritten Notes')]")
        print(f"Found {len(hn_elements)} elements with 'Handwritten Notes'")
        hn_el = None
        for el in hn_elements:
            p = el
            while p and p.tag_name not in ['div', 'button', 'a']:
                p = p.find_element(By.XPATH, "..")
            hn_el = p
            break
            
        if hn_el:
            print(f"Clicking Handwritten Notes element: {hn_el.tag_name} with text: {hn_el.text[:40]}")
            hn_el.click()
            time.sleep(3)
            
        driver.save_screenshot("step4_notes.png")
        print("Current URL:", driver.current_url)
        body = driver.find_element(By.TAG_NAME, "body")
        print("Body text after clicking Handwritten Notes (first 1000 chars):")
        print(body.text[:1000].encode('ascii', errors='backslashreplace').decode())

        # Check links / buttons on this final view
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Total links on notes view: {len(links)}")
        for l in links:
            print(f"  Link: href={l.get_attribute('href')}, text={l.text}")

        # Check network logs
        logs = driver.get_log('performance')
        network_events = []
        for entry in logs:
            try:
                msg = json.loads(entry['message'])['message']
                if 'Network.' in msg.get('method', ''):
                    network_events.append(msg)
            except Exception:
                pass
        with open("network_events_full_flow.json", "w", encoding="utf-8") as f:
            json.dump(network_events, f, indent=2)

    finally:
        driver.quit()

if __name__ == '__main__':
    run()

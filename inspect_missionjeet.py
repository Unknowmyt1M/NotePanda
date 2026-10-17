import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def inspect_missionjeet():
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
        url = "https://studypanda.study/missionjeet"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(5)

        with open("missionjeet_rendered.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = soup.find_all('a', href=True)
        print(f"Total links found on /missionjeet: {len(links)}")
        mj_links = [l for l in links if '/missionjeet/' in l['href']]
        print(f"MissionJeet batch links count: {len(mj_links)}")
        for l in mj_links[:15]:
            title = l.get_text(strip=True)
            print(f"  {l['href']} -> {title[:60]}")

        # Check performance logs for network calls
        logs = driver.get_log('performance')
        network_events = []
        for entry in logs:
            try:
                msg = json.loads(entry['message'])['message']
                if 'Network.' in msg.get('method', ''):
                    network_events.append(msg)
            except Exception:
                pass

        with open("network_events_missionjeet.json", "w", encoding="utf-8") as f:
            json.dump(network_events, f, indent=2)

    finally:
        driver.quit()

if __name__ == '__main__':
    inspect_missionjeet()

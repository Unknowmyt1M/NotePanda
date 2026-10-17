import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def run():
    options = Options()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    
    # Enable performance logging to capture all network events
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    print("Launching Chrome...")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://studypanda.study/missionjeet/151"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(6) # wait for page to render and make dynamic calls

        print("Page Title:", driver.title)
        with open("page_151_rendered.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Wrote page_151_rendered.html")

        driver.save_screenshot("page_151.png")
        print("Saved page_151.png")

        # Extract network logs
        logs = driver.get_log('performance')
        print(f"Total performance logs: {len(logs)}")
        
        network_events = []
        for entry in logs:
            try:
                msg = json.loads(entry['message'])['message']
                method = msg.get('method', '')
                if 'Network.' in method:
                    network_events.append(msg)
            except Exception:
                pass
        
        print(f"Total Network events: {len(network_events)}")
        
        # Save all network events
        with open("network_events.json", "w", encoding="utf-8") as f:
            json.dump(network_events, f, indent=2)
        print("Saved network_events.json")

        # Extract requested URLs
        requested_urls = []
        for ev in network_events:
            if ev.get('method') == 'Network.requestWillBeSent':
                req = ev.get('params', {}).get('request', {})
                url = req.get('url', '')
                method = req.get('method', '')
                req_type = ev.get('params', {}).get('type', '')
                requested_urls.append({'method': method, 'url': url, 'type': req_type})

        print("\n--- XHR / Fetch / API Requests ---")
        for r in requested_urls:
            if r['type'] in ['XHR', 'Fetch'] or '/api' in r['url'] or 'json' in r['url'] or 'cloudfront' in r['url']:
                print(f"[{r['type']}] {r['method']} {r['url']}")

    finally:
        driver.quit()

if __name__ == '__main__':
    run()

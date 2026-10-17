from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

print("Initializing Chrome WebDriver...")
try:
    driver = webdriver.Chrome(options=options)
    print("Driver started successfully!")
    print("Navigating to https://studypanda.study/missionjeet/151 ...")
    driver.get("https://studypanda.study/missionjeet/151")
    time.sleep(5)
    print("Title:", driver.title)
    print("Current URL:", driver.current_url)
    
    # Check page text
    body = driver.find_element("tag name", "body")
    print("Body text snippet (first 500 chars):")
    print(body.text[:500])
    
    # Save screenshot
    driver.save_screenshot("page_151_rendered.png")
    print("Saved page_151_rendered.png")
    
    # Save page source
    with open("page_151_rendered.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved page_151_rendered.html")
    
    driver.quit()
except Exception as e:
    print("Error:", e)

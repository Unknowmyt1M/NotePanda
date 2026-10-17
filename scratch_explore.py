import httpx
from bs4 import BeautifulSoup
import re
import json

def inspect_page_html():
    url = 'https://studypanda.study/missionjeet/151'
    r = httpx.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    
    # Save the html to a file for analysis
    with open('page_151.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print("Saved page_151.html")

    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Inspect all script tags
    for i, s in enumerate(soup.find_all('script')):
        src = s.get('src')
        if src:
            print(f"Script {i}: src={src}")
        else:
            txt = s.string or ""
            print(f"Script {i}: inline length={len(txt)}")
            if len(txt) > 0:
                print(f"   preview: {txt[:200]}")

if __name__ == '__main__':
    inspect_page_html()

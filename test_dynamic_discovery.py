import httpx
from bs4 import BeautifulSoup
import re
import json

def discover_server_actions(course_url: str):
    client = httpx.Client(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    print(f"1. Fetching page HTML: {course_url}")
    r = client.get(course_url)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch course page HTML: {r.status_code}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    page_chunk_src = None
    for script in soup.find_all('script', src=True):
        src = script['src']
        if 'page-' in src and ('courseId' in src or 'missionjeet' in src or 'nexttoppers' in src):
            page_chunk_src = src
            break
            
    if not page_chunk_src:
        raise RuntimeError("Could not find course page JS chunk in HTML scripts")
        
    chunk_url = f"https://studypanda.study{page_chunk_src}"
    print(f"2. Found JS chunk URL: {chunk_url}")
    
    cr = client.get(chunk_url)
    if cr.status_code != 200:
        raise RuntimeError(f"Failed to fetch JS chunk: {cr.status_code}")
        
    # Extract actions using regex
    # Pattern: createServerReference)("hash",...,"functionName")
    actions = {}
    matches = re.finditer(r'createServerReference\)\("([0-9a-f]+)",[^,]+,[^,]+,[^,]+,"([^"]+)"\)', cr.text)
    for m in matches:
        actions[m.group(2)] = m.group(1)
        
    print(f"3. Discovered {len(actions)} server actions: {actions}")
    return actions

if __name__ == '__main__':
    actions = discover_server_actions('https://studypanda.study/missionjeet/151')
    assert 'fetchAllContent' in actions
    print("SUCCESS! Discovered fetchAllContent action hash:", actions['fetchAllContent'])

import httpx
import json
import time

ACTION_ID = "701556fce4b1c5cb1fc02f580e17b4d5bdbcd23b06"

def call_fetch_all_content(course_id: str, parent_id: str = "0"):
    url = f"https://studypanda.study/missionjeet/{course_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Next-Action': ACTION_ID,
        'Content-Type': 'text/plain;charset=UTF-8',
        'Accept': 'text/x-component'
    }
    data = json.dumps(["mj", course_id, str(parent_id)])
    
    r = httpx.post(url, headers=headers, content=data, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    
    for line in r.text.splitlines():
        if line.startswith("1:"):
            return json.loads(line[2:])
    return None

def test_exploration():
    print("=== Exploring Course 151: Drona JEE Class 11th ===")
    root = call_fetch_all_content("151", "0")
    subjects = root.get('data', [])
    print(f"Total root subjects/categories: {len(subjects)}")

    # Test Mathematics (ID: 6591)
    print("\n--- Investigating Mathematics (ID: 6591) ---")
    time.sleep(1)
    math_res = call_fetch_all_content("151", "6591")
    math_chapters = math_res.get('data', [])
    print(f"Total chapters in Mathematics: {len(math_chapters)}")
    for ch in math_chapters:
        print(f"  [Folder {ch.get('entity_id')}] {ch.get('title')}")
    
    # Pick first chapter of math (e.g. Set Theory or Quadratic or whatever is first)
    if math_chapters:
        first_ch = math_chapters[0]
        ch_id = first_ch.get('entity_id')
        ch_title = first_ch.get('title')
        print(f"\n  Inspecting Math Chapter: {ch_title} (ID: {ch_id})")
        time.sleep(1)
        ch_content = call_fetch_all_content("151", ch_id)
        for item in ch_content.get('data', []):
            itype = item.get('type')
            title = item.get('title')
            eid = item.get('entity_id')
            furl = item.get('data', {}).get('file_url')
            print(f"    - [{itype}] {title} (ID: {eid}) | file_url: {furl}")
            if itype == 'folder':
                # Check inside folder
                time.sleep(1)
                sub_res = call_fetch_all_content("151", eid)
                for sitem in sub_res.get('data', []):
                    stitle = sitem.get('title')
                    sfurl = sitem.get('data', {}).get('file_url')
                    print(f"        * [{sitem.get('type')}] {stitle} -> {sfurl}")

    # Test Chemistry (ID: 6605)
    print("\n--- Investigating Chemistry (ID: 6605) ---")
    time.sleep(1)
    chem_res = call_fetch_all_content("151", "6605")
    chem_chapters = chem_res.get('data', [])
    print(f"Total chapters in Chemistry: {len(chem_chapters)}")
    for ch in chem_chapters[:5]:
        print(f"  [Folder {ch.get('entity_id')}] {ch.get('title')}")

    # Test Formula Sheets (ID: 7032)
    print("\n--- Investigating Formula Sheets (ID: 7032) ---")
    time.sleep(1)
    formula_res = call_fetch_all_content("151", "7032")
    for item in formula_res.get('data', []):
        title = item.get('title')
        eid = item.get('entity_id')
        itype = item.get('type')
        furl = item.get('data', {}).get('file_url')
        print(f"  [{itype}] {title} (ID: {eid}) -> {furl}")

if __name__ == '__main__':
    test_exploration()

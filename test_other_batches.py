import httpx
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Next-Action': '701556fce4b1c5cb1fc02f580e17b4d5bdbcd23b06',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': 'text/x-component'
}

client = httpx.Client(timeout=15)

for course_id in ['185', '184', '152']:
    url = f'https://studypanda.study/missionjeet/{course_id}'
    data = json.dumps(["mj", course_id, "0"])
    try:
        r = client.post(url, headers=headers, content=data)
        print(f"\nCourse {course_id} -> Status: {r.status_code}")
        for line in r.text.splitlines():
            if line.startswith('1:'):
                resp = json.loads(line[2:])
                items = resp.get('data', [])
                print(f"  Success: {resp.get('success')}, Root items count: {len(items)}")
                for item in items[:5]:
                    print(f"    ID: {item.get('entity_id')} | Title: {item.get('title')}")
    except Exception as e:
        print(f"Course {course_id} Error:", e)

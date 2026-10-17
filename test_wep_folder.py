import httpx
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Next-Action': '701556fce4b1c5cb1fc02f580e17b4d5bdbcd23b06',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': 'text/x-component'
}
data = '["mj","151","20571"]'

r = httpx.post('https://studypanda.study/missionjeet/151', headers=headers, content=data, timeout=15)
print("Status:", r.status_code)
with open('wep_response.txt', 'w', encoding='utf-8') as f:
    f.write(r.text)

for line in r.text.splitlines():
    if line.startswith('1:'):
        resp_json = json.loads(line[2:])
        print(f"Success: {resp_json.get('success')}, count: {len(resp_json.get('data', []))}")
        for item in resp_json.get('data', []):
            print(f"ID: {item.get('entity_id')} | Title: {item.get('title')} | Type: {item.get('type')}")

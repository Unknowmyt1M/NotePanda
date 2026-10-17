import httpx

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Next-Action': '701556fce4b1c5cb1fc02f580e17b4d5bdbcd23b06',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': 'text/x-component'
}
data = '["mj","151","0"]'

r = httpx.post('https://studypanda.study/missionjeet/151', headers=headers, content=data, timeout=15)
with open('subjects_response.txt', 'w', encoding='utf-8') as f:
    f.write(r.text)
print("Saved subjects_response.txt, length:", len(r.text))

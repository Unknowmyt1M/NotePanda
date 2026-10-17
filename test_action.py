import httpx

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Next-Action': '60588aa9db4640bbad0c03145c9656b403d8d6afdf',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': 'text/x-component'
}
data = '["mj","151"]'

r = httpx.post('https://studypanda.study/missionjeet/151', headers=headers, content=data, timeout=15)
with open('server_action_response.txt', 'w', encoding='utf-8') as f:
    f.write(r.text)
print("Saved server_action_response.txt, length:", len(r.text))

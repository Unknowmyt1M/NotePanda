import httpx

r = httpx.get('http://localhost:3000', timeout=5)
print('Server status:', r.status_code)
print('NotePanda in HTML:', 'NotePanda' in r.text)

r_api = httpx.get('http://localhost:3000/api/notepanda?q=Work', timeout=5)
print('API search status:', r_api.status_code)
data = r_api.json()
print('Hits count for Work:', data.get('count'))
if data.get('results'):
    print('First hit title:', data['results'][0]['title'])
    print('First hit URL:', data['results'][0]['file_url'])

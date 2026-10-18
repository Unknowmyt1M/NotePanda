import json

with open('wep_response.txt', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if line.startswith('1:'):
        data = json.loads(line[2:])
        for item in data.get('data', []):
            if item.get('type') == 'file':
                d = item.get('data', {})
                title = item.get('title')
                file_type = d.get('file_type')
                content_type = d.get('content_type')
                url = d.get('file_url') or ''
                print(f"Title: {title:<25} | file_type={file_type} | content_type={content_type} | url_ext={url[-5:]}")

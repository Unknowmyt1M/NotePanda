import json

with open('subjects_response.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('1:'):
            data = json.loads(line[2:])
            print(f"Success: {data.get('success')}, ResponseCode: {data.get('responseCode')}")
            for item in data.get('data', []):
                counts = item.get('data', {}).get('content_counts', {})
                print(f"ID: {item.get('entity_id'):<6} | Title: {item.get('title'):<25} | Counts: {counts}")

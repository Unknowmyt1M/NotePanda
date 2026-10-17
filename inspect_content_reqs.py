import json

with open('network_events_content.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

for ev in events:
    if ev.get('method') == 'Network.requestWillBeSent':
        params = ev.get('params', {})
        req = params.get('request', {})
        url = req.get('url', '')
        # Ignore analytics/static fonts
        if not any(x in url for x in ['google-analytics', 'clarity.ms', 'doubleclick', 'static/media']):
            rtype = params.get('type', '')
            method = req.get('method', '')
            print(f"[{rtype}] {method} {url}")
            if req.get('postData'):
                print(f"   POST: {req['postData'][:300]}")
            if 'Next-Action' in req.get('headers', {}):
                print(f"   Next-Action: {req['headers']['Next-Action']}")

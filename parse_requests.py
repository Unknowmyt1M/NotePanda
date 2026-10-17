import json

with open("network_events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

# Group by requestId
requests = {}
for ev in events:
    method = ev.get('method', '')
    params = ev.get('params', {})
    req_id = params.get('requestId')
    if not req_id:
        continue
    
    if req_id not in requests:
        requests[req_id] = {'events': []}
    requests[req_id]['events'].append((method, params))

print(f"Total unique requests: {len(requests)}")

for req_id, data in requests.items():
    ev_list = data['events']
    req_event = next((p for m, p in ev_list if m == 'Network.requestWillBeSent'), None)
    resp_event = next((p for m, p in ev_list if m == 'Network.responseReceived'), None)
    
    if req_event:
        req = req_event.get('request', {})
        url = req.get('url', '')
        method = req.get('method', '')
        post_data = req.get('postData', '')
        headers = req.get('headers', {})
        status = resp_event.get('response', {}).get('status', 'N/A') if resp_event else 'N/A'
        
        # Filter interesting requests
        if any(k in url for k in ['studypanda', 'firestore', 'api', 'cloudfront']):
            print("="*80)
            print(f"ID: {req_id} | {method} {url} -> Status: {status}")
            if post_data:
                print(f"  POST DATA: {post_data[:300]}")
            if 'Next-Action' in headers or 'next-action' in headers:
                print(f"  NEXT-ACTION HEADER: {headers.get('Next-Action') or headers.get('next-action')}")

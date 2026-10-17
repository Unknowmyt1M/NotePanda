import httpx

pdf_url = "https://dulae92u7241v.cloudfront.net/1772100600/admin_v2/content/pdf//4187742_162_WORK%20POWER%20AND%20ENERGY%20handwritten%20nots%20.pdf"

client = httpx.Client(follow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
try:
    head_resp = client.head(pdf_url, timeout=10)
    print("HEAD Status:", head_resp.status_code)
    print("HEAD Headers:")
    for k, v in head_resp.headers.items():
        print(f"  {k}: {v}")
except Exception as e:
    print("HEAD error:", e)

# Test GET range for first 1024 bytes (to check magic bytes without downloading entire file)
try:
    range_resp = client.get(pdf_url, headers={'Range': 'bytes=0-1023'}, timeout=10)
    print("\nGET Range Status:", range_resp.status_code)
    print("GET Range Headers:")
    for k, v in range_resp.headers.items():
        print(f"  {k}: {v}")
    print("First 10 bytes:", range_resp.content[:10])
    print("Is PDF magic (%PDF):", range_resp.content.startswith(b'%PDF'))
except Exception as e:
    print("GET error:", e)

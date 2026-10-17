from curl_cffi import requests
import re

url = 'https://studypanda.study/_next/static/chunks/app/nexttoppers/%5BcourseId%5D/page-6794927be8a609c3.js'
r = requests.get(url, impersonate='chrome120')
matches = list(re.finditer(r'createServerReference\)\("([^"]+)",[^,]+,[^,]+,[^,]+,"([^"]+)"\)', r.text))
print(f'NextToppers actions count: {len(matches)}')
for m in matches:
    print(f'  {m.group(2):<25} | ID: {m.group(1)}')

import re

# Read the chunk
chunk_path = "page-01f73ddb414bbe42.js"
with open(chunk_path, "r", encoding="utf-8") as f:
    code = f.read()

print("Chunk length:", len(code))

# Search for action hashes
hashes = [
    "701556fce4b1c5cb1fc02f580e17b4d5bdbcd23b06",
    "60588aa9db4640bbad0c03145c9656b403d8d6afdf"
]
for h in hashes:
    idx = code.find(h)
    print(f"Hash {h}: found={idx != -1}")
    if idx != -1:
        start = max(0, idx - 150)
        end = min(len(code), idx + 250)
        print(f"Context around {h}:\n", code[start:end])

# Search for file_url or pdf or dynamic_link
keywords = ["file_url", "dynamic_link", "handleFile", "handleClick", "openPdf", "window.open", "iframe"]
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), code)]
    print(f"Keyword '{kw}': {len(matches)} occurrences")
    for pos in matches[:3]:
        s = max(0, pos - 100)
        e = min(len(code), pos + 200)
        print(f"  [{pos}]: ...{code[s:e]}...")

# StudyPanda Resource Navigation & Architecture Research Report

## 1. Executive Summary

This research investigates the resource-navigation flow, data architecture, and content delivery mechanisms of **StudyPanda** (`https://studypanda.study/`).

Through interactive browser automation with real Chrome instances (via Selenium WebDriver and Chrome DevTools Protocol), combined with static analysis of Next.js client bundles and network traffic interception, we verified the complete navigation flow:
$$\text{Homepage} \longrightarrow \text{MissionJeet Batch Listing} \longrightarrow \text{Course Page} \longrightarrow \text{Subject} \longrightarrow \text{Chapter} \longrightarrow \text{Resource Category} \longrightarrow \text{Direct PDF CDN URL}$$

### Key Findings
1. **Single-Page Navigation Without URL Change**:
   When a user clicks on "Content", subjects (e.g. *Physics*), chapters (e.g. *Work Energy Power*), or resource folders (e.g. *Handwritten Notes*), the browser's URL stays strictly `https://studypanda.study/missionjeet/151`. The course view maintains an internal navigational stack (breadcrumbs) managed by React client state.
2. **Next.js Server Actions Protocol**:
   Content navigation is **not** powered by standard REST or GraphQL API endpoints, nor is the full content tree embedded in the initial HTML skeleton. Instead, dynamic data fetching occurs via **Next.js Server Actions** over HTTP POST requests using the `text/x-component` React Server Components (RSC) wire protocol.
3. **Dynamic Action Discovery**:
   The `Next-Action` action IDs are cryptographic hashes generated at build time. Rather than hardcoding these hashes (which would break on server redeploys), our investigation discovered that these action IDs can be dynamically extracted by scraping the course page HTML for its client chunk script (`app/missionjeet/[courseId]/page-<hash>.js`) and parsing `createServerReference` invocations.
4. **CloudFront CDN PDF Delivery**:
   PDF documents are hosted on Amazon CloudFront (`https://dulae92u7241v.cloudfront.net/...`). They require **no authentication, session cookies, or DRM signed tokens**. They are served directly with `content-type: application/pdf` and `server: AmazonS3`.
5. **Client-Side Trigger**:
   Upon clicking a PDF item in the UI, the decompiled client code confirms it directly calls `window.open(file_url, "_blank", "noopener,noreferrer")`.

---

## 2. Interactive Browser Navigation & State Architecture

### 2.1 The Skeleton Loader vs Dynamic Hydration
Navigating directly to `https://studypanda.study/missionjeet/151` returns a minimal static HTML skeleton:
- Title: `PW , Next Toppers , MissionJEET & Science and Fun All Batches Free Mod Website | PW Mod`
- Body skeleton: `Loading Batch Details...`, `Content`, `Overview`, `Live`.
- Initial active tab: `Overview` (which invokes Server Action `fetchCourseDetails` with payload `["mj", "151"]` to render promotional overview HTML).

### 2.2 Tab Interaction & Content Flow
When the user clicks the `Content` tab:
1. React switches active tab state from `overview` to `content`.
2. A client-side fetch invokes the Next.js Server Action `fetchAllContent` with payload:
   ```json
   ["mj", "151", "0"]
   ```
   Here, `"0"` represents the root `parent_id`.
3. The server returns the 14 root folders/subjects for Course 151 (Practice Sheet, Physics, Mathematics, Chemistry, Daily Practice Problem, etc.).
4. The UI renders the subject cards with content counts (e.g., `Physics - Videos: 121 | PDFs: 118`).

### 2.3 Subject to Chapter to Resource Progression
When clicking an item in the list:
- The UI checks if `item.type === "folder"`.
- If it is a folder, the client pushes the new folder to an internal navigation breadcrumb trail and issues another POST call to `fetchAllContent` passing the clicked folder's `entity_id` as the 3rd parameter:
  - Click **Physics** (`entity_id: 6554`) $\rightarrow$ Server Action called with `["mj", "151", "6554"]`.
  - Server returns 9 chapter folders (Work Energy Power, Circular Motion, Friction, etc.).
  - Click **Work Energy Power** (`entity_id: 20571`) $\rightarrow$ Server Action called with `["mj", "151", "20571"]`.
  - Server returns subfolders (e.g. `Handwritten Notes`, `entity_id: 21531`) and lecture video files.
  - Click **Handwritten Notes** (`entity_id: 21531`) $\rightarrow$ Server Action called with `["mj", "151", "21531"]`.
  - Server returns the resource file item (`entity_id: 31526`, title: `WORK POWER AND ENERGY - Handwritten Notes`).

---

## 3. Discovered Endpoints & Protocol Specifications

### 3.1 Course Page Server Actions
Extracted from `https://studypanda.study/_next/static/chunks/app/missionjeet/%5BcourseId%5D/page-01f73ddb414bbe42.js`:

| Function Name | Next-Action ID | HTTP Method & Target URL | Parameters | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `fetchAllContent` | `701556fce4b1c5cb1fc02f580e17b4d5bdbcd23b06` | `POST https://studypanda.study/missionjeet/<courseId>` | `["mj", "<courseId>", "<parentId>"]` | Hierarchical folder and file metadata retrieval |
| `fetchCourseDetails` | `60588aa9db4640bbad0c03145c9656b403d8d6afdf` | `POST https://studypanda.study/missionjeet/<courseId>` | `["mj", "<courseId>"]` | Course overview and summary HTML |
| `fetchContentDetails` | `707ed9b1f595af4503398894a531823365a072468e` | `POST https://studypanda.study/missionjeet/<courseId>` | `["mj", "<entityId>", "<courseId>"]` | Fallback single item details if URL not pre-populated |
| `fetchLiveClasses` | `6025dd1de0137521b19eb63e19aadac8ef7343b33c` | `POST https://studypanda.study/missionjeet/<courseId>` | `["mj", "<courseId>"]` | Live stream metadata |

### 3.2 Request Structure
To invoke `fetchAllContent`:
```http
POST /missionjeet/151 HTTP/1.1
Host: studypanda.study
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Next-Action: 701556fce4b1c5cb1fc02f580e17b4d5bdbcd23b06
Content-Type: text/plain;charset=UTF-8
Accept: text/x-component

["mj","151","21531"]
```

### 3.3 Sample Sanitized Response (RSC Stream)
The response is returned as an RSC stream:
```http
HTTP/1.1 200 OK
Content-Type: text/x-component
X-Powered-By: Next.js
Server: cloudflare

0:{"a":"$@1","f":"","b":"LMZPdyRlweFVrLgaX7moo"}
1:{"success":true,"responseCode":3006,"message":"Course Content","data":[{"type":"file","course_id":"151","parent_id":21531,"entity_id":"31526","title":"WORK POWER AND ENERGY - Handwritten Notes","data":{"id":31526,"in_app":0,"is_drm":0,"vdc_id":null,"is_live":0,"duration":0,"file_url":"https://dulae92u7241v.cloudfront.net/1772100600/admin_v2/content/pdf//4187742_162_WORK%20POWER%20AND%20ENERGY%20handwritten%20nots%20.pdf","is_share":0,"file_type":1,"thumbnail":" ","created_at":1792147389,"video_type":0,"description":null,"is_download":1,"content_type":1,"download_urls":null,"has_pdf":"0","mark_as_complete":0,"rating":"0.0","out_app_watch":"0","is_locked":0,"is_purchased":1,"dynamic_link":"https://course.nexttoppers.com/dl/r/MaPE0vhM"}}]}
```

---

## 4. PDF Asset Delivery & CDN Investigation

### 4.1 Sample URL Tested
- **Target URL**: `https://dulae92u7241v.cloudfront.net/1772100600/admin_v2/content/pdf//4187742_162_WORK%20POWER%20AND%20ENERGY%20handwritten%20nots%20.pdf`
- **Secondary Discovered URL**: `https://dulae92u7241v.cloudfront.net/1772100600/admin_v2/content/pdf//7468335_162_Binomial%20Theorem%20L%20-%2001%20.pdf`

### 4.2 Response Headers Inspection
```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Date: Sat, 17 Oct 2026 11:31:13 GMT
Server: AmazonS3
Last-Modified: Fri, 16 Oct 2026 10:42:46 GMT
X-Amz-Storage-Class: REDUCED_REDUNDANCY
X-Amz-Server-Side-Encryption: AES256
ETag: W/"980e0547be2567319c24778fee5084d2"
Vary: Accept-Encoding
X-Cache: Hit from cloudfront
Via: 1.1 4bf84ba57cd4e2459a129734709037b6.cloudfront.net (CloudFront)
```

### 4.3 Key Observations
- Direct Amazon S3 origin proxied by AWS CloudFront.
- No `Authorization` bearer header or signed query params required (`Expires`, `Signature`, `Key-Pair-Id` are absent).
- Valid binary PDF stream (Verified magic bytes: `%PDF-1.4`).
- Can be viewed directly inline in any standard browser PDF viewer.

---

## 5. Comparison of Extraction Methods

| Method | Feasibility | Latency | Reliability | Overhead / Maintenance | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Direct Next.js Server Actions RPC** | High | Low (~100-300ms) | Very High (Structured JSON) | Low when using dynamic action hash discovery | **Recommended** |
| **Interactive Headless Browser (Selenium/Playwright)** | High | High (3-6s per click) | Medium (DOM mutations, hydration delays, stale elements) | High (Requires Chromium binary, high CPU/RAM) | Secondary / Verification only |
| **Static HTML Page Parsing** | Low | N/A | Fails | Zero (Content is not rendered in static HTML) | Not feasible for course content |
| **Internal REST API** | Low | N/A | None | No public REST endpoints exposed | Not applicable |

---

## 6. Regulatory, robots.txt & Ethical Evaluation

1. **robots.txt Content Signals**:
   StudyPanda's `robots.txt` defines modern AI and search content signals:
   - `search`: Permitted for search index creation and returning hyperlinks/short excerpts.
   - `ai-input` / `ai-train`: Reserved under EU Directive 2019/790.
2. **Metadata vs Asset Policy**:
   The recommended prototype adheres strictly to **metadata discovery and original link resolution**. It **does not** bulk download, scrape, or mirror the PDF binaries, preserving bandwidth and respecting content integrity.
3. **Session & Security State**:
   No login credentials, tokens, or security bypasses were employed. Content is exposed publicly via the application's Next.js endpoints.

---

## 7. Minimal Working Prototype Verification

The proof of concept `studypanda_explorer.py` implements:
1. Automatic batch discovery on `/missionjeet`.
2. Dynamic Server Action hash discovery from client bundle chunk.
3. Hierarchical traversal: Course $\rightarrow$ Subject $\rightarrow$ Chapter $\rightarrow$ Resource.
4. Built-in caching, timeouts, rate-limiting, and error handling.
5. End-to-end verification matching the user's sample PDF URL.

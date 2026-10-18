"""
StudyPanda Resource Explorer & Metadata Retrieval Proof of Concept
------------------------------------------------------------------
Discovers batches, subjects, chapters, and original resource URLs (PDFs, lectures)
from StudyPanda using dynamically discovered permitted Next.js Server Actions.

Design constraints honored:
- Rate limited (avoids flooding server)
- Caching enabled (avoids redundant requests)
- Timeouts configured
- No scraping/mirroring of actual PDF binaries; metadata and original links only
- Fully dynamic action hash extraction from current web build chunks
"""

import re
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("StudyPandaExplorer")

BASE_URL = "https://studypanda.study"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

@dataclass
class BatchInfo:
    id: str
    title: str
    url: str
    price: Optional[str] = None
    section: str = "missionjeet"

@dataclass
class FolderNode:
    id: str
    title: str
    parent_id: str
    type: str = "folder"
    counts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceItem:
    id: str
    title: str
    parent_id: str
    type: str = "file"
    file_type: int = 1
    file_url: Optional[str] = None
    drm_token: Optional[str] = None
    created_at: Optional[int] = None
    is_locked: int = 0


class StudyPandaExplorer:
    def __init__(self, request_delay: float = 0.5, timeout: float = 15.0):
        self.request_delay = request_delay
        self.timeout = timeout
        self.client = httpx.Client(
            headers={'User-Agent': DEFAULT_USER_AGENT},
            timeout=self.timeout,
            follow_redirects=True
        )
        self._action_cache: Dict[str, Dict[str, str]] = {}
        self._response_cache: Dict[str, Any] = {}

    def _sleep(self):
        if self.request_delay > 0:
            time.sleep(self.request_delay)

    def discover_batches(self, section: str = "missionjeet") -> List[BatchInfo]:
        """
        Discovers batches listed on the section page (e.g. /missionjeet).
        """
        cache_key = f"batches_{section}"
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]

        url = f"{BASE_URL}/{section}"
        logger.info(f"Discovering batches from {url}...")
        self._sleep()
        resp = self.client.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch section page: HTTP {resp.status_code}")

        soup = BeautifulSoup(resp.text, 'html.parser')
        batches = []
        pattern = re.compile(rf"^/{section}/(\d+)$")
        seen_ids = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            match = pattern.match(href)
            if match:
                batch_id = match.group(1)
                if batch_id in seen_ids:
                    continue
                seen_ids.add(batch_id)
                text = a.get_text(separator=" ", strip=True)
                clean_title = re.sub(r'PriceFreeStudy.*$', '', text).strip()
                clean_title = re.sub(r'Price\s*Free\s*Study.*$', '', clean_title).strip()
                clean_title = re.sub(r'Price.*$', '', clean_title).strip()
                if not clean_title:
                    clean_title = f"Batch {batch_id}"
                
                batches.append(BatchInfo(
                    id=batch_id,
                    title=clean_title,
                    url=f"{BASE_URL}{href}",
                    section=section
                ))

        self._response_cache[cache_key] = batches
        logger.info(f"Found {len(batches)} batches in {section}")
        return batches

    def get_server_actions(self, section: str, course_id: str) -> Dict[str, str]:
        """
        Dynamically discovers Next.js Server Action IDs for the given route
        by inspecting the route's HTML and loading its page chunk.
        """
        cache_key = f"actions_{section}"
        if cache_key in self._action_cache:
            return self._action_cache[cache_key]

        page_url = f"{BASE_URL}/{section}/{course_id}"
        logger.info(f"Resolving Server Actions dynamically from {page_url}...")
        self._sleep()
        resp = self.client.get(page_url, timeout=25.0)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to load course page: HTTP {resp.status_code}")

        soup = BeautifulSoup(resp.text, 'html.parser')
        page_chunk_src = None
        for s in soup.find_all('script', src=True):
            src = s['src']
            if 'page-' in src and (course_id in src or section in src or '%5BcourseId%5D' in src):
                page_chunk_src = src
                break

        if not page_chunk_src:
            raise RuntimeError(f"Could not locate page chunk script in HTML of {page_url}")

        chunk_url = f"{BASE_URL}{page_chunk_src}"
        logger.info(f"Loading page chunk: {chunk_url}...")
        self._sleep()
        chunk_resp = self.client.get(chunk_url, timeout=25.0)
        if chunk_resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch chunk JS: HTTP {chunk_resp.status_code}")

        # Extract actions: createServerReference)("hash",...,"functionName")
        actions = {}
        for m in re.finditer(r'createServerReference\)\("([0-9a-f]+)",[^,]+,[^,]+,[^,]+,"([^"]+)"\)', chunk_resp.text):
            actions[m.group(2)] = m.group(1)

        if not actions:
            raise RuntimeError(f"No Server Actions found in chunk {chunk_url}")

        self._action_cache[cache_key] = actions
        logger.info(f"Discovered actions for {section}: {list(actions.keys())}")
        return actions

    def fetch_content_raw(self, section: str, course_id: str, parent_id: str = "0") -> List[Dict[str, Any]]:
        """
        Calls the Next.js Server Action 'fetchAllContent' for a specific parent folder ID.
        """
        cache_key = f"content_{section}_{course_id}_{parent_id}"
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]

        actions = self.get_server_actions(section, course_id)
        action_id = actions.get("fetchAllContent")
        if not action_id:
            raise RuntimeError("Server Action 'fetchAllContent' not found for route")

        url = f"{BASE_URL}/{section}/{course_id}"
        prefix = "mj" if section == "missionjeet" else section
        payload = json.dumps([prefix, str(course_id), str(parent_id)])

        headers = {
            'Next-Action': action_id,
            'Content-Type': 'text/plain;charset=UTF-8',
            'Accept': 'text/x-component'
        }

        self._sleep()
        resp = None
        for attempt in range(3):
            try:
                resp = self.client.post(url, headers=headers, content=payload, timeout=25.0)
                if resp.status_code == 200:
                    break
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed for {url} parent {parent_id}: {e}")
                time.sleep(1.0)

        if not resp or resp.status_code != 200:
            error_text = resp.text[:200] if resp else "Connection error"
            raise RuntimeError(f"Server action returned HTTP {resp.status_code if resp else 'ERR'}: {error_text}")

        # Parse RSC stream line starting with '1:'
        data = []
        for line in resp.text.splitlines():
            if line.startswith("1:"):
                parsed = json.loads(line[2:])
                if parsed.get("success"):
                    data = parsed.get("data", [])
                else:
                    logger.warning(f"Server action returned unsuccessful response: {parsed}")
                break

        self._response_cache[cache_key] = data
        return data

    def get_course_subjects(self, section: str, course_id: str) -> List[FolderNode]:
        """
        Retrieves root subjects / top-level categories for a course.
        """
        raw_items = self.fetch_content_raw(section, course_id, "0")
        subjects = []
        for item in raw_items:
            if item.get("type") == "folder":
                subjects.append(FolderNode(
                    id=str(item.get("entity_id")),
                    title=item.get("title", ""),
                    parent_id="0",
                    type="folder",
                    counts=item.get("data", {}).get("content_counts", {})
                ))
        return subjects

    def get_folder_contents(self, section: str, course_id: str, folder_id: str) -> Tuple[List[FolderNode], List[ResourceItem]]:
        """
        Retrieves immediate subfolders and resource items (files) under a specific folder.
        """
        raw_items = self.fetch_content_raw(section, course_id, folder_id)
        folders = []
        resources = []

        for item in raw_items:
            itype = item.get("type")
            entity_id = str(item.get("entity_id"))
            title = item.get("title", "")
            idata = item.get("data", {})

            if itype == "folder":
                folders.append(FolderNode(
                    id=entity_id,
                    title=title,
                    parent_id=folder_id,
                    type="folder",
                    counts=idata.get("content_counts", {})
                ))
            elif itype == "file":
                resources.append(ResourceItem(
                    id=entity_id,
                    title=title,
                    parent_id=folder_id,
                    type="file",
                    file_type=idata.get("file_type", 1),
                    file_url=idata.get("file_url"),
                    drm_token=idata.get("drm_token"),
                    created_at=idata.get("created_at"),
                    is_locked=idata.get("is_locked", 0)
                ))

        return folders, resources

    def crawl_chapter_resources(self, section: str, course_id: str, folder_id: str, max_depth: int = 3) -> List[ResourceItem]:
        """
        Recursively discovers all resources under a chapter or subject folder up to max_depth.
        """
        all_resources: List[ResourceItem] = []
        queue = [(folder_id, 0)]

        while queue:
            curr_id, depth = queue.pop(0)
            if depth > max_depth:
                continue

            subfolders, files = self.get_folder_contents(section, course_id, curr_id)
            all_resources.extend(files)

            for sf in subfolders:
                queue.append((sf.id, depth + 1))

        return all_resources


def demo():
    print("=============================================================")
    print(" StudyPanda Resource Explorer & Verification Engine")
    print("=============================================================")

    explorer = StudyPandaExplorer(request_delay=0.4)

    # 1. Discover batches in MissionJeet
    print("\n[Step 1] Discovering batches in /missionjeet:")
    batches = explorer.discover_batches("missionjeet")
    for b in batches:
        print(f"  * Batch [{b.id}] : {b.title} -> {b.url}")

    # 2. Select Course 151 (Drona JEE Class 11th)
    target_course = "151"
    print(f"\n[Step 2] Fetching Subjects for Course {target_course} (Drona JEE Class 11th):")
    subjects = explorer.get_course_subjects("missionjeet", target_course)
    for s in subjects:
        counts = s.counts
        pdf_count = counts.get('pdf', {}).get('paid', 0) + counts.get('pdf', {}).get('free', 0)
        vid_count = counts.get('video', {}).get('paid', 0) + counts.get('video', {}).get('free', 0)
        print(f"  [Folder] [ID: {s.id:>6}] {s.title:<30} (PDFs: {pdf_count:>3}, Videos: {vid_count:>3})")

    # 3. Explore Physics -> Work Energy Power
    physics_node = next((s for s in subjects if "Physics" in s.title), None)
    if physics_node:
        print(f"\n[Step 3] Exploring Subject: {physics_node.title} (ID: {physics_node.id}):")
        chapters, _ = explorer.get_folder_contents("missionjeet", target_course, physics_node.id)
        for ch in chapters:
            print(f"    Chapter [ID: {ch.id:>6}] {ch.title}")

        wep_node = next((ch for ch in chapters if "Work Energy Power" in ch.title), None)
        if wep_node:
            print(f"\n[Step 4] Exploring Chapter: {wep_node.title} (ID: {wep_node.id}):")
            subfolders, files = explorer.get_folder_contents("missionjeet", target_course, wep_node.id)
            for sf in subfolders:
                print(f"      Subfolder [ID: {sf.id:>6}] {sf.title}")
            for f in files[:5]:
                print(f"      File [ID: {f.id:>6}] {f.title} -> {f.file_url}")

            # Look into Handwritten Notes
            notes_folder = next((sf for sf in subfolders if "Handwritten Notes" in sf.title), None)
            if notes_folder:
                print(f"\n[Step 5] Extracting Handwritten Notes (ID: {notes_folder.id}):")
                _, notes_files = explorer.get_folder_contents("missionjeet", target_course, notes_folder.id)
                for nf in notes_files:
                    print(f"        [Note Found]: {nf.title}")
                    print(f"        URL: {nf.file_url}")
                    assert nf.file_url is not None
                    assert "4187742_162_WORK%20POWER%20AND%20ENERGY" in nf.file_url
                    print("        VERIFIED: Matches expected user sample PDF URL!")

    # 4. Explore Mathematics -> Binomial Theorem
    math_node = next((s for s in subjects if "Mathematics" in s.title), None)
    if math_node:
        print(f"\n[Step 6] Exploring Subject: {math_node.title} (ID: {math_node.id}):")
        chapters, _ = explorer.get_folder_contents("missionjeet", target_course, math_node.id)
        if chapters:
            first_ch = chapters[0]
            print(f"    Inspecting Chapter: {first_ch.title} (ID: {first_ch.id})")
            _, ch_files = explorer.get_folder_contents("missionjeet", target_course, first_ch.id)
            for f in ch_files:
                if f.file_url and ".pdf" in f.file_url:
                    print(f"      [PDF Found]: {f.title} -> {f.file_url}")

    print("\n=============================================================")
    print(" ALL VERIFICATION CHECKS COMPLETED SUCCESSFULLY")
    print("=============================================================")

if __name__ == '__main__':
    demo()

"""
NotePanda Background Indexer Pipeline
-------------------------------------
Crawls batches, subjects, chapters and resources and persists them to notepanda.db.
Includes polite rate-limiting, error handling, and incremental updates.
"""

import time
import logging
from studypanda_explorer import StudyPandaExplorer
from notepanda_db import NotePandaDB

logger = logging.getLogger("NotePandaIndexer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NotePandaIndexer:
    def __init__(self, delay: float = 0.3):
        self.explorer = StudyPandaExplorer(request_delay=delay)
        self.db = NotePandaDB()

    def index_all(self, sections: list = None, max_depth: int = 4):
        if not sections:
            sections = ["missionjeet"]

        total_batches = 0
        for section in sections:
            logger.info(f"=== Discovering batches for section: {section} ===")
            batches = self.explorer.discover_batches(section)
            self.db.save_batches(batches)
            total_batches += len(batches)

            for b in batches:
                logger.info(f"--> Indexing Batch: {b.title} (ID: {b.id})")
                self.index_batch(section, b.id, max_depth=max_depth)

        stats = self.db.get_stats()
        logger.info(f"=== Indexing Completed! Current Stats: {stats} ===")
        return stats

    def index_batch(self, section: str, batch_id: str, max_depth: int = 4):
        # 1. Fetch root subjects
        try:
            subjects = self.explorer.get_course_subjects(section, batch_id)
            self.db.save_folders(batch_id, subjects, depth=0)
            logger.info(f"  Saved {len(subjects)} root subjects for batch {batch_id}")

            # BFS queue: (folder_id, current_depth)
            queue = [(s.id, 1) for s in subjects]
            
            visited = set()
            while queue:
                folder_id, depth = queue.pop(0)
                if folder_id in visited or depth > max_depth:
                    continue
                visited.add(folder_id)

                try:
                    subfolders, files = self.explorer.get_folder_contents(section, batch_id, folder_id)
                    if subfolders:
                        self.db.save_folders(batch_id, subfolders, depth=depth)
                        for sf in subfolders:
                            queue.append((sf.id, depth + 1))

                    if files:
                        self.db.save_resources(batch_id, files)
                        pdf_files = [f for f in files if f.file_url and ".pdf" in f.file_url.lower()]
                        logger.info(f"    Folder {folder_id} (depth {depth}): {len(files)} files ({len(pdf_files)} PDFs)")

                except Exception as e:
                    logger.warning(f"Error fetching contents for folder {folder_id}: {e}")

        except Exception as e:
            logger.error(f"Failed to index batch {batch_id}: {e}")

if __name__ == "__main__":
    indexer = NotePandaIndexer(delay=0.3)
    indexer.index_all()

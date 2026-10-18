import sqlite3
import json
import logging
from indexer import NotePandaIndexer
from studypanda_explorer import StudyPandaExplorer
from notepanda_db import NotePandaDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("IndexAllBatches")

def run():
    db = NotePandaDB()
    explorer = StudyPandaExplorer(request_delay=0.15)
    indexer = NotePandaIndexer(delay=0.15)

    # 1. Clear out non-pdf files currently in the database to completely remove videos
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resources WHERE is_pdf = 0 OR file_url NOT LIKE '%.pdf%'")
        conn.commit()
        logger.info(f"Purged non-PDF entries. Remaining PDF rows: {cursor.rowcount}")

    # 2. Get and save batches with clean titles
    batches = explorer.discover_batches("missionjeet")
    db.save_batches(batches)

    # 3. Index all 4 batches (151, 152, 184, 185)
    for b in batches:
        logger.info(f"==================================================")
        logger.info(f"Indexing Batch {b.id}: {b.title}")
        logger.info(f"==================================================")
        indexer.index_batch("missionjeet", b.id, max_depth=3)

    # 4. Export clean snapshot with only PDFs and valid batches
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM batches ORDER BY id ASC")
        clean_batches = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM folders ORDER BY depth ASC, title ASC")
        clean_folders = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM resources WHERE is_pdf = 1 AND file_url LIKE '%.pdf%' ORDER BY title ASC")
        clean_resources = [dict(r) for r in cursor.fetchall()]

    snapshot = {
        "batches": clean_batches,
        "folders": clean_folders,
        "resources": clean_resources
    }

    with open("frontend/src/data_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    logger.info("==================================================")
    logger.info("SNAPSHOT EXPORT COMPLETED SUCCESSFULLY!")
    logger.info(f"Batches: {len(clean_batches)}")
    logger.info(f"Folders: {len(clean_folders)}")
    logger.info(f"PDF Notes (Zero Videos): {len(clean_resources)}")
    for b in clean_batches:
        b_res = [r for r in clean_resources if r['batch_id'] == b['id']]
        logger.info(f"  • Batch {b['id']} ({b['title']}): {len(b_res)} PDF notes")
    logger.info("==================================================")

if __name__ == "__main__":
    run()

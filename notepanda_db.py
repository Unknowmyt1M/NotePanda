"""
NotePanda SQLite Database & Indexing Engine
------------------------------------------
Persistently caches batches, subjects, chapters, folders, and resources (PDFs, Notes).
Enables sub-millisecond local search and fast API responses.
"""

import sqlite3
import json
import time
import os
import logging
from typing import List, Dict, Optional, Any, Tuple
from studypanda_explorer import StudyPandaExplorer, BatchInfo, FolderNode, ResourceItem

logger = logging.getLogger("NotePandaDB")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notepanda.db")

class NotePandaDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_schema()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Batches table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                id TEXT PRIMARY KEY,
                section TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                total_pdfs INTEGER DEFAULT 0,
                total_videos INTEGER DEFAULT 0,
                updated_at REAL NOT NULL
            )
            """)

            # Folders / Categories table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS folders (
                id TEXT PRIMARY KEY,
                batch_id TEXT NOT NULL,
                parent_id TEXT NOT NULL,
                title TEXT NOT NULL,
                depth INTEGER DEFAULT 0,
                pdf_count INTEGER DEFAULT 0,
                video_count INTEGER DEFAULT 0,
                updated_at REAL NOT NULL,
                FOREIGN KEY (batch_id) REFERENCES batches(id)
            )
            """)

            # Resources / Files (Notes, PDFs, DPPs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                batch_id TEXT NOT NULL,
                folder_id TEXT NOT NULL,
                title TEXT NOT NULL,
                file_type INTEGER DEFAULT 1,
                file_url TEXT,
                drm_token TEXT,
                is_pdf INTEGER DEFAULT 1,
                created_at INTEGER,
                updated_at REAL NOT NULL,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (folder_id) REFERENCES folders(id)
            )
            """)

            # Indexes for ultra-fast querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_folders_batch ON folders(batch_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders(parent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_folder ON resources(folder_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_batch ON resources(batch_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_title ON resources(title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_is_pdf ON resources(is_pdf)")
            
            conn.commit()
            logger.info("Database schema initialized successfully.")

    def save_batches(self, batches: List[BatchInfo]):
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for b in batches:
                cursor.execute("""
                INSERT INTO batches (id, section, title, url, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    url=excluded.url,
                    updated_at=excluded.updated_at
                """, (b.id, b.section, b.title, b.url, now))
            conn.commit()

    def save_folders(self, batch_id: str, folders: List[FolderNode], depth: int = 0):
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for f in folders:
                pdf_count = f.counts.get('pdf', {}).get('paid', 0) + f.counts.get('pdf', {}).get('free', 0)
                vid_count = f.counts.get('video', {}).get('paid', 0) + f.counts.get('video', {}).get('free', 0)
                cursor.execute("""
                INSERT INTO folders (id, batch_id, parent_id, title, depth, pdf_count, video_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    pdf_count=excluded.pdf_count,
                    video_count=excluded.video_count,
                    updated_at=excluded.updated_at
                """, (f.id, batch_id, f.parent_id, f.title, depth, pdf_count, vid_count, now))
            conn.commit()

    def save_resources(self, batch_id: str, resources: List[ResourceItem]):
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for r in resources:
                # Strictly index only PDF documents (notes, DPPs, formula sheets)
                if not (r.file_url and ".pdf" in r.file_url.lower()):
                    continue
                cursor.execute("""
                INSERT INTO resources (id, batch_id, folder_id, title, file_type, file_url, drm_token, is_pdf, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    file_url=excluded.file_url,
                    is_pdf=excluded.is_pdf,
                    updated_at=excluded.updated_at
                """, (r.id, batch_id, r.parent_id, r.title, r.file_type, r.file_url, r.drm_token, 1, r.created_at, now))
            conn.commit()

    # --- Query Methods ---
    def get_all_batches(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT b.*, 
                   COUNT(DISTINCT r.id) as indexed_resources,
                   COUNT(DISTINCT CASE WHEN r.is_pdf = 1 THEN r.id END) as indexed_pdfs
            FROM batches b
            LEFT JOIN resources r ON b.id = r.batch_id
            GROUP BY b.id
            ORDER BY b.id ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM batches WHERE id = ?", (batch_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_subfolders(self, batch_id: str, parent_id: str = "0") -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM folders 
            WHERE batch_id = ? AND parent_id = ?
            ORDER BY title ASC
            """, (batch_id, parent_id))
            return [dict(row) for row in cursor.fetchall()]

    def get_folder(self, folder_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM folders WHERE id = ?", (folder_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_folder_resources(self, folder_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM resources 
            WHERE folder_id = ?
            ORDER BY created_at DESC, title ASC
            """, (folder_id,))
            return [dict(row) for row in cursor.fetchall()]

    def search_resources(self, query: str, limit: int = 50, pdf_only: bool = True) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            sql = """
            SELECT r.*, f.title as folder_title, b.title as batch_title
            FROM resources r
            JOIN folders f ON r.folder_id = f.id
            JOIN batches b ON r.batch_id = b.id
            WHERE r.title LIKE ?
            """
            params = [f"%{query}%"]
            if pdf_only:
                sql += " AND r.is_pdf = 1"
            sql += " ORDER BY r.title ASC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM batches")
            batches_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM folders")
            folders_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM resources")
            resources_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM resources WHERE is_pdf = 1")
            pdfs_count = cursor.fetchone()[0]

            return {
                "batches": batches_count,
                "folders": folders_count,
                "resources": resources_count,
                "pdf_notes": pdfs_count
            }

if __name__ == "__main__":
    db = NotePandaDB()
    stats = db.get_stats()
    print("Database ready. Current stats:", stats)

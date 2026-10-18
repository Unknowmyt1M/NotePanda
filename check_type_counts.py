import sqlite3

conn = sqlite3.connect('notepanda.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM resources WHERE is_pdf = 1 AND file_url NOT LIKE '%.pdf%'")
print("PDFs without .pdf in URL:", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM resources WHERE file_type = 2")
print("Total video files in DB:", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM resources WHERE file_type = 1")
print("Total doc/pdf files in DB:", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM resources WHERE is_pdf = 1")
print("Total resources marked is_pdf=1:", cursor.fetchone()[0])

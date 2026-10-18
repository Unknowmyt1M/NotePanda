import sqlite3

conn = sqlite3.connect('notepanda.db')
cursor = conn.cursor()
cursor.execute("SELECT title, file_url, is_pdf FROM resources WHERE folder_id = '20571'")
rows = cursor.fetchall()
print(f"Total rows in folder 20571 (Work Energy Power): {len(rows)}")
for title, url, is_pdf in rows[:10]:
    print(f"  Title: {title} | is_pdf={is_pdf} | URL: {url}")

import sqlite3

conn = sqlite3.connect('notepanda.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM resources')
print('Total resources:', cursor.fetchone()[0])
cursor.execute('SELECT COUNT(*) FROM resources WHERE is_pdf = 1')
print('Total PDFs:', cursor.fetchone()[0])
cursor.execute("SELECT title, file_url FROM resources WHERE title LIKE '%Energy%' LIMIT 5")
print("\nEnergy sample resources:")
for r in cursor.fetchall():
    print(" -", r[0], "->", r[1])

cursor.execute("SELECT title, file_url FROM resources WHERE is_pdf = 1 LIMIT 5")
print("\nSample PDF resources:")
for r in cursor.fetchall():
    print(" -", r[0], "->", r[1])

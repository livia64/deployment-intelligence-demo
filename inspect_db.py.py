import sqlite3

conn = sqlite3.connect("deployment.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1")
tables = cursor.fetchall()

print("Tables found:")
for table in tables:
    print("-", table[0])

conn.close()

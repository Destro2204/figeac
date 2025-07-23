import sqlite3

conn = sqlite3.connect('employees.db')
cur = conn.cursor()
cur.execute("INSERT OR REPLACE INTO instrument (id, name, status) VALUES (?, ?, ?)", (1, 'pieds a coulisse', 'available'))
cur.execute("INSERT OR REPLACE INTO instrument (id, name, status) VALUES (?, ?, ?)", (2, 'micrometre', 'taken'))
conn.commit()
conn.close()
print("Instruments added.") 
import os

db_path = os.path.abspath("users.db")
print(f"📂 Database file should be here: {db_path}")

import sqlite3

conn = sqlite3.connect("users.db")  # Make sure this is the correct file!
c = conn.cursor()

# List all tables in the database
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()

print("📋 Tables in database:", tables)

conn.close()

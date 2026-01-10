import sqlite3
import os

db_path = "dev.db"
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("USERS:")
cursor.execute("SELECT id, full_name FROM users;")
for row in cursor.fetchall():
    print(row)

print("\nORDERS:")
cursor.execute("SELECT id, user_id, status FROM orders;")
for row in cursor.fetchall():
    print(row)

print("\nORDER ITEMS:")
cursor.execute("SELECT id, order_id, product_id, product_name FROM order_items;")
for row in cursor.fetchall():
    print(row)

conn.close()

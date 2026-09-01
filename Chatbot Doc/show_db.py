import sqlite3

conn = sqlite3.connect("clinic.db")
cur = conn.cursor()

# List all tables in the database
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# For each table, print column info and all rows
for table in tables:
    print(f"\nTable: {table}")
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    print("Columns:")
    for col in cols:
        # PRAGMA table_info returns (cid, name, type, notnull, dflt_value, pk)
        print(" -", col)
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    print(f"Rows ({len(rows)}):")
    for row in rows:
        print(row)

conn.close()

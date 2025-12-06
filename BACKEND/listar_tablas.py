import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tablas = cursor.fetchall()

print("\nTablas en la base de datos:")
print("="*40)
for tabla in tablas:
    print(f"  - {tabla[0]}")

conn.close()


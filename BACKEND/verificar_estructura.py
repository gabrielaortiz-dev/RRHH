import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

# Ver todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = [row[0] for row in cursor.fetchall()]

print("📋 TABLAS EXISTENTES:")
for tabla in tablas:
    print(f"\n🔹 {tabla}")
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = cursor.fetchall()
    for col in columnas:
        print(f"   - {col[1]} ({col[2]})")

conn.close()


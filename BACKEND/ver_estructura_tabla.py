import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

# Ver todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = cursor.fetchall()

print("Tablas en la base de datos:")
for tabla in tablas:
    print(f"\n{tabla[0]}:")
    cursor.execute(f"PRAGMA table_info({tabla[0]})")
    columnas = cursor.fetchall()
    for col in columnas:
        print(f"  - {col[1]} ({col[2]})")

conn.close()


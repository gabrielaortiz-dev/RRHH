"""
Script para verificar la estructura real de las tablas
"""
import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

print("="*70)
print("VERIFICANDO ESTRUCTURA DE TABLAS")
print("="*70)

# Verificar estructura de empleados
print("\n[TABLA: empleados]")
cursor.execute("PRAGMA table_info(empleados)")
cols = cursor.fetchall()
for col in cols:
    print(f"   {col[1]} ({col[2]})")

cursor.execute("SELECT * FROM empleados LIMIT 3")
empleados = cursor.fetchall()
print(f"\n   Total registros: {len(empleados)}")
if empleados:
    print(f"   Primer registro: {empleados[0]}")

# Verificar estructura de departamentos
print("\n[TABLA: departamentos]")
cursor.execute("PRAGMA table_info(departamentos)")
cols = cursor.fetchall()
for col in cols:
    print(f"   {col[1]} ({col[2]})")

cursor.execute("SELECT * FROM departamentos LIMIT 3")
deptos = cursor.fetchall()
print(f"\n   Total registros: {len(deptos)}")
if deptos:
    print(f"   Primer registro: {deptos[0]}")

# Verificar estructura de Contratos
print("\n[TABLA: Contratos]")
cursor.execute("PRAGMA table_info(Contratos)")
cols = cursor.fetchall()
for col in cols:
    print(f"   {col[1]} ({col[2]})")

cursor.execute("SELECT COUNT(*) FROM Contratos")
total = cursor.fetchone()[0]
print(f"\n   Total registros: {total}")

# Verificar estructura de Evaluaciones
print("\n[TABLA: Evaluaciones]")
cursor.execute("PRAGMA table_info(Evaluaciones)")
cols = cursor.fetchall()
for col in cols:
    print(f"   {col[1]} ({col[2]})")

cursor.execute("SELECT COUNT(*) FROM Evaluaciones")
total = cursor.fetchone()[0]
print(f"\n   Total registros: {total}")

# Verificar estructura de Roles
print("\n[TABLA: Roles]")
cursor.execute("PRAGMA table_info(Roles)")
cols = cursor.fetchall()
for col in cols:
    print(f"   {col[1]} ({col[2]})")

cursor.execute("SELECT COUNT(*) FROM Roles")
total = cursor.fetchone()[0]
print(f"\n   Total registros: {total}")

# Verificar estructura de usuarios
print("\n[TABLA: usuarios]")
cursor.execute("PRAGMA table_info(usuarios)")
cols = cursor.fetchall()
for col in cols:
    print(f"   {col[1]} ({col[2]})")

cursor.execute("SELECT COUNT(*) FROM usuarios")
total = cursor.fetchone()[0]
print(f"\n   Total registros: {total}")

print("\n" + "="*70)

conn.close()


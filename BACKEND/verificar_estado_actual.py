"""
Script para verificar el estado actual de la base de datos
"""
import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

print("="*70)
print("VERIFICANDO ESTADO ACTUAL DE LA BASE DE DATOS")
print("="*70)

# Verificar tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print("\n[TABLAS EXISTENTES]")
for table in tables:
    print(f"   - {table[0]}")

# Verificar empleados
print("\n[EMPLEADOS]")
cursor.execute("SELECT id_empleado, nombre, apellido FROM Empleados ORDER BY id_empleado LIMIT 15")
empleados = cursor.fetchall()
for emp in empleados:
    print(f"   ID: {emp[0]} - {emp[1]} {emp[2]}")

cursor.execute("SELECT COUNT(*) FROM Empleados")
total_emp = cursor.fetchone()[0]
print(f"\n   Total empleados: {total_emp}")

# Verificar departamentos
print("\n[DEPARTAMENTOS]")
cursor.execute("SELECT id_departamento, nombre_departamento FROM Departamentos ORDER BY id_departamento LIMIT 15")
deptos = cursor.fetchall()
for dept in deptos:
    print(f"   ID: {dept[0]} - {dept[1]}")

cursor.execute("SELECT COUNT(*) FROM Departamentos")
total_dept = cursor.fetchone()[0]
print(f"\n   Total departamentos: {total_dept}")

# Verificar contratos
print("\n[CONTRATOS]")
cursor.execute("SELECT COUNT(*) FROM Contratos")
total_contratos = cursor.fetchone()[0]
print(f"   Total contratos: {total_contratos}")

cursor.execute("SELECT id_contrato, id_empleado FROM Contratos ORDER BY id_contrato LIMIT 10")
contratos = cursor.fetchall()
for cont in contratos:
    print(f"   ID: {cont[0]} - Empleado: {cont[1]}")

# Verificar evaluaciones
print("\n[EVALUACIONES]")
cursor.execute("SELECT COUNT(*) FROM Evaluaciones")
total_eval = cursor.fetchone()[0]
print(f"   Total evaluaciones: {total_eval}")

# Verificar usuarios
print("\n[USUARIOS]")
cursor.execute("SELECT COUNT(*) FROM usuarios")
total_users = cursor.fetchone()[0]
print(f"   Total usuarios: {total_users}")

# Verificar roles
print("\n[ROLES]")
try:
    cursor.execute("SELECT COUNT(*) FROM Roles")
    total_roles = cursor.fetchone()[0]
    print(f"   Total roles: {total_roles}")
except:
    print("   Tabla Roles no existe")

print("\n" + "="*70)

conn.close()


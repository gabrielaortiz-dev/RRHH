"""
Instalacion Completa del Sistema - Version Simple (Sin Emojis)
"""
import subprocess
import sys

print("\n" + "="*70)
print("INSTALACION COMPLETA DEL SISTEMA DE ROLES")
print("="*70)

# Paso 1: Actualizar estructura
print("\n[1/3] Actualizando estructura de base de datos...")
try:
    resultado1 = subprocess.run(
        [sys.executable, "actualizar_estructura_roles.py"],
        capture_output=True,
        text=True,
        cwd=r"C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND"
    )
    if "Todas las tablas verificadas" in resultado1.stdout:
        print("OK - Estructura actualizada")
    else:
        print("WARNING - Verificar salida")
except Exception as e:
    print(f"ERROR: {e}")

# Paso 2: Configurar roles y puestos
print("\n[2/3] Configurando roles y puestos...")
try:
    resultado2 = subprocess.run(
        [sys.executable, "configurar_roles_y_puestos.py"],
        capture_output=True,
        text=True,
        input="s\n",
        cwd=r"C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND"
    )
    if "roles creados" in resultado2.stdout.lower():
        print("OK - Roles configurados")
    else:
        print("WARNING - Verificar salida")
except Exception as e:
    print(f"ERROR: {e}")

# Paso 3: Vincular empleados
print("\n[3/3] Vinculando empleados con usuarios y roles...")
try:
    resultado3 = subprocess.run(
        [sys.executable, "vincular_empleados_usuarios_roles.py"],
        capture_output=True,
        text=True,
        cwd=r"C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND"
    )
    if "empleados" in resultado3.stdout.lower():
        print("OK - Empleados vinculados")
    else:
        print("WARNING - Verificar salida")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
print("INSTALACION COMPLETADA")
print("="*70)
print("\nAhora ejecuta: python verificar_estado_completo_roles.py")
print("="*70)


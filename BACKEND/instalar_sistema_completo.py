"""
Script Maestro - Instalación Completa del Sistema de Roles
==========================================================

Este script ejecuta TODO el proceso de instalación en el orden correcto:
1. Actualiza estructura de base de datos
2. Crea roles y puestos
3. Vincula empleados con usuarios y roles

Autor: Sistema RRHH
Fecha: 2025
"""

import subprocess
import sys
from datetime import datetime


def ejecutar_script(nombre_script, descripcion):
    """Ejecuta un script Python y muestra el resultado"""
    print("\n" + "="*70)
    print(f"EJECUTANDO: {descripcion}")
    print("="*70)
    
    try:
        resultado = subprocess.run(
            [sys.executable, nombre_script],
            capture_output=False,
            text=True
        )
        
        if resultado.returncode == 0:
            print(f"\n✅ {descripcion} - COMPLETADO")
            return True
        else:
            print(f"\n❌ {descripcion} - ERROR")
            return False
            
    except Exception as e:
        print(f"\n❌ Error al ejecutar {nombre_script}: {e}")
        return False


def main():
    """Función principal que ejecuta todo el proceso"""
    print("\n" + "="*70)
    print("🚀 INSTALACIÓN COMPLETA DEL SISTEMA DE ROLES")
    print("="*70)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nEste script ejecutará 3 pasos:")
    print("  1️⃣  Actualizar estructura de base de datos")
    print("  2️⃣  Configurar roles y puestos (5 roles + 25 puestos)")
    print("  3️⃣  Vincular empleados con usuarios y roles")
    print("\n" + "="*70)
    
    respuesta = input("\n¿Desea continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("\nOperación cancelada.")
        return
    
    # Paso 1: Actualizar estructura
    if not ejecutar_script(
        "actualizar_estructura_roles.py",
        "Paso 1: Actualizar estructura de BD"
    ):
        print("\n❌ Error en Paso 1. Abortando instalación.")
        return
    
    # Paso 2: Configurar roles y puestos
    if not ejecutar_script(
        "configurar_roles_y_puestos.py",
        "Paso 2: Configurar roles y puestos"
    ):
        print("\n❌ Error en Paso 2. Abortando instalación.")
        return
    
    # Paso 3: Vincular empleados con usuarios y roles
    if not ejecutar_script(
        "vincular_empleados_usuarios_roles.py",
        "Paso 3: Vincular empleados con usuarios y roles"
    ):
        print("\n❌ Error en Paso 3. Abortando instalación.")
        return
    
    # Resumen final
    print("\n" + "="*70)
    print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)
    
    print("\n✅ Sistema de Roles Instalado:")
    print("   • 5 roles jerárquicos creados")
    print("   • 25 puestos distribuidos correctamente")
    print("   • ~35 permisos configurados")
    print("   • Empleados vinculados con usuarios")
    print("   • Roles asignados automáticamente")
    
    print("\n📌 PRÓXIMOS PASOS:")
    print("   1. Revisar el reporte generado")
    print("   2. Informar a los empleados su contraseña: Empleado123")
    print("   3. Solicitar que cambien su contraseña en el primer login")
    print("   4. Implementar verificación de permisos en el backend")
    print("   5. Implementar verificación en el frontend")
    
    print("\n📚 DOCUMENTACIÓN:")
    print("   • EMPIEZA_AQUI.md")
    print("   • README_SISTEMA_ROLES.md")
    print("   • DOCUMENTACION_SISTEMA_ROLES.md")
    
    print("\n" + "="*70)
    print("Sistema listo para usar ✅")
    print("="*70)


if __name__ == "__main__":
    main()


"""
Script para limpiar la base de datos y repoblar con datos correctos
Elimina duplicados y crea datos coherentes
"""
import sqlite3
from datetime import datetime

def limpiar_y_repoblar():
    print("="*80)
    print("LIMPIANDO Y REPOBLANDO BASE DE DATOS")
    print("="*80)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # 1. ELIMINAR DATOS EXISTENTES (excepto usuarios admin)
        print("\n[1/3] Limpiando datos existentes...")
        
        # Guardar admin
        cursor.execute("SELECT * FROM usuarios WHERE email = 'admin@empresa.hn'")
        admin = cursor.fetchone()
        
        # Limpiar tablas
        tablas = [
            'Notificaciones',
            'Capacitaciones',
            'Evaluaciones',
            'Vacaciones_Permisos',
            'Nomina',
            'asistencias',
            'Contratos',
            'empleados',
            'departamentos',
            'Puestos'
        ]
        
        for tabla in tablas:
            try:
                cursor.execute(f"DELETE FROM {tabla}")
                print(f"   - {tabla}: limpiado")
            except Exception as e:
                print(f"   - {tabla}: ERROR - {str(e)}")
        
        # Limpiar usuarios excepto admin
        cursor.execute("DELETE FROM usuarios WHERE email != 'admin@empresa.hn'")
        print(f"   - usuarios: limpiado (excepto admin)")
        
        conn.commit()
        print("[OK] Limpieza completada")
        
        # 2. REPOBLAR
        print("\n[2/3] Repoblando base de datos...")
        print("Ejecutando script de poblado...")
        
        conn.close()
        
        # Importar y ejecutar el script de poblado
        import poblar_datos_empresariales
        poblar_datos_empresariales.poblar_datos_empresariales()
        
        # 3. VERIFICAR COHERENCIA
        print("\n[3/3] Verificando coherencia...")
        conn = sqlite3.connect('rrhh.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM empleados")
        num_empleados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Contratos")
        num_contratos = cursor.fetchone()[0]
        
        print(f"\n   Empleados: {num_empleados}")
        print(f"   Contratos: {num_contratos}")
        
        if num_empleados != num_contratos:
            print(f"\n   [ADVERTENCIA] Hay {num_contratos - num_empleados} contratos extra")
            print("   Corrigiendo...")
            
            # Eliminar contratos duplicados, mantener solo el más reciente por empleado
            cursor.execute("""
                DELETE FROM Contratos
                WHERE id_contrato NOT IN (
                    SELECT MAX(id_contrato)
                    FROM Contratos
                    GROUP BY id_empleado
                )
            """)
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM Contratos")
            num_contratos = cursor.fetchone()[0]
            print(f"   [OK] Contratos corregidos: {num_contratos}")
        
        print("\n" + "="*80)
        print("[OK] BASE DE DATOS LISTA Y COHERENTE")
        print("="*80)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    respuesta = input("Esto eliminara todos los datos existentes. Continuar? (si/no): ")
    if respuesta.lower() == 'si':
        limpiar_y_repoblar()
    else:
        print("Operacion cancelada")


"""
Script para corregir la base de datos
Elimina contratos duplicados y verifica coherencia
"""
import sqlite3

def corregir_base_datos():
    print("="*80)
    print("CORRIGIENDO BASE DE DATOS")
    print("="*80)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # 1. Verificar estado actual
        print("\n[1/3] Verificando estado actual...")
        
        cursor.execute("SELECT COUNT(*) FROM empleados")
        num_empleados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Contratos")
        num_contratos = cursor.fetchone()[0]
        
        print(f"   Empleados: {num_empleados}")
        print(f"   Contratos: {num_contratos}")
        
        # 2. Eliminar contratos duplicados
        if num_contratos > num_empleados:
            print(f"\n[2/3] Eliminando {num_contratos - num_empleados} contratos duplicados...")
            
            # Mantener solo el contrato más reciente por empleado
            cursor.execute("""
                DELETE FROM Contratos
                WHERE id_contrato NOT IN (
                    SELECT MAX(id_contrato)
                    FROM Contratos
                    GROUP BY id_empleado
                )
            """)
            
            eliminados = cursor.rowcount
            conn.commit()
            print(f"   [OK] {eliminados} contratos duplicados eliminados")
        else:
            print("\n[2/3] No hay contratos duplicados")
        
        # 3. Crear contratos faltantes
        cursor.execute("""
            SELECT e.id, e.nombre, e.apellido, e.salario, e.fecha_ingreso, e.puesto
            FROM empleados e
            WHERE e.id NOT IN (SELECT id_empleado FROM Contratos)
        """)
        empleados_sin_contrato = cursor.fetchall()
        
        if empleados_sin_contrato:
            print(f"\n[3/3] Creando {len(empleados_sin_contrato)} contratos faltantes...")
            
            for emp in empleados_sin_contrato:
                emp_id, nombre, apellido, salario, fecha_ingreso, puesto = emp
                
                cursor.execute("""
                    INSERT INTO Contratos 
                    (id_empleado, empresa_nombre, trabajador_nombre_completo,
                     nombre_puesto, tipo_contrato, salario_base, salario,
                     fecha_inicio, estado)
                    VALUES (?, 'Empresa Honduras S.A.', ?, ?, 'tiempo_indefinido', ?, ?, ?, 'activo')
                """, (emp_id, f"{nombre} {apellido}", puesto, salario, salario, fecha_ingreso))
            
            conn.commit()
            print(f"   [OK] {len(empleados_sin_contrato)} contratos creados")
        else:
            print("\n[3/3] Todos los empleados tienen contrato")
        
        # Verificación final
        cursor.execute("SELECT COUNT(*) FROM empleados")
        num_empleados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Contratos")
        num_contratos = cursor.fetchone()[0]
        
        print("\n" + "="*80)
        print("RESULTADO FINAL:")
        print(f"   Empleados: {num_empleados}")
        print(f"   Contratos: {num_contratos}")
        
        if num_empleados == num_contratos:
            print("\n[OK] BASE DE DATOS COHERENTE - 1 contrato por empleado")
        else:
            print(f"\n[ADVERTENCIA] Diferencia: {abs(num_empleados - num_contratos)}")
        
        print("="*80)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    corregir_base_datos()


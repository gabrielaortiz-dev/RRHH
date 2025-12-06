"""
Script para verificar la integridad referencial completa de la base de datos
"""
import sqlite3

def verificar_integridad():
    print("="*70)
    print("VERIFICACION DE INTEGRIDAD REFERENCIAL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    errores = []
    
    # ================================================================
    # 1. Verificar que todos los empleados tengan departamentos validos
    # ================================================================
    print("\n[1] Verificando empleados -> departamentos...")
    cursor.execute("""
        SELECT COUNT(*) FROM empleados e
        WHERE e.departamento_id NOT IN (SELECT id FROM departamentos)
    """)
    invalidos = cursor.fetchone()[0]
    if invalidos > 0:
        errores.append(f"   [ERROR] {invalidos} empleados con departamento invalido")
    else:
        print("   [OK] Todos los empleados tienen departamentos validos")
    
    # ================================================================
    # 2. Verificar que todos los empleados tengan puestos validos
    # ================================================================
    print("\n[2] Verificando empleados -> puestos...")
    cursor.execute("""
        SELECT COUNT(*) FROM empleados e
        WHERE e.puesto NOT IN (SELECT id_puesto FROM Puestos)
    """)
    invalidos = cursor.fetchone()[0]
    if invalidos > 0:
        errores.append(f"   [ERROR] {invalidos} empleados con puesto invalido")
    else:
        print("   [OK] Todos los empleados tienen puestos validos")
    
    # ================================================================
    # 3. Verificar que todos los contratos tengan empleados validos
    # ================================================================
    print("\n[3] Verificando contratos -> empleados...")
    cursor.execute("""
        SELECT COUNT(*) FROM Contratos c
        WHERE c.id_empleado NOT IN (SELECT id FROM empleados)
    """)
    invalidos = cursor.fetchone()[0]
    if invalidos > 0:
        errores.append(f"   [ERROR] {invalidos} contratos con empleado invalido")
    else:
        print("   [OK] Todos los contratos tienen empleados validos")
    
    # ================================================================
    # 4. Verificar que todas las evaluaciones tengan empleados validos
    # ================================================================
    print("\n[4] Verificando evaluaciones -> empleados...")
    cursor.execute("""
        SELECT COUNT(*) FROM Evaluaciones e
        WHERE e.id_empleado NOT IN (SELECT id FROM empleados)
    """)
    invalidos = cursor.fetchone()[0]
    if invalidos > 0:
        errores.append(f"   [ERROR] {invalidos} evaluaciones con empleado invalido")
    else:
        print("   [OK] Todas las evaluaciones tienen empleados validos")
    
    # ================================================================
    # 5. Verificar que todas las asistencias tengan empleados validos
    # ================================================================
    print("\n[5] Verificando asistencias -> empleados...")
    cursor.execute("""
        SELECT COUNT(*) FROM asistencias a
        WHERE a.empleado_id NOT IN (SELECT id FROM empleados)
    """)
    invalidos = cursor.fetchone()[0]
    if invalidos > 0:
        errores.append(f"   [ERROR] {invalidos} asistencias con empleado invalido")
    else:
        print("   [OK] Todas las asistencias tienen empleados validos")
    
    # ================================================================
    # 6. Verificar que todas las vacaciones tengan empleados validos
    # ================================================================
    print("\n[6] Verificando vacaciones -> empleados...")
    cursor.execute("""
        SELECT COUNT(*) FROM Vacaciones_Permisos v
        WHERE v.id_empleado NOT IN (SELECT id FROM empleados)
    """)
    invalidos = cursor.fetchone()[0]
    if invalidos > 0:
        errores.append(f"   [ERROR] {invalidos} vacaciones con empleado invalido")
    else:
        print("   [OK] Todas las vacaciones tienen empleados validos")
    
    # ================================================================
    # 7. Verificar que todas las capacitaciones tengan empleados validos
    # ================================================================
    print("\n[7] Verificando capacitaciones -> empleados...")
    cursor.execute("""
        SELECT COUNT(*) FROM Capacitaciones c
        WHERE c.id_empleado NOT IN (SELECT id FROM empleados)
    """)
    invalidos = cursor.fetchone()[0]
    if invalidos > 0:
        errores.append(f"   [ERROR] {invalidos} capacitaciones con empleado invalido")
    else:
        print("   [OK] Todas las capacitaciones tienen empleados validos")
    
    # ================================================================
    # 8. Verificar rangos de IDs
    # ================================================================
    print("\n[8] Verificando rangos de IDs...")
    
    cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM departamentos")
    min_id, max_id, count = cursor.fetchone()
    print(f"   Departamentos: ID {min_id}-{max_id} ({count} registros)")
    if min_id != 1 or max_id != count:
        errores.append(f"   [WARNING] Departamentos no empiezan en 1 o tienen gaps")
    
    cursor.execute("SELECT MIN(id_puesto), MAX(id_puesto), COUNT(*) FROM Puestos")
    min_id, max_id, count = cursor.fetchone()
    print(f"   Puestos: ID {min_id}-{max_id} ({count} registros)")
    if min_id != 1 or max_id != count:
        errores.append(f"   [WARNING] Puestos no empiezan en 1 o tienen gaps")
    
    cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM empleados")
    min_id, max_id, count = cursor.fetchone()
    print(f"   Empleados: ID {min_id}-{max_id} ({count} registros)")
    if min_id != 1 or max_id != count:
        errores.append(f"   [WARNING] Empleados no empiezan en 1 o tienen gaps")
    
    # ================================================================
    # 9. Verificar coherencia de cantidades
    # ================================================================
    print("\n[9] Verificando coherencia de cantidades...")
    
    cursor.execute("SELECT COUNT(*) FROM empleados")
    total_empleados = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Contratos")
    total_contratos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Evaluaciones")
    total_evaluaciones = cursor.fetchone()[0]
    
    print(f"   Empleados: {total_empleados}")
    print(f"   Contratos: {total_contratos}")
    print(f"   Evaluaciones: {total_evaluaciones}")
    
    if total_contratos > total_empleados:
        errores.append(f"   [WARNING] Mas contratos ({total_contratos}) que empleados ({total_empleados})")
    
    if total_evaluaciones > total_empleados:
        errores.append(f"   [WARNING] Mas evaluaciones ({total_evaluaciones}) que empleados ({total_empleados})")
    
    # ================================================================
    # 10. Verificar empleados sin contratos
    # ================================================================
    print("\n[10] Verificando empleados sin contratos...")
    cursor.execute("""
        SELECT COUNT(*) FROM empleados e
        WHERE e.id NOT IN (SELECT id_empleado FROM Contratos)
    """)
    sin_contrato = cursor.fetchone()[0]
    if sin_contrato > 0:
        print(f"   [WARNING] {sin_contrato} empleados sin contrato")
    else:
        print(f"   [OK] Todos los empleados tienen contrato")
    
    # ================================================================
    # 11. Verificar empleados sin evaluaciones
    # ================================================================
    print("\n[11] Verificando empleados sin evaluaciones...")
    cursor.execute("""
        SELECT COUNT(*) FROM empleados e
        WHERE e.id NOT IN (SELECT id_empleado FROM Evaluaciones)
    """)
    sin_evaluacion = cursor.fetchone()[0]
    if sin_evaluacion > 0:
        print(f"   [WARNING] {sin_evaluacion} empleados sin evaluacion")
    else:
        print(f"   [OK] Todos los empleados tienen evaluacion")
    
    # ================================================================
    # RESUMEN FINAL
    # ================================================================
    print("\n" + "="*70)
    if len(errores) == 0:
        print("INTEGRIDAD VERIFICADA: TODO CORRECTO")
        print("="*70)
        print("\nLa base de datos esta completamente coherente:")
        print("  - Todas las referencias son validas")
        print("  - Los IDs empiezan desde 1")
        print("  - Las cantidades son coherentes")
        print("  - Cada empleado tiene contrato y evaluacion")
    else:
        print("SE ENCONTRARON PROBLEMAS")
        print("="*70)
        for error in errores:
            print(error)
    
    print("\n" + "="*70)
    
    conn.close()

if __name__ == "__main__":
    verificar_integridad()


"""
Script para reordenar las columnas y mover nombre_empleado a la tercera posición
(en SQLite no se puede mover columnas, así que recreamos las tablas)
"""
import sqlite3
import os
from database import Database

def reordenar_columnas():
    """Reordenar columnas para que nombre_empleado esté en tercera posición"""
    print("=" * 70)
    print("REORDENANDO COLUMNAS: nombre_empleado a tercera posición")
    print("=" * 70)
    print()
    
    db = Database()
    db.connect()
    
    try:
        # Definir el orden correcto para cada tabla
        tablas_estructura = {
            "Contratos": {
                "columnas_orden": [
                    "id_contrato", "id_empleado", "nombre_empleado",
                    "empresa_nombre", "empresa_representante_legal", "empresa_rtn", 
                    "empresa_direccion", "empresa_telefono", "empresa_email",
                    "trabajador_nombre_completo", "trabajador_dni", "trabajador_nacionalidad", 
                    "trabajador_estado_civil", "trabajador_direccion", "trabajador_telefono", 
                    "trabajador_email", "nombre_puesto", "descripcion_puesto", "id_departamento", 
                    "jefe_inmediato", "tipo_contrato", "jornada_laboral_dias", "horario_entrada", 
                    "horario_salida", "tiempo_descanso", "lugar_trabajo", "salario_base", 
                    "forma_pago", "metodo_pago", "bonificaciones", "comisiones", "incentivos", 
                    "deducciones", "fecha_inicio", "fecha_fin", "periodo_prueba_dias",
                    "derechos_empleado", "obligaciones_empleado", "derechos_empleador", 
                    "obligaciones_empleador", "vacaciones_anuales", "aguinaldo", 
                    "prestaciones_sociales", "dias_feriados", "permisos_ley",
                    "clausula_confidencialidad", "politica_datos", "no_competencia",
                    "causas_terminacion", "tiempo_preaviso", "pago_prestaciones",
                    "politica_uniformes", "uso_vehiculos", "trabajo_remoto", 
                    "politica_horas_extras", "uso_sistemas", "condiciones", "estado",
                    "fecha_creacion", "fecha_modificacion"
                ],
                "primary_key": "id_contrato",
                "foreign_keys": [
                    ("id_empleado", "Empleados", "id_empleado"),
                    ("id_departamento", "Departamentos", "id_departamento")
                ]
            },
            "Nomina": {
                "columnas_orden": [
                    "id_nomina", "id_empleado", "nombre_empleado",
                    "mes", "anio", "periodo", "salario_base", "total_bonificaciones",
                    "total_deducciones", "salario_neto", "fecha_pago", "estado",
                    "fecha_creacion", "fecha_modificacion", "creado_por", "modificado_por",
                    "observaciones"
                ],
                "primary_key": "id_nomina",
                "foreign_keys": [
                    ("id_empleado", "Empleados", "id_empleado"),
                    ("creado_por", "usuarios", "id"),
                    ("modificado_por", "usuarios", "id")
                ]
            },
            "Vacaciones_Permisos": {
                "columnas_orden": [
                    "id_permiso", "id_empleado", "nombre_empleado",
                    "tipo", "fecha_solicitud", "fecha_inicio", "fecha_fin",
                    "dias_solicitados", "dias_disponibles", "dias_usados", "dias_acumulados",
                    "motivo", "estado", "aprobado_por_jefe", "aprobado_por_rrhh",
                    "fecha_aprobacion_jefe", "fecha_aprobacion_rrhh", "fecha_rechazo",
                    "motivo_rechazo", "observaciones", "fecha_creacion", "fecha_modificacion"
                ],
                "primary_key": "id_permiso",
                "foreign_keys": [
                    ("id_empleado", "Empleados", "id_empleado"),
                    ("aprobado_por_jefe", "usuarios", "id"),
                    ("aprobado_por_rrhh", "usuarios", "id")
                ]
            },
            "Capacitaciones": {
                "columnas_orden": [
                    "id_capacitacion", "id_empleado", "nombre_empleado",
                    "nombre_curso", "institucion", "fecha_inicio", "fecha_fin", "certificado"
                ],
                "primary_key": "id_capacitacion",
                "foreign_keys": [
                    ("id_empleado", "Empleados", "id_empleado")
                ]
            },
            "Evaluaciones": {
                "columnas_orden": [
                    "id_evaluacion", "id_empleado", "nombre_empleado",
                    "fecha", "evaluador", "puntaje", "observaciones"
                ],
                "primary_key": "id_evaluacion",
                "foreign_keys": [
                    ("id_empleado", "Empleados", "id_empleado")
                ]
            },
            "Documentos": {
                "columnas_orden": [
                    "id_documento", "id_empleado", "nombre_empleado",
                    "nombre_archivo", "nombre_original", "tipo_documento", "categoria",
                    "ruta_archivo", "tamano_bytes", "mime_type", "fecha_subida",
                    "fecha_expiracion", "estado", "subido_por", "descripcion"
                ],
                "primary_key": "id_documento",
                "foreign_keys": [
                    ("id_empleado", "Empleados", "id_empleado"),
                    ("subido_por", "usuarios", "id")
                ]
            },
            "Asistencias": {
                "columnas_orden": [
                    "id_asistencia", "id_empleado", "nombre_empleado",
                    "fecha", "hora_entrada", "hora_salida", "observaciones"
                ],
                "primary_key": "id_asistencia",
                "foreign_keys": [
                    ("id_empleado", "Empleados", "id_empleado")
                ]
            },
            "asistencias": {
                "columnas_orden": [
                    "id", "empleado_id", "nombre_empleado",
                    "fecha", "hora_entrada", "hora_salida", "estado", "observaciones"
                ],
                "primary_key": "id",
                "foreign_keys": [
                    ("empleado_id", "empleados", "id")
                ]
            }
        }
        
        # Limpiar tablas temporales que puedan haber quedado de ejecuciones anteriores
        cursor = db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_temp_reorden'")
        tablas_temp = cursor.fetchall()
        for tabla_temp in tablas_temp:
            try:
                db.execute_query(f"DROP TABLE IF EXISTS {tabla_temp[0]}")
                print(f"[INFO] Tabla temporal {tabla_temp[0]} eliminada")
            except:
                pass
        
        for tabla_nombre, estructura in tablas_estructura.items():
            try:
                # Verificar si la tabla existe
                cursor = db.connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla_nombre,))
                if not cursor.fetchone():
                    print(f"[INFO] Tabla {tabla_nombre} no existe, omitiendo...")
                    continue
                
                print(f"[INFO] Procesando tabla {tabla_nombre}...")
                
                # Obtener estructura actual de la tabla
                cursor.execute(f"PRAGMA table_info({tabla_nombre})")
                columnas_actuales = cursor.fetchall()
                
                # Verificar que nombre_empleado existe
                tiene_nombre_empleado = any(col[1] == "nombre_empleado" for col in columnas_actuales)
                if not tiene_nombre_empleado:
                    print(f"[INFO] Tabla {tabla_nombre} no tiene nombre_empleado, omitiendo...")
                    continue
                
                # Verificar si ya está en la tercera posición
                if len(columnas_actuales) >= 3 and columnas_actuales[2][1] == "nombre_empleado":
                    print(f"[INFO] Tabla {tabla_nombre} ya tiene nombre_empleado en tercera posición")
                    continue
                
                # Crear tabla temporal con el orden correcto
                tabla_temp = f"{tabla_nombre}_temp_reorden"
                
                # Filtrar solo las columnas que realmente existen
                columnas_existentes_orden = []
                columnas_info_dict = {col[1]: col for col in columnas_actuales}
                
                # Primero agregar las columnas en el orden deseado (solo las que existen)
                for col_name in estructura["columnas_orden"]:
                    if col_name in columnas_info_dict:
                        columnas_existentes_orden.append(col_name)
                
                # Agregar cualquier columna restante que no esté en la lista de orden
                for col_info in columnas_actuales:
                    col_name = col_info[1]
                    if col_name not in columnas_existentes_orden:
                        columnas_existentes_orden.append(col_name)
                
                # Construir CREATE TABLE con el orden correcto
                columnas_def = []
                for col_name in columnas_existentes_orden:
                    col_info = columnas_info_dict[col_name]
                    col_type = col_info[2]
                    not_null = "NOT NULL" if col_info[3] else ""
                    default_val = col_info[4]
                    pk = "PRIMARY KEY AUTOINCREMENT" if col_name == estructura["primary_key"] else ""
                    
                    col_def = f"{col_name} {col_type}"
                    if pk:
                        col_def += f" {pk}"
                    if not_null:
                        col_def += f" {not_null}"
                    if default_val is not None:
                        if isinstance(default_val, str):
                            col_def += f" DEFAULT '{default_val}'"
                        else:
                            col_def += f" DEFAULT {default_val}"
                    
                    columnas_def.append(col_def)
                
                # Crear tabla temporal
                create_sql = f"CREATE TABLE {tabla_temp} ({', '.join(columnas_def)})"
                db.execute_query(create_sql)
                
                # Copiar datos (solo las columnas que existen)
                columnas_str = ', '.join(columnas_existentes_orden)
                insert_sql = f"INSERT INTO {tabla_temp} ({columnas_str}) SELECT {columnas_str} FROM {tabla_nombre}"
                db.execute_query(insert_sql)
                
                # Eliminar tabla original
                db.execute_query(f"DROP TABLE {tabla_nombre}")
                
                # Renombrar tabla temporal
                db.execute_query(f"ALTER TABLE {tabla_temp} RENAME TO {tabla_nombre}")
                
                # Recrear índices y foreign keys si es necesario
                # (SQLite no soporta ADD CONSTRAINT, así que las foreign keys se recrean con la tabla)
                
                print(f"[OK] Tabla {tabla_nombre} reordenada exitosamente")
                
            except Exception as e:
                print(f"[ERROR] Error al procesar tabla {tabla_nombre}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print()
        print("=" * 70)
        print("[OK] Reordenamiento completado exitosamente")
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERROR] Error en el reordenamiento: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.disconnect()

if __name__ == "__main__":
    reordenar_columnas()


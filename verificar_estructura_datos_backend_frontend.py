"""
Script para verificar que la estructura de datos del backend (SQLite) 
coincida con lo que el frontend espera
"""
import sqlite3
import urllib.request
import urllib.error
import json
import os
import sys

def obtener_estructura_tabla(db_path, tabla):
    """Obtiene la estructura de una tabla SQLite"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener información de las columnas
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = cursor.fetchall()
        
        # Obtener un registro de ejemplo
        cursor.execute(f"SELECT * FROM {tabla} LIMIT 1")
        ejemplo = cursor.fetchone()
        
        conn.close()
        
        return {
            'columnas': [col[1] for col in columnas],  # Nombre de la columna
            'tipos': [col[2] for col in columnas],    # Tipo de dato
            'ejemplo': dict(zip([col[1] for col in columnas], ejemplo)) if ejemplo else None
        }
    except Exception as e:
        return {'error': str(e)}


def obtener_datos_backend(endpoint):
    """Obtiene datos del backend mediante HTTP"""
    base_url = "http://localhost:8000"
    try:
        req = urllib.request.Request(f"{base_url}{endpoint}")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.URLError:
        return {'error': 'Backend no disponible'}
    except Exception as e:
        return {'error': str(e)}


def comparar_estructuras(tabla_db, datos_backend, campos_frontend, nombre_entidad):
    """Compara las estructuras entre base de datos, backend y frontend"""
    print(f"\n{'='*70}")
    print(f"ENTIDAD: {nombre_entidad.upper()}")
    print(f"{'='*70}")
    
    problemas = []
    
    # 1. Verificar estructura de la base de datos
    if 'error' in tabla_db:
        print(f"[ERROR] No se pudo obtener estructura de tabla: {tabla_db['error']}")
        return problemas
    
    columnas_db = set(tabla_db['columnas'])
    print(f"\n[1] BASE DE DATOS (SQLite):")
    print(f"    Columnas encontradas: {len(columnas_db)}")
    print(f"    Columnas: {', '.join(sorted(columnas_db))}")
    
    # 2. Verificar datos del backend
    if 'error' in datos_backend:
        print(f"\n[2] BACKEND (API):")
        print(f"    [ERROR] {datos_backend['error']}")
        return problemas
    
    # Extraer datos de la respuesta
    datos = None
    if isinstance(datos_backend, dict):
        if 'data' in datos_backend:
            data = datos_backend['data']
            if isinstance(data, list) and len(data) > 0:
                datos = data[0]
            elif isinstance(data, dict):
                datos = data
        else:
            datos = datos_backend
    elif isinstance(datos_backend, list) and len(datos_backend) > 0:
        datos = datos_backend[0]
    
    if datos:
        campos_backend = set(datos.keys())
        print(f"\n[2] BACKEND (API):")
        print(f"    Campos devueltos: {len(campos_backend)}")
        print(f"    Campos: {', '.join(sorted(campos_backend))}")
    else:
        print(f"\n[2] BACKEND (API):")
        print(f"    [ADVERTENCIA] No se encontraron datos de ejemplo")
        campos_backend = set()
    
    # 3. Verificar campos esperados por el frontend
    campos_frontend_set = set(campos_frontend)
    print(f"\n[3] FRONTEND (Interfaces TypeScript):")
    print(f"    Campos esperados: {len(campos_frontend_set)}")
    print(f"    Campos: {', '.join(sorted(campos_frontend_set))}")
    
    # 4. Comparaciones
    print(f"\n[4] COMPARACIONES:")
    
    # Campos en DB pero no en Backend
    solo_db = columnas_db - campos_backend
    if solo_db:
        print(f"    [INFO] Campos solo en DB: {', '.join(sorted(solo_db))}")
    
    # Campos en Backend pero no en DB
    solo_backend = campos_backend - columnas_db
    if solo_backend:
        print(f"    [INFO] Campos calculados/join en Backend: {', '.join(sorted(solo_backend))}")
    
    # Campos en Frontend pero no en Backend
    faltantes_backend = campos_frontend_set - campos_backend
    if faltantes_backend:
        print(f"    [ADVERTENCIA] Campos esperados por Frontend pero no en Backend: {', '.join(sorted(faltantes_backend))}")
        problemas.append(f"Frontend espera campos que Backend no devuelve: {faltantes_backend}")
    
    # Campos en Backend pero no en Frontend (puede ser normal si el frontend los ignora)
    extras_backend = campos_backend - campos_frontend_set
    if extras_backend:
        print(f"    [INFO] Campos en Backend no usados por Frontend: {', '.join(sorted(extras_backend))}")
    
    # Verificar campos críticos
    campos_criticos = ['id', 'nombre']
    for campo in campos_criticos:
        if campo not in campos_backend and campo not in [f'id_{nombre_entidad}', f'{nombre_entidad}_id']:
            variantes = [f'id_{nombre_entidad}', f'{nombre_entidad}_id', f'{campo}_{nombre_entidad}']
            encontrado = any(v in campos_backend for v in variantes)
            if not encontrado:
                print(f"    [ERROR] Campo critico '{campo}' no encontrado en Backend")
                problemas.append(f"Campo critico '{campo}' faltante")
    
    return problemas


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("VERIFICACION DE ESTRUCTURA DE DATOS: BACKEND <-> FRONTEND")
    print("="*70)
    
    db_path = os.path.join("BACKEND", "rrhh.db")
    
    if not os.path.exists(db_path):
        print(f"[ERROR] No se encuentra la base de datos: {db_path}")
        return
    
    print(f"\n[OK] Base de datos encontrada: {db_path}")
    
    # Verificar backend disponible
    print("\nVerificando que el backend este disponible...")
    health = obtener_datos_backend("/api/health")
    if 'error' in health:
        print(f"[ERROR] Backend no disponible: {health['error']}")
        print("        Ejecuta: cd BACKEND && python main.py")
        return
    
    print("[OK] Backend disponible")
    
    # Definir entidades a verificar
    entidades = [
        {
            'nombre': 'empleados',
            'tabla_db': 'empleados',
            'endpoint': '/api/empleados',
            'campos_frontend': [
                'id', 'id_empleado', 'nombre', 'apellido', 'email', 'correo', 
                'telefono', 'direccion', 'cedula', 'fecha_nacimiento', 'fechaNacimiento',
                'genero', 'estado_civil', 'estadoCivil', 'nacionalidad',
                'puesto', 'departamento', 'id_departamento', 'id_puesto',
                'salario', 'fecha_ingreso', 'fechaIngreso', 'estado', 'activo'
            ]
        },
        {
            'nombre': 'departamentos',
            'tabla_db': 'departamentos',
            'endpoint': '/api/departamentos',
            'campos_frontend': [
                'id', 'id_departamento', 'nombre', 'nombre_departamento',
                'descripcion', 'gerente', 'numeroEmpleados', 'presupuesto',
                'estado', 'fechaCreacion', 'fecha_creacion', 'activo'
            ]
        },
        {
            'nombre': 'puestos',
            'tabla_db': 'Puestos',
            'endpoint': '/api/puestos',
            'campos_frontend': [
                'id', 'id_puesto', 'nombre', 'nombre_puesto',
                'nivel', 'salario_base', 'salarioBase'
            ]
        },
        {
            'nombre': 'usuarios',
            'tabla_db': 'usuarios',
            'endpoint': '/api/usuarios',
            'campos_frontend': [
                'id', 'nombre', 'email', 'rol', 'fecha_creacion', 'activo'
            ]
        },
        {
            'nombre': 'asistencias',
            'tabla_db': 'asistencias',
            'endpoint': '/api/asistencias',
            'campos_frontend': [
                'id_asistencia', 'id_empleado', 'fecha', 'hora_entrada',
                'hora_salida', 'observaciones', 'empleado_nombre', 'nombre_empleado',
                'estado_asistencia'
            ]
        },
        {
            'nombre': 'nomina',
            'tabla_db': 'Nomina',
            'endpoint': '/api/nomina',
            'campos_frontend': [
                'id_nomina', 'id_empleado', 'nombre_empleado', 'mes', 'anio',
                'periodo', 'salario_base', 'total_bonificaciones', 'total_deducciones',
                'salario_neto', 'fecha_pago', 'estado', 'observaciones',
                'bonificaciones_detalle', 'deducciones_detalle'
            ]
        },
        {
            'nombre': 'vacaciones',
            'tabla_db': 'Vacaciones_Permisos',
            'endpoint': '/api/vacaciones',
            'campos_frontend': [
                'id_permiso', 'id_empleado', 'nombre_empleado', 'tipo',
                'fecha_solicitud', 'fecha_inicio', 'fecha_fin',
                'dias_solicitados', 'dias_disponibles', 'motivo', 'estado',
                'aprobado_por_jefe', 'aprobado_por_rrhh', 'fecha_aprobacion_jefe',
                'fecha_aprobacion_rrhh', 'motivo_rechazo'
            ]
        },
        {
            'nombre': 'notificaciones',
            'tabla_db': 'Notificaciones',
            'endpoint': '/api/notificaciones',
            'campos_frontend': [
                'id', 'userId', 'usuario_id', 'type', 'tipo', 'title', 'titulo',
                'message', 'mensaje', 'module', 'modulo', 'moduleId', 'modulo_id',
                'redirectUrl', 'redirect_url', 'isRead', 'is_read', 'createdAt',
                'created_at', 'readAt', 'read_at'
            ]
        }
    ]
    
    todos_problemas = []
    
    for entidad in entidades:
        # Obtener estructura de la tabla
        estructura_db = obtener_estructura_tabla(db_path, entidad['tabla_db'])
        
        # Obtener datos del backend
        datos_backend = obtener_datos_backend(entidad['endpoint'])
        
        # Comparar
        problemas = comparar_estructuras(
            estructura_db,
            datos_backend,
            entidad['campos_frontend'],
            entidad['nombre']
        )
        
        todos_problemas.extend(problemas)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    
    if todos_problemas:
        print(f"\n[ADVERTENCIA] Se encontraron {len(todos_problemas)} problema(s):")
        for i, problema in enumerate(todos_problemas, 1):
            print(f"  {i}. {problema}")
    else:
        print("\n[OK] Todas las estructuras coinciden correctamente")
        print("\nEl backend y frontend estan sincronizados:")
        print("  - Las tablas SQLite tienen los campos correctos")
        print("  - El backend devuelve los datos esperados")
        print("  - El frontend puede procesar los datos correctamente")
    
    print("\n" + "="*70)
    print("\nNOTAS:")
    print("  - Los campos 'calculados' o de JOINs pueden aparecer en Backend pero no en DB")
    print("  - Algunos campos del Frontend pueden ser opcionales o calculados")
    print("  - Los servicios del Frontend tienen funciones normalize*() para mapear datos")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()


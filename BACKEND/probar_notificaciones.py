"""
Script para probar el sistema de notificaciones
"""
import sqlite3
import requests
from datetime import datetime

def verificar_estructura():
    """Verifica que las tablas existan"""
    print("🔍 Verificando estructura de la base de datos...\n")
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Verificar tabla Notificaciones
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Notificaciones'")
    if cursor.fetchone():
        print("✅ Tabla 'Notificaciones' existe")
        
        # Ver estructura
        cursor.execute("PRAGMA table_info(Notificaciones)")
        print("\n   Columnas:")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
    else:
        print("❌ Tabla 'Notificaciones' NO existe")
        return False
    
    conn.close()
    return True

def ver_usuarios():
    """Muestra los usuarios disponibles"""
    print("\n👥 Usuarios disponibles:\n")
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre, email FROM Usuarios LIMIT 5")
    usuarios = cursor.fetchall()
    
    for user in usuarios:
        print(f"   ID: {user[0]}, Nombre: {user[1]}, Email: {user[2]}")
    
    conn.close()
    return usuarios

def ver_notificaciones():
    """Muestra las notificaciones existentes"""
    print("\n🔔 Notificaciones en la base de datos:\n")
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, usuario_id, tipo, titulo, mensaje, is_read, created_at
        FROM Notificaciones
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    notificaciones = cursor.fetchall()
    
    if notificaciones:
        for notif in notificaciones:
            leida = "✓ Leída" if notif[5] else "○ No leída"
            print(f"   [{leida}] ID: {notif[0]}")
            print(f"      Usuario: {notif[1]}")
            print(f"      Tipo: {notif[2]}")
            print(f"      Título: {notif[3]}")
            print(f"      Mensaje: {notif[4][:50]}...")
            print(f"      Fecha: {notif[6]}")
            print()
    else:
        print("   No hay notificaciones")
    
    conn.close()
    return len(notificaciones)

def estadisticas():
    """Muestra estadísticas de notificaciones"""
    print("\n📊 Estadísticas:\n")
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Total por usuario
    cursor.execute("""
        SELECT usuario_id,
               COUNT(*) as total,
               SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as no_leidas,
               SUM(CASE WHEN is_read = 1 THEN 1 ELSE 0 END) as leidas
        FROM Notificaciones
        GROUP BY usuario_id
    """)
    
    stats = cursor.fetchall()
    
    if stats:
        for stat in stats:
            print(f"   Usuario {stat[0]}:")
            print(f"      Total: {stat[1]}")
            print(f"      No leídas: {stat[2]}")
            print(f"      Leídas: {stat[3]}")
            print()
    else:
        print("   No hay datos")
    
    # Total por tipo
    cursor.execute("""
        SELECT tipo, COUNT(*) as cantidad
        FROM Notificaciones
        GROUP BY tipo
        ORDER BY cantidad DESC
    """)
    
    print("   Por tipo:")
    for row in cursor.fetchall():
        print(f"      {row[0]}: {row[1]}")
    
    conn.close()

def probar_api():
    """Prueba los endpoints de la API"""
    print("\n🌐 Probando API (debe estar corriendo en puerto 8000)...\n")
    
    base_url = "http://localhost:8000"
    
    try:
        # Probar GET notificaciones
        print("   Probando GET /api/notificaciones...")
        response = requests.get(f"{base_url}/api/notificaciones?usuario_id=1&limit=5")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa: {data.get('count', 0)} notificaciones")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            return False
        
        # Probar contador
        print("   Probando GET /api/notificaciones/usuario/1/count...")
        response = requests.get(f"{base_url}/api/notificaciones/usuario/1/count")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Contador: {data.get('unread_count', 0)} no leídas")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el backend esté corriendo:")
        print("   python main.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def crear_notificacion_prueba():
    """Crea una notificación de prueba vía API"""
    print("\n➕ ¿Deseas crear una notificación de prueba? (s/n): ", end="")
    respuesta = input().lower()
    
    if respuesta != 's':
        return
    
    print("\n   ID del usuario (1): ", end="")
    usuario_id = input() or "1"
    
    try:
        response = requests.post(
            "http://localhost:8000/api/notificaciones",
            json={
                "usuario_id": int(usuario_id),
                "tipo": "info",
                "titulo": "Notificación de Prueba",
                "mensaje": f"Creada desde el script de prueba a las {datetime.now().strftime('%H:%M:%S')}",
                "modulo": "test"
            }
        )
        
        if response.status_code == 201:
            print("   ✅ Notificación creada exitosamente")
            data = response.json()
            print(f"   ID: {data.get('data', {}).get('id')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def main():
    print("=" * 70)
    print("🧪 PRUEBA DEL SISTEMA DE NOTIFICACIONES")
    print("=" * 70)
    
    # 1. Verificar estructura
    if not verificar_estructura():
        print("\n❌ La tabla no existe. Ejecuta:")
        print("   python recrear_tabla_notificaciones.py")
        return
    
    # 2. Ver usuarios
    usuarios = ver_usuarios()
    if not usuarios:
        print("\n⚠️  No hay usuarios en la base de datos")
    
    # 3. Ver notificaciones
    count = ver_notificaciones()
    
    # 4. Estadísticas
    if count > 0:
        estadisticas()
    
    # 5. Probar API
    api_ok = probar_api()
    
    # 6. Crear notificación de prueba
    if api_ok:
        crear_notificacion_prueba()
    
    print("\n" + "=" * 70)
    print("✅ Prueba completada")
    print("=" * 70)
    
    if api_ok and count > 0:
        print("\n🎉 ¡El sistema está funcionando correctamente!")
        print("\nPróximos pasos:")
        print("1. Abre el frontend: http://localhost:4200")
        print("2. Inicia sesión")
        print("3. Click en el icono de campana 🔔")
        print("4. Deberías ver las notificaciones")
    else:
        print("\n⚠️  Revisa que el backend esté corriendo:")
        print("   python main.py")

if __name__ == "__main__":
    main()


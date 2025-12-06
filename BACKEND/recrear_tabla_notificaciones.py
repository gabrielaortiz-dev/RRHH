"""
Script para recrear la tabla de notificaciones en la base de datos
"""
import sqlite3

def recrear_tabla_notificaciones():
    """Elimina y recrea la tabla de notificaciones"""
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Eliminar tablas existentes si existen
        print("📋 Eliminando tablas existentes...")
        cursor.execute('DROP TABLE IF EXISTS Notificaciones')
        cursor.execute('DROP TABLE IF EXISTS NotificacionesConfig')
        print("✅ Tablas anteriores eliminadas")
        
        # Crear tabla de notificaciones
        print("\n📋 Creando tabla Notificaciones...")
        cursor.execute('''
        CREATE TABLE Notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            mensaje TEXT NOT NULL,
            modulo VARCHAR(50),
            modulo_id VARCHAR(100),
            redirect_url VARCHAR(500),
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
        )
        ''')
        print("✅ Tabla 'Notificaciones' creada exitosamente")
        
        # Crear tabla de configuración
        print("📋 Creando tabla NotificacionesConfig...")
        cursor.execute('''
        CREATE TABLE NotificacionesConfig (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL UNIQUE,
            email_notifications BOOLEAN DEFAULT 1,
            enabled_types TEXT,
            enabled_modules TEXT,
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
        )
        ''')
        print("✅ Tabla 'NotificacionesConfig' creada exitosamente")
        
        # Crear índices
        print("📋 Creando índices...")
        cursor.execute('''
        CREATE INDEX idx_notificaciones_usuario 
        ON Notificaciones(usuario_id)
        ''')
        
        cursor.execute('''
        CREATE INDEX idx_notificaciones_leidas 
        ON Notificaciones(usuario_id, is_read)
        ''')
        
        cursor.execute('''
        CREATE INDEX idx_notificaciones_fecha 
        ON Notificaciones(created_at DESC)
        ''')
        print("✅ Índices creados exitosamente")
        
        conn.commit()
        
        # Insertar notificaciones de prueba
        print("\n📋 Insertando notificaciones de prueba...")
        cursor.execute("SELECT id, nombre, email FROM Usuarios LIMIT 1")
        usuario = cursor.fetchone()
        
        if usuario:
            usuario_id = usuario[0]
            nombre_usuario = usuario[1]
            
            notificaciones_prueba = [
                (usuario_id, 'info', '¡Bienvenido al Sistema de Notificaciones!', 
                 'El sistema de notificaciones ahora está conectado a la base de datos y completamente funcional.', 
                 'dashboard', None, None, 0),
                (usuario_id, 'success', 'Sistema Actualizado Correctamente', 
                 'Todos los formularios ahora tienen fondos blancos para mejor legibilidad.', 
                 'config', None, None, 0),
                (usuario_id, 'info', 'Nueva Funcionalidad Disponible', 
                 'Las notificaciones ahora se guardan permanentemente en la base de datos.', 
                 'notifications', None, '/config/notification-settings', 0)
            ]
            
            for notif in notificaciones_prueba:
                cursor.execute('''
                    INSERT INTO Notificaciones 
                    (usuario_id, tipo, titulo, mensaje, modulo, modulo_id, redirect_url, is_read)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', notif)
            
            conn.commit()
            print(f"✅ {len(notificaciones_prueba)} notificaciones de prueba insertadas para {nombre_usuario}")
        else:
            print("⚠️  No hay usuarios en la base de datos")
        
        # Verificar la estructura de la tabla
        cursor.execute("PRAGMA table_info(Notificaciones)")
        columnas = cursor.fetchall()
        print("\n📊 Estructura de la tabla Notificaciones:")
        for col in columnas:
            print(f"   - {col[1]} ({col[2]})")
        
        print("\n🎉 ¡Tablas de notificaciones creadas exitosamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Recreando tablas de notificaciones...\n")
    recrear_tabla_notificaciones()


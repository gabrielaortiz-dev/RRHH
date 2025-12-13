"""
Script simple para agregar tu email a la lista de acceso total
"""
import re

def agregar_email_a_lista(email):
    """Agrega un email a la lista USUARIOS_ACCESO_TOTAL en auth.py"""
    archivo = "auth.py"
    
    try:
        # Leer el archivo
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar la lista USUARIOS_ACCESO_TOTAL
        # Patrón para encontrar la lista
        patron = r'(USUARIOS_ACCESO_TOTAL = \[)'
        match = re.search(patron, contenido)
        
        if not match:
            print(f"[ERROR] No se encontro USUARIOS_ACCESO_TOTAL en {archivo}")
            return False
        
        inicio = match.end()
        
        # Buscar el final del array
        # Buscar el primer ']' que cierra el array
        pos = inicio
        nivel = 1
        while pos < len(contenido) and nivel > 0:
            if contenido[pos] == '[':
                nivel += 1
            elif contenido[pos] == ']':
                nivel -= 1
            pos += 1
        
        if nivel != 0:
            print(f"[ERROR] No se pudo encontrar el cierre del array")
            return False
        
        # Extraer el contenido actual del array
        contenido_array = contenido[inicio:pos-1].strip()
        
        # Verificar si el email ya está en la lista
        email_lower = email.lower().strip()
        emails_en_lista = re.findall(r'"([^"]+)"', contenido_array)
        
        if any(email_lower == e.lower().strip() for e in emails_en_lista):
            print(f"[INFO] El email {email} ya esta en la lista de acceso total")
            return True
        
        # Agregar el email
        if contenido_array and not contenido_array.endswith(','):
            contenido_array += ','
        contenido_array += f'\n    "{email}",  # Agregado automaticamente\n'
        
        # Reconstruir el archivo
        nuevo_contenido = (
            contenido[:inicio] + 
            contenido_array + 
            contenido[pos-1:]
        )
        
        # Escribir el archivo
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        
        print(f"[OK] Email {email} agregado exitosamente a USUARIOS_ACCESO_TOTAL")
        print(f"[INFO] Reinicia el servidor para que los cambios surtan efecto")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al modificar archivo: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("AGREGAR EMAIL A LISTA DE ACCESO TOTAL")
    print("=" * 70)
    print()
    
    # Mostrar usuarios activos primero
    try:
        from database import get_db
        
        db = get_db()
        usuarios_activos = db.fetch_all(
            "SELECT id, nombre, email, rol FROM usuarios WHERE activo = 1 ORDER BY email"
        )
        
        if usuarios_activos:
            print("Usuarios activos disponibles:")
            print("-" * 70)
            for u in usuarios_activos[:20]:  # Mostrar solo los primeros 20
                print(f"  {u['id']:3}. {u['email']:<40} - {u['nombre']}")
            if len(usuarios_activos) > 20:
                print(f"  ... y {len(usuarios_activos) - 20} usuarios mas")
            print("-" * 70)
            print()
        
        db.disconnect()
    except Exception as e:
        print(f"[INFO] No se pudieron cargar usuarios: {e}")
        print()
    
    # Pedir el email
    email = input("Ingresa tu email para agregarlo a la lista de acceso total: ").strip()
    
    if not email:
        print("[ERROR] Debes ingresar un email")
        exit(1)
    
    # Validar formato básico de email
    if '@' not in email or '.' not in email.split('@')[-1]:
        print("[ADVERTENCIA] El email no parece tener un formato valido")
        respuesta = input("¿Deseas continuar de todos modos? (s/n): ")
        if respuesta.lower() != 's':
            exit(1)
    
    # Confirmar
    print()
    print(f"Se agregara el email: {email}")
    respuesta = input("¿Confirmar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("Operacion cancelada")
        exit(0)
    
    # Agregar el email
    print()
    if agregar_email_a_lista(email):
        print()
        print("=" * 70)
        print("¡LISTO!")
        print("=" * 70)
        print("Tu email ha sido agregado a la lista de acceso total.")
        print("Ahora tienes acceso completo a todos los endpoints.")
        print()
        print("IMPORTANTE: Reinicia el servidor para que los cambios surtan efecto.")
        print()
    else:
        print()
        print("[ERROR] No se pudo agregar el email.")
        print("Puedes agregarlo manualmente editando BACKEND/auth.py")
        print("Busca USUARIOS_ACCESO_TOTAL y agrega tu email alli.")


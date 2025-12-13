"""
Script para configurar TU usuario con acceso total SIN RESTRICCIONES
"""
import re

def configurar_mi_usuario():
    """Configura tu email para acceso total"""
    print("=" * 70)
    print("CONFIGURAR TU USUARIO CON ACCESO TOTAL")
    print("=" * 70)
    print()
    
    archivo = "auth.py"
    
    try:
        # Leer el archivo
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar la lista USUARIOS_ACCESO_TOTAL
        patron = r'(USUARIOS_ACCESO_TOTAL = \[)'
        match = re.search(patron, contenido)
        
        if not match:
            print(f"[ERROR] No se encontro USUARIOS_ACCESO_TOTAL en {archivo}")
            return False
        
        inicio = match.end()
        
        # Buscar el final del array
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
        
        # Mostrar emails actuales
        emails_en_lista = re.findall(r'"([^"]+)"', contenido_array)
        if emails_en_lista:
            print("Emails actualmente con acceso total:")
            for email in emails_en_lista:
                print(f"  - {email}")
            print()
        
        # Pedir el email
        print("=" * 70)
        email = input("Ingresa TU email para acceso total SIN RESTRICCIONES: ").strip()
        
        if not email:
            print("[ERROR] Debes ingresar un email")
            return False
        
        # Verificar si ya está en la lista
        email_lower = email.lower().strip()
        if any(email_lower == e.lower().strip() for e in emails_en_lista):
            print(f"[INFO] El email {email} ya esta en la lista de acceso total")
            return True
        
        # Agregar el email
        if contenido_array and not contenido_array.endswith(','):
            contenido_array += ','
        contenido_array += f'\n    "{email}",  # Acceso total sin restricciones\n'
        
        # Reconstruir el archivo
        nuevo_contenido = (
            contenido[:inicio] + 
            contenido_array + 
            contenido[pos-1:]
        )
        
        # Escribir el archivo
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        
        print()
        print("=" * 70)
        print("[OK] EMAIL AGREGADO EXITOSAMENTE")
        print("=" * 70)
        print()
        print(f"Tu email '{email}' ha sido agregado a la lista de acceso total.")
        print("Ahora tienes acceso COMPLETO a TODO sin restricciones.")
        print()
        print("IMPORTANTE:")
        print("  1. Reinicia el servidor para que los cambios surtan efecto")
        print("  2. Haz login nuevamente con tu email")
        print("  3. Ya no recibiras mas errores de 'Acceso Denegado'")
        print()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al modificar archivo: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import os
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    configurar_mi_usuario()


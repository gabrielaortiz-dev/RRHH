"""
Script para probar los endpoints de exportación
"""
import requests

print("="*60)
print("PROBANDO ENDPOINTS DE EXPORTACIÓN")
print("="*60)

base_url = "http://localhost:8000/api"

# 1. Probar PDF de empleados
print("\n1. Probando PDF de empleados...")
try:
    response = requests.get(f"{base_url}/reportes/empleados/export/pdf")
    if response.status_code == 200:
        print(f"   ✓ OK - Tamaño: {len(response.content)} bytes")
        print(f"   Content-Type: {response.headers.get('content-type')}")
    else:
        print(f"   ✗ ERROR {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ✗ ERROR: {str(e)}")

# 2. Probar Excel de empleados
print("\n2. Probando Excel de empleados...")
try:
    response = requests.get(f"{base_url}/reportes/empleados/export/excel")
    if response.status_code == 200:
        print(f"   ✓ OK - Tamaño: {len(response.content)} bytes")
        print(f"   Content-Type: {response.headers.get('content-type')}")
    else:
        print(f"   ✗ ERROR {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ✗ ERROR: {str(e)}")

# 3. Probar POST de asistencias
print("\n3. Probando PDF de asistencias...")
try:
    data = {
        "fecha_inicio": "2025-11-01",
        "fecha_fin": "2025-12-05",
        "id_empleado": None
    }
    response = requests.post(f"{base_url}/reportes/asistencias/export/pdf", json=data)
    if response.status_code == 200:
        print(f"   ✓ OK - Tamaño: {len(response.content)} bytes")
        print(f"   Content-Type: {response.headers.get('content-type')}")
    else:
        print(f"   ✗ ERROR {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ✗ ERROR: {str(e)}")

print("\n" + "="*60)
print("PRUEBA COMPLETADA")
print("="*60)

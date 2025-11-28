# 🚀 COMANDOS PARA POWERSHELL - PROYECTO RRHH

## ⚠️ IMPORTANTE: Comandos Correctos para PowerShell

En PowerShell, cuando ejecutas un archivo `.bat` desde la ubicación actual, **debes usar `.\` antes del nombre**.

---

## 📋 Opción 1: Usar los Scripts PowerShell (RECOMENDADO)

### Iniciar Backend:
```powershell
.\INICIAR_BACKEND.ps1
```

### Iniciar Frontend:
```powershell
.\INICIAR_FRONTEND.ps1
```

---

## 📋 Opción 2: Comandos Manuales en PowerShell

### 1. Iniciar Backend (Terminal 1):

**Desde la raíz del proyecto:**
```powershell
cd BACKEND
.\iniciar-servidor.bat
```

**O directamente con Python:**
```powershell
cd BACKEND
python main.py
```

**O con uvicorn:**
```powershell
cd BACKEND
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### 2. Iniciar Frontend (Terminal 2):

**Desde la raíz del proyecto:**
```powershell
cd RRHH
.\iniciar-servidor.bat
```

**O directamente con npm:**
```powershell
cd RRHH
npm start
```

**O con Angular CLI:**
```powershell
cd RRHH
ng serve --open
```

---

## 🔧 Comandos Corregidos para tu Error

### ❌ INCORRECTO (lo que intentaste):
```powershell
cd backend          # ← Carpeta incorrecta (minúscula)
cd BACKEND          # ← Error si ya estás en otra carpeta
iniciar-servidor.bat # ← Falta .\
```

### ✅ CORRECTO:
```powershell
# Opción 1: Desde la raíz del proyecto
cd "C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH"
cd BACKEND
.\iniciar-servidor.bat

# Opción 2: Ruta completa
cd "C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND"
.\iniciar-servidor.bat

# Opción 3: Directamente con Python
cd "C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND"
python main.py
```

---

## 📝 Verificar Ubicación Actual

Antes de ejecutar comandos, verifica dónde estás:

```powershell
# Ver directorio actual
pwd
# O
Get-Location

# Ver contenido del directorio
ls
# O
Get-ChildItem

# Ver si existe la carpeta BACKEND
Test-Path "BACKEND"
Test-Path "RRHH"
```

---

## 🎯 Comandos Rápidos desde la Raíz

### Si estás en la raíz del proyecto (`PROYECTO RRHH`):

**Backend:**
```powershell
cd BACKEND
.\iniciar-servidor.bat
```

**Frontend:**
```powershell
cd RRHH
.\iniciar-servidor.bat
```

---

## 🔍 Solución a tu Error Específico

El error que tuviste fue porque:
1. Estabas en una carpeta `backend` (minúscula) que no existe
2. PowerShell requiere `.\` antes de ejecutar archivos `.bat`

**Solución:**
```powershell
# 1. Ir a la raíz del proyecto
cd "C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH"

# 2. Verificar que estás en el lugar correcto
pwd
ls

# 3. Ir a BACKEND (mayúscula)
cd BACKEND

# 4. Ejecutar con .\
.\iniciar-servidor.bat
```

---

## 📦 Instalación de Dependencias (PowerShell)

### Backend:
```powershell
cd BACKEND
pip install -r requirements.txt
```

### Frontend:
```powershell
cd RRHH
npm install --legacy-peer-deps
```

---

## 🌐 URLs del Proyecto

| Servicio | URL |
|----------|-----|
| **Frontend** | http://localhost:4200 |
| **Backend API** | http://localhost:8000 |
| **Documentación API** | http://localhost:8000/docs |

---

## 💡 Tips para PowerShell

1. **Usa comillas si hay espacios en las rutas:**
   ```powershell
   cd "C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH"
   ```

2. **Usa `.\` para ejecutar archivos en el directorio actual:**
   ```powershell
   .\iniciar-servidor.bat
   ```

3. **Verifica la ubicación antes de ejecutar:**
   ```powershell
   pwd
   ```

4. **Las carpetas son case-sensitive en algunos casos, usa mayúsculas:**
   - ✅ `BACKEND` (correcto)
   - ❌ `backend` (puede no funcionar)

---

¡Listo! Ahora puedes ejecutar el proyecto correctamente desde PowerShell. 🎉


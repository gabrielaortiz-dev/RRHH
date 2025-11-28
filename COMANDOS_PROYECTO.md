# 🚀 COMANDOS PARA EJECUTAR EL PROYECTO RRHH

## 📋 Opción 1: Iniciar Todo Automáticamente (RECOMENDADO)

### Windows (Doble clic o desde terminal):
```bash
INICIAR_PROYECTO.bat
```

Este script:
- ✅ Inicia el backend automáticamente si no está corriendo
- ✅ Espera a que el backend esté listo
- ✅ Inicia el frontend Angular
- ✅ Abre el navegador automáticamente

---

## 📋 Opción 2: Iniciar Manualmente (Paso a Paso)

### Paso 1: Iniciar el Backend

**Opción A - Desde la carpeta BACKEND:**
```bash
cd BACKEND
iniciar-servidor.bat
```

**Opción B - Desde la raíz del proyecto:**
```bash
cd BACKEND
python main.py
```

**Opción C - Con uvicorn directamente:**
```bash
cd BACKEND
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en:
- 🌐 **API**: http://localhost:8000
- 📚 **Documentación**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

---

### Paso 2: Iniciar el Frontend

**Opción A - Desde la carpeta RRHH:**
```bash
cd RRHH
iniciar-servidor.bat
```

**Opción B - Con npm:**
```bash
cd RRHH
npm start
```

**Opción C - Con Angular CLI:**
```bash
cd RRHH
ng serve --open
```

El frontend estará disponible en:
- 🌐 **Aplicación**: http://localhost:4200

---

## 📋 Opción 3: Comandos desde PowerShell

### Iniciar Backend (en una terminal):
```powershell
cd BACKEND
python main.py
```

### Iniciar Frontend (en otra terminal):
```powershell
cd RRHH
ng serve --open
```

---

## 🔧 Verificar que Todo Funciona

### Verificar Backend:
```bash
# Desde cualquier terminal
curl http://localhost:8000/api/health

# O en el navegador:
http://localhost:8000/api/health
```

### Verificar Frontend:
```bash
# Abre en el navegador:
http://localhost:4200
```

---

## 📦 Instalación de Dependencias (Si es necesario)

### Backend:
```bash
cd BACKEND
pip install -r requirements.txt
```

### Frontend:
```bash
cd RRHH
npm install --legacy-peer-deps
```

---

## 🛑 Detener los Servidores

### Backend:
- Presiona `Ctrl+C` en la ventana del backend
- O cierra la ventana de la terminal

### Frontend:
- Presiona `Ctrl+C` en la ventana del frontend
- O cierra la ventana de la terminal

---

## 📝 Resumen de URLs

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:4200 | Aplicación Angular |
| Backend API | http://localhost:8000 | API FastAPI |
| API Docs | http://localhost:8000/docs | Documentación Swagger |
| API Health | http://localhost:8000/api/health | Estado del sistema |

---

## ⚠️ Notas Importantes

1. **El backend debe estar corriendo antes que el frontend** para que la aplicación funcione correctamente.

2. **Puertos:**
   - Backend: `8000`
   - Frontend: `4200`

3. **Si los puertos están ocupados:**
   - Backend: Cambia el puerto en `BACKEND/main.py`
   - Frontend: Usa `ng serve --port 4201` (o el puerto que prefieras)

4. **Credenciales de prueba** (si están configuradas):
   - Email: `admin@rrhh.com`
   - Password: `admin123`

---

## 🆘 Solución de Problemas

### Backend no inicia:
```bash
# Verificar Python
python --version

# Instalar dependencias
cd BACKEND
pip install -r requirements.txt
```

### Frontend no inicia:
```bash
# Verificar Node.js
node --version
npm --version

# Instalar dependencias
cd RRHH
npm install --legacy-peer-deps
```

### Error de CORS:
- Verifica que el backend tenga configurado CORS para `http://localhost:4200`
- Revisa `BACKEND/main.py` línea 33

---

¡Listo! 🎉 Tu proyecto está organizado y listo para ejecutarse.


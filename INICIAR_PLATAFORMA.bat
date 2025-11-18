@echo off
chcp 65001 >nul
echo ========================================
echo   INICIANDO PLATAFORMA DE RRHH
echo   Conectada a Base de Datos Backend
echo ========================================
echo.

echo [1/3] Verificando que el backend este corriendo...
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El backend NO esta corriendo en el puerto 8000
    echo.
    echo Por favor, inicia el backend primero:
    echo   1. Abre otra ventana de terminal
    echo   2. Ve a la carpeta BACKEND
    echo   3. Ejecuta: iniciar-servidor.bat
    echo.
    pause
    exit /b 1
)
echo [OK] Backend esta corriendo y conectado a la base de datos
echo.

echo [2/3] Verificando conexion con la base de datos...
python -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:8000/api/health'); d=json.loads(r.read().decode()); print('[OK] Estado:', d.get('status'), '- Base de datos:', d.get('database'))" 2>nul
echo.

echo [3/3] Iniciando servidor de Angular...
echo.
echo ========================================
echo   PLATAFORMA RRHH
echo ========================================
echo   Frontend: http://localhost:4200
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo La plataforma se abrira automaticamente en tu navegador
echo Presiona Ctrl+C para detener el servidor
echo.
cd /d "%~dp0"
ng serve --host 127.0.0.1 --port 4200 --open


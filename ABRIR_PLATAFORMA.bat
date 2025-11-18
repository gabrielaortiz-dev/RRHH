@echo off
chcp 65001 >nul
echo ========================================
echo   ABRIENDO PLATAFORMA RRHH
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Verificando backend...
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend no esta corriendo
    echo Por favor inicia el backend primero desde la carpeta BACKEND
    pause
    exit /b 1
)
echo [OK] Backend conectado
echo.

echo [2/2] Iniciando servidor Angular...
echo.
echo Abriendo en: http://127.0.0.1:4200
echo.
echo Espera a que compile (puede tardar 1-2 minutos)...
echo.

ng serve --host 127.0.0.1 --port 4200 --open

pause


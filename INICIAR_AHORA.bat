@echo off
echo ========================================
echo   INICIANDO SISTEMA RRHH
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    pause
    exit /b 1
)

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no esta instalado
    pause
    exit /b 1
)

echo [OK] Python y Node.js encontrados
echo.

REM Detener procesos en puertos 8000 y 4200
echo [1/3] Liberando puertos...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":4200"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [2/3] Iniciando Backend (puerto 8000)...
start "Backend RRHH" cmd /k "cd /d %~dp0BACKEND && python iniciar_servidor_mejorado.py"

timeout /t 5 /nobreak >nul

echo [3/3] Iniciando Frontend (puerto 4200)...
start "Frontend RRHH" cmd /k "cd /d %~dp0RRHH && npm start"

echo.
echo ========================================
echo   SERVIDORES INICIADOS
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:4200
echo.
echo Espera 30-60 segundos para que compile...
echo Luego abre: http://localhost:4200
echo.
echo Presiona cualquier tecla para cerrar esta ventana
echo (Los servidores seguiran corriendo en sus ventanas)
pause >nul


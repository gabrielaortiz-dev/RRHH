@echo off
echo ========================================
echo   SOLUCION RAPIDA - INICIAR RRHH
echo ========================================
echo.
echo Este script iniciara ambos servidores
echo.
pause

cd /d "%~dp0"

REM Iniciar Backend
echo Iniciando Backend...
start "Backend" cmd /k "cd /d %~dp0BACKEND && python main.py"

REM Esperar un poco
timeout /t 5 /nobreak >nul

REM Iniciar Frontend
echo Iniciando Frontend...
cd /d "%~dp0RRHH"
start "Frontend" cmd /k "npm start"

echo.
echo Servidores iniciados en ventanas separadas
echo.
echo Frontend: http://localhost:4200
echo Backend:  http://localhost:8000
echo.
echo Credenciales: admin@rrhh.com / admin123
echo.
pause


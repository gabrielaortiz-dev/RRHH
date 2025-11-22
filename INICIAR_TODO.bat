@echo off
echo ========================================
echo   INICIANDO SISTEMA RRHH COMPLETO
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    echo Por favor, instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Iniciar el backend en una nueva ventana
echo [INFO] Iniciando servidor backend...
start "Backend RRHH - Puerto 8000" cmd /k "cd /d %~dp0BACKEND && python main.py"
echo [OK] Servidor backend iniciado en http://localhost:8000
echo.

REM Esperar un momento para que el backend se inicie
timeout /t 3 /nobreak >nul

REM Verificar si Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no está instalado o no está en el PATH
    echo Por favor, instala Node.js desde https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
echo.

REM Iniciar el frontend
echo [INFO] Iniciando servidor frontend Angular...
echo [INFO] Esto puede tomar unos momentos...
echo.
cd /d %~dp0RRHH
call npm start

pause

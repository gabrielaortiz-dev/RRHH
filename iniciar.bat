@echo off
chcp 65001 >nul
title Sistema RRHH - Iniciar Todo
color 0A
cls
echo.
echo ========================================================================
echo                    INICIANDO SISTEMA RRHH
echo ========================================================================
echo.
echo Por favor espera, esto puede tomar unos minutos...
echo.

cd /d "%~dp0"

REM Verificar e iniciar Backend
echo [1/2] Verificando Backend...
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)" >nul 2>&1
if errorlevel 1 (
    echo        Iniciando Backend en nueva ventana...
    start "Backend RRHH" cmd /k "cd /d %~dp0BACKEND && iniciar-servidor.bat"
    echo        Esperando a que el backend este listo...
    timeout /t 5 /nobreak >nul
    set /a contador=0
    :esperar
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)" >nul 2>&1
    if errorlevel 1 (
        set /a contador+=1
        if %contador% lss 30 (
            timeout /t 2 /nobreak >nul
            goto esperar
        )
    )
    echo        [OK] Backend iniciado
) else (
    echo        [OK] Backend ya esta corriendo
)
echo.

REM Determinar directorio Angular
set "DIR_ANGULAR=%~dp0"
if exist "RRHH\angular.json" (
    set "DIR_ANGULAR=%~dp0RRHH"
)

REM Verificar dependencias
echo [2/2] Verificando Frontend...
cd /d "%DIR_ANGULAR%"
if not exist "node_modules" (
    echo        Instalando dependencias (esto puede tardar)...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

REM Iniciar Frontend
echo        Iniciando servidor Angular...
echo.
echo ========================================================================
echo                    SISTEMA INICIADO
echo ========================================================================
echo.
echo   Frontend: http://localhost:4200
echo   Backend:  http://localhost:8000
echo.
echo   Credenciales:
echo   Email:    admin@rrhh.com
echo   Password: admin123
echo.
echo   El navegador se abrira en unos segundos...
echo.
echo   Para detener: Presiona Ctrl+C
echo.
echo ========================================================================
echo.
timeout /t 3 /nobreak >nul

call ng serve --host 127.0.0.1 --port 4200 --open

pause

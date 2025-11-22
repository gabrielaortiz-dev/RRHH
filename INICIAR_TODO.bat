@echo off
chcp 65001 >nul
title Iniciar Sistema RRHH Completo
color 0B
echo ========================================
echo   INICIANDO SISTEMA RRHH COMPLETO
echo ========================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM ========================================================================
REM PASO 1: INICIAR BACKEND
REM ========================================================================
echo [1/2] Iniciando Backend (Puerto 8000)...
echo.

REM Verificar si el backend ya está corriendo
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Backend no esta corriendo. Iniciando...
    
    if not exist "BACKEND\iniciar-servidor.bat" (
        echo [ERROR] No se encuentra BACKEND\iniciar-servidor.bat
        pause
        exit /b 1
    )
    
    REM Iniciar backend en nueva ventana
    start "Backend RRHH - Puerto 8000" cmd /k "cd /d %~dp0BACKEND && iniciar-servidor.bat"
    
    REM Esperar a que el backend esté listo
    echo [INFO] Esperando a que el backend inicie...
    set /a intentos=0
    :esperar_backend
    timeout /t 3 /nobreak >nul
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)" >nul 2>&1
    if errorlevel 1 (
        set /a intentos+=1
        if %intentos% lss 20 (
            echo [INFO] Esperando backend... (%intentos%/20)
            goto esperar_backend
        ) else (
            echo [ERROR] El backend no respondio despues de 60 segundos
            pause
            exit /b 1
        )
    )
    echo [OK] Backend iniciado correctamente
) else (
    echo [OK] Backend ya esta corriendo
)
echo.

REM ========================================================================
REM PASO 2: INICIAR FRONTEND
REM ========================================================================
echo [2/2] Iniciando Frontend (Puerto 4200)...
echo.

REM Determinar directorio de Angular
set "ANGULAR_DIR=%~dp0"
if exist "RRHH\angular.json" (
    set "ANGULAR_DIR=%~dp0RRHH"
    echo [INFO] Proyecto Angular encontrado en: RRHH
) else if not exist "angular.json" (
    echo [ERROR] No se encuentra angular.json
    pause
    exit /b 1
) else (
    echo [INFO] Proyecto Angular encontrado en: raiz
)

REM Cambiar al directorio de Angular
cd /d "%ANGULAR_DIR%"

REM Verificar e instalar dependencias
if not exist "node_modules" (
    echo [INFO] Instalando dependencias de Node.js...
    echo Esto puede tomar varios minutos...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
) else (
    echo [OK] Dependencias encontradas
)
echo.

REM Iniciar servidor Angular
echo ========================================
echo   SISTEMA RRHH INICIADO
echo ========================================
echo   Frontend: http://localhost:4200
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo   Credenciales de prueba:
echo   Email:    admin@rrhh.com
echo   Password: admin123
echo.
echo   El navegador se abrira automaticamente...
echo.
echo   Para detener:
echo   - Presiona Ctrl+C en esta ventana (frontend)
echo   - Cierra la ventana del backend
echo.
timeout /t 3 /nobreak >nul

REM Iniciar Angular
call ng serve --host 127.0.0.1 --port 4200 --open

pause


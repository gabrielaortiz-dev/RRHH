@echo off
chcp 65001 >nul
title Iniciar Proyecto RRHH Completo
color 0B
echo ========================================
echo   INICIANDO PROYECTO RRHH COMPLETO
echo ========================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

echo [1/3] Verificando si el backend esta corriendo...
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)" >nul 2>&1
if errorlevel 1 (
    echo [INFO] El backend NO esta corriendo. Iniciando backend...
    echo.
    
    REM Verificar que existe la carpeta BACKEND
    if not exist "BACKEND\iniciar-servidor.bat" (
        echo [ERROR] No se encuentra BACKEND\iniciar-servidor.bat
        echo.
        pause
        exit /b 1
    )
    
    REM Iniciar el backend en una nueva ventana
    echo [INFO] Abriendo ventana del backend...
    start "Backend RRHH - Puerto 8000" cmd /k "cd /d %~dp0BACKEND && iniciar-servidor.bat"
    
    REM Esperar a que el backend esté listo
    echo [INFO] Esperando a que el backend inicie (esto puede tomar unos segundos)...
    set /a intentos=0
    :esperar_backend
    timeout /t 2 /nobreak >nul
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)" >nul 2>&1
    if errorlevel 1 (
        set /a intentos+=1
        if %intentos% lss 15 (
            echo [INFO] Esperando... (%intentos%/15)
            goto esperar_backend
        ) else (
            echo [ERROR] El backend no respondio despues de 30 segundos
            echo Por favor, verifica que Python y las dependencias esten instaladas
            echo.
            pause
            exit /b 1
        )
    )
    echo [OK] Backend iniciado correctamente
) else (
    echo [OK] Backend ya esta corriendo
)
echo.

echo [2/3] Verificando proyecto Angular...
REM Verificar que existe la carpeta RRHH
if not exist "RRHH\angular.json" (
    echo [ERROR] No se encuentra RRHH\angular.json
    echo.
    pause
    exit /b 1
)
echo [OK] Proyecto Angular encontrado en RRHH\
echo.

echo [3/3] Iniciando servidor Angular...
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
echo.
echo IMPORTANTE: Para detener todo:
echo   - Presiona Ctrl+C en esta ventana para detener el frontend
echo   - Cierra la ventana del backend para detener el servidor API
echo.
timeout /t 2 /nobreak >nul

REM Cambiar al directorio de Angular e iniciar
cd /d "%~dp0RRHH"
call ng serve --host 127.0.0.1 --port 4200 --open

pause


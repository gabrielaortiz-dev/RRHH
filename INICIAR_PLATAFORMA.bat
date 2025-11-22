@echo off
chcp 65001 >nul
title Iniciar Plataforma RRHH
color 0B
echo ========================================
echo   INICIANDO PLATAFORMA DE RRHH
echo   Conectada a Base de Datos Backend
echo ========================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

echo [1/4] Verificando si el backend esta corriendo...
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

echo [2/4] Verificando conexion con la base de datos...
python -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:8000/api/health', timeout=2); d=json.loads(r.read().decode()); print('[OK] Estado:', d.get('status'), '- Base de datos:', d.get('database'))" 2>nul
if errorlevel 1 (
    echo [ADVERTENCIA] No se pudo verificar la conexion a la base de datos
)
echo.

echo [3/4] Verificando proyecto Angular...
REM Determinar el directorio del proyecto Angular
set "ANGULAR_DIR=%~dp0"
if exist "RRHH\angular.json" (
    set "ANGULAR_DIR=%~dp0RRHH"
    echo [INFO] Proyecto Angular encontrado en subcarpeta RRHH
) else if not exist "angular.json" (
    echo [ERROR] No se encuentra angular.json en la raiz ni en RRHH
    echo.
    pause
    exit /b 1
) else (
    echo [INFO] Proyecto Angular encontrado en la raiz
)
echo [OK] Directorio Angular: %ANGULAR_DIR%
echo.

REM Cambiar al directorio de Angular
cd /d "%ANGULAR_DIR%"

echo [4/5] Verificando dependencias de Node.js...
if not exist "node_modules" (
    echo [INFO] node_modules no encontrado. Instalando dependencias...
    echo Esto puede tomar varios minutos, por favor espera...
    echo.
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo.
        echo [ERROR] Error al instalar las dependencias de Node.js
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencias de Node.js instaladas correctamente
) else (
    echo [OK] Dependencias de Node.js encontradas
)
echo.

echo [5/5] Iniciando servidor de Angular...
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
call ng serve --host 127.0.0.1 --port 4200 --open


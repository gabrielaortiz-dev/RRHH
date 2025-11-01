@echo off
title Iniciar Servidor RRHH
color 0A
echo.
echo ========================================================================
echo   INICIANDO SERVIDOR DE RECURSOS HUMANOS
echo ========================================================================
echo.
echo Por favor espera, esto puede tomar unos segundos...
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que estamos en el directorio correcto
if not exist "angular.json" (
    echo [ERROR] No se encuentra angular.json
    echo.
    echo Por favor, ejecuta este archivo desde la carpeta:
    echo C:\Users\GABRIELAORTIZ\Desktop\RRHH\RRHH
    echo.
    pause
    exit /b 1
)

if not exist "package.json" (
    echo [ERROR] No se encuentra package.json
    echo.
    echo Por favor, ejecuta este archivo desde la carpeta:
    echo C:\Users\GABRIELAORTIZ\Desktop\RRHH\RRHH
    echo.
    pause
    exit /b 1
)

echo [OK] Directorio correcto detectado
echo [OK] Archivos encontrados: angular.json, package.json
echo.
echo Iniciando servidor de desarrollo...
echo.
echo ========================================================================
echo   El navegador se abrira automaticamente en unos segundos
echo   URL: http://localhost:4200
echo.
echo   Para detener el servidor, presiona Ctrl+C
echo ========================================================================
echo.

REM Iniciar el servidor
call npm start

pause


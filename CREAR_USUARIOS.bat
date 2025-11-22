@echo off
chcp 65001 >nul
title Crear Usuarios de Ejemplo - RRHH
color 0B
echo ========================================
echo   CREANDO USUARIOS DE EJEMPLO
echo ========================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que existe la carpeta BACKEND
if not exist "BACKEND\crear_usuarios.py" (
    echo [ERROR] No se encuentra BACKEND\crear_usuarios.py
    echo.
    pause
    exit /b 1
)

echo [INFO] Ejecutando script de creacion de usuarios...
echo.
cd BACKEND
python crear_usuarios.py

if errorlevel 1 (
    echo.
    echo [ERROR] Error al ejecutar el script
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   PROCESO COMPLETADO
echo ========================================
echo.
echo Ahora puedes intentar iniciar sesion con las credenciales mostradas arriba
echo.
pause


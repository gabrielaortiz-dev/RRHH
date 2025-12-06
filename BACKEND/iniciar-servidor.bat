@echo off
echo ========================================
echo   Iniciando Servidor Backend - RRHH
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

REM Verificar si las dependencias están instaladas
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        pause
        exit /b 1
    )
)

echo [OK] Dependencias instaladas
echo.
echo ========================================
echo   Servidor iniciado en:
echo   http://localhost:8000
echo   Documentación: http://localhost:8000/docs
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar el servidor con el script mejorado
python iniciar_servidor_mejorado.py

if errorlevel 1 (
    echo.
    echo [ERROR] El servidor no pudo iniciarse correctamente
    echo.
    echo Verifica:
    echo 1. Que el puerto 8000 no esté en uso
    echo 2. Que todas las dependencias estén instaladas
    echo 3. Que no haya errores en main.py
    echo.
    pause
    exit /b 1
)

pause


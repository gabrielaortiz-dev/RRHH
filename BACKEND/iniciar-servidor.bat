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

REM Iniciar el servidor
python main.py

pause


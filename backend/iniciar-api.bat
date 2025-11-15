@echo off
echo ========================================
echo   Iniciando API del Sistema de RRHH
echo ========================================
echo.

cd /d %~dp0

if not exist ".env" (
    echo Archivo .env no encontrado.
    if exist ".env.example" (
        echo Creando .env desde .env.example...
        copy ".env.example" ".env" >nul
        echo Archivo .env creado. Por favor, revisa y ajusta los valores segun sea necesario.
    ) else (
        echo ADVERTENCIA: No se encontro .env.example. El sistema usara valores por defecto.
    )
    echo.
)

echo Verificando dependencias...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    echo.
)

echo Inicializando base de datos...
python database.py
echo.

echo Iniciando servidor Flask...
echo API disponible en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python app.py

pause


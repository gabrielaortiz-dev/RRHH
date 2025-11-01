@echo off
echo ====================================
echo   INICIANDO SERVIDOR RRHH
echo ====================================
echo.
cd /d "%~dp0"
echo Directorio actual: %CD%
echo.
echo Verificando angular.json...
if exist angular.json (
    echo ✓ angular.json encontrado
    echo.
    echo Iniciando servidor de desarrollo...
    echo Por favor, espera mientras se compila...
    echo.
    ng serve --open
) else (
    echo ✗ ERROR: angular.json no encontrado
    echo.
    echo Por favor, ejecuta este archivo desde la carpeta del proyecto.
    echo.
    pause
)


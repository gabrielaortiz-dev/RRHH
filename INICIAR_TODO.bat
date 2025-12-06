@echo off
echo ==================================================
echo    SISTEMA RRHH - INICIO COMPLETO
echo ==================================================
echo.
echo Este script iniciará:
echo   - Backend (FastAPI) en http://localhost:8000
echo   - Frontend (Angular) en http://localhost:4200
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0INICIAR_SISTEMA_COMPLETO.ps1"


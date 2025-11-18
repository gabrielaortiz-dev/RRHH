@echo off
chcp 65001 >nul
echo ========================================
echo   VERIFICACION DE CONEXION DEL BACKEND
echo ========================================
echo.

cd /d "%~dp0"
python verificar_conexion.py

echo.
pause


@echo off
echo ========================================
echo   REINICIANDO SERVIDOR DE DESARROLLO
echo ========================================
echo.
echo Deteniendo procesos anteriores...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Limpiando cache...
cd /d "%~dp0"
if exist node_modules\.cache rmdir /s /q node_modules\.cache
echo.
echo Iniciando servidor...
call npm start
pause


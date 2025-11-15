@echo off
echo ========================================
echo LIMPIANDO CACHE Y REINICIANDO SERVIDOR
echo ========================================
echo.

cd /d "C:\Users\GABRIELAORTIZ\Desktop\RRHH\RRHH"

echo [1/5] Deteniendo procesos Node.js...
taskkill /F /IM node.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Eliminando cache de Angular...
if exist ".angular\cache" rd /s /q ".angular\cache"
if exist "dist" rd /s /q "dist"

echo [3/5] Eliminando node_modules y reinstalando...
echo (ESTO PUEDE TOMAR 2-3 MINUTOS)
if exist "node_modules\.cache" rd /s /q "node_modules\.cache"

echo [4/5] Iniciando servidor...
start "SERVIDOR ANGULAR" cmd /k "npm start"

echo [5/5] Esperando compilacion (30 segundos)...
timeout /t 30 /nobreak >nul

echo.
echo ========================================
echo SERVIDOR LISTO!
echo ========================================
echo.
echo Ahora abriendo navegador en modo INCOGNITO...
echo.

REM Abrir en Chrome modo incognito
start chrome --incognito --new-window "http://localhost:4200/empleados/nuevo"

echo.
echo Si no abre Chrome, copia esta URL:
echo http://localhost:4200/empleados/nuevo
echo.
echo Y abrela en MODO INCOGNITO (Ctrl + Shift + N)
echo.
pause


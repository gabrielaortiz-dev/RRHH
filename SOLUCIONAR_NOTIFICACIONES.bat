@echo off
cls
echo ============================================
echo    SOLUCION DEFINITIVA - NOTIFICACIONES
echo ============================================
echo.
echo Este script va a:
echo 1. Detener el servidor
echo 2. Limpiar la cache
echo 3. Reiniciar el servidor
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo [PASO 1/4] Deteniendo servidor...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [PASO 2/4] Limpiando cache...
if exist .angular (
    rmdir /s /q .angular
    echo Cache eliminado
) else (
    echo No hay cache para eliminar
)

if exist dist (
    rmdir /s /q dist
    echo Dist eliminado
)

echo.
echo [PASO 3/4] Esperando...
timeout /t 2 /nobreak >nul

echo.
echo [PASO 4/4] Iniciando servidor...
echo.
echo IMPORTANTE: Espera a que compile completamente
echo Veras el mensaje: "Compiled successfully"
echo.
echo Una vez compilado:
echo 1. Ve a http://localhost:4200
echo 2. Presiona Ctrl + Shift + R
echo 3. Login: admin@rrhh.com / Admin123
echo 4. Busca la campana en la esquina superior derecha
echo 5. Haz clic en la campana
echo.
echo Presiona Ctrl+C para detener el servidor cuando quieras
echo.
npm start


@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "INICIAR_SISTEMA_SIEMPRE_DISPONIBLE.ps1"
pause


# Script para iniciar el Backend RRHH
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  INICIANDO BACKEND RRHH" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar al directorio del backend
$backendPath = Join-Path $PSScriptRoot "BACKEND"
if (-not (Test-Path $backendPath)) {
    Write-Host "✗ ERROR: No se encuentra la carpeta BACKEND" -ForegroundColor Red
    Write-Host "Directorio actual: $PWD" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Set-Location $backendPath

Write-Host "Directorio actual: $PWD" -ForegroundColor Gray
Write-Host ""

# Verificar que main.py existe
if (Test-Path "main.py") {
    Write-Host "✓ main.py encontrado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando servidor backend..." -ForegroundColor Yellow
    Write-Host "Servidor disponible en: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Documentación: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Gray
    Write-Host ""
    
    # Iniciar el servidor
    python main.py
} else {
    Write-Host "✗ ERROR: main.py no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}


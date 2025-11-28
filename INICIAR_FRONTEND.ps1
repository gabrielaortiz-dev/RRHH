# Script para iniciar el Frontend RRHH
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  INICIANDO FRONTEND RRHH" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar al directorio del frontend
$frontendPath = Join-Path $PSScriptRoot "RRHH"
if (-not (Test-Path $frontendPath)) {
    Write-Host "✗ ERROR: No se encuentra la carpeta RRHH" -ForegroundColor Red
    Write-Host "Directorio actual: $PWD" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Set-Location $frontendPath

Write-Host "Directorio actual: $PWD" -ForegroundColor Gray
Write-Host ""

# Verificar que angular.json existe
if (Test-Path "angular.json") {
    Write-Host "✓ angular.json encontrado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando servidor de desarrollo..." -ForegroundColor Yellow
    Write-Host "Por favor, espera mientras se compila..." -ForegroundColor Yellow
    Write-Host "Servidor disponible en: http://localhost:4200" -ForegroundColor Cyan
    Write-Host ""
    
    # Iniciar el servidor
    ng serve --open
} else {
    Write-Host "✗ ERROR: angular.json no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}


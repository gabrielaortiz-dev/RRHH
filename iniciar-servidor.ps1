# Script para iniciar el servidor de desarrollo RRHH
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  INICIANDO SERVIDOR RRHH" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar al directorio del script
Set-Location $PSScriptRoot

Write-Host "Directorio actual: $PWD" -ForegroundColor Gray
Write-Host ""

# Verificar que angular.json existe
if (Test-Path "angular.json") {
    Write-Host "✓ angular.json encontrado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando servidor de desarrollo..." -ForegroundColor Yellow
    Write-Host "Por favor, espera mientras se compila..." -ForegroundColor Yellow
    Write-Host ""
    
    # Iniciar el servidor
    ng serve --open
} else {
    Write-Host "✗ ERROR: angular.json no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, ejecuta este script desde la carpeta del proyecto." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}


# ============================================================================
# Script para Verificar y Corregir el Sistema RRHH
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   VERIFICACIÓN Y CORRECCIÓN DEL SISTEMA RRHH" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot
$backendPath = Join-Path $rootPath "BACKEND"

# Cambiar al directorio del backend
Set-Location $backendPath

Write-Host "[PASO 1] Verificando código Python..." -ForegroundColor Yellow
Write-Host ""

# Ejecutar verificación del código
python verificar_codigo.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Se encontraron errores en el código" -ForegroundColor Red
    Write-Host ""
    Write-Host "Intentando corregir automáticamente..." -ForegroundColor Yellow
    
    # Verificar dependencias
    Write-Host ""
    Write-Host "[PASO 2] Verificando dependencias..." -ForegroundColor Yellow
    
    python -c "import fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Instalando dependencias..." -ForegroundColor Yellow
        pip install -r requirements.txt
    } else {
        Write-Host "   ✓ Dependencias instaladas" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "[PASO 3] Verificando nuevamente..." -ForegroundColor Yellow
    python verificar_codigo.py
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Volver al directorio raíz
Set-Location $rootPath

Write-Host "¿Deseas iniciar el sistema ahora? (S/N)" -ForegroundColor Yellow
$respuesta = Read-Host

if ($respuesta -eq "S" -or $respuesta -eq "s") {
    Write-Host ""
    Write-Host "Iniciando sistema..." -ForegroundColor Green
    .\INICIAR_SISTEMA_ROBUSTO.ps1
} else {
    Write-Host ""
    Write-Host "Para iniciar el sistema más tarde, ejecuta:" -ForegroundColor Cyan
    Write-Host "  .\INICIAR_SISTEMA_ROBUSTO.ps1" -ForegroundColor White
    Write-Host ""
}


# Script mejorado para iniciar el Backend RRHH
# Con manejo de errores y verificación de puerto

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  INICIANDO BACKEND RRHH" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Función para verificar si Python está instalado
function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Función para verificar si el puerto está en uso
function Test-PortInUse {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Función para verificar dependencias
function Test-Dependencies {
    try {
        $fastapi = pip show fastapi 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠ Instalando dependencias..." -ForegroundColor Yellow
            pip install -r requirements.txt
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Dependencias instaladas correctamente" -ForegroundColor Green
                return $true
            } else {
                Write-Host "✗ Error al instalar dependencias" -ForegroundColor Red
                return $false
            }
        }
    } catch {
        Write-Host "⚠ Instalando dependencias..." -ForegroundColor Yellow
        pip install -r requirements.txt
        return $LASTEXITCODE -eq 0
    }
}

# Verificar Python
if (-not (Test-PythonInstalled)) {
    Write-Host "✗ ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor, instala Python desde https://www.python.org/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

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
Write-Host "Directorio: $PWD" -ForegroundColor Gray
Write-Host ""

# Verificar que main.py existe
if (-not (Test-Path "main.py")) {
    Write-Host "✗ ERROR: main.py no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "✓ main.py encontrado" -ForegroundColor Green

# Verificar dependencias
if (-not (Test-Dependencies)) {
    Write-Host "✗ ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Verificar si el puerto 8000 está en uso
Write-Host ""
Write-Host "Verificando puerto 8000..." -ForegroundColor Yellow
if (Test-PortInUse -Port 8000) {
    Write-Host "⚠ ADVERTENCIA: El puerto 8000 está en uso" -ForegroundColor Yellow
    Write-Host "Si hay otro servidor ejecutándose, ciérralo primero" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "¿Deseas continuar de todos modos? (S/N)"
    if ($response -ne "S" -and $response -ne "s") {
        Write-Host "Operación cancelada" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "✓ Puerto 8000 disponible" -ForegroundColor Green
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  INICIANDO SERVIDOR" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Servidor disponible en:" -ForegroundColor White
Write-Host "  • http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentación API:" -ForegroundColor White
Write-Host "  • http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  • http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Health Check:" -ForegroundColor White
Write-Host "  • http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "════════════════════════════════════" -ForegroundColor Gray
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host "════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

# Manejar Ctrl+C de forma elegante
$ErrorActionPreference = "Continue"
trap {
    Write-Host ""
    Write-Host "════════════════════════════════════" -ForegroundColor Gray
    Write-Host "Servidor detenido" -ForegroundColor Yellow
    Write-Host "════════════════════════════════════" -ForegroundColor Gray
    break
}

# Iniciar el servidor
try {
    python main.py
} catch {
    Write-Host ""
    Write-Host "✗ ERROR: El servidor se cerró inesperadamente" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}


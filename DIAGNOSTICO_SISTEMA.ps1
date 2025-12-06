# ============================================================================
# Script de Diagnóstico del Sistema RRHH
# Verifica el estado de backend y frontend
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   DIAGNÓSTICO DEL SISTEMA RRHH" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot
$backendPath = Join-Path $rootPath "BACKEND"
$frontendPath = Join-Path $rootPath "RRHH"
$errors = @()

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

function Test-PortInUse {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $null -ne $connection
    } catch {
        return $false
    }
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Test-HttpEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 5
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSeconds -UseBasicParsing -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# ============================================================================
# VERIFICACIÓN 1: REQUISITOS DEL SISTEMA
# ============================================================================

Write-Host "[1/6] Verificando requisitos del sistema..." -ForegroundColor Yellow

# Python
if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Python NO encontrado" -ForegroundColor Red
    $errors += "Python no está instalado o no está en el PATH"
}

# Node.js
if (Test-Command "node") {
    $nodeVersion = node --version 2>&1
    Write-Host "   ✓ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Node.js NO encontrado" -ForegroundColor Red
    $errors += "Node.js no está instalado o no está en el PATH"
}

# npm
if (Test-Command "npm") {
    $npmVersion = npm --version 2>&1
    Write-Host "   ✓ npm: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ npm NO encontrado" -ForegroundColor Red
    $errors += "npm no está instalado o no está en el PATH"
}

Write-Host ""

# ============================================================================
# VERIFICACIÓN 2: ESTRUCTURA DE CARPETAS
# ============================================================================

Write-Host "[2/6] Verificando estructura de carpetas..." -ForegroundColor Yellow

if (Test-Path $backendPath) {
    Write-Host "   ✓ Carpeta BACKEND encontrada" -ForegroundColor Green
} else {
    Write-Host "   ✗ Carpeta BACKEND NO encontrada" -ForegroundColor Red
    $errors += "Carpeta BACKEND no existe en: $rootPath"
}

if (Test-Path $frontendPath) {
    Write-Host "   ✓ Carpeta RRHH encontrada" -ForegroundColor Green
} else {
    Write-Host "   ✗ Carpeta RRHH NO encontrada" -ForegroundColor Red
    $errors += "Carpeta RRHH no existe en: $rootPath"
}

Write-Host ""

# ============================================================================
# VERIFICACIÓN 3: ARCHIVOS CRÍTICOS DEL BACKEND
# ============================================================================

Write-Host "[3/6] Verificando archivos del backend..." -ForegroundColor Yellow

$backendFiles = @(
    "main.py",
    "database.py",
    "models.py",
    "auth.py",
    "requirements.txt",
    "iniciar_servidor_mejorado.py"
)

foreach ($file in $backendFiles) {
    $filePath = Join-Path $backendPath $file
    if (Test-Path $filePath) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file NO encontrado" -ForegroundColor Red
        $errors += "Archivo faltante en backend: $file"
    }
}

Write-Host ""

# ============================================================================
# VERIFICACIÓN 4: DEPENDENCIAS DEL BACKEND
# ============================================================================

Write-Host "[4/6] Verificando dependencias del backend..." -ForegroundColor Yellow

Set-Location $backendPath
try {
    python -c "import fastapi" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ FastAPI instalado" -ForegroundColor Green
    } else {
        Write-Host "   ✗ FastAPI NO instalado" -ForegroundColor Red
        $errors += "FastAPI no está instalado. Ejecuta: pip install -r requirements.txt"
    }
    
    python -c "import uvicorn" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Uvicorn instalado" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Uvicorn NO instalado" -ForegroundColor Red
        $errors += "Uvicorn no está instalado. Ejecuta: pip install -r requirements.txt"
    }
    
    python -c "import bcrypt" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ bcrypt instalado" -ForegroundColor Green
    } else {
        Write-Host "   ✗ bcrypt NO instalado" -ForegroundColor Red
        $errors += "bcrypt no está instalado. Ejecuta: pip install -r requirements.txt"
    }
} catch {
    Write-Host "   ⚠ Error al verificar dependencias: $_" -ForegroundColor Yellow
}
Set-Location $rootPath

Write-Host ""

# ============================================================================
# VERIFICACIÓN 5: DEPENDENCIAS DEL FRONTEND
# ============================================================================

Write-Host "[5/6] Verificando dependencias del frontend..." -ForegroundColor Yellow

$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (Test-Path $nodeModulesPath) {
    Write-Host "   ✓ node_modules encontrado" -ForegroundColor Green
} else {
    Write-Host "   ✗ node_modules NO encontrado" -ForegroundColor Red
    $errors += "Dependencias de Node.js no instaladas. Ejecuta: cd RRHH && npm install"
}

$packageJsonPath = Join-Path $frontendPath "package.json"
if (Test-Path $packageJsonPath) {
    Write-Host "   ✓ package.json encontrado" -ForegroundColor Green
} else {
    Write-Host "   ✗ package.json NO encontrado" -ForegroundColor Red
    $errors += "package.json no encontrado en frontend"
}

Write-Host ""

# ============================================================================
# VERIFICACIÓN 6: ESTADO DE LOS SERVIDORES
# ============================================================================

Write-Host "[6/6] Verificando estado de los servidores..." -ForegroundColor Yellow

# Backend (Puerto 8000)
$backendRunning = Test-PortInUse -Port 8000
if ($backendRunning) {
    Write-Host "   ✓ Backend está corriendo en puerto 8000" -ForegroundColor Green
    
    # Verificar si responde HTTP
    $backendResponds = Test-HttpEndpoint -Url "http://localhost:8000/api/health"
    if ($backendResponds) {
        Write-Host "   ✓ Backend responde correctamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Backend está corriendo pero no responde a /api/health" -ForegroundColor Yellow
        $errors += "Backend no responde correctamente"
    }
} else {
    Write-Host "   ✗ Backend NO está corriendo (puerto 8000)" -ForegroundColor Red
    $errors += "Backend no está corriendo. Inicia con: cd BACKEND && python iniciar_servidor_mejorado.py"
}

# Frontend (Puerto 4200)
$frontendRunning = Test-PortInUse -Port 4200
if ($frontendRunning) {
    Write-Host "   ✓ Frontend está corriendo en puerto 4200" -ForegroundColor Green
    
    # Verificar si responde HTTP
    $frontendResponds = Test-HttpEndpoint -Url "http://localhost:4200"
    if ($frontendResponds) {
        Write-Host "   ✓ Frontend responde correctamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Frontend está corriendo pero no responde" -ForegroundColor Yellow
        $errors += "Frontend no responde correctamente"
    }
} else {
    Write-Host "   ✗ Frontend NO está corriendo (puerto 4200)" -ForegroundColor Red
    $errors += "Frontend no está corriendo. Inicia con: cd RRHH && npm start"
}

Write-Host ""

# ============================================================================
# RESUMEN Y RECOMENDACIONES
# ============================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   RESUMEN DEL DIAGNÓSTICO" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -eq 0) {
    Write-Host "✅ TODO ESTÁ CORRECTO" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ambos servidores deberían estar funcionando correctamente." -ForegroundColor Green
    Write-Host ""
    Write-Host "URLs:" -ForegroundColor Cyan
    Write-Host "  - Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "  - Frontend: http://localhost:4200" -ForegroundColor White
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
} else {
    Write-Host "❌ SE ENCONTRARON $($errors.Count) PROBLEMA(S)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Problemas detectados:" -ForegroundColor Yellow
    foreach ($error in $errors) {
        Write-Host "  • $error" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "SOLUCIONES:" -ForegroundColor Cyan
    Write-Host ""
    
    if ($errors -like "*Python*") {
        Write-Host "1. Instala Python desde https://www.python.org/" -ForegroundColor White
    }
    
    if ($errors -like "*Node.js*" -or $errors -like "*npm*") {
        Write-Host "2. Instala Node.js desde https://nodejs.org/" -ForegroundColor White
    }
    
    if ($errors -like "*FastAPI*" -or $errors -like "*Uvicorn*" -or $errors -like "*bcrypt*") {
        Write-Host "3. Instala dependencias del backend:" -ForegroundColor White
        Write-Host "   cd BACKEND" -ForegroundColor Gray
        Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
    }
    
    if ($errors -like "*node_modules*") {
        Write-Host "4. Instala dependencias del frontend:" -ForegroundColor White
        Write-Host "   cd RRHH" -ForegroundColor Gray
        Write-Host "   npm install" -ForegroundColor Gray
    }
    
    if ($errors -like "*Backend no está corriendo*") {
        Write-Host "5. Inicia el backend:" -ForegroundColor White
        Write-Host "   cd BACKEND" -ForegroundColor Gray
        Write-Host "   python iniciar_servidor_mejorado.py" -ForegroundColor Gray
    }
    
    if ($errors -like "*Frontend no está corriendo*") {
        Write-Host "6. Inicia el frontend:" -ForegroundColor White
        Write-Host "   cd RRHH" -ForegroundColor Gray
        Write-Host "   npm start" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "O usa el script automatizado:" -ForegroundColor Cyan
    Write-Host "   .\INICIAR_SISTEMA_ROBUSTO.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""


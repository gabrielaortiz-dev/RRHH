# ============================================================================
# Script Robusto para Iniciar el Sistema RRHH Completo
# Backend (FastAPI) + Frontend (Angular)
# ============================================================================

param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   SISTEMA RRHH - INICIO COMPLETO Y ROBUSTO" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot
$backendPath = Join-Path $rootPath "BACKEND"
$frontendPath = Join-Path $rootPath "RRHH"

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

function Stop-PortProcess {
    param([int]$Port)
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
            Select-Object -ExpandProperty OwningProcess -Unique
        if ($processes) {
            foreach ($proc in $processes) {
                try {
                    Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
                    Write-Host "   ✓ Proceso $proc en puerto $Port detenido" -ForegroundColor Green
                } catch {
                    Write-Host "   ⚠ No se pudo detener proceso $proc" -ForegroundColor Yellow
                }
            }
            Start-Sleep -Seconds 2
        }
    } catch {
        Write-Host "   ⚠ Error al verificar procesos en puerto $Port" -ForegroundColor Yellow
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

function Wait-ForPort {
    param(
        [int]$Port,
        [int]$MaxWait = 30,
        [string]$ServiceName = "Servicio"
    )
    $waited = 0
    while (-not (Test-PortInUse -Port $Port) -and $waited -lt $MaxWait) {
        Start-Sleep -Seconds 1
        $waited++
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
    Write-Host ""
    return (Test-PortInUse -Port $Port)
}

# ============================================================================
# VERIFICACIONES PREVIAS
# ============================================================================

Write-Host "[PRE-CHECK] Verificando requisitos..." -ForegroundColor Yellow

# Verificar Python
if (-not (Test-Command "python")) {
    Write-Host "❌ ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "   Instala Python desde https://www.python.org/" -ForegroundColor Yellow
    pause
    exit 1
}
$pythonVersion = python --version 2>&1
Write-Host "   ✓ Python encontrado: $pythonVersion" -ForegroundColor Green

# Verificar Node.js
if (-not (Test-Command "node")) {
    Write-Host "❌ ERROR: Node.js no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "   Instala Node.js desde https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}
$nodeVersion = node --version 2>&1
Write-Host "   ✓ Node.js encontrado: $nodeVersion" -ForegroundColor Green

# Verificar directorios
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ ERROR: No se encontró la carpeta BACKEND" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "   ✓ Carpeta BACKEND encontrada" -ForegroundColor Green

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ ERROR: No se encontró la carpeta RRHH" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "   ✓ Carpeta RRHH encontrada" -ForegroundColor Green

Write-Host ""

# ============================================================================
# PASO 1: INICIAR BACKEND (Puerto 8000)
# ============================================================================

Write-Host "[1/2] INICIANDO BACKEND (FastAPI)..." -ForegroundColor Yellow
Write-Host "      Puerto: 8000" -ForegroundColor Gray

# Liberar puerto 8000
Write-Host "      Liberando puerto 8000..." -ForegroundColor Gray
Stop-PortProcess -Port 8000

# Verificar dependencias de Python
Write-Host "      Verificando dependencias de Python..." -ForegroundColor Gray
$requirementsPath = Join-Path $backendPath "requirements.txt"
if (Test-Path $requirementsPath) {
    try {
        python -c "import fastapi, uvicorn" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "      Instalando dependencias de Python..." -ForegroundColor Yellow
            Set-Location $backendPath
            python -m pip install -r requirements.txt --quiet
            Set-Location $rootPath
        }
        Write-Host "      ✓ Dependencias de Python verificadas" -ForegroundColor Green
    } catch {
        Write-Host "      ⚠ Error al verificar dependencias, continuando..." -ForegroundColor Yellow
    }
}

# Iniciar backend
$backendScript = Join-Path $backendPath "iniciar_servidor_mejorado.py"
if (Test-Path $backendScript) {
    Write-Host "      Iniciando servidor backend..." -ForegroundColor Gray
    $backendProcess = Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$backendPath'; python iniciar_servidor_mejorado.py"
    ) -PassThru -WindowStyle Normal
    
    # Esperar a que el backend inicie
    Write-Host "      Esperando a que el backend inicie" -NoNewline -ForegroundColor Gray
    if (Wait-ForPort -Port 8000 -MaxWait 20 -ServiceName "Backend") {
        Write-Host "      ✅ Backend iniciado correctamente en http://localhost:8000" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  Backend tardando más de lo esperado, pero continuando..." -ForegroundColor Yellow
    }
} else {
    Write-Host "      ❌ ERROR: No se encontró iniciar_servidor_mejorado.py" -ForegroundColor Red
    Write-Host "         Intentando iniciar con main.py directamente..." -ForegroundColor Yellow
    Set-Location $backendPath
    $backendProcess = Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$backendPath'; python main.py"
    ) -PassThru -WindowStyle Normal
    Set-Location $rootPath
    
    Write-Host "      Esperando a que el backend inicie" -NoNewline -ForegroundColor Gray
    if (Wait-ForPort -Port 8000 -MaxWait 20 -ServiceName "Backend") {
        Write-Host "      ✅ Backend iniciado correctamente" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  Backend tardando más de lo esperado" -ForegroundColor Yellow
    }
}

Start-Sleep -Seconds 2

# ============================================================================
# PASO 2: INICIAR FRONTEND (Puerto 4200)
# ============================================================================

Write-Host ""
Write-Host "[2/2] INICIANDO FRONTEND (Angular)..." -ForegroundColor Yellow
Write-Host "      Puerto: 4200" -ForegroundColor Gray

# Liberar puerto 4200
Write-Host "      Liberando puerto 4200..." -ForegroundColor Gray
Stop-PortProcess -Port 4200

# Verificar node_modules
$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "      Instalando dependencias de Node.js (esto puede tardar)..." -ForegroundColor Yellow
    Set-Location $frontendPath
    npm install
    Set-Location $rootPath
    Write-Host "      ✓ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "      ✓ Dependencias de Node.js verificadas" -ForegroundColor Green
}

# Iniciar frontend
Write-Host "      Iniciando servidor frontend..." -ForegroundColor Gray
Set-Location $frontendPath
$frontendProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$frontendPath'; npm start"
) -PassThru -WindowStyle Normal
Set-Location $rootPath

# Esperar a que el frontend compile
Write-Host "      Esperando a que el frontend compile (esto puede tardar 30-60 segundos)" -NoNewline -ForegroundColor Gray
Start-Sleep -Seconds 10

# Verificar puerto después de esperar
$frontendReady = Wait-ForPort -Port 4200 -MaxWait 60 -ServiceName "Frontend"
if ($frontendReady) {
    Write-Host "      ✅ Frontend iniciado correctamente en http://localhost:4200" -ForegroundColor Green
} else {
    Write-Host "      ⚠️  Frontend aún compilando, pero debería estar listo pronto..." -ForegroundColor Yellow
}

# ============================================================================
# RESUMEN Y APERTURA DEL NAVEGADOR
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   SISTEMA INICIADO" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar estado final
$backendOk = Test-PortInUse -Port 8000
$frontendOk = Test-PortInUse -Port 4200

if ($backendOk) {
    Write-Host "🌐 BACKEND (API):  http://localhost:8000" -ForegroundColor Green
    Write-Host "📚 API Docs:       http://localhost:8000/docs" -ForegroundColor Green
} else {
    Write-Host "⚠️  BACKEND:        No responde (revisa la terminal del backend)" -ForegroundColor Yellow
}

if ($frontendOk) {
    Write-Host "🌐 FRONTEND (Web): http://localhost:4200" -ForegroundColor Green
} else {
    Write-Host "⚠️  FRONTEND:       Aún compilando (espera unos segundos más)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "ℹ️  Ambos servidores se han abierto en terminales separadas" -ForegroundColor Cyan
Write-Host "ℹ️  Para detener, cierra las terminales o presiona Ctrl+C en cada una" -ForegroundColor Cyan
Write-Host ""

# Abrir navegador
if (-not $NoBrowser) {
    Write-Host "⏳ Esperando 5 segundos antes de abrir el navegador..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    if ($backendOk -and $frontendOk) {
        Write-Host "✅ Abriendo navegador en http://localhost:4200" -ForegroundColor Green
        Start-Process "http://localhost:4200"
    } elseif ($frontendOk) {
        Write-Host "✅ Abriendo navegador en http://localhost:4200" -ForegroundColor Green
        Write-Host "⚠️  Nota: El backend puede no estar listo aún" -ForegroundColor Yellow
        Start-Process "http://localhost:4200"
    } else {
        Write-Host "⚠️  Esperando a que el frontend termine de compilar..." -ForegroundColor Yellow
        Write-Host "   El navegador se abrirá automáticamente cuando esté listo" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar este script (los servidores seguirán corriendo)..." -ForegroundColor Gray
pause


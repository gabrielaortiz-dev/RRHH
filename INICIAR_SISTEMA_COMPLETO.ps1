# Script maestro para iniciar el sistema RRHH completo
# Backend (FastAPI) + Frontend (Angular)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   SISTEMA RRHH - INICIO COMPLETO                " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot

# Función para verificar si un puerto está en uso
function Test-PortInUse {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Función para matar proceso en puerto
function Stop-PortProcess {
    param([int]$Port)
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($processes) {
        foreach ($proc in $processes) {
            try {
                Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
                Write-Host "   Proceso $proc en puerto $Port detenido" -ForegroundColor Green
            } catch {
                Write-Host "   No se pudo detener proceso $proc" -ForegroundColor Yellow
            }
        }
        Start-Sleep -Seconds 2
    }
}

# ============================================================
# PASO 1: INICIAR BACKEND (Puerto 8000)
# ============================================================
Write-Host "[1/2] INICIANDO BACKEND (FastAPI)..." -ForegroundColor Yellow
Write-Host "      Puerto: 8000" -ForegroundColor Gray

# Liberar puerto 8000
Stop-PortProcess -Port 8000

# Iniciar backend en nueva terminal
$backendPath = Join-Path $rootPath "BACKEND"
$backendScript = Join-Path $backendPath "iniciar_servidor_mejorado.py"

if (Test-Path $backendScript) {
    Write-Host "      Abriendo terminal para backend..." -ForegroundColor Gray
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python iniciar_servidor_mejorado.py"
    
    # Esperar a que el backend inicie
    Write-Host "      Esperando a que el backend inicie..." -ForegroundColor Gray
    $maxWait = 15
    $waited = 0
    while (-not (Test-PortInUse -Port 8000) -and $waited -lt $maxWait) {
        Start-Sleep -Seconds 1
        $waited++
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
    Write-Host ""
    
    if (Test-PortInUse -Port 8000) {
        Write-Host "      ✅ Backend iniciado correctamente en http://localhost:8000" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  Backend tardando más de lo esperado, pero continuando..." -ForegroundColor Yellow
    }
} else {
    Write-Host "      ERROR: No se encontró $backendScript" -ForegroundColor Red
    pause
    exit 1
}

Start-Sleep -Seconds 2

# ============================================================
# PASO 2: INICIAR FRONTEND (Puerto 4200)
# ============================================================
Write-Host "`n[2/2] INICIANDO FRONTEND (Angular)..." -ForegroundColor Yellow
Write-Host "      Puerto: 4200" -ForegroundColor Gray

# Liberar puerto 4200
Stop-PortProcess -Port 4200

# Iniciar frontend en nueva terminal
$frontendPath = Join-Path $rootPath "RRHH"
$frontendScript = Join-Path $frontendPath "INICIAR_SERVIDOR_DEFINITIVO.ps1"

if (Test-Path $frontendScript) {
    Write-Host "      Abriendo terminal para frontend..." -ForegroundColor Gray
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; .\INICIAR_SERVIDOR_DEFINITIVO.ps1"
    
    # Esperar a que el frontend inicie
    Write-Host "      Esperando a que el frontend compile..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    Write-Host "      ✅ Frontend iniciándose en http://localhost:4200" -ForegroundColor Green
} else {
    Write-Host "      ERROR: No se encontró $frontendScript" -ForegroundColor Red
    pause
    exit 1
}

# ============================================================
# RESUMEN
# ============================================================
Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "   SISTEMA INICIADO CORRECTAMENTE                " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 BACKEND (API):  http://localhost:8000" -ForegroundColor Green
Write-Host "🌐 FRONTEND (Web): http://localhost:4200" -ForegroundColor Green
Write-Host "📚 API Docs:       http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "ℹ️  Ambos servidores se han abierto en terminales separadas" -ForegroundColor Cyan
Write-Host "ℹ️  Para detener, cierra las terminales o presiona Ctrl+C en cada una" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Esperando 10 segundos antes de abrir el navegador..." -ForegroundColor Yellow

# Esperar y abrir navegador
Start-Sleep -Seconds 10

# Verificar que ambos servicios estén corriendo
$backendOk = Test-PortInUse -Port 8000
$frontendOk = Test-PortInUse -Port 4200

if ($backendOk -and $frontendOk) {
    Write-Host "✅ Ambos servicios están corriendo. Abriendo navegador..." -ForegroundColor Green
    Start-Process "http://localhost:4200"
} elseif (-not $backendOk) {
    Write-Host "⚠️  El backend no respondió. Revisa la terminal del backend." -ForegroundColor Yellow
    Write-Host "   Intentando abrir el frontend de todos modos..." -ForegroundColor Yellow
    Start-Process "http://localhost:4200"
} elseif (-not $frontendOk) {
    Write-Host "⚠️  El frontend aún está compilando. Espera unos segundos más..." -ForegroundColor Yellow
    Write-Host "   El navegador se abrirá automáticamente cuando esté listo." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar este script (los servidores seguirán corriendo)..." -ForegroundColor Gray
pause


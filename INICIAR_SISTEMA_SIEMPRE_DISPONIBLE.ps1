# ============================================================
# SCRIPT MAESTRO - SISTEMA SIEMPRE DISPONIBLE
# ============================================================
# Este script garantiza que tanto el BACKEND como el FRONTEND
# estén SIEMPRE corriendo y se reinicien automáticamente si se caen
# ============================================================

param(
    [int]$CheckInterval = 10,
    [int]$MaxRestartAttempts = 999
)

$ErrorActionPreference = "Continue"
$script:BackendProcess = $null
$script:FrontendProcess = $null
$script:BackendRestartCount = 0
$script:FrontendRestartCount = 0
$script:IsShuttingDown = $false
$script:StartTime = Get-Date
$script:RootPath = $PSScriptRoot

# Colores para mensajes
function Write-Header { param([string]$Text) Write-Host "`n========================================" -ForegroundColor Cyan; Write-Host $Text -ForegroundColor Cyan; Write-Host "========================================`n" -ForegroundColor Cyan }
function Write-Success { param([string]$Text) Write-Host "✓ $Text" -ForegroundColor Green }
function Write-Error { param([string]$Text) Write-Host "✗ $Text" -ForegroundColor Red }
function Write-Warning { param([string]$Text) Write-Host "⚠ $Text" -ForegroundColor Yellow }
function Write-Info { param([string]$Text) Write-Host "ℹ $Text" -ForegroundColor Cyan }

# Función para verificar si un puerto está en uso
function Test-Port {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $null -ne $connection
    } catch {
        return $false
    }
}

# Función para verificar si un servicio responde
function Test-ServiceHealth {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Función para limpiar procesos en un puerto
function Stop-PortProcesses {
    param([int]$Port)
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
            Select-Object -ExpandProperty OwningProcess -Unique
        
        foreach ($pid in $processes) {
            if ($pid -gt 0) {
                try {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                } catch {}
            }
        }
        Start-Sleep -Seconds 2
    } catch {}
}

# Función para iniciar el BACKEND
function Start-Backend {
    Write-Info "Iniciando BACKEND (FastAPI) en puerto 8000..."
    
    $backendPath = Join-Path $script:RootPath "BACKEND"
    Set-Location $backendPath
    
    # Verificar Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Python no está instalado"
            return $false
        }
        Write-Success "Python: $pythonVersion"
    } catch {
        Write-Error "Python no está instalado"
        return $false
    }
    
    # Limpiar puerto 8000
    Stop-PortProcesses -Port 8000
    
    # Iniciar backend
    try {
        $script:BackendProcess = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory $backendPath -PassThru -NoNewWindow
        
        if (-not $script:BackendProcess) {
            Write-Error "No se pudo iniciar el proceso del backend"
            return $false
        }
        
        Write-Success "Backend iniciado con PID: $($script:BackendProcess.Id)"
        
        # Esperar a que el backend esté listo
        Write-Info "Esperando a que el backend esté listo (máximo 30 segundos)..."
        
        $maxWait = 30
        $waited = 0
        $checkInterval = 2
        
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds $checkInterval
            $waited += $checkInterval
            
            # Verificar si el proceso sigue vivo
            try {
                if ($script:BackendProcess.HasExited) {
                    Write-Error "El proceso del backend terminó inesperadamente"
                    return $false
                }
            } catch {
                Write-Error "No se pudo verificar el proceso del backend"
                return $false
            }
            
            # Verificar si el servicio responde
            if (Test-ServiceHealth -Url "http://localhost:8000/api/health") {
                Write-Success "Backend iniciado correctamente en http://localhost:8000"
                return $true
            }
            
            Write-Info "Esperando... ($waited/$maxWait segundos)"
        }
        
        # Si llegamos aquí, verificar si el puerto está activo
        if (Test-Port -Port 8000) {
            Write-Info "Backend iniciado (puerto activo, puede estar inicializando)"
            return $true
        } else {
            Write-Error "Backend no respondió en el tiempo esperado"
            return $false
        }
        
    } catch {
        Write-Error "Error al iniciar el backend: $_"
        return $false
    }
}

# Función para iniciar el FRONTEND
function Start-Frontend {
    Write-Info "Iniciando FRONTEND (Angular) en puerto 4200..."
    
    $frontendPath = Join-Path $script:RootPath "RRHH"
    Set-Location $frontendPath
    
    # Verificar Node.js
    try {
        $nodeVersion = node --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Node.js no está instalado"
            return $false
        }
        Write-Success "Node.js: $nodeVersion"
    } catch {
        Write-Error "Node.js no está instalado"
        return $false
    }
    
    # Verificar dependencias
    if (-not (Test-Path "node_modules")) {
        Write-Warning "Instalando dependencias del frontend..."
        npm install --legacy-peer-deps
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error al instalar dependencias"
            return $false
        }
    }
    
    # Limpiar puerto 4200
    Stop-PortProcesses -Port 4200
    
    # Iniciar frontend
    try {
        $script:FrontendProcess = Start-Process -FilePath "npm" -ArgumentList "start" -WorkingDirectory $frontendPath -PassThru -NoNewWindow
        
        if (-not $script:FrontendProcess) {
            Write-Error "No se pudo iniciar el proceso del frontend"
            return $false
        }
        
        Write-Success "Frontend iniciado con PID: $($script:FrontendProcess.Id)"
        
        # Esperar a que el frontend esté listo
        Write-Info "Esperando a que el frontend compile (máximo 120 segundos)..."
        
        $maxWait = 120
        $waited = 0
        $checkInterval = 5
        
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds $checkInterval
            $waited += $checkInterval
            
            # Verificar si el proceso sigue vivo
            try {
                if ($script:FrontendProcess.HasExited) {
                    Write-Error "El proceso del frontend terminó inesperadamente"
                    return $false
                }
            } catch {
                Write-Error "No se pudo verificar el proceso del frontend"
                return $false
            }
            
            # Verificar si el servicio responde
            if (Test-ServiceHealth -Url "http://localhost:4200") {
                Write-Success "Frontend iniciado correctamente en http://localhost:4200"
                return $true
            }
            
            # Verificar si el puerto está activo
            if (Test-Port -Port 4200) {
                Write-Info "Frontend compilando... ($waited/$maxWait segundos)"
            } else {
                Write-Info "Esperando inicio del frontend... ($waited/$maxWait segundos)"
            }
        }
        
        # Si llegamos aquí, verificar si el puerto está activo
        if (Test-Port -Port 4200) {
            Write-Info "Frontend iniciado (puerto activo, puede estar compilando)"
            return $true
        } else {
            Write-Error "Frontend no respondió en el tiempo esperado"
            return $false
        }
        
    } catch {
        Write-Error "Error al iniciar el frontend: $_"
        return $false
    }
}

# Función para monitorear los servicios
function Start-Monitoring {
    Write-Header "MONITOREO ACTIVO - Los servicios se reiniciarán automáticamente si se caen"
    Write-Info "Intervalo de verificación: $CheckInterval segundos"
    Write-Info "Presiona Ctrl+C para detener todos los servicios"
    Write-Host ""
    
    while (-not $script:IsShuttingDown) {
        Start-Sleep -Seconds $CheckInterval
        
        # Verificar BACKEND
        $backendPortActive = Test-Port -Port 8000
        $backendResponding = Test-ServiceHealth -Url "http://localhost:8000/api/health"
        $backendProcessAlive = $false
        
        if ($script:BackendProcess) {
            try {
                $backendProcessAlive = -not $script:BackendProcess.HasExited
            } catch {
                $backendProcessAlive = $false
            }
        }
        
        if (-not $backendPortActive -or -not $backendResponding -or -not $backendProcessAlive) {
            $script:BackendRestartCount++
            
            if ($script:BackendRestartCount -gt $MaxRestartAttempts) {
                Write-Error "Número máximo de reintentos del backend alcanzado ($MaxRestartAttempts)"
            } else {
                Write-Warning "Backend no responde. Reiniciando... (Intento $script:BackendRestartCount)"
                
                # Detener proceso anterior
                if ($script:BackendProcess -and $backendProcessAlive) {
                    try {
                        $script:BackendProcess.Kill()
                        Start-Sleep -Seconds 2
                    } catch {}
                }
                
                # Reiniciar
                if (Start-Backend) {
                    Write-Success "Backend reiniciado exitosamente"
                    $script:BackendRestartCount = 0
                } else {
                    Write-Error "No se pudo reiniciar el backend"
                }
            }
        } else {
            if ($script:BackendRestartCount -gt 0) {
                $script:BackendRestartCount = 0
                Write-Success "Backend recuperado y funcionando correctamente"
            }
        }
        
        # Verificar FRONTEND
        $frontendPortActive = Test-Port -Port 4200
        $frontendResponding = Test-ServiceHealth -Url "http://localhost:4200"
        $frontendProcessAlive = $false
        
        if ($script:FrontendProcess) {
            try {
                $frontendProcessAlive = -not $script:FrontendProcess.HasExited
            } catch {
                $frontendProcessAlive = $false
            }
        }
        
        if (-not $frontendPortActive -or -not $frontendResponding -or -not $frontendProcessAlive) {
            $script:FrontendRestartCount++
            
            if ($script:FrontendRestartCount -gt $MaxRestartAttempts) {
                Write-Error "Número máximo de reintentos del frontend alcanzado ($MaxRestartAttempts)"
            } else {
                Write-Warning "Frontend no responde. Reiniciando... (Intento $script:FrontendRestartCount)"
                
                # Detener proceso anterior
                if ($script:FrontendProcess -and $frontendProcessAlive) {
                    try {
                        $script:FrontendProcess.Kill()
                        Start-Sleep -Seconds 2
                    } catch {}
                }
                
                # Reiniciar
                if (Start-Frontend) {
                    Write-Success "Frontend reiniciado exitosamente"
                    $script:FrontendRestartCount = 0
                } else {
                    Write-Error "No se pudo reiniciar el frontend"
                }
            }
        } else {
            if ($script:FrontendRestartCount -gt 0) {
                $script:FrontendRestartCount = 0
                Write-Success "Frontend recuperado y funcionando correctamente"
            }
        }
        
        # Mostrar estadísticas cada 5 minutos
        $elapsed = (Get-Date) - $script:StartTime
        if (($elapsed.TotalMinutes % 5) -lt ($CheckInterval / 60)) {
            Write-Info "Sistema estable. Tiempo activo: $($elapsed.ToString('hh\:mm\:ss'))"
            Write-Info "  Backend: $(if ($backendResponding) { '✓ OK' } else { '✗ ERROR' })"
            Write-Info "  Frontend: $(if ($frontendResponding) { '✓ OK' } else { '✗ ERROR' })"
        }
    }
}

# Función de limpieza
function Stop-AllServices {
    Write-Host ""
    Write-Warning "Deteniendo todos los servicios..."
    $script:IsShuttingDown = $true
    
    # Detener frontend
    if ($script:FrontendProcess) {
        try {
            if (-not $script:FrontendProcess.HasExited) {
                $script:FrontendProcess.Kill()
            }
            Write-Success "Frontend detenido"
        } catch {}
    }
    
    # Detener backend
    if ($script:BackendProcess) {
        try {
            if (-not $script:BackendProcess.HasExited) {
                $script:BackendProcess.Kill()
            }
            Write-Success "Backend detenido"
        } catch {}
    }
    
    # Limpiar puertos
    Stop-PortProcesses -Port 8000
    Stop-PortProcesses -Port 4200
    
    Write-Info "Limpieza completada"
}

# Registrar manejador de interrupción
[Console]::TreatControlCAsInput = $false
$null = Register-EngineEvent PowerShell.Exiting -Action {
    Stop-AllServices
}

# Manejar Ctrl+C
$Host.UI.RawUI.add_KeyDown({
    param($key)
    if ($key.VirtualKeyCode -eq 3) { # Ctrl+C
        Stop-AllServices
        exit 0
    }
})

# ============================================================
# INICIO DEL SCRIPT
# ============================================================

Clear-Host
Write-Header "SISTEMA RRHH - SIEMPRE DISPONIBLE"

# Verificar prerrequisitos
Write-Info "Verificando prerrequisitos..."

# Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python: $pythonVersion"
    } else {
        Write-Error "Python no está instalado"
        exit 1
    }
} catch {
    Write-Error "Python no está instalado"
    exit 1
}

# Node.js
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Node.js: $nodeVersion"
    } else {
        Write-Error "Node.js no está instalado"
        exit 1
    }
} catch {
    Write-Error "Node.js no está instalado"
    exit 1
}

Write-Host ""

# Iniciar servicios
Write-Header "INICIANDO SERVICIOS"

$backendStarted = Start-Backend
$frontendStarted = Start-Frontend

if ($backendStarted -and $frontendStarted) {
    Write-Host ""
    Write-Header "SISTEMA INICIADO CORRECTAMENTE"
    Write-Success "Backend:  http://localhost:8000"
    Write-Success "Frontend: http://localhost:4200"
    Write-Success "API Docs: http://localhost:8000/docs"
    Write-Host ""
    Write-Info "Los servicios se reiniciarán automáticamente si se caen"
    Write-Info "Presiona Ctrl+C para detener todos los servicios"
    Write-Host ""
    
    # Iniciar monitoreo
    try {
        Start-Monitoring
    } catch {
        Write-Error "Error en el monitoreo: $_"
    } finally {
        Stop-AllServices
    }
} else {
    Write-Error "No se pudieron iniciar todos los servicios"
    if (-not $backendStarted) {
        Write-Error "  - Backend no inició"
    }
    if (-not $frontendStarted) {
        Write-Error "  - Frontend no inició"
    }
    Stop-AllServices
    exit 1
}


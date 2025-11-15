# Script PowerShell para iniciar la API
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando API del Sistema de RRHH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Verificar si existe el archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "Archivo .env no encontrado." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "Creando .env desde .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "Archivo .env creado. Por favor, revisa y ajusta los valores según sea necesario." -ForegroundColor Green
    } else {
        Write-Host "ADVERTENCIA: No se encontró .env.example. El sistema usará valores por defecto." -ForegroundColor Red
    }
    Write-Host ""
}

# Verificar e instalar dependencias si es necesario
Write-Host "Verificando dependencias..." -ForegroundColor Yellow
$flaskInstalled = pip show Flask 2>$null
if (-not $flaskInstalled) {
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ""
}

# Inicializar base de datos
Write-Host "Inicializando base de datos..." -ForegroundColor Yellow
python database.py
Write-Host ""

# Iniciar servidor
Write-Host "Iniciando servidor Flask..." -ForegroundColor Green
Write-Host "API disponible en: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

python app.py


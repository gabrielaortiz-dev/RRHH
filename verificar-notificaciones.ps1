# Script de Verificación del Sistema de Notificaciones
# Ejecutar: .\verificar-notificaciones.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Verificando Sistema de Notificaciones" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$todosExisten = $true

# Lista de archivos que deben existir
$archivosNecesarios = @(
    "src\app\models\notification.model.ts",
    "src\app\services\notification.service.ts",
    "src\app\notifications\notification-panel.ts",
    "src\app\notifications\notification-panel.html",
    "src\app\notifications\notification-panel.css",
    "src\app\config\notification-settings\notification-settings.ts",
    "src\app\config\notification-settings\notification-settings.html",
    "src\app\config\notification-settings\notification-settings.css"
)

Write-Host "1. Verificando archivos creados..." -ForegroundColor Yellow
Write-Host ""

foreach ($archivo in $archivosNecesarios) {
    if (Test-Path $archivo) {
        Write-Host "  ✓ $archivo" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $archivo" -ForegroundColor Red
        $todosExisten = $false
    }
}

Write-Host ""

# Verificar archivos modificados
Write-Host "2. Verificando archivos modificados..." -ForegroundColor Yellow
Write-Host ""

$archivosModificados = @(
    "src\app\menu\menu.ts",
    "src\app\menu\menu.html",
    "src\app\services\employee.service.ts",
    "src\app\services\department.service.ts",
    "src\app\app.routes.ts"
)

foreach ($archivo in $archivosModificados) {
    if (Test-Path $archivo) {
        Write-Host "  ✓ $archivo" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $archivo (¡FALTA!)" -ForegroundColor Red
        $todosExisten = $false
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan

if ($todosExisten) {
    Write-Host "✓ TODOS LOS ARCHIVOS ESTÁN PRESENTES" -ForegroundColor Green
    Write-Host ""
    Write-Host "¿Deseas reiniciar el servidor ahora? (S/N)" -ForegroundColor Yellow
    $respuesta = Read-Host
    
    if ($respuesta -eq "S" -or $respuesta -eq "s") {
        Write-Host ""
        Write-Host "Deteniendo procesos en puerto 4200..." -ForegroundColor Yellow
        
        # Intentar detener procesos en puerto 4200
        $procesos = netstat -ano | Select-String ":4200" | ForEach-Object {
            $_.ToString().Split(' ')[-1]
        } | Select-Object -Unique
        
        foreach ($pid in $procesos) {
            if ($pid -match '^\d+$') {
                try {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-Host "  Proceso $pid detenido" -ForegroundColor Green
                } catch {
                    Write-Host "  No se pudo detener proceso $pid" -ForegroundColor Yellow
                }
            }
        }
        
        Write-Host ""
        Write-Host "Limpiando caché de Angular..." -ForegroundColor Yellow
        if (Test-Path ".angular") {
            Remove-Item -Recurse -Force .angular
            Write-Host "  ✓ Caché eliminado" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "Iniciando servidor..." -ForegroundColor Yellow
        Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Cyan
        Write-Host ""
        
        # Iniciar el servidor
        npm start
    } else {
        Write-Host ""
        Write-Host "Para reiniciar manualmente, ejecuta:" -ForegroundColor Yellow
        Write-Host "  npm start" -ForegroundColor White
        Write-Host ""
        Write-Host "Luego en el navegador:" -ForegroundColor Yellow
        Write-Host "  1. Presiona Ctrl + F5 para refrescar" -ForegroundColor White
        Write-Host "  2. Inicia sesión: admin@rrhh.com / Admin123" -ForegroundColor White
        Write-Host "  3. Busca el icono 🔔 en el header" -ForegroundColor White
    }
} else {
    Write-Host "✗ FALTAN ALGUNOS ARCHIVOS" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, verifica que todos los archivos se hayan creado correctamente." -ForegroundColor Yellow
    Write-Host "Revisa el documento INSTRUCCIONES_REINICIO.md para más detalles." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""


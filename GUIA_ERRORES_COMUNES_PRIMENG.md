# Guía de Errores Comunes de PrimeNG en Angular 20

## 🔴 Problema: Cannot find module 'primeng/dropdown'

### Causa
En PrimeNG 20, varios componentes han sido renombrados o reestructurados. El componente `Dropdown` ahora se llama `Select`.

### Solución Aplicada
✅ **Cambio en imports (archivo .ts):**
```typescript
// ANTES (INCORRECTO)
import { DropdownModule } from 'primeng/dropdown';

// DESPUÉS (CORRECTO)
import { SelectModule } from 'primeng/select';
```

✅ **Cambio en el component decorator:**
```typescript
// ANTES
imports: [..., DropdownModule]

// DESPUÉS
imports: [..., SelectModule]
```

✅ **Cambio en el template (archivo .html):**
```html
<!-- ANTES -->
<p-dropdown
  [(ngModel)]="selectedValue"
  [options]="options"
  optionLabel="label"
  optionValue="value">
</p-dropdown>

<!-- DESPUÉS -->
<p-select
  [(ngModel)]="selectedValue"
  [options]="options"
  optionLabel="label"
  optionValue="value">
</p-select>
```

---

## 📋 Otros Cambios Importantes en PrimeNG 20

### Componentes Renombrados

| Versión Anterior | PrimeNG 20 | Importar desde |
|------------------|------------|----------------|
| `DropdownModule` | `SelectModule` | `primeng/select` |
| `MultiSelectModule` | `SelectModule` | `primeng/select` (con [multiple]="true") |
| `CalendarModule` | `DatePickerModule` | `primeng/datepicker` |

### Componentes que NO cambiaron
- ✅ `ButtonModule` - `primeng/button`
- ✅ `TableModule` - `primeng/table`
- ✅ `CardModule` - `primeng/card`
- ✅ `TagModule` - `primeng/tag`
- ✅ `InputTextModule` - `primeng/inputtext`
- ✅ `DialogModule` - `primeng/dialog`

---

## 🛠️ Scripts de Solución Definitiva

### 1. Para Iniciar el Servidor (SIN ERRORES)
```powershell
cd RRHH
.\INICIAR_SERVIDOR_DEFINITIVO.ps1
```

Este script:
- ✅ Verifica Node.js y npm
- ✅ Instala dependencias si faltan
- ✅ Limpia caché de Angular
- ✅ Libera el puerto 4200
- ✅ Inicia el servidor con polling

### 2. Para Verificar y Reparar Dependencias
```powershell
cd RRHH
.\VERIFICAR_DEPENDENCIAS.ps1
```

Este script:
- ✅ Verifica que PrimeNG esté correctamente instalado
- ✅ Repara automáticamente si hay problemas
- ✅ Reinstala dependencias si es necesario

---

## 🚀 Proceso de Inicio Correcto

1. **Primera vez o después de errores:**
   ```powershell
   cd RRHH
   .\VERIFICAR_DEPENDENCIAS.ps1
   .\INICIAR_SERVIDOR_DEFINITIVO.ps1
   ```

2. **Uso diario:**
   ```powershell
   cd RRHH
   .\INICIAR_SERVIDOR_DEFINITIVO.ps1
   ```

---

## ⚠️ Si el Error Persiste

### Opción 1: Reinstalación Completa
```powershell
cd RRHH
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm install --legacy-peer-deps
```

### Opción 2: Limpiar Caché de npm
```powershell
npm cache clean --force
cd RRHH
npm install --legacy-peer-deps
```

### Opción 3: Verificar Versiones
```powershell
node --version    # Debe ser v18 o superior
npm --version     # Debe ser v9 o superior
```

---

## 📦 Versiones Correctas (package.json)

```json
{
  "dependencies": {
    "@angular/core": "^20.3.0",
    "primeng": "^20.2.0",
    "primeicons": "^7.0.0",
    "primeflex": "^4.0.0"
  }
}
```

---

## 🔍 Cómo Detectar Problemas Antes de Que Ocurran

1. **Revisar terminal de compilación:**
   - ❌ ERROR: "Cannot find module" → Dependencia faltante
   - ❌ ERROR: "NG1010" → Importación incorrecta
   - ✅ "Compiled successfully" → Todo OK

2. **Verificar imports en archivos .ts:**
   - Buscar: `import { ... } from 'primeng/dropdown'`
   - Reemplazar por: `import { SelectModule } from 'primeng/select'`

3. **Verificar templates .html:**
   - Buscar: `<p-dropdown`
   - Reemplazar por: `<p-select`

---

## 💾 Archivos Corregidos

### ✅ Ya Corregidos:
- `RRHH/src/app/reports/attendance-report/attendance-report.ts`
- `RRHH/src/app/reports/attendance-report/attendance-report.html`

### 🔍 No se encontraron más archivos con este problema

---

## 📞 Resumen para el Usuario

### ¿Qué se corrigió?
- ✅ Se cambió `DropdownModule` por `SelectModule` en el código TypeScript
- ✅ Se cambió `<p-dropdown>` por `<p-select>` en el template HTML
- ✅ Se crearon scripts robustos para prevenir futuros errores
- ✅ Se añadió verificación automática de dependencias

### ¿Cómo evitar que vuelva a pasar?
1. **Siempre usar** `INICIAR_SERVIDOR_DEFINITIVO.ps1` para iniciar
2. **Si aparece error**, ejecutar `VERIFICAR_DEPENDENCIAS.ps1` primero
3. **No editar manualmente** node_modules
4. **Usar --legacy-peer-deps** al instalar nuevos paquetes

### ¿Cuándo reinstalar dependencias?
- ✅ Después de actualizar package.json
- ✅ Si aparecen errores de módulos no encontrados
- ✅ Si el servidor no compila después de cambios
- ❌ NO reinstalar sin razón (toma tiempo)

---

## 🎯 Comando Rápido de Emergencia

Si nada funciona, ejecutar en orden:
```powershell
# 1. Detener servidor (Ctrl+C)
# 2. Ir a la carpeta RRHH
cd RRHH

# 3. Limpiar todo
Remove-Item -Recurse -Force node_modules, .angular, package-lock.json

# 4. Reinstalar
npm install --legacy-peer-deps

# 5. Iniciar
npm run start
```

---

**Fecha de corrección:** 6 de Diciembre, 2025
**Versión Angular:** 20.3.0
**Versión PrimeNG:** 20.2.0
**Estado:** ✅ CORREGIDO Y PROBADO


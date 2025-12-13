"""
Módulo para calcular nómina mensual en Honduras
Incluye cálculo de deducciones legales: IHSS, RAP, ISR
"""

from typing import Dict, List, Optional
from datetime import datetime
from models import BonificacionItem, DeduccionItem


def calcular_nomina_mensual(
    salario_base: float,
    bonificaciones: Optional[List[Dict]] = None,
    deducciones_adicionales: Optional[List[Dict]] = None,
    mes: Optional[int] = None,
    anio: Optional[int] = None
) -> Dict:
    """
    Calcula la nómina mensual para un empleado en Honduras
    
    Args:
        salario_base: Salario base del empleado
        bonificaciones: Lista de bonificaciones adicionales
        deducciones_adicionales: Lista de deducciones adicionales (además de las legales)
        mes: Mes de la nómina (opcional, para validaciones)
        anio: Año de la nómina (opcional, para validaciones)
    
    Returns:
        Dict con el desglose completo de la nómina:
        - salario_base
        - total_bonificaciones
        - salario_bruto (base + bonificaciones)
        - deducciones_legales (IHSS, RAP, ISR)
        - deducciones_adicionales
        - total_deducciones
        - salario_neto
        - detalle_deducciones_legales
        - detalle_bonificaciones
        - detalle_deducciones
    """
    
    # Validar salario base
    if salario_base <= 0:
        raise ValueError("El salario base debe ser mayor que cero")
    
    # Inicializar valores
    total_bonificaciones = 0.0
    detalle_bonificaciones = []
    
    # Calcular bonificaciones
    if bonificaciones:
        for bonif in bonificaciones:
            if isinstance(bonif, dict):
                monto = bonif.get('monto', 0)
            else:
                monto = bonif.monto if hasattr(bonif, 'monto') else 0
            
            if monto > 0:
                total_bonificaciones += monto
                detalle_bonificaciones.append({
                    'concepto': bonif.get('concepto', '') if isinstance(bonif, dict) else bonif.concepto,
                    'tipo': bonif.get('tipo') if isinstance(bonif, dict) else getattr(bonif, 'tipo', None),
                    'monto': monto,
                    'descripcion': bonif.get('descripcion') if isinstance(bonif, dict) else getattr(bonif, 'descripcion', None)
                })
    
    # Salario bruto (base + bonificaciones)
    salario_bruto = salario_base + total_bonificaciones
    
    # Calcular deducciones legales de Honduras
    deducciones_legales = calcular_deducciones_legales_honduras(salario_bruto)
    
    # Calcular deducciones adicionales
    total_deducciones_adicionales = 0.0
    detalle_deducciones = []
    
    if deducciones_adicionales:
        for deduc in deducciones_adicionales:
            if isinstance(deduc, dict):
                monto = deduc.get('monto', 0)
            else:
                monto = deduc.monto if hasattr(deduc, 'monto') else 0
            
            if monto > 0:
                total_deducciones_adicionales += monto
                detalle_deducciones.append({
                    'concepto': deduc.get('concepto', '') if isinstance(deduc, dict) else deduc.concepto,
                    'tipo': deduc.get('tipo') if isinstance(deduc, dict) else getattr(deduc, 'tipo', None),
                    'monto': monto,
                    'descripcion': deduc.get('descripcion') if isinstance(deduc, dict) else getattr(deduc, 'descripcion', None)
                })
    
    # Total de deducciones (legales + adicionales)
    total_deducciones = deducciones_legales['total'] + total_deducciones_adicionales
    
    # Salario neto
    salario_neto = max(0, salario_bruto - total_deducciones)  # No puede ser negativo
    
    return {
        'salario_base': round(salario_base, 2),
        'total_bonificaciones': round(total_bonificaciones, 2),
        'salario_bruto': round(salario_bruto, 2),
        'deducciones_legales': round(deducciones_legales['total'], 2),
        'deducciones_adicionales': round(total_deducciones_adicionales, 2),
        'total_deducciones': round(total_deducciones, 2),
        'salario_neto': round(salario_neto, 2),
        'detalle_deducciones_legales': deducciones_legales['detalle'],
        'detalle_bonificaciones': detalle_bonificaciones,
        'detalle_deducciones': detalle_deducciones
    }


def calcular_deducciones_legales_honduras(salario_bruto: float) -> Dict:
    """
    Calcula las deducciones legales obligatorias en Honduras
    
    Deducciones:
    - IHSS (Instituto Hondureño de Seguridad Social): 2.5% del empleado
    - RAP (Régimen de Ahorro Público): 1% del empleado
    - ISR (Impuesto sobre la Renta): Escalonado según tabla vigente
    
    Args:
        salario_bruto: Salario bruto (base + bonificaciones)
    
    Returns:
        Dict con total y detalle de deducciones legales
    """
    
    detalle = []
    total = 0.0
    
    # IHSS: 2.5% del salario bruto (máximo sobre base de L. 50,000.00)
    base_ihss = min(salario_bruto, 50000.00)  # Base máxima para IHSS
    ihss = base_ihss * 0.025
    detalle.append({
        'concepto': 'IHSS',
        'tipo': 'seguro_social',
        'monto': round(ihss, 2),
        'descripcion': f'Instituto Hondureño de Seguridad Social (2.5% sobre base de {base_ihss:,.2f})'
    })
    total += ihss
    
    # RAP: 1% del salario bruto (máximo sobre base de L. 50,000.00)
    base_rap = min(salario_bruto, 50000.00)  # Base máxima para RAP
    rap = base_rap * 0.01
    detalle.append({
        'concepto': 'RAP',
        'tipo': 'ahorro_publico',
        'monto': round(rap, 2),
        'descripcion': f'Régimen de Ahorro Público (1% sobre base de {base_rap:,.2f})'
    })
    total += rap
    
    # ISR: Impuesto sobre la Renta (escalonado)
    # Tabla ISR 2025 (Honduras) - Ejemplo simplificado
    # Rango 1: Hasta L. 10,000.00 - Exento
    # Rango 2: L. 10,000.01 - L. 20,000.00 - 15% sobre excedente
    # Rango 3: L. 20,000.01 - L. 50,000.00 - 20% sobre excedente
    # Rango 4: Más de L. 50,000.00 - 25% sobre excedente
    
    isr = 0.0
    if salario_bruto > 10000.00:
        if salario_bruto <= 20000.00:
            # 15% sobre el excedente de L. 10,000.00
            isr = (salario_bruto - 10000.00) * 0.15
        elif salario_bruto <= 50000.00:
            # L. 1,500.00 (15% de L. 10,000) + 20% sobre excedente de L. 20,000
            isr = 1500.00 + (salario_bruto - 20000.00) * 0.20
        else:
            # L. 7,500.00 (L. 1,500 + 20% de L. 30,000) + 25% sobre excedente de L. 50,000
            isr = 7500.00 + (salario_bruto - 50000.00) * 0.25
    
    if isr > 0:
        detalle.append({
            'concepto': 'ISR',
            'tipo': 'impuesto_renta',
            'monto': round(isr, 2),
            'descripcion': f'Impuesto sobre la Renta calculado según tabla vigente'
        })
        total += isr
    
    return {
        'total': round(total, 2),
        'detalle': detalle
    }


def calcular_nomina_empleado(
    id_empleado: int,
    mes: int,
    anio: int,
    salario_base: float,
    bonificaciones: Optional[List[Dict]] = None,
    deducciones_adicionales: Optional[List[Dict]] = None,
    db=None
) -> Dict:
    """
    Calcula la nómina completa para un empleado, incluyendo validaciones
    
    Args:
        id_empleado: ID del empleado
        mes: Mes de la nómina (1-12)
        anio: Año de la nómina
        salario_base: Salario base del empleado
        bonificaciones: Lista de bonificaciones
        deducciones_adicionales: Lista de deducciones adicionales
        db: Instancia de Database para consultas adicionales
    
    Returns:
        Dict con el cálculo completo de nómina
    """
    
    # Validaciones básicas
    if not (1 <= mes <= 12):
        raise ValueError("El mes debe estar entre 1 y 12")
    
    if not (2000 <= anio <= 2100):
        raise ValueError("El año debe estar entre 2000 y 2100")
    
    if salario_base <= 0:
        raise ValueError("El salario base debe ser mayor que cero")
    
    # Calcular nómina
    resultado = calcular_nomina_mensual(
        salario_base=salario_base,
        bonificaciones=bonificaciones,
        deducciones_adicionales=deducciones_adicionales,
        mes=mes,
        anio=anio
    )
    
    # Agregar información adicional
    resultado['id_empleado'] = id_empleado
    resultado['mes'] = mes
    resultado['anio'] = anio
    resultado['periodo'] = f"{mes:02d}/{anio}"
    
    return resultado


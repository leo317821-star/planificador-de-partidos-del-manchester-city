"""
=============================================================================
MÓDULO UTILS - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Este módulo contiene utilidades y funciones auxiliares:
- Funciones de validación y formateo de fechas
- Funciones de ayuda para entrada de usuario
=============================================================================
"""

from .fecha_utils import (
    validar_fecha,
    parsear_fecha,
    formatear_fecha,
    formatear_fecha_larga,
    calcular_diferencia_dias,
    obtener_rango_semana,
    fecha_en_rango,
    sumar_dias,
    validar_numero_positivo,
    validar_texto_no_vacio
)

__all__ = [
    # Funciones de fecha
    'validar_fecha',
    'parsear_fecha',
    'formatear_fecha',
    'formatear_fecha_larga',
    'calcular_diferencia_dias',
    'obtener_rango_semana',
    'fecha_en_rango',
    'sumar_dias',
    
    # Funciones de validación
    'validar_numero_positivo',
    'validar_texto_no_vacio'
]
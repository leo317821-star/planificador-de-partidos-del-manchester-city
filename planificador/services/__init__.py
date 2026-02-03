"""
=============================================================================
MÓDULO SERVICES - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Este módulo contiene los servicios del sistema:
- PlanificadorEventos: Motor principal de planificación
- Validador: Validación de restricciones y conflictos
- GestorPersistencia: Guardado y carga de datos en archivos
=============================================================================
"""

from .planificador import PlanificadorEventos
from .validador import Validador
from .persistencia import GestorPersistencia

__all__ = [
    'PlanificadorEventos',
    'Validador',
    'GestorPersistencia'
]
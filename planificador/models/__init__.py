"""
=============================================================================
MÓDULO MODELS - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Este módulo contiene las clases de dominio del sistema:
- Evento y Partido: Representan los eventos a planificar
- Recurso y Arbitro: Representan los recursos del sistema
- Restricciones: Reglas de validación del negocio
=============================================================================
"""

from .evento import Evento, Partido
from .recurso import Recurso, Arbitro, TipoArbitro
from .restricciones import (
    Restriccion, 
    RestriccionCoRequisito, 
    RestriccionExclusionMutua
)

__all__ = [
    # Eventos
    'Evento',
    'Partido',
    
    # Recursos
    'Recurso',
    'Arbitro',
    'TipoArbitro',
    
    # Restricciones
    'Restriccion',
    'RestriccionCoRequisito',
    'RestriccionExclusionMutua'
]
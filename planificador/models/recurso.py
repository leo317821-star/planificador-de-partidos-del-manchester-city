"""
=============================================================================
MÓDULO RECURSO - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Define las clases para representar recursos del sistema (árbitros).
=============================================================================
"""

from enum import Enum
from typing import Optional
import uuid


class TipoArbitro(Enum):
    """
    Enumeración de los tipos de árbitros disponibles.
    
    Cada partido requiere:
    - 1 Árbitro Principal
    - 2 Árbitros de Línea
    - 1 Cuarto Árbitro (reserva)
    """
    PRINCIPAL = "Árbitro Principal"
    LINEA = "Árbitro de Línea"
    CUARTO = "Cuarto Árbitro"


class Recurso:
    """
    Clase base para representar un recurso del sistema.
    
    Un recurso es cualquier activo finito, compartido y reutilizable
    que los eventos necesitan para llevarse a cabo.
    
    Attributes:
        id (str): Identificador único del recurso
        nombre (str): Nombre descriptivo del recurso
        descripcion (str): Descripción opcional del recurso
    """
    
    def __init__(self, nombre: str, descripcion: str = ""):
        """
        Inicializa un nuevo recurso.
        
        Args:
            nombre: Nombre descriptivo del recurso
            descripcion: Descripción opcional del recurso
        """
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.descripcion = descripcion
    
    def __str__(self) -> str:
        """Representación en cadena del recurso."""
        return self.nombre
    
    def __repr__(self) -> str:
        """Representación técnica del recurso."""
        return f"Recurso(id={self.id[:8]}..., nombre='{self.nombre}')"
    
    def __eq__(self, other) -> bool:
        """Compara dos recursos por su ID."""
        if isinstance(other, Recurso):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        """Hash basado en el ID del recurso."""
        return hash(self.id)
    
    def to_dict(self) -> dict:
        """
        Convierte el recurso a diccionario para serialización JSON.
        
        Returns:
            dict: Representación del recurso como diccionario
        """
        return {
            'id': self.id,
            'tipo_clase': self.__class__.__name__,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Recurso':
        """
        Crea un recurso desde un diccionario.
        
        Args:
            data: Diccionario con los datos del recurso
            
        Returns:
            Recurso: Nueva instancia del recurso
        """
        recurso = cls(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', '')
        )
        recurso.id = data['id']
        return recurso


class Arbitro(Recurso):
    """
    Representa un árbitro de fútbol.
    
    Los árbitros son recursos especiales con las siguientes restricciones:
    - Requieren 7 días de descanso entre partidos
    - No pueden estar en dos partidos la misma semana
    
    Attributes:
        tipo (TipoArbitro): Tipo de árbitro (Principal, Línea, Cuarto)
        nacionalidad (str): País de origen del árbitro
        experiencia_anios (int): Años de experiencia como árbitro
    """
    
    # Días de descanso requeridos entre partidos
    DIAS_DESCANSO_REQUERIDOS = 7
    
    def __init__(self, nombre: str, tipo: TipoArbitro, 
                 nacionalidad: str = "Inglaterra", 
                 experiencia_anios: int = 0):
        """
        Inicializa un nuevo árbitro.
        
        Args:
            nombre: Nombre completo del árbitro
            tipo: Tipo de árbitro (Principal, Línea, Cuarto)
            nacionalidad: País de origen (default: Inglaterra)
            experiencia_anios: Años de experiencia (default: 0)
        """
        descripcion = f"{tipo.value} - {nacionalidad}"
        super().__init__(nombre, descripcion)
        self.tipo = tipo
        self.nacionalidad = nacionalidad
        self.experiencia_anios = experiencia_anios
    
    def __str__(self) -> str:
        """Representación en cadena del árbitro."""
        return f"{self.nombre} ({self.tipo.value})"
    
    def __repr__(self) -> str:
        """Representación técnica del árbitro."""
        return f"Arbitro(nombre='{self.nombre}', tipo={self.tipo.value})"
    
    def obtener_info_completa(self) -> str:
        """
        Retorna información completa del árbitro.
        
        Returns:
            str: Información detallada del árbitro
        """
        return (
            f"👨‍⚖️ {self.nombre}\n"
            f"   Tipo: {self.tipo.value}\n"
            f"   Nacionalidad: {self.nacionalidad}\n"
            f"   Experiencia: {self.experiencia_anios} años\n"
            f"   Descanso requerido: {self.DIAS_DESCANSO_REQUERIDOS} días entre partidos"
        )
    
    def es_tipo(self, tipo: TipoArbitro) -> bool:
        """
        Verifica si el árbitro es de un tipo específico.
        
        Args:
            tipo: Tipo de árbitro a verificar
            
        Returns:
            bool: True si el árbitro es del tipo especificado
        """
        return self.tipo == tipo
    
    def to_dict(self) -> dict:
        """
        Convierte el árbitro a diccionario para serialización JSON.
        
        Returns:
            dict: Representación del árbitro como diccionario
        """
        data = super().to_dict()
        data['tipo_arbitro'] = self.tipo.value
        data['nacionalidad'] = self.nacionalidad
        data['experiencia_anios'] = self.experiencia_anios
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Arbitro':
        """
        Crea un árbitro desde un diccionario.
        
        Args:
            data: Diccionario con los datos del árbitro
            
        Returns:
            Arbitro: Nueva instancia del árbitro
        """
        # Mapear el valor del tipo al enum
        tipo_map = {t.value: t for t in TipoArbitro}
        tipo = tipo_map.get(data.get('tipo_arbitro'), TipoArbitro.PRINCIPAL)
        
        arbitro = cls(
            nombre=data['nombre'],
            tipo=tipo,
            nacionalidad=data.get('nacionalidad', 'Inglaterra'),
            experiencia_anios=data.get('experiencia_anios', 0)
        )
        arbitro.id = data['id']
        return arbitro
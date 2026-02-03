"""
=============================================================================
MÓDULO EVENTO - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Define las clases para representar eventos (partidos de fútbol).
=============================================================================
"""

from datetime import datetime
from typing import List, Optional
import uuid


class Evento:
    """
    Clase base para representar un evento que consume recursos.
    
    Un evento es una actividad planificada en el tiempo que requiere
    la asignación de recursos específicos para llevarse a cabo.
    
    Attributes:
        id (str): Identificador único del evento
        nombre (str): Nombre descriptivo del evento
        fecha_inicio (datetime): Fecha y hora de inicio
        fecha_fin (datetime): Fecha y hora de finalización
        recursos (List): Lista de recursos asignados al evento
    """
    
    def __init__(self, nombre: str, fecha_inicio: datetime, 
                 fecha_fin: datetime, recursos: List = None):
        """
        Inicializa un nuevo evento.
        
        Args:
            nombre: Nombre descriptivo del evento
            fecha_inicio: Fecha y hora de inicio del evento
            fecha_fin: Fecha y hora de finalización del evento
            recursos: Lista opcional de recursos asignados
        """
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.recursos = recursos or []
    
    def __str__(self) -> str:
        """Representación en cadena del evento."""
        return f"{self.nombre} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"
    
    def __repr__(self) -> str:
        """Representación técnica del evento."""
        return f"Evento(id={self.id[:8]}..., nombre='{self.nombre}')"
    
    def __eq__(self, other) -> bool:
        """Compara dos eventos por su ID."""
        if isinstance(other, Evento):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        """Hash basado en el ID del evento."""
        return hash(self.id)
    
    def obtener_detalles(self) -> str:
        """
        Retorna una representación detallada del evento.
        
        Returns:
            str: Cadena con todos los detalles del evento
        """
        detalles = [
            f"\n{'='*50}",
            f"📌 DETALLES DEL EVENTO",
            f"{'='*50}",
            f"\nNombre: {self.nombre}",
            f"ID: {self.id[:8]}...",
            f"\n📅 HORARIO:",
            f"   Inicio: {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}",
            f"   Fin: {self.fecha_fin.strftime('%d/%m/%Y %H:%M')}",
            f"   Duración: {self._calcular_duracion()}",
            f"\n📦 RECURSOS ASIGNADOS ({len(self.recursos)}):"
        ]
        
        if self.recursos:
            for recurso in self.recursos:
                detalles.append(f"   • {recurso}")
        else:
            detalles.append("   (Sin recursos asignados)")
        
        detalles.append(f"\n{'='*50}")
        
        return "\n".join(detalles)
    
    def _calcular_duracion(self) -> str:
        """
        Calcula la duración del evento en formato legible.
        
        Returns:
            str: Duración en formato "X horas Y minutos"
        """
        diferencia = self.fecha_fin - self.fecha_inicio
        horas = diferencia.seconds // 3600
        minutos = (diferencia.seconds % 3600) // 60
        
        if horas > 0 and minutos > 0:
            return f"{horas} hora(s) {minutos} minuto(s)"
        elif horas > 0:
            return f"{horas} hora(s)"
        else:
            return f"{minutos} minuto(s)"
    
    def se_superpone_con(self, otra_fecha_inicio: datetime, 
                         otra_fecha_fin: datetime) -> bool:
        """
        Verifica si este evento se superpone con otro intervalo de tiempo.
        
        Dos intervalos se superponen si NO se cumple que uno termine
        antes de que el otro empiece.
        
        Args:
            otra_fecha_inicio: Inicio del otro intervalo
            otra_fecha_fin: Fin del otro intervalo
            
        Returns:
            bool: True si hay superposición, False en caso contrario
        """
        # No hay superposición si:
        # - Este evento termina antes de que el otro empiece, O
        # - Este evento empieza después de que el otro termine
        return not (self.fecha_fin <= otra_fecha_inicio or 
                    self.fecha_inicio >= otra_fecha_fin)
    
    def contiene_recurso(self, recurso_id: str) -> bool:
        """
        Verifica si un recurso está asignado a este evento.
        
        Args:
            recurso_id: ID del recurso a buscar
            
        Returns:
            bool: True si el recurso está asignado
        """
        return any(r.id == recurso_id for r in self.recursos)
    
    def agregar_recurso(self, recurso) -> bool:
        """
        Agrega un recurso al evento si no está ya asignado.
        
        Args:
            recurso: Recurso a agregar
            
        Returns:
            bool: True si se agregó, False si ya existía
        """
        if not self.contiene_recurso(recurso.id):
            self.recursos.append(recurso)
            return True
        return False
    
    def remover_recurso(self, recurso_id: str) -> bool:
        """
        Remueve un recurso del evento.
        
        Args:
            recurso_id: ID del recurso a remover
            
        Returns:
            bool: True si se removió, False si no existía
        """
        for i, recurso in enumerate(self.recursos):
            if recurso.id == recurso_id:
                self.recursos.pop(i)
                return True
        return False
    
    def to_dict(self) -> dict:
        """
        Convierte el evento a diccionario para serialización JSON.
        
        Returns:
            dict: Representación del evento como diccionario
        """
        return {
            'id': self.id,
            'tipo': self.__class__.__name__,
            'nombre': self.nombre,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat(),
            'recursos_ids': [r.id for r in self.recursos]
        }
    
    @classmethod
    def from_dict(cls, data: dict, recursos_map: dict) -> 'Evento':
        """
        Crea un evento desde un diccionario.
        
        Args:
            data: Diccionario con los datos del evento
            recursos_map: Diccionario de recursos {id: recurso}
            
        Returns:
            Evento: Nueva instancia del evento
        """
        evento = cls(
            nombre=data['nombre'],
            fecha_inicio=datetime.fromisoformat(data['fecha_inicio']),
            fecha_fin=datetime.fromisoformat(data['fecha_fin']),
            recursos=[
                recursos_map[rid] 
                for rid in data.get('recursos_ids', []) 
                if rid in recursos_map
            ]
        )
        evento.id = data['id']
        return evento


class Partido(Evento):
    """
    Representa un partido de fútbol en el Etihad Stadium.
    
    Extiende la clase Evento con información específica de partidos:
    equipos local y visitante.
    
    Attributes:
        equipo_local (str): Nombre del equipo local (Manchester City)
        equipo_visitante (str): Nombre del equipo visitante
    """
    
    # Duración estándar de un partido en horas (90 min + descanso + extras)
    DURACION_ESTANDAR_HORAS = 2
    
    def __init__(self, equipo_local: str, equipo_visitante: str,
                 fecha_inicio: datetime, fecha_fin: datetime, 
                 recursos: List = None):
        """
        Inicializa un nuevo partido.
        
        Args:
            equipo_local: Nombre del equipo local
            equipo_visitante: Nombre del equipo visitante
            fecha_inicio: Fecha y hora de inicio del partido
            fecha_fin: Fecha y hora de finalización del partido
            recursos: Lista opcional de recursos (árbitros)
        """
        nombre = f"{equipo_local} vs {equipo_visitante}"
        super().__init__(nombre, fecha_inicio, fecha_fin, recursos)
        self.equipo_local = equipo_local
        self.equipo_visitante = equipo_visitante
    
    def __str__(self) -> str:
        """Representación en cadena del partido."""
        return f"⚽ {self.nombre} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def obtener_detalles(self) -> str:
        """
        Retorna una representación detallada del partido.
        
        Returns:
            str: Cadena con todos los detalles del partido
        """
        # Importación local para evitar dependencia circular
        from .recurso import TipoArbitro
        
        lineas = [
            f"\n{'='*55}",
            f"⚽ PARTIDO DE FÚTBOL - ETIHAD STADIUM",
            f"{'='*55}",
            f"\n🏠 Equipo Local:     {self.equipo_local}",
            f"✈️  Equipo Visitante: {self.equipo_visitante}",
            f"\n📅 FECHA Y HORA:",
            f"   Fecha: {self.fecha_inicio.strftime('%d/%m/%Y')}",
            f"   Hora:  {self.fecha_inicio.strftime('%H:%M')} - {self.fecha_fin.strftime('%H:%M')}",
            f"\n👨‍⚖️ EQUIPO ARBITRAL:",
            f"{'-'*35}"
        ]
        
        # Organizar árbitros por tipo
        arbitros_por_tipo = {
            'Árbitro Principal': [],
            'Árbitro de Línea': [],
            'Cuarto Árbitro': []
        }
        
        for recurso in self.recursos:
            if hasattr(recurso, 'tipo'):
                tipo = recurso.tipo.value
                if tipo in arbitros_por_tipo:
                    arbitros_por_tipo[tipo].append(recurso.nombre)
        
        # Mostrar árbitros en orden
        for tipo in ['Árbitro Principal', 'Árbitro de Línea', 'Cuarto Árbitro']:
            arbitros = arbitros_por_tipo[tipo]
            if arbitros:
                for nombre in arbitros:
                    lineas.append(f"   {tipo}: {nombre}")
            else:
                lineas.append(f"   {tipo}: (No asignado)")
        
        lineas.append(f"\n{'='*55}")
        
        return "\n".join(lineas)
    
    def to_dict(self) -> dict:
        """
        Convierte el partido a diccionario para serialización JSON.
        
        Returns:
            dict: Representación del partido como diccionario
        """
        data = super().to_dict()
        data['equipo_local'] = self.equipo_local
        data['equipo_visitante'] = self.equipo_visitante
        return data
    
    @classmethod
    def from_dict(cls, data: dict, recursos_map: dict) -> 'Partido':
        """
        Crea un partido desde un diccionario.
        
        Args:
            data: Diccionario con los datos del partido
            recursos_map: Diccionario de recursos {id: recurso}
            
        Returns:
            Partido: Nueva instancia del partido
        """
        partido = cls(
            equipo_local=data['equipo_local'],
            equipo_visitante=data['equipo_visitante'],
            fecha_inicio=datetime.fromisoformat(data['fecha_inicio']),
            fecha_fin=datetime.fromisoformat(data['fecha_fin']),
            recursos=[
                recursos_map[rid] 
                for rid in data.get('recursos_ids', []) 
                if rid in recursos_map
            ]
        )
        partido.id = data['id']
        return partido
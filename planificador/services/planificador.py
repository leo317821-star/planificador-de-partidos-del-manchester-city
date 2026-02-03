"""
=============================================================================
MÓDULO PLANIFICADOR - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Motor principal de planificación de eventos.
Gestiona el calendario, recursos y coordina las validaciones.
=============================================================================
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any

from models.evento import Evento, Partido
from models.recurso import Recurso, Arbitro, TipoArbitro
from models.restricciones import (
    RestriccionCoRequisito,
    RestriccionExclusionMutua,
    RestriccionDescansoEstadio,
    ValidadorRestricciones,
    crear_validador_estadio
)
from .validador import Validador


class PlanificadorEventos:
    """
    Motor principal de planificación de eventos del Etihad Stadium.
    
    Esta clase coordina todas las operaciones de planificación:
    - Gestión de recursos (árbitros)
    - Gestión de eventos (partidos)
    - Validación de restricciones
    - Búsqueda de horarios disponibles
    
    Attributes:
        eventos (Dict[str, Evento]): Diccionario de eventos {id: evento}
        recursos (Dict[str, Recurso]): Diccionario de recursos {id: recurso}
        validador (Validador): Instancia del validador de restricciones
    
    Example:
        >>> planificador = PlanificadorEventos()
        >>> planificador.agregar_recurso(Arbitro("Michael Oliver", TipoArbitro.PRINCIPAL))
        >>> exito, mensaje = planificador.planificar_evento(partido)
    """
    
    def __init__(self):
        """Inicializa el planificador con colecciones vacías."""
        self.eventos: Dict[str, Evento] = {}
        self.recursos: Dict[str, Recurso] = {}
        self.validador = Validador()
    
    # =========================================================================
    # GESTIÓN DE RECURSOS
    # =========================================================================
    
    def agregar_recurso(self, recurso: Recurso) -> bool:
        """
        Agrega un recurso al sistema.
        
        Args:
            recurso: Recurso a agregar
            
        Returns:
            bool: True si se agregó correctamente, False si ya existía
        """
        if recurso.id not in self.recursos:
            self.recursos[recurso.id] = recurso
            return True
        return False
    
    def eliminar_recurso(self, recurso_id: str) -> Tuple[bool, str]:
        """
        Elimina un recurso del sistema.
        
        No se puede eliminar un recurso que esté asignado a eventos futuros.
        
        Args:
            recurso_id: ID del recurso a eliminar
            
        Returns:
            Tuple[bool, str]: (True, mensaje) si se eliminó, (False, error) si no
        """
        if recurso_id not in self.recursos:
            return False, "Recurso no encontrado"
        
        # Verificar si está asignado a eventos futuros
        eventos_futuros = self.obtener_eventos_recurso(recurso_id)
        eventos_futuros = [e for e in eventos_futuros if e.fecha_inicio > datetime.now()]
        
        if eventos_futuros:
            return False, (
                f"No se puede eliminar: el recurso está asignado a "
                f"{len(eventos_futuros)} evento(s) futuro(s)"
            )
        
        del self.recursos[recurso_id]
        return True, "Recurso eliminado exitosamente"
    
    def obtener_recurso(self, recurso_id: str) -> Optional[Recurso]:
        """
        Obtiene un recurso por su ID.
        
        Args:
            recurso_id: ID del recurso
            
        Returns:
            Recurso o None si no existe
        """
        return self.recursos.get(recurso_id)
    
    def obtener_todos_recursos(self) -> List[Recurso]:
        """
        Obtiene todos los recursos del sistema.
        
        Returns:
            List[Recurso]: Lista de todos los recursos
        """
        return list(self.recursos.values())
    
    def obtener_recursos_por_tipo(self, tipo: TipoArbitro) -> List[Arbitro]:
        """
        Obtiene todos los árbitros de un tipo específico.
        
        Args:
            tipo: Tipo de árbitro a buscar
            
        Returns:
            List[Arbitro]: Lista de árbitros del tipo especificado
        """
        return [
            r for r in self.recursos.values()
            if isinstance(r, Arbitro) and r.tipo == tipo
        ]
    
    def obtener_arbitros_disponibles(self, tipo: TipoArbitro, 
                                      fecha_inicio: datetime,
                                      fecha_fin: datetime,
                                      excluir_ids: List[str] = None) -> List[Arbitro]:
        """
        Obtiene los árbitros disponibles de un tipo para una fecha específica.
        
        Args:
            tipo: Tipo de árbitro a buscar
            fecha_inicio: Fecha de inicio del evento
            fecha_fin: Fecha de fin del evento
            excluir_ids: Lista de IDs de árbitros a excluir
            
        Returns:
            List[Arbitro]: Lista de árbitros disponibles
        """
        excluir_ids = excluir_ids or []
        arbitros_tipo = self.obtener_recursos_por_tipo(tipo)
        disponibles = []
        
        for arbitro in arbitros_tipo:
            if arbitro.id in excluir_ids:
                continue
            
            disponible, _ = self.verificar_disponibilidad_recurso(
                arbitro, fecha_inicio, fecha_fin
            )
            
            if disponible:
                disponibles.append(arbitro)
        
        return disponibles
    
    # =========================================================================
    # GESTIÓN DE EVENTOS
    # =========================================================================
    
    def obtener_eventos(self) -> List[Evento]:
        """
        Obtiene todos los eventos planificados.
        
        Returns:
            List[Evento]: Lista de todos los eventos
        """
        return list(self.eventos.values())
    
    def obtener_eventos_futuros(self) -> List[Evento]:
        """
        Obtiene solo los eventos futuros (fecha mayor a ahora).
        
        Returns:
            List[Evento]: Lista de eventos futuros ordenados por fecha
        """
        ahora = datetime.now()
        futuros = [e for e in self.eventos.values() if e.fecha_inicio > ahora]
        return sorted(futuros, key=lambda e: e.fecha_inicio)
    
    def obtener_eventos_pasados(self) -> List[Evento]:
        """
        Obtiene solo los eventos pasados.
        
        Returns:
            List[Evento]: Lista de eventos pasados ordenados por fecha
        """
        ahora = datetime.now()
        pasados = [e for e in self.eventos.values() if e.fecha_inicio <= ahora]
        return sorted(pasados, key=lambda e: e.fecha_inicio, reverse=True)
    
    def obtener_evento(self, evento_id: str) -> Optional[Evento]:
        """
        Obtiene un evento por su ID.
        
        Args:
            evento_id: ID del evento
            
        Returns:
            Evento o None si no existe
        """
        return self.eventos.get(evento_id)
    
    def obtener_eventos_recurso(self, recurso_id: str) -> List[Evento]:
        """
        Obtiene todos los eventos donde participa un recurso.
        
        Args:
            recurso_id: ID del recurso
            
        Returns:
            List[Evento]: Lista de eventos donde participa el recurso
        """
        eventos_recurso = []
        
        for evento in self.eventos.values():
            if evento.contiene_recurso(recurso_id):
                eventos_recurso.append(evento)
        
        return sorted(eventos_recurso, key=lambda e: e.fecha_inicio)
    
    def obtener_eventos_en_rango(self, fecha_inicio: datetime, 
                                  fecha_fin: datetime) -> List[Evento]:
        """
        Obtiene los eventos dentro de un rango de fechas.
        
        Args:
            fecha_inicio: Inicio del rango
            fecha_fin: Fin del rango
            
        Returns:
            List[Evento]: Lista de eventos en el rango
        """
        eventos_rango = []
        
        for evento in self.eventos.values():
            if evento.se_superpone_con(fecha_inicio, fecha_fin):
                eventos_rango.append(evento)
        
        return sorted(eventos_rango, key=lambda e: e.fecha_inicio)
    
    # =========================================================================
    # PLANIFICACIÓN DE EVENTOS
    # =========================================================================
    
    def verificar_disponibilidad_recurso(self, recurso: Recurso,
                                          fecha_inicio: datetime,
                                          fecha_fin: datetime) -> Tuple[bool, str]:
        """
        Verifica si un recurso está disponible en un rango de fechas.
        
        Args:
            recurso: Recurso a verificar
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Tuple[bool, str]: (True, "") si disponible, (False, mensaje) si no
        """
        eventos_existentes = self.obtener_eventos()
        
        if isinstance(recurso, Arbitro):
            return self.validador.validar_disponibilidad_arbitro(
                recurso, fecha_inicio, fecha_fin, eventos_existentes
            )
        
        return True, ""
    
    def planificar_evento(self, evento: Evento) -> Tuple[bool, str]:
        """
        Intenta planificar un nuevo evento.
        
        Realiza todas las validaciones necesarias:
        1. Conflictos de horario del estadio
        2. Disponibilidad de árbitros
        3. Restricciones de co-requisito
        4. Restricciones de exclusión mutua
        
        Args:
            evento: Evento a planificar
            
        Returns:
            Tuple[bool, str]: (True, "Éxito") o (False, "mensaje de error")
        """
        eventos_existentes = self.obtener_eventos()
        
        # Validar el evento completo
        es_valido, errores = self.validador.validar_evento_completo(
            evento, eventos_existentes
        )
        
        if not es_valido:
            return False, "\n".join(errores)
        
        # Agregar el evento
        self.eventos[evento.id] = evento
        return True, "Evento planificado exitosamente"
    
    def eliminar_evento(self, evento_id: str) -> Tuple[bool, str]:
        """
        Elimina un evento planificado.
        
        Al eliminar un evento, los recursos asignados quedan liberados
        automáticamente.
        
        Args:
            evento_id: ID del evento a eliminar
            
        Returns:
            Tuple[bool, str]: (True, "Éxito") o (False, "mensaje de error")
        """
        if evento_id not in self.eventos:
            return False, "Evento no encontrado"
        
        evento = self.eventos[evento_id]
        del self.eventos[evento_id]
        
        return True, f"Evento '{evento.nombre}' eliminado exitosamente"
    
    def modificar_evento(self, evento_id: str, 
                         nueva_fecha_inicio: datetime = None,
                         nueva_fecha_fin: datetime = None,
                         nuevos_recursos: List[Recurso] = None) -> Tuple[bool, str]:
        """
        Modifica un evento existente.
        
        Args:
            evento_id: ID del evento a modificar
            nueva_fecha_inicio: Nueva fecha de inicio (opcional)
            nueva_fecha_fin: Nueva fecha de fin (opcional)
            nuevos_recursos: Nueva lista de recursos (opcional)
            
        Returns:
            Tuple[bool, str]: (True, "Éxito") o (False, "mensaje de error")
        """
        if evento_id not in self.eventos:
            return False, "Evento no encontrado"
        
        evento_original = self.eventos[evento_id]
        
        # Crear copia temporal con los cambios
        fecha_inicio = nueva_fecha_inicio or evento_original.fecha_inicio
        fecha_fin = nueva_fecha_fin or evento_original.fecha_fin
        recursos = nuevos_recursos if nuevos_recursos is not None else evento_original.recursos
        
        # Crear evento temporal para validar
        if isinstance(evento_original, Partido):
            evento_temp = Partido(
                equipo_local=evento_original.equipo_local,
                equipo_visitante=evento_original.equipo_visitante,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                recursos=recursos
            )
        else:
            evento_temp = Evento(
                nombre=evento_original.nombre,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                recursos=recursos
            )
        
        # Validar excluyendo el evento original
        eventos_sin_original = [e for e in self.eventos.values() if e.id != evento_id]
        es_valido, errores = self.validador.validar_evento_completo(
            evento_temp, eventos_sin_original
        )
        
        if not es_valido:
            return False, "\n".join(errores)
        
        # Aplicar cambios
        evento_original.fecha_inicio = fecha_inicio
        evento_original.fecha_fin = fecha_fin
        evento_original.recursos = recursos
        
        return True, "Evento modificado exitosamente"
    
    # =========================================================================
    # BÚSQUEDA DE HORARIOS
    # =========================================================================
    
    def buscar_proximo_horario(self, fecha_desde: datetime,
                                duracion_horas: int = 2,
                                max_dias_busqueda: int = 60) -> Optional[Tuple[datetime, Dict]]:
        """
        Busca el próximo horario disponible para un partido.
        
        Analiza el calendario y encuentra el próximo intervalo donde:
        - El estadio esté disponible (2 días de descanso)
        - Haya árbitros disponibles de todos los tipos
        
        Args:
            fecha_desde: Fecha desde donde iniciar la búsqueda
            duracion_horas: Duración del evento en horas (default: 2)
            max_dias_busqueda: Máximo de días a buscar (default: 60)
            
        Returns:
            Tuple[datetime, Dict] o None: (fecha_sugerida, arbitros_disponibles)
                                          None si no se encuentra horario
        """
        fecha_actual = fecha_desde
        fecha_limite = fecha_desde + timedelta(days=max_dias_busqueda)
        
        # Horarios típicos de partidos
        horarios_partido = [12, 15, 17, 20]
        
        while fecha_actual < fecha_limite:
            for hora in horarios_partido:
                fecha_inicio = fecha_actual.replace(
                    hour=hora, minute=0, second=0, microsecond=0
                )
                
                # Saltar si la fecha ya pasó
                if fecha_inicio < datetime.now():
                    continue
                
                fecha_fin = fecha_inicio + timedelta(hours=duracion_horas)
                
                # Verificar disponibilidad del estadio
                estadio_disponible = self._verificar_disponibilidad_estadio(
                    fecha_inicio, fecha_fin
                )
                
                if not estadio_disponible:
                    continue
                
                # Verificar disponibilidad de árbitros
                arbitros_disponibles = self._obtener_arbitros_disponibles_todos_tipos(
                    fecha_inicio, fecha_fin
                )
                
                # Verificar que haya suficientes árbitros de cada tipo
                if self._hay_equipo_arbitral_completo(arbitros_disponibles):
                    return fecha_inicio, arbitros_disponibles
            
            # Pasar al siguiente día
            fecha_actual += timedelta(days=1)
        
        return None
    
    def _verificar_disponibilidad_estadio(self, fecha_inicio: datetime,
                                           fecha_fin: datetime) -> bool:
        """
        Verifica si el estadio está disponible en un horario.
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            bool: True si el estadio está disponible
        """
        eventos_existentes = self.obtener_eventos()
        
        valido, _ = self.validador.validar_conflicto_estadio(
            fecha_inicio, fecha_fin, eventos_existentes
        )
        
        return valido
    
    def _obtener_arbitros_disponibles_todos_tipos(self, fecha_inicio: datetime,
                                                    fecha_fin: datetime) -> Dict[str, List[Arbitro]]:
        """
        Obtiene los árbitros disponibles de todos los tipos.
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Dict[str, List[Arbitro]]: Diccionario {tipo: [arbitros_disponibles]}
        """
        return {
            'Árbitro Principal': self.obtener_arbitros_disponibles(
                TipoArbitro.PRINCIPAL, fecha_inicio, fecha_fin
            ),
            'Árbitro de Línea': self.obtener_arbitros_disponibles(
                TipoArbitro.LINEA, fecha_inicio, fecha_fin
            ),
            'Cuarto Árbitro': self.obtener_arbitros_disponibles(
                TipoArbitro.CUARTO, fecha_inicio, fecha_fin
            )
        }
    
    def _hay_equipo_arbitral_completo(self, arbitros_disponibles: Dict[str, List[Arbitro]]) -> bool:
        """
        Verifica si hay suficientes árbitros para formar un equipo completo.
        
        Args:
            arbitros_disponibles: Diccionario con árbitros por tipo
            
        Returns:
            bool: True si hay equipo completo disponible
        """
        return (
            len(arbitros_disponibles.get('Árbitro Principal', [])) >= 1 and
            len(arbitros_disponibles.get('Árbitro de Línea', [])) >= 2 and
            len(arbitros_disponibles.get('Cuarto Árbitro', [])) >= 1
        )
    
    def sugerir_arbitros(self, fecha_inicio: datetime,
                          fecha_fin: datetime) -> Optional[Dict[str, List[Arbitro]]]:
        """
        Sugiere un equipo arbitral completo para una fecha.
        
        Args:
            fecha_inicio: Fecha de inicio del partido
            fecha_fin: Fecha de fin del partido
            
        Returns:
            Dict o None: Diccionario con árbitros sugeridos por tipo,
                         None si no hay equipo completo disponible
        """
        arbitros_disponibles = self._obtener_arbitros_disponibles_todos_tipos(
            fecha_inicio, fecha_fin
        )
        
        if not self._hay_equipo_arbitral_completo(arbitros_disponibles):
            return None
        
        # Seleccionar los primeros disponibles de cada tipo
        sugerencia = {
            'principal': arbitros_disponibles['Árbitro Principal'][0],
            'linea': arbitros_disponibles['Árbitro de Línea'][:2],
            'cuarto': arbitros_disponibles['Cuarto Árbitro'][0]
        }
        
        return sugerencia
    
    # =========================================================================
    # ESTADÍSTICAS Y REPORTES
    # =========================================================================
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del sistema.
        
        Returns:
            Dict: Diccionario con estadísticas
        """
        eventos = self.obtener_eventos()
        ahora = datetime.now()
        
        eventos_futuros = [e for e in eventos if e.fecha_inicio > ahora]
        eventos_pasados = [e for e in eventos if e.fecha_inicio <= ahora]
        
        # Contar árbitros por tipo
        arbitros_por_tipo = {
            'principales': len(self.obtener_recursos_por_tipo(TipoArbitro.PRINCIPAL)),
            'linea': len(self.obtener_recursos_por_tipo(TipoArbitro.LINEA)),
            'cuartos': len(self.obtener_recursos_por_tipo(TipoArbitro.CUARTO))
        }
        
        return {
            'total_eventos': len(eventos),
            'eventos_futuros': len(eventos_futuros),
            'eventos_pasados': len(eventos_pasados),
            'total_recursos': len(self.recursos),
            'arbitros_por_tipo': arbitros_por_tipo,
            'proximo_partido': eventos_futuros[0] if eventos_futuros else None
        }
    
    def obtener_agenda_recurso(self, recurso_id: str) -> Dict[str, Any]:
        """
        Obtiene la agenda completa de un recurso.
        
        Args:
            recurso_id: ID del recurso
            
        Returns:
            Dict: Información de la agenda del recurso
        """
        recurso = self.obtener_recurso(recurso_id)
        
        if not recurso:
            return {'error': 'Recurso no encontrado'}
        
        eventos = self.obtener_eventos_recurso(recurso_id)
        ahora = datetime.now()
        
        eventos_futuros = [e for e in eventos if e.fecha_inicio > ahora]
        eventos_pasados = [e for e in eventos if e.fecha_inicio <= ahora]
        
        return {
            'recurso': recurso,
            'total_eventos': len(eventos),
            'eventos_futuros': eventos_futuros,
            'eventos_pasados': eventos_pasados,
            'proximo_evento': eventos_futuros[0] if eventos_futuros else None
        }
    
    # =========================================================================
    # SERIALIZACIÓN
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """
        Convierte el estado del planificador a diccionario.
        
        Returns:
            Dict: Estado completo del planificador
        """
        return {
            'recursos': [r.to_dict() for r in self.recursos.values()],
            'eventos': [e.to_dict() for e in self.eventos.values()]
        }
    
    def cargar_desde_dict(self, data: Dict) -> Tuple[bool, str]:
        """
        Carga el estado del planificador desde un diccionario.
        
        Args:
            data: Diccionario con el estado a cargar
            
        Returns:
            Tuple[bool, str]: (True, mensaje) si se cargó correctamente
        """
        try:
            # Limpiar estado actual
            self.recursos.clear()
            self.eventos.clear()
            
            # Cargar recursos
            for recurso_data in data.get('recursos', []):
                if recurso_data.get('tipo_clase') == 'Arbitro':
                    recurso = Arbitro.from_dict(recurso_data)
                else:
                    recurso = Recurso.from_dict(recurso_data)
                self.recursos[recurso.id] = recurso
            
            # Cargar eventos
            for evento_data in data.get('eventos', []):
                if evento_data.get('tipo') == 'Partido':
                    evento = Partido.from_dict(evento_data, self.recursos)
                else:
                    evento = Evento.from_dict(evento_data, self.recursos)
                self.eventos[evento.id] = evento
            
            return True, (
                f"Datos cargados: {len(self.recursos)} recursos, "
                f"{len(self.eventos)} eventos"
            )
            
        except Exception as e:
            return False, f"Error al cargar datos: {str(e)}"
    
    def __str__(self) -> str:
        """Representación en cadena del planificador."""
        return (
            f"PlanificadorEventos("
            f"recursos={len(self.recursos)}, "
            f"eventos={len(self.eventos)})"
        )
    
    def __repr__(self) -> str:
        """Representación técnica del planificador."""
        return self.__str__()
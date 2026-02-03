"""
=============================================================================
MÓDULO RESTRICCIONES - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Define las restricciones del sistema de planificación.

Restricciones implementadas:
1. Co-requisito: Todo partido requiere un equipo arbitral completo
2. Exclusión Mutua: Los árbitros necesitan 7 días de descanso entre partidos
=============================================================================
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Tuple, TYPE_CHECKING

# Importación condicional para evitar dependencias circulares
if TYPE_CHECKING:
    from .recurso import Recurso, Arbitro
    from .evento import Evento


class Restriccion(ABC):
    """
    Clase base abstracta para las restricciones del sistema.
    
    Las restricciones son reglas que deben cumplirse para que
    un evento pueda ser planificado correctamente.
    
    Attributes:
        nombre (str): Nombre identificativo de la restricción
        descripcion (str): Descripción detallada de la restricción
    """
    
    def __init__(self, nombre: str, descripcion: str = ""):
        """
        Inicializa una nueva restricción.
        
        Args:
            nombre: Nombre identificativo de la restricción
            descripcion: Descripción detallada de la restricción
        """
        self.nombre = nombre
        self.descripcion = descripcion
    
    def __str__(self) -> str:
        """Representación en cadena de la restricción."""
        return f"{self.nombre}: {self.descripcion}"
    
    def __repr__(self) -> str:
        """Representación técnica de la restricción."""
        return f"Restriccion(nombre='{self.nombre}')"
    
    @abstractmethod
    def validar(self, recursos: List, fecha_inicio: datetime, 
                fecha_fin: datetime, eventos_existentes: List) -> Tuple[bool, str]:
        """
        Valida si la restricción se cumple.
        
        Args:
            recursos: Lista de recursos a validar
            fecha_inicio: Fecha de inicio del evento
            fecha_fin: Fecha de fin del evento
            eventos_existentes: Lista de eventos ya planificados
            
        Returns:
            Tuple[bool, str]: (True, "") si es válido, (False, mensaje_error) si no
        """
        pass


class RestriccionCoRequisito(Restriccion):
    """
    Restricción de Co-requisito: Un recurso siempre requiere de otro.
    
    En el contexto del Etihad Stadium, todo partido requiere:
    - Exactamente 1 árbitro principal
    - Exactamente 2 árbitros de línea
    - Exactamente 1 cuarto árbitro (reserva)
    
    Esta restricción garantiza que no se pueda planificar un partido
    sin el equipo arbitral completo.
    
    Example:
        >>> restriccion = RestriccionCoRequisito()
        >>> valido, mensaje = restriccion.validar(recursos, fecha_ini, fecha_fin, [])
        >>> if not valido:
        ...     print(f"Error: {mensaje}")
    """
    
    # Requisitos del equipo arbitral
    ARBITROS_PRINCIPALES_REQUERIDOS = 1
    ARBITROS_LINEA_REQUERIDOS = 2
    CUARTOS_ARBITROS_REQUERIDOS = 1
    
    def __init__(self):
        """Inicializa la restricción de co-requisito."""
        super().__init__(
            nombre="Co-requisito de Árbitros",
            descripcion=(
                f"Todo partido requiere: "
                f"{self.ARBITROS_PRINCIPALES_REQUERIDOS} árbitro principal, "
                f"{self.ARBITROS_LINEA_REQUERIDOS} árbitros de línea y "
                f"{self.CUARTOS_ARBITROS_REQUERIDOS} cuarto árbitro"
            )
        )
    
    def validar(self, recursos: List, fecha_inicio: datetime,
                fecha_fin: datetime, eventos_existentes: List) -> Tuple[bool, str]:
        """
        Valida que estén todos los árbitros requeridos.
        
        Args:
            recursos: Lista de recursos (árbitros) asignados
            fecha_inicio: Fecha de inicio del partido
            fecha_fin: Fecha de fin del partido
            eventos_existentes: Lista de eventos ya planificados (no usado aquí)
            
        Returns:
            Tuple[bool, str]: (True, "") si el equipo está completo,
                              (False, mensaje_error) si falta algún árbitro
        """
        # Importación local para evitar dependencia circular
        from .recurso import Arbitro, TipoArbitro
        
        # Inicializar conteo de árbitros por tipo
        conteo = {
            TipoArbitro.PRINCIPAL: 0,
            TipoArbitro.LINEA: 0,
            TipoArbitro.CUARTO: 0
        }
        
        # Contar árbitros por tipo
        for recurso in recursos:
            if isinstance(recurso, Arbitro):
                if recurso.tipo in conteo:
                    conteo[recurso.tipo] += 1
        
        # Validar cantidades requeridas
        errores = []
        
        # Validar árbitro principal
        if conteo[TipoArbitro.PRINCIPAL] < self.ARBITROS_PRINCIPALES_REQUERIDOS:
            errores.append(
                f"Se requiere {self.ARBITROS_PRINCIPALES_REQUERIDOS} árbitro principal "
                f"(tiene {conteo[TipoArbitro.PRINCIPAL]})"
            )
        elif conteo[TipoArbitro.PRINCIPAL] > self.ARBITROS_PRINCIPALES_REQUERIDOS:
            errores.append(
                f"Solo se permite {self.ARBITROS_PRINCIPALES_REQUERIDOS} árbitro principal "
                f"(tiene {conteo[TipoArbitro.PRINCIPAL]})"
            )
        
        # Validar árbitros de línea
        if conteo[TipoArbitro.LINEA] < self.ARBITROS_LINEA_REQUERIDOS:
            errores.append(
                f"Se requieren {self.ARBITROS_LINEA_REQUERIDOS} árbitros de línea "
                f"(tiene {conteo[TipoArbitro.LINEA]})"
            )
        elif conteo[TipoArbitro.LINEA] > self.ARBITROS_LINEA_REQUERIDOS:
            errores.append(
                f"Solo se permiten {self.ARBITROS_LINEA_REQUERIDOS} árbitros de línea "
                f"(tiene {conteo[TipoArbitro.LINEA]})"
            )
        
        # Validar cuarto árbitro
        if conteo[TipoArbitro.CUARTO] < self.CUARTOS_ARBITROS_REQUERIDOS:
            errores.append(
                f"Se requiere {self.CUARTOS_ARBITROS_REQUERIDOS} cuarto árbitro "
                f"(tiene {conteo[TipoArbitro.CUARTO]})"
            )
        elif conteo[TipoArbitro.CUARTO] > self.CUARTOS_ARBITROS_REQUERIDOS:
            errores.append(
                f"Solo se permite {self.CUARTOS_ARBITROS_REQUERIDOS} cuarto árbitro "
                f"(tiene {conteo[TipoArbitro.CUARTO]})"
            )
        
        # Retornar resultado
        if errores:
            return False, "; ".join(errores)
        
        return True, ""


class RestriccionExclusionMutua(Restriccion):
    """
    Restricción de Exclusión Mutua: Un árbitro no puede estar en dos
    partidos dentro del período de descanso requerido.
    
    En el contexto del Etihad Stadium:
    - Los árbitros necesitan mínimo 7 días de descanso entre partidos
    - Un árbitro no puede estar asignado a dos partidos en la misma semana
    
    Esta restricción garantiza el bienestar de los árbitros y evita
    conflictos de disponibilidad.
    
    Attributes:
        dias_descanso (int): Días mínimos de descanso entre partidos
    
    Example:
        >>> restriccion = RestriccionExclusionMutua(dias_descanso=7)
        >>> valido, mensaje = restriccion.validar(recursos, fecha_ini, fecha_fin, eventos)
        >>> if not valido:
        ...     print(f"Error: {mensaje}")
    """
    
    def __init__(self, dias_descanso: int = 7):
        """
        Inicializa la restricción de exclusión mutua.
        
        Args:
            dias_descanso: Días mínimos de descanso entre partidos (default: 7)
        """
        super().__init__(
            nombre="Descanso de Árbitros",
            descripcion=f"Los árbitros requieren {dias_descanso} días de descanso entre partidos"
        )
        self.dias_descanso = dias_descanso
    
    def validar(self, recursos: List, fecha_inicio: datetime,
                fecha_fin: datetime, eventos_existentes: List) -> Tuple[bool, str]:
        """
        Valida que los árbitros tengan suficiente descanso entre partidos.
        
        Args:
            recursos: Lista de recursos (árbitros) a asignar
            fecha_inicio: Fecha de inicio del nuevo partido
            fecha_fin: Fecha de fin del nuevo partido
            eventos_existentes: Lista de partidos ya planificados
            
        Returns:
            Tuple[bool, str]: (True, "") si todos los árbitros están disponibles,
                              (False, mensaje_error) si alguno no tiene suficiente descanso
        """
        # Importación local para evitar dependencia circular
        from .recurso import Arbitro
        
        errores = []
        
        # Verificar cada árbitro
        for recurso in recursos:
            if isinstance(recurso, Arbitro):
                # Buscar partidos donde participa este árbitro
                for evento in eventos_existentes:
                    # Verificar si el árbitro está en este evento
                    arbitro_en_evento = any(
                        r.id == recurso.id for r in evento.recursos
                    )
                    
                    if arbitro_en_evento:
                        # Calcular días de diferencia entre partidos
                        dias_diferencia = self._calcular_dias_diferencia(
                            fecha_inicio, evento.fecha_inicio
                        )
                        
                        # Verificar si cumple con el descanso mínimo
                        if dias_diferencia < self.dias_descanso:
                            errores.append(
                                f"{recurso.nombre} no tiene suficiente descanso. "
                                f"Tiene partido el {evento.fecha_inicio.strftime('%d/%m/%Y')} "
                                f"({dias_diferencia} días de diferencia, "
                                f"mínimo requerido: {self.dias_descanso} días)"
                            )
        
        # Retornar resultado
        if errores:
            return False, "; ".join(errores)
        
        return True, ""
    
    def _calcular_dias_diferencia(self, fecha1: datetime, fecha2: datetime) -> int:
        """
        Calcula la diferencia absoluta en días entre dos fechas.
        
        Args:
            fecha1: Primera fecha
            fecha2: Segunda fecha
            
        Returns:
            int: Diferencia absoluta en días
        """
        return abs((fecha1.date() - fecha2.date()).days)
    
    def verificar_disponibilidad_arbitro(self, arbitro, fecha_inicio: datetime,
                                          eventos_existentes: List) -> Tuple[bool, str]:
        """
        Verifica si un árbitro específico está disponible para una fecha.
        
        Args:
            arbitro: Árbitro a verificar
            fecha_inicio: Fecha del nuevo partido
            eventos_existentes: Lista de partidos ya planificados
            
        Returns:
            Tuple[bool, str]: (True, "") si está disponible,
                              (False, mensaje) con el motivo si no lo está
        """
        for evento in eventos_existentes:
            # Verificar si el árbitro está en este evento
            arbitro_en_evento = any(
                r.id == arbitro.id for r in evento.recursos
            )
            
            if arbitro_en_evento:
                dias_diferencia = self._calcular_dias_diferencia(
                    fecha_inicio, evento.fecha_inicio
                )
                
                if dias_diferencia < self.dias_descanso:
                    return False, (
                        f"Partido asignado el {evento.fecha_inicio.strftime('%d/%m/%Y')} "
                        f"({dias_diferencia} días de diferencia)"
                    )
        
        return True, ""


class RestriccionDescansoEstadio(Restriccion):
    """
    Restricción adicional: El estadio necesita días de descanso entre partidos.
    
    En el contexto del Etihad Stadium:
    - Se requieren mínimo 2 días de descanso entre partidos
    - Esto permite mantenimiento del césped y preparación del estadio
    
    Attributes:
        dias_descanso (int): Días mínimos de descanso del estadio
    """
    
    def __init__(self, dias_descanso: int = 2):
        """
        Inicializa la restricción de descanso del estadio.
        
        Args:
            dias_descanso: Días mínimos entre partidos (default: 2)
        """
        super().__init__(
            nombre="Descanso del Estadio",
            descripcion=f"El estadio requiere {dias_descanso} días de descanso entre partidos"
        )
        self.dias_descanso = dias_descanso
    
    def validar(self, recursos: List, fecha_inicio: datetime,
                fecha_fin: datetime, eventos_existentes: List) -> Tuple[bool, str]:
        """
        Valida que el estadio tenga suficiente descanso entre partidos.
        
        Args:
            recursos: Lista de recursos (no usado aquí)
            fecha_inicio: Fecha de inicio del nuevo partido
            fecha_fin: Fecha de fin del nuevo partido
            eventos_existentes: Lista de partidos ya planificados
            
        Returns:
            Tuple[bool, str]: (True, "") si hay suficiente descanso,
                              (False, mensaje_error) si no lo hay
        """
        for evento in eventos_existentes:
            # Verificar superposición directa
            if evento.se_superpone_con(fecha_inicio, fecha_fin):
                return False, (
                    f"Conflicto de horario: Ya existe el partido '{evento.nombre}' "
                    f"programado para {evento.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
                )
            
            # Calcular días de diferencia
            dias_antes = (fecha_inicio.date() - evento.fecha_fin.date()).days
            dias_despues = (evento.fecha_inicio.date() - fecha_fin.date()).days
            
            # Verificar descanso antes del partido existente
            if 0 <= dias_antes < self.dias_descanso:
                return False, (
                                        f"El estadio necesita {self.dias_descanso} días de descanso. "
                    f"Hay un partido el {evento.fecha_inicio.strftime('%d/%m/%Y')} "
                    f"(solo {dias_antes} día(s) de diferencia)"
                )
            
            # Verificar descanso después del partido existente
            if 0 <= dias_despues < self.dias_descanso:
                return False, (
                    f"El estadio necesita {self.dias_descanso} días de descanso. "
                    f"Hay un partido el {evento.fecha_inicio.strftime('%d/%m/%Y')} "
                    f"(solo {dias_despues} día(s) de diferencia)"
                )
        
        return True, ""


class ValidadorRestricciones:
    """
    Clase utilitaria para validar múltiples restricciones a la vez.
    
    Permite agregar restricciones dinámicamente y validarlas todas
    en una sola llamada.
    
    Attributes:
        restricciones (List[Restriccion]): Lista de restricciones a validar
    
    Example:
        >>> validador = ValidadorRestricciones()
        >>> validador.agregar_restriccion(RestriccionCoRequisito())
        >>> validador.agregar_restriccion(RestriccionExclusionMutua())
        >>> valido, errores = validador.validar_todas(recursos, fecha_ini, fecha_fin, eventos)
    """
    
    def __init__(self):
        """Inicializa el validador sin restricciones."""
        self.restricciones: List[Restriccion] = []
    
    def agregar_restriccion(self, restriccion: Restriccion) -> None:
        """
        Agrega una restricción al validador.
        
        Args:
            restriccion: Restricción a agregar
        """
        self.restricciones.append(restriccion)
    
    def remover_restriccion(self, nombre: str) -> bool:
        """
        Remueve una restricción por su nombre.
        
        Args:
            nombre: Nombre de la restricción a remover
            
        Returns:
            bool: True si se removió, False si no existía
        """
        for i, restriccion in enumerate(self.restricciones):
            if restriccion.nombre == nombre:
                self.restricciones.pop(i)
                return True
        return False
    
    def obtener_restricciones(self) -> List[Restriccion]:
        """
        Obtiene la lista de restricciones configuradas.
        
        Returns:
            List[Restriccion]: Lista de restricciones
        """
        return self.restricciones.copy()
    
    def validar_todas(self, recursos: List, fecha_inicio: datetime,
                      fecha_fin: datetime, 
                      eventos_existentes: List) -> Tuple[bool, List[str]]:
        """
        Valida todas las restricciones configuradas.
        
        Args:
            recursos: Lista de recursos a validar
            fecha_inicio: Fecha de inicio del evento
            fecha_fin: Fecha de fin del evento
            eventos_existentes: Lista de eventos ya planificados
            
        Returns:
            Tuple[bool, List[str]]: (True, []) si todas las restricciones se cumplen,
                                    (False, [lista_de_errores]) si alguna falla
        """
        errores = []
        
        for restriccion in self.restricciones:
            es_valido, mensaje = restriccion.validar(
                recursos, fecha_inicio, fecha_fin, eventos_existentes
            )
            
            if not es_valido:
                errores.append(f"[{restriccion.nombre}] {mensaje}")
        
        return len(errores) == 0, errores
    
    def __str__(self) -> str:
        """Representación en cadena del validador."""
        nombres = [r.nombre for r in self.restricciones]
        return f"ValidadorRestricciones({len(self.restricciones)} restricciones: {', '.join(nombres)})"


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def crear_validador_estadio() -> ValidadorRestricciones:
    """
    Crea un validador preconfigurado con las restricciones del Etihad Stadium.
    
    Restricciones incluidas:
    - Co-requisito de árbitros (equipo arbitral completo)
    - Exclusión mutua de árbitros (7 días de descanso)
    - Descanso del estadio (2 días entre partidos)
    
    Returns:
        ValidadorRestricciones: Validador configurado
        
    Example:
        >>> validador = crear_validador_estadio()
        >>> valido, errores = validador.validar_todas(recursos, fecha_ini, fecha_fin, eventos)
    """
    validador = ValidadorRestricciones()
    
    # Agregar restricciones del estadio
    validador.agregar_restriccion(RestriccionCoRequisito())
    validador.agregar_restriccion(RestriccionExclusionMutua(dias_descanso=7))
    validador.agregar_restriccion(RestriccionDescansoEstadio(dias_descanso=2))
    
    return validador


def verificar_equipo_arbitral_completo(recursos: List) -> Tuple[bool, dict]:
    """
    Verifica si una lista de recursos contiene un equipo arbitral completo.
    
    Args:
        recursos: Lista de recursos a verificar
        
    Returns:
        Tuple[bool, dict]: (True/False, diccionario con conteo por tipo)
        
    Example:
        >>> completo, conteo = verificar_equipo_arbitral_completo(arbitros)
        >>> print(f"Equipo completo: {completo}")
        >>> print(f"Principales: {conteo['principal']}")
    """
    from .recurso import Arbitro, TipoArbitro
    
    conteo = {
        'principal': 0,
        'linea': 0,
        'cuarto': 0
    }
    
    for recurso in recursos:
        if isinstance(recurso, Arbitro):
            if recurso.tipo == TipoArbitro.PRINCIPAL:
                conteo['principal'] += 1
            elif recurso.tipo == TipoArbitro.LINEA:
                conteo['linea'] += 1
            elif recurso.tipo == TipoArbitro.CUARTO:
                conteo['cuarto'] += 1
    
    equipo_completo = (
        conteo['principal'] == RestriccionCoRequisito.ARBITROS_PRINCIPALES_REQUERIDOS and
        conteo['linea'] == RestriccionCoRequisito.ARBITROS_LINEA_REQUERIDOS and
        conteo['cuarto'] == RestriccionCoRequisito.CUARTOS_ARBITROS_REQUERIDOS
    )
    
    return equipo_completo, conteo
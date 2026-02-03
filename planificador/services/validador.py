"""
=============================================================================
MÓDULO VALIDADOR - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Servicio de validación de restricciones y conflictos.
Centraliza toda la lógica de validación del sistema.
=============================================================================
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Any, Optional

from models.evento import Evento, Partido
from models.recurso import Recurso, Arbitro, TipoArbitro
from models.restricciones import (
    Restriccion,
    RestriccionCoRequisito,
    RestriccionExclusionMutua,
    RestriccionDescansoEstadio
)


class Validador:
    """
    Clase encargada de validar todas las restricciones y conflictos
    del sistema de planificación.
    
    Centraliza la validación de:
    - Formato de fechas (sin letras, sin números negativos)
    - Conflictos de horario del estadio
    - Disponibilidad de árbitros
    - Restricciones de co-requisito y exclusión mutua
    
    Attributes:
        DIAS_DESCANSO_ESTADIO (int): Días mínimos entre partidos en el estadio
        DIAS_DESCANSO_ARBITROS (int): Días mínimos de descanso para árbitros
        restricciones (List[Restriccion]): Lista de restricciones activas
    
    Example:
        >>> validador = Validador()
        >>> valido, errores = validador.validar_evento_completo(partido, eventos)
        >>> if not valido:
        ...     for error in errores:
        ...         print(f"Error: {error}")
    """
    
    # Constantes de configuración
    DIAS_DESCANSO_ESTADIO = 2
    DIAS_DESCANSO_ARBITROS = 7
    HORA_MINIMA_PARTIDO = 10
    HORA_MAXIMA_PARTIDO = 22
    ANIO_MINIMO = 2020
    ANIO_MAXIMO = 2100
    
    def __init__(self):
        """Inicializa el validador con las restricciones predefinidas."""
        self.restricciones: List[Restriccion] = [
            RestriccionCoRequisito(),
            RestriccionExclusionMutua(dias_descanso=self.DIAS_DESCANSO_ARBITROS),
            RestriccionDescansoEstadio(dias_descanso=self.DIAS_DESCANSO_ESTADIO)
        ]
    
    # =========================================================================
    # VALIDACIÓN DE FORMATO DE FECHAS
    # =========================================================================
    
    def validar_fecha_formato(self, fecha_str: str) -> Tuple[bool, Any]:
        """
        Valida que una cadena tenga formato de fecha válido.
        
        Restricciones aplicadas:
        - No se permiten letras
        - No se permiten números negativos
        - Formato requerido: DD/MM/AAAA HH:MM
        - Hora entre 10:00 y 22:00
        - Año entre 2020 y 2100
        - No se permiten fechas pasadas
        
        Args:
            fecha_str: Cadena con la fecha a validar
            
        Returns:
            Tuple[bool, Any]: (True, datetime) si es válida,
                              (False, mensaje_error) si no es válida
        
        Examples:
            >>> validador = Validador()
            >>> validador.validar_fecha_formato("25/12/2024 15:00")
            (True, datetime(2024, 12, 25, 15, 0))
            
            >>> validador.validar_fecha_formato("25/12/2024abc")
            (False, "La fecha no puede contener letras...")
            
            >>> validador.validar_fecha_formato("-5/12/2024 15:00")
            (False, "No se permiten números negativos en la fecha")
        """
        # Validar que no esté vacía
        if not fecha_str or not fecha_str.strip():
            return False, "La fecha no puede estar vacía"
        
        fecha_str = fecha_str.strip()
        
        # Validar que no contenga números negativos
        if '-' in fecha_str:
            return False, "No se permiten números negativos en la fecha"
        
        # Validar que no contenga letras
        for char in fecha_str:
            if char.isalpha():
                return False, (
                    "La fecha no puede contener letras. "
                    "Use solo números y los separadores / y :"
                )
        
        # Validar caracteres permitidos
        caracteres_permitidos = set('0123456789/: ')
        caracteres_entrada = set(fecha_str)
        caracteres_invalidos = caracteres_entrada - caracteres_permitidos
        
        if caracteres_invalidos:
            return False, (
                f"La fecha contiene caracteres no válidos: "
                f"{', '.join(caracteres_invalidos)}"
            )
        
        # Validar que tenga los separadores necesarios
        if '/' not in fecha_str:
            return False, (
                "Formato incorrecto. Use DD/MM/AAAA HH:MM "
                "(falta el separador /)"
            )
        
        if ':' not in fecha_str:
            return False, (
                "Formato incorrecto. Use DD/MM/AAAA HH:MM "
                "(falta la hora con :)"
            )
        
        # Intentar parsear la fecha
        try:
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y %H:%M')
        except ValueError as e:
            error_str = str(e).lower()
            
            if "day is out of range" in error_str:
                return False, "El día ingresado no es válido para el mes especificado"
            elif "month must be in" in error_str:
                return False, "El mes debe estar entre 1 y 12"
            elif "unconverted data" in error_str:
                return False, "Formato incorrecto. Use exactamente: DD/MM/AAAA HH:MM"
            elif "does not match format" in error_str:
                return False, (
                    "Formato incorrecto. Use: DD/MM/AAAA HH:MM "
                    "(ejemplo: 25/12/2024 15:00)"
                )
            else:
                return False, f"Fecha inválida: {str(e)}"
        
        # Validar que no sea fecha pasada
        if fecha < datetime.now():
            return False, "No se pueden programar partidos en fechas pasadas"
        
        # Validar rango de año
        if fecha.year < self.ANIO_MINIMO:
            return False, f"El año no puede ser menor a {self.ANIO_MINIMO}"
        
        if fecha.year > self.ANIO_MAXIMO:
            return False, f"El año no puede ser mayor a {self.ANIO_MAXIMO}"
        
        # Validar hora razonable para partido
        if fecha.hour < self.HORA_MINIMA_PARTIDO:
            return False, (
                f"La hora del partido debe ser a partir de las "
                f"{self.HORA_MINIMA_PARTIDO}:00"
            )
        
        if fecha.hour > self.HORA_MAXIMA_PARTIDO:
            return False, (
                f"La hora del partido no puede ser después de las "
                f"{self.HORA_MAXIMA_PARTIDO}:00"
            )
        
        return True, fecha
    
    def validar_numero_positivo(self, valor_str: str, 
                                 nombre_campo: str = "valor") -> Tuple[bool, Any]:
        """
        Valida que una cadena sea un número entero positivo.
        
        Args:
            valor_str: Cadena a validar
            nombre_campo: Nombre del campo para mensajes de error
            
        Returns:
            Tuple[bool, Any]: (True, numero) si es válido,
                              (False, mensaje_error) si no
        """
        if not valor_str or not valor_str.strip():
            return False, f"El {nombre_campo} no puede estar vacío"
        
        valor_str = valor_str.strip()
        
        # Verificar letras
        if any(c.isalpha() for c in valor_str):
            return False, f"El {nombre_campo} no puede contener letras"
        
        # Verificar signo negativo
        if '-' in valor_str:
            return False, f"El {nombre_campo} no puede ser negativo"
        
        try:
            numero = int(valor_str)
            if numero < 0:
                return False, f"El {nombre_campo} no puede ser negativo"
            return True, numero
        except ValueError:
            return False, f"El {nombre_campo} debe ser un número válido"
    
    # =========================================================================
    # VALIDACIÓN DE CONFLICTOS DE ESTADIO
    # =========================================================================
    
    def validar_conflicto_estadio(self, fecha_inicio: datetime, 
                                   fecha_fin: datetime,
                                   eventos_existentes: List[Evento]) -> Tuple[bool, str]:
        """
        Valida que no haya conflictos de uso del estadio.
        
        El estadio necesita mínimo 2 días de descanso entre partidos
        para mantenimiento del césped y preparación.
        
        Args:
            fecha_inicio: Fecha de inicio del nuevo evento
            fecha_fin: Fecha de fin del nuevo evento
            eventos_existentes: Lista de eventos ya planificados
            
        Returns:
            Tuple[bool, str]: (True, "") si no hay conflicto,
                              (False, mensaje_error) si hay conflicto
        """
        for evento in eventos_existentes:
            # Verificar superposición directa
            if evento.se_superpone_con(fecha_inicio, fecha_fin):
                return False, (
                    f"Conflicto de horario: Ya existe el partido "
                    f"'{evento.nombre}' programado del "
                    f"{evento.fecha_inicio.strftime('%d/%m/%Y %H:%M')} al "
                    f"{evento.fecha_fin.strftime('%d/%m/%Y %H:%M')}"
                )
            
            # Calcular días de diferencia
            dias_antes = (fecha_inicio.date() - evento.fecha_fin.date()).days
            dias_despues = (evento.fecha_inicio.date() - fecha_fin.date()).days
            
            # Verificar descanso del estadio (antes del evento existente)
            if 0 <= dias_antes < self.DIAS_DESCANSO_ESTADIO:
                return False, (
                    f"El estadio necesita {self.DIAS_DESCANSO_ESTADIO} días "
                    f"de descanso entre partidos. Hay un partido el "
                    f"{evento.fecha_inicio.strftime('%d/%m/%Y')} "
                    f"(solo {dias_antes} día(s) de diferencia)"
                )
            
            # Verificar descanso del estadio (después del evento existente)
            if 0 <= dias_despues < self.DIAS_DESCANSO_ESTADIO:
                return False, (
                    f"El estadio necesita {self.DIAS_DESCANSO_ESTADIO} días "
                    f"de descanso entre partidos. Hay un partido el "
                    f"{evento.fecha_inicio.strftime('%d/%m/%Y')} "
                    f"(solo {dias_despues} día(s) de diferencia)"
                )
        
        return True, ""
    
    # =========================================================================
    # VALIDACIÓN DE DISPONIBILIDAD DE ÁRBITROS
    # =========================================================================
    
    def validar_disponibilidad_arbitro(self, arbitro: Arbitro,
                                        fecha_inicio: datetime,
                                        fecha_fin: datetime,
                                        eventos_existentes: List[Evento]) -> Tuple[bool, str]:
        """
        Valida que un árbitro esté disponible para una fecha.
        
        Los árbitros necesitan 7 días de descanso entre partidos,
        por lo que no pueden estar en dos partidos la misma semana.
        
        Args:
            arbitro: Árbitro a validar
            fecha_inicio: Fecha de inicio del nuevo evento
            fecha_fin: Fecha de fin del nuevo evento
            eventos_existentes: Lista de eventos ya planificados
            
        Returns:
            Tuple[bool, str]: (True, "") si está disponible,
                              (False, mensaje_error) si no está disponible
        """
        for evento in eventos_existentes:
            # Verificar si el árbitro está asignado a este evento
            arbitro_en_evento = any(
                r.id == arbitro.id for r in evento.recursos
            )
            
            if arbitro_en_evento:
                # Calcular días de diferencia
                dias_diferencia = abs(
                    (fecha_inicio.date() - evento.fecha_inicio.date()).days
                )
                
                if dias_diferencia < self.DIAS_DESCANSO_ARBITROS:
                    return False, (
                        f"{arbitro.nombre} no está disponible. "
                        f"Tiene partido el "
                        f"{evento.fecha_inicio.strftime('%d/%m/%Y')} "
                        f"y necesita {self.DIAS_DESCANSO_ARBITROS} días de descanso "
                        f"(solo hay {dias_diferencia} día(s) de diferencia)"
                    )
        
        return True, ""
    
    def validar_equipo_arbitral(self, recursos: List[Recurso]) -> Tuple[bool, str]:
        """
        Valida que la lista de recursos contenga un equipo arbitral completo.
        
        Requisitos:
        - 1 árbitro principal
        - 2 árbitros de línea
        - 1 cuarto árbitro
        
        Args:
            recursos: Lista de recursos a validar
            
        Returns:
            Tuple[bool, str]: (True, "") si el equipo está completo,
                              (False, mensaje_error) si falta algún árbitro
        """
        restriccion = RestriccionCoRequisito()
        return restriccion.validar(recursos, datetime.now(), datetime.now(), [])
    
    # =========================================================================
    # VALIDACIÓN DE RESTRICCIONES
    # =========================================================================
    
    def validar_restricciones(self, recursos: List[Recurso],
                               fecha_inicio: datetime,
                               fecha_fin: datetime,
                               eventos_existentes: List[Evento]) -> Tuple[bool, List[str]]:
        """
        Valida todas las restricciones configuradas.
        
        Args:
            recursos: Lista de recursos a asignar
            fecha_inicio: Fecha de inicio del evento
            fecha_fin: Fecha de fin del evento
            eventos_existentes: Lista de eventos ya planificados
            
        Returns:
            Tuple[bool, List[str]]: (True, []) si todas las restricciones se cumplen,
                                    (False, [lista_errores]) si alguna falla
        """
        errores = []
        
        for restriccion in self.restricciones:
            es_valido, mensaje = restriccion.validar(
                recursos, fecha_inicio, fecha_fin, eventos_existentes
            )
            
            if not es_valido:
                errores.append(f"[{restriccion.nombre}] {mensaje}")
        
        return len(errores) == 0, errores
    
    # =========================================================================
    # VALIDACIÓN COMPLETA DE EVENTOS
    # =========================================================================
    
    def validar_evento_completo(self, evento: Evento,
                                 eventos_existentes: List[Evento]) -> Tuple[bool, List[str]]:
        """
        Realiza una validación completa de un evento.
        
        Valida en orden:
        1. Conflictos de horario del estadio (2 días de descanso)
        2. Disponibilidad de cada árbitro (7 días de descanso)
        3. Restricciones de co-requisito (equipo arbitral completo)
        4. Restricciones de exclusión mutua
        
        Args:
            evento: Evento a validar
            eventos_existentes: Lista de eventos ya planificados
            
        Returns:
            Tuple[bool, List[str]]: (True, []) si todo es válido,
                                    (False, [lista_errores]) si hay problemas
        
        Example:
            >>> validador = Validador()
            >>> valido, errores = validador.validar_evento_completo(partido, eventos)
            >>> if not valido:
            ...     print("Errores encontrados:")
            ...     for error in errores:
            ...         print(f"  - {error}")
        """
        errores = []
        
        # 1. Validar conflicto de horario del estadio
        valido, mensaje = self.validar_conflicto_estadio(
            evento.fecha_inicio, 
            evento.fecha_fin, 
            eventos_existentes
        )
        if not valido:
            errores.append(mensaje)
        
        # 2. Validar disponibilidad de cada árbitro individualmente
        for recurso in evento.recursos:
            if isinstance(recurso, Arbitro):
                valido, mensaje = self.validar_disponibilidad_arbitro(
                    recurso, 
                    evento.fecha_inicio, 
                    evento.fecha_fin, 
                    eventos_existentes
                )
                if not valido:
                    errores.append(mensaje)
        
        # 3. Validar restricciones de co-requisito y exclusión mutua
        valido, mensajes_restricciones = self.validar_restricciones(
            evento.recursos, 
            evento.fecha_inicio, 
            evento.fecha_fin, 
            eventos_existentes
        )
        
        # Agregar errores de restricciones (evitando duplicados)
        for mensaje in mensajes_restricciones:
            if mensaje not in errores:
                errores.append(mensaje)
        
        return len(errores) == 0, errores
    
    # =========================================================================
    # VALIDACIÓN DE TEXTO Y ENTRADA DE USUARIO
    # =========================================================================
    
    def validar_texto_no_vacio(self, texto: str, 
                                nombre_campo: str = "campo",
                                min_longitud: int = 1,
                                max_longitud: int = None) -> Tuple[bool, str]:
        """
        Valida que un texto no esté vacío y cumpla con la longitud requerida.
        
        Args:
            texto: Texto a validar
            nombre_campo: Nombre del campo para mensajes de error
            min_longitud: Longitud mínima requerida (default: 1)
            max_longitud: Longitud máxima permitida (opcional)
            
        Returns:
            Tuple[bool, str]: (True, texto_limpio) si es válido,
                              (False, mensaje_error) si no es válido
        """
        if texto is None:
            return False, f"El {nombre_campo} no puede estar vacío"
        
        texto_limpio = texto.strip()
        
        if len(texto_limpio) < min_longitud:
            if min_longitud == 1:
                return False, f"El {nombre_campo} no puede estar vacío"
            else:
                return False, (
                    f"El {nombre_campo} debe tener al menos "
                    f"{min_longitud} caracteres"
                )
        
        if max_longitud is not None and len(texto_limpio) > max_longitud:
            return False, (
                f"El {nombre_campo} no puede tener más de "
                f"{max_longitud} caracteres"
            )
        
        return True, texto_limpio
    
    def validar_nombre_equipo(self, nombre: str) -> Tuple[bool, str]:
        """
        Valida el nombre de un equipo de fútbol.
        
        Args:
            nombre: Nombre del equipo a validar
            
        Returns:
            Tuple[bool, str]: (True, nombre_limpio) si es válido,
                              (False, mensaje_error) si no es válido
        """
        valido, resultado = self.validar_texto_no_vacio(
            nombre, 
            "nombre del equipo",
            min_longitud=2,
            max_longitud=50
        )
        
        if not valido:
            return False, resultado
        
        # Validar que no contenga caracteres especiales extraños
        caracteres_permitidos = set(
            'abcdefghijklmnopqrstuvwxyz'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '0123456789'
            ' .-áéíóúÁÉÍÓÚñÑüÜ'
        )
        
        for char in resultado:
            if char not in caracteres_permitidos:
                return False, (
                    f"El nombre del equipo contiene caracteres no válidos: '{char}'"
                )
        
        return True, resultado
    
    # =========================================================================
    # UTILIDADES DE VALIDACIÓN
    # =========================================================================
    
    def obtener_restricciones_activas(self) -> List[Restriccion]:
        """
        Obtiene la lista de restricciones activas.
        
        Returns:
            List[Restriccion]: Lista de restricciones configuradas
        """
        return self.restricciones.copy()
    
    def agregar_restriccion(self, restriccion: Restriccion) -> None:
        """
        Agrega una nueva restricción al validador.
        
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
    
    def obtener_resumen_restricciones(self) -> str:
        """
        Obtiene un resumen de todas las restricciones activas.
        
        Returns:
            str: Resumen formateado de las restricciones
        """
        lineas = [
            "=" * 50,
            "RESTRICCIONES ACTIVAS DEL SISTEMA",
            "=" * 50,
            ""
        ]
        
        for i, restriccion in enumerate(self.restricciones, 1):
            lineas.append(f"{i}. {restriccion.nombre}")
            lineas.append(f"   {restriccion.descripcion}")
            lineas.append("")
        
        lineas.append("=" * 50)
        
        return "\n".join(lineas)
    
    def __str__(self) -> str:
        """Representación en cadena del validador."""
        return f"Validador({len(self.restricciones)} restricciones activas)"
    
    def __repr__(self) -> str:
        """Representación técnica del validador."""
        nombres = [r.nombre for r in self.restricciones]
        return f"Validador(restricciones={nombres})"
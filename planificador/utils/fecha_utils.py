"""
=============================================================================
MÓDULO FECHA_UTILS - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Utilidades para manejo, validación y formateo de fechas.
Incluye validaciones específicas para evitar números negativos y letras.
=============================================================================
"""

from datetime import datetime, timedelta
from typing import Tuple, Any, Optional


# =============================================================================
# CONSTANTES
# =============================================================================

FORMATO_FECHA_HORA = '%d/%m/%Y %H:%M'
FORMATO_FECHA = '%d/%m/%Y'
FORMATO_HORA = '%H:%M'

HORA_MINIMA_PARTIDO = 10
HORA_MAXIMA_PARTIDO = 22
ANIO_MINIMO = 2020
ANIO_MAXIMO = 2100

DIAS_SEMANA = [
    'Lunes', 'Martes', 'Miércoles', 'Jueves',
    'Viernes', 'Sábado', 'Domingo'
]

MESES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]


# =============================================================================
# VALIDACIÓN DE FECHAS
# =============================================================================

def validar_fecha(fecha_str: str) -> Tuple[bool, Any]:
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
        >>> validar_fecha("25/12/2024 15:00")
        (True, datetime(2024, 12, 25, 15, 0))
        
        >>> validar_fecha("25/12/2024abc")
        (False, "La fecha no puede contener letras...")
        
        >>> validar_fecha("-5/12/2024 15:00")
        (False, "No se permiten números negativos en la fecha")
    """
    # Validar que no esté vacía
    if not fecha_str or not fecha_str.strip():
        return False, "La fecha no puede estar vacía"
    
    fecha_str = fecha_str.strip()
    
    # Validar que no contenga números negativos (signo menos)
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
        caracteres_str = ', '.join(f"'{c}'" for c in caracteres_invalidos)
        return False, f"La fecha contiene caracteres no válidos: {caracteres_str}"
    
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
    
    # Validar cantidad de separadores
    if fecha_str.count('/') != 2:
        return False, (
            "Formato incorrecto. La fecha debe tener formato DD/MM/AAAA "
            "(dos separadores /)"
        )
    
    if fecha_str.count(':') != 1:
        return False, (
            "Formato incorrecto. La hora debe tener formato HH:MM "
            "(un separador :)"
        )
    
    # Intentar parsear la fecha
    try:
        fecha = datetime.strptime(fecha_str, FORMATO_FECHA_HORA)
    except ValueError as e:
        error_str = str(e).lower()
        
        if "day is out of range" in error_str:
            return False, "El día ingresado no es válido para el mes especificado"
        elif "month must be in" in error_str:
            return False, "El mes debe estar entre 1 y 12"
        elif "hour must be in" in error_str:
            return False, "La hora debe estar entre 0 y 23"
        elif "minute must be in" in error_str:
            return False, "Los minutos deben estar entre 0 y 59"
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
    if fecha.year < ANIO_MINIMO:
        return False, f"El año no puede ser menor a {ANIO_MINIMO}"
    
    if fecha.year > ANIO_MAXIMO:
        return False, f"El año no puede ser mayor a {ANIO_MAXIMO}"
    
    # Validar hora razonable para partido
    if fecha.hour < HORA_MINIMA_PARTIDO:
        return False, (
            f"La hora del partido debe ser a partir de las "
            f"{HORA_MINIMA_PARTIDO}:00"
        )
    
    if fecha.hour > HORA_MAXIMA_PARTIDO:
        return False, (
            f"La hora del partido no puede ser después de las "
            f"{HORA_MAXIMA_PARTIDO}:00"
        )
    
    return True, fecha


def parsear_fecha(fecha_str: str) -> Optional[datetime]:
    """
    Parsea una cadena de fecha al formato datetime.
    
    A diferencia de validar_fecha, esta función solo retorna
    el datetime o None, sin mensajes de error.
    
    Args:
        fecha_str: Cadena con formato DD/MM/AAAA HH:MM
        
    Returns:
        datetime si es válida, None si no lo es
    
    Example:
        >>> fecha = parsear_fecha("25/12/2024 15:00")
        >>> if fecha:
        ...     print(f"Fecha válida: {fecha}")
        ... else:
        ...     print("Fecha inválida")
    """
    es_valida, resultado = validar_fecha(fecha_str)
    if es_valida:
        return resultado
    return None


# =============================================================================
# FORMATEO DE FECHAS
# =============================================================================

def formatear_fecha(fecha: datetime, incluir_hora: bool = True) -> str:
    """
    Formatea una fecha para mostrar al usuario.
    
    Args:
        fecha: Objeto datetime a formatear
        incluir_hora: Si se debe incluir la hora (default: True)
        
    Returns:
        str: Fecha formateada
    
    Examples:
        >>> formatear_fecha(datetime(2024, 12, 25, 15, 0))
        "25/12/2024 15:00"
        
        >>> formatear_fecha(datetime(2024, 12, 25, 15, 0), incluir_hora=False)
        "25/12/2024"
    """
    if incluir_hora:
        return fecha.strftime(FORMATO_FECHA_HORA)
    return fecha.strftime(FORMATO_FECHA)


def formatear_fecha_larga(fecha: datetime) -> str:
    """
    Formatea una fecha en formato largo legible.
    
    Args:
        fecha: Objeto datetime a formatear
        
    Returns:
        str: Fecha en formato largo
    
    Example:
        >>> formatear_fecha_larga(datetime(2024, 12, 25, 15, 0))
        "Miércoles, 25 de Diciembre de 2024 a las 15:00"
    """
    dia_semana = DIAS_SEMANA[fecha.weekday()]
    mes = MESES[fecha.month - 1]
    
    return (
        f"{dia_semana}, {fecha.day} de {mes} de {fecha.year} "
        f"a las {fecha.strftime(FORMATO_HORA)}"
    )


def formatear_duracion(inicio: datetime, fin: datetime) -> str:
    """
    Formatea la duración entre dos fechas.
    
    Args:
        inicio: Fecha de inicio
        fin: Fecha de fin
        
    Returns:
        str: Duración formateada
    
    Example:
        >>> inicio = datetime(2024, 12, 25, 15, 0)
        >>> fin = datetime(2024, 12, 25, 17, 30)
        >>> formatear_duracion(inicio, fin)
        "2 hora(s) 30 minuto(s)"
    """
    diferencia = fin - inicio
    total_segundos = int(diferencia.total_seconds())
    
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    
    partes = []
    if horas > 0:
        partes.append(f"{horas} hora(s)")
    if minutos > 0:
        partes.append(f"{minutos} minuto(s)")
    
    if not partes:
        return "0 minutos"
    
    return " ".join(partes)


# =============================================================================
# CÁLCULOS CON FECHAS
# =============================================================================

def calcular_diferencia_dias(fecha1: datetime, fecha2: datetime) -> int:
    """
    Calcula la diferencia absoluta en días entre dos fechas.
    
    Args:
        fecha1: Primera fecha
        fecha2: Segunda fecha
        
    Returns:
        int: Diferencia absoluta en días
    
    Example:
        >>> fecha1 = datetime(2024, 12, 25, 15, 0)
        >>> fecha2 = datetime(2024, 12, 20, 10, 0)
        >>> calcular_diferencia_dias(fecha1, fecha2)
        5
    """
    return abs((fecha1.date() - fecha2.date()).days)


def obtener_rango_semana(fecha: datetime) -> Tuple[datetime, datetime]:
    """
    Obtiene el inicio (lunes) y fin (domingo) de la semana para una fecha.
    
    Args:
        fecha: Fecha de referencia
        
    Returns:
        Tuple[datetime, datetime]: (inicio_semana, fin_semana)
    
    Example:
        >>> fecha = datetime(2024, 12, 25, 15, 0)  # Miércoles
        >>> inicio, fin = obtener_rango_semana(fecha)
        >>> print(inicio.strftime('%A'))  # Lunes
        >>> print(fin.strftime('%A'))     # Domingo
    """
    # Calcular inicio de semana (lunes)
    dias_desde_lunes = fecha.weekday()
    inicio_semana = fecha - timedelta(days=dias_desde_lunes)
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calcular fin de semana (domingo)
    fin_semana = inicio_semana + timedelta(days=6)
    fin_semana = fin_semana.replace(hour=23, minute=59, second=59, microsecond=0)
    
    return inicio_semana, fin_semana


def fecha_en_rango(fecha: datetime, inicio: datetime, fin: datetime) -> bool:
    """
    Verifica si una fecha está dentro de un rango (inclusive).
    
    Args:
        fecha: Fecha a verificar
        inicio: Inicio del rango
        fin: Fin del rango
        
    Returns:
        bool: True si la fecha está en el rango
    
    Example:
        >>> fecha = datetime(2024, 12, 25, 15, 0)
        >>> inicio = datetime(2024, 12, 1, 0, 0)
        >>> fin = datetime(2024, 12, 31, 23, 59)
        >>> fecha_en_rango(fecha, inicio, fin)
        True
    """
    return inicio <= fecha <= fin


def sumar_dias(fecha: datetime, dias: int) -> datetime:
    """
    Suma (o resta) días a una fecha.
    
    Args:
        fecha: Fecha base
        dias: Número de días a sumar (puede ser negativo para restar)
        
    Returns:
        datetime: Nueva fecha
    
    Examples:
        >>> fecha = datetime(2024, 12, 25, 15, 0)
        >>> sumar_dias(fecha, 5)
        datetime(2024, 12, 30, 15, 0)
        
        >>> sumar_dias(fecha, -3)
        datetime(2024, 12, 22, 15, 0)
    """
    return fecha + timedelta(days=dias)


def sumar_horas(fecha: datetime, horas: int) -> datetime:
    """
    Suma (o resta) horas a una fecha.
    
    Args:
        fecha: Fecha base
        horas: Número de horas a sumar (puede ser negativo)
        
    Returns:
        datetime: Nueva fecha
    """
    return fecha + timedelta(hours=horas)


def es_fin_de_semana(fecha: datetime) -> bool:
    """
    Verifica si una fecha cae en fin de semana.
    
    Args:
        fecha: Fecha a verificar
        
    Returns:
        bool: True si es sábado o domingo
    """
    return fecha.weekday() >= 5  # 5 = Sábado, 6 = Domingo


def obtener_nombre_dia(fecha: datetime) -> str:
    """
    Obtiene el nombre del día de la semana.
    
    Args:
        fecha: Fecha
        
    Returns:
        str: Nombre del día en español
    """
    return DIAS_SEMANA[fecha.weekday()]


def obtener_nombre_mes(fecha: datetime) -> str:
    """
    Obtiene el nombre del mes.
    
    Args:
        fecha: Fecha
        
    Returns:
        str: Nombre del mes en español
    """
    return MESES[fecha.month - 1]


# =============================================================================
# VALIDACIÓN DE NÚMEROS Y TEXTO
# =============================================================================

def validar_numero_positivo(valor_str: str, 
                            nombre_campo: str = "valor",
                            minimo: int = None,
                            maximo: int = None) -> Tuple[bool, Any]:
    """
    Valida que una cadena sea un número entero positivo.
    
    Restricciones:
    - No se permiten letras
    - No se permiten números negativos
    - Opcionalmente valida rango mínimo y máximo
    
    Args:
        valor_str: Cadena a validar
        nombre_campo: Nombre del campo para mensajes de error
        minimo: Valor mínimo permitido (opcional)
        maximo: Valor máximo permitido (opcional)
        
    Returns:
        Tuple[bool, Any]: (True, numero) si es válido,
                          (False, mensaje_error) si no es válido
    
    Examples:
        >>> validar_numero_positivo("25")
        (True, 25)
        
        >>> validar_numero_positivo("-5")
        (False, "El valor no puede ser negativo")
        
        >>> validar_numero_positivo("abc")
        (False, "El valor no puede contener letras")
        
        >>> validar_numero_positivo("15", minimo=1, maximo=10)
        (False, "El valor no puede ser mayor a 10")
    """
    # Validar que no esté vacío
    if not valor_str or not valor_str.strip():
        return False, f"El {nombre_campo} no puede estar vacío"
    
    valor_str = valor_str.strip()
    
    # Verificar que no contenga letras
    if any(c.isalpha() for c in valor_str):
        return False, f"El {nombre_campo} no puede contener letras"
    
    # Verificar signo negativo
    if '-' in valor_str:
        return False, f"El {nombre_campo} no puede ser negativo"
    
    # Verificar caracteres válidos
    caracteres_permitidos = set('0123456789')
    caracteres_entrada = set(valor_str)
    caracteres_invalidos = caracteres_entrada - caracteres_permitidos
    
    if caracteres_invalidos:
        caracteres_str = ', '.join(f"'{c}'" for c in caracteres_invalidos)
        return False, f"El {nombre_campo} contiene caracteres no válidos: {caracteres_str}"
    
    # Intentar convertir a número
    try:
        numero = int(valor_str)
    except ValueError:
        return False, f"El {nombre_campo} debe ser un número válido"
    
    # Validar que sea positivo
    if numero < 0:
        return False, f"El {nombre_campo} no puede ser negativo"
    
    # Validar mínimo
    if minimo is not None and numero < minimo:
        return False, f"El {nombre_campo} debe ser al menos {minimo}"
    
    # Validar máximo
    if maximo is not None and numero > maximo:
        return False, f"El {nombre_campo} no puede ser mayor a {maximo}"
    
    return True, numero


def validar_texto_no_vacio(texto: str, 
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
    
    Examples:
        >>> validar_texto_no_vacio("Manchester United", "equipo")
        (True, "Manchester United")
        
        >>> validar_texto_no_vacio("", "equipo")
        (False, "El equipo no puede estar vacío")
        
        >>> validar_texto_no_vacio("AB", "equipo", min_longitud=3)
        (False, "El equipo debe tener al menos 3 caracteres")
    """
    # Validar None
    if texto is None:
        return False, f"El {nombre_campo} no puede estar vacío"
    
    # Limpiar espacios
    texto_limpio = texto.strip()
    
    # Validar longitud mínima
    if len(texto_limpio) < min_longitud:
        if min_longitud == 1:
            return False, f"El {nombre_campo} no puede estar vacío"
        else:
            return False, f"El {nombre_campo} debe tener al menos {min_longitud} caracteres"
    
    # Validar longitud máxima
    if max_longitud is not None and len(texto_limpio) > max_longitud:
        return False, f"El {nombre_campo} no puede tener más de {max_longitud} caracteres"
    
    return True, texto_limpio


def validar_nombre_equipo(nombre: str) -> Tuple[bool, str]:
    """
    Valida el nombre de un equipo de fútbol.
    
    Permite letras (incluyendo acentos), números, espacios, puntos y guiones.
    
    Args:
        nombre: Nombre del equipo a validar
        
    Returns:
        Tuple[bool, str]: (True, nombre_limpio) si es válido,
                          (False, mensaje_error) si no es válido
    
    Examples:
        >>> validar_nombre_equipo("Manchester United")
        (True, "Manchester United")
        
        >>> validar_nombre_equipo("Real Madrid C.F.")
        (True, "Real Madrid C.F.")
        
        >>> validar_nombre_equipo("")
        (False, "El nombre del equipo no puede estar vacío")
    """
    # Validar longitud básica
    valido, resultado = validar_texto_no_vacio(
        nombre,
        "nombre del equipo",
        min_longitud=2,
        max_longitud=50
    )
    
    if not valido:
        return False, resultado
    
    # Caracteres permitidos para nombres de equipos
    caracteres_permitidos = set(
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        ' .-'
        'áéíóúÁÉÍÓÚ'
        'àèìòùÀÈÌÒÙ'
        'äëïöüÄËÏÖÜ'
        'âêîôûÂÊÎÔÛ'
        'ñÑçÇ'
        "'"
    )
    
    for char in resultado:
        if char not in caracteres_permitidos:
            return False, f"El nombre del equipo contiene caracteres no válidos: '{char}'"
    
    return True, resultado


# =============================================================================
# FUNCIONES DE AYUDA PARA INTERFAZ
# =============================================================================

def obtener_fecha_actual_formateada() -> str:
    """
    Obtiene la fecha y hora actual formateada.
    
    Returns:
        str: Fecha actual en formato DD/MM/AAAA HH:MM
    """
    return formatear_fecha(datetime.now())


def obtener_proxima_hora_partido(fecha_base: datetime = None) -> datetime:
    """
    Obtiene la próxima hora válida para un partido.
    
    Busca la próxima hora entre las 10:00 y 22:00.
    
    Args:
        fecha_base: Fecha base (default: ahora)
        
    Returns:
        datetime: Próxima fecha/hora válida para partido
    """
    if fecha_base is None:
        fecha_base = datetime.now()
    
    # Si la hora actual es válida, usar la siguiente hora completa
    if HORA_MINIMA_PARTIDO <= fecha_base.hour < HORA_MAXIMA_PARTIDO:
        proxima = fecha_base.replace(minute=0, second=0, microsecond=0)
        proxima = proxima + timedelta(hours=1)
        
        if proxima.hour <= HORA_MAXIMA_PARTIDO:
            return proxima
    
    # Si es muy tarde, ir al día siguiente
    if fecha_base.hour >= HORA_MAXIMA_PARTIDO:
        siguiente_dia = fecha_base + timedelta(days=1)
        return siguiente_dia.replace(
            hour=HORA_MINIMA_PARTIDO, 
            minute=0, 
            second=0, 
            microsecond=0
        )
    
    # Si es muy temprano, usar la hora mínima del mismo día
    return fecha_base.replace(
        hour=HORA_MINIMA_PARTIDO, 
        minute=0, 
        second=0, 
        microsecond=0
    )


def generar_opciones_horario(fecha: datetime) -> list:
    """
    Genera una lista de horarios típicos para partidos.
    
    Args:
        fecha: Fecha para la cual generar horarios
        
    Returns:
        list: Lista de tuplas (datetime, str_formateado)
    """
    horarios_tipicos = [12, 14, 16, 17, 18, 20, 21]
    opciones = []
    
    for hora in horarios_tipicos:
        if HORA_MINIMA_PARTIDO <= hora <= HORA_MAXIMA_PARTIDO:
            fecha_opcion = fecha.replace(
                hour=hora, 
                minute=0, 
                second=0, 
                microsecond=0
            )
            
            # Solo incluir si es fecha futura
            if fecha_opcion > datetime.now():
                opciones.append((
                    fecha_opcion,
                    formatear_fecha(fecha_opcion)
                ))
    
    return opciones


def calcular_fecha_fin_partido(fecha_inicio: datetime, 
                                duracion_horas: int = 2) -> datetime:
    """
    Calcula la fecha de fin de un partido.
    
    Args:
        fecha_inicio: Fecha y hora de inicio
        duracion_horas: Duración en horas (default: 2)
        
    Returns:
        datetime: Fecha y hora de fin
    """
    return fecha_inicio + timedelta(hours=duracion_horas)
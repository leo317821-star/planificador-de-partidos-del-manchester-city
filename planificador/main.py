"""
=============================================================================
PLANIFICADOR INTELIGENTE DE EVENTOS - ETIHAD STADIUM
=============================================================================
Sistema de gestión de partidos de fútbol con control de recursos
y restricciones de disponibilidad.

Autor: Asistente IA
Dominio: Estadio de Fútbol (Etihad Stadium - Manchester City FC)

Restricciones implementadas:
1. Co-requisito: Todo partido requiere equipo arbitral completo
   - 1 árbitro principal
   - 2 árbitros de línea
   - 1 cuarto árbitro

2. Exclusión mutua: Los árbitros necesitan 7 días de descanso entre partidos

3. Descanso del estadio: Mínimo 2 días entre partidos
=============================================================================
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.evento import Partido
from models.recurso import Arbitro, TipoArbitro
from services.planificador import PlanificadorEventos
from services.persistencia import GestorPersistencia
from utils.fecha_utils import validar_fecha, formatear_fecha, formatear_fecha_larga


class InterfazConsola:
    """
    Interfaz de línea de comandos para el Planificador de Eventos del Etihad Stadium.
    
    Proporciona un menú interactivo para:
    - Planificar nuevos partidos
    - Listar partidos existentes
    - Ver detalles de partidos y árbitros
    - Buscar horarios disponibles
    - Guardar y cargar datos
    """
    
    def __init__(self):
        """Inicializa la interfaz con el planificador y recursos por defecto."""
        self.planificador = PlanificadorEventos()
        self.gestor_persistencia = GestorPersistencia()
        self.archivo_datos = "data/datos_ejemplo.json"
        self._inicializar_recursos_default()
    
    def _inicializar_recursos_default(self):
        """
        Inicializa los árbitros disponibles por defecto.
        
        Crea:
        - 6 árbitros principales
        - 10 árbitros de línea
        - 6 cuartos árbitros
        """
        # Árbitros principales
        arbitros_principales = [
            "Michael Oliver", "Anthony Taylor", "Martin Atkinson",
            "Paul Tierney", "Craig Pawson", "David Coote"
        ]
        
        # Árbitros de línea
        arbitros_linea = [
            "Gary Beswick", "Adam Nunn", "Scott Ledger",
            "Constantine Hatzidakis", "Nick Hopton", "Ian Hussin",
            "Simon Long", "Derek Eaton", "Marc Perry", "James Mainwaring"
        ]
        
        # Cuartos árbitros
        cuartos_arbitros = [
            "Robert Jones", "Andy Madley", "Peter Bankes",
            "John Brooks", "Graham Scott", "Darren Bond"
        ]
        
        # Agregar árbitros principales
        for nombre in arbitros_principales:
            self.planificador.agregar_recurso(
                Arbitro(nombre, TipoArbitro.PRINCIPAL)
            )
        
        # Agregar árbitros de línea
        for nombre in arbitros_linea:
            self.planificador.agregar_recurso(
                Arbitro(nombre, TipoArbitro.LINEA)
            )
        
        # Agregar cuartos árbitros
        for nombre in cuartos_arbitros:
            self.planificador.agregar_recurso(
                Arbitro(nombre, TipoArbitro.CUARTO)
            )
    
    # =========================================================================
    # UTILIDADES DE INTERFAZ
    # =========================================================================
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pausar(self, mensaje: str = "Presione ENTER para continuar..."):
        """Pausa la ejecución hasta que el usuario presione ENTER."""
        input(f"\n{mensaje}")
    
    def mostrar_banner(self):
        """Muestra el banner principal de la aplicación."""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ⚽  PLANIFICADOR DE EVENTOS - ETIHAD STADIUM  ⚽             ║
║                                                                  ║
║         Sistema Inteligente de Gestión de Partidos               ║
║                    Manchester City FC                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal de opciones."""
        menu = """
┌──────────────────────────────────────────────────────────────────┐
│                      MENÚ PRINCIPAL                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [1] 📅  Planificar nuevo partido                               │
│   [2] 📋  Listar todos los partidos                              │
│   [3] 🔍  Ver detalles de un partido                             │
│   [4] ❌  Eliminar un partido                                    │
│   [5] 🔎  Buscar próximo horario disponible                      │
│   [6] 👨‍⚖️  Ver árbitros disponibles                              │
│   [7] 📊  Ver agenda de un árbitro                               │
│   [8] 💾  Guardar datos                                          │
│   [9] 📂  Cargar datos                                           │
│   [0] 🚪  Salir                                                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
        """
        print(menu)
    
    # =========================================================================
    # MÉTODOS DE ENTRADA CON VALIDACIÓN
    # =========================================================================
    
    def solicitar_fecha(self, mensaje: str) -> datetime:
        """
        Solicita una fecha al usuario con validación completa.
        
        Valida que:
        - No contenga letras
        - No contenga números negativos
        - Tenga el formato correcto DD/MM/AAAA HH:MM
        - Sea una fecha futura
        - La hora esté entre 10:00 y 22:00
        
        Args:
            mensaje: Mensaje a mostrar al usuario
            
        Returns:
            datetime: Fecha válida ingresada por el usuario
        """
        while True:
            print(f"\n{mensaje}")
            print("Formato: DD/MM/AAAA HH:MM (ejemplo: 25/12/2024 15:00)")
            print("⚠️  No se permiten letras ni números negativos")
            
            entrada = input(">>> ").strip()
            
            es_valida, resultado = validar_fecha(entrada)
            
            if es_valida:
                return resultado
            else:
                print(f"\n❌ ERROR: {resultado}")
                print("   Por favor, intente nuevamente.")
    
    def solicitar_entero_positivo(self, mensaje: str, 
                                   minimo: int = 0, 
                                   maximo: int = None) -> int:
        """
        Solicita un número entero positivo al usuario.
        
        Valida que:
        - No contenga letras
        - No sea negativo
        - Esté dentro del rango especificado
        
        Args:
            mensaje: Mensaje a mostrar
            minimo: Valor mínimo permitido (default: 0)
            maximo: Valor máximo permitido (opcional)
            
        Returns:
            int: Número válido ingresado
        """
        while True:
            try:
                entrada = input(f"{mensaje}: ").strip()
                
                # Verificar que no contenga letras
                if any(c.isalpha() for c in entrada):
                    print("❌ ERROR: No se permiten letras. Ingrese solo números.")
                    continue
                
                # Verificar que no sea negativo (incluyendo el signo -)
                if '-' in entrada:
                    print("❌ ERROR: No se permiten números negativos.")
                    continue
                
                # Verificar que no esté vacío
                if not entrada:
                    print("❌ ERROR: Debe ingresar un valor.")
                    continue
                
                numero = int(entrada)
                
                # Validar mínimo
                if numero < minimo:
                    print(f"❌ ERROR: El valor debe ser al menos {minimo}.")
                    continue
                
                # Validar máximo
                if maximo is not None and numero > maximo:
                    print(f"❌ ERROR: El valor no puede ser mayor a {maximo}.")
                    continue
                
                return numero
                
            except ValueError:
                print("❌ ERROR: Ingrese un número válido.")
    
    def solicitar_texto(self, mensaje: str, minimo_caracteres: int = 1) -> str:
        """
        Solicita texto al usuario con validación.
        
        Args:
            mensaje: Mensaje a mostrar
            minimo_caracteres: Longitud mínima del texto (default: 1)
            
        Returns:
            str: Texto válido ingresado
        """
        while True:
            entrada = input(f"{mensaje}: ").strip()
            
            if len(entrada) < minimo_caracteres:
                print(f"❌ ERROR: Debe ingresar al menos {minimo_caracteres} caracter(es).")
                continue
            
            return entrada
    
    # =========================================================================
    # FUNCIONALIDAD: PLANIFICAR PARTIDO
    # =========================================================================
    
    def planificar_partido(self):
        """
        Proceso completo para planificar un nuevo partido.
        
        Pasos:
        1. Solicitar equipo visitante
        2. Solicitar fecha y hora
        3. Seleccionar árbitro principal
        4. Seleccionar 2 árbitros de línea
        5. Seleccionar cuarto árbitro
        6. Validar y crear el partido
        """
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         📅 PLANIFICAR NUEVO PARTIDO")
        print("=" * 60)
        
        # Solicitar equipo visitante
        print("\n📌 INFORMACIÓN DEL PARTIDO")
        print("-" * 40)
        equipo_visitante = self.solicitar_texto(
            "Nombre del equipo visitante",
            minimo_caracteres=2
        )
        
        # Solicitar fecha y hora
        print("\n📌 FECHA Y HORA DEL PARTIDO")
        print("-" * 40)
        fecha_inicio = self.solicitar_fecha("Ingrese la fecha y hora del partido:")
        
        # Duración estándar de un partido (2 horas incluyendo descanso)
        duracion_horas = 2
        fecha_fin = fecha_inicio + timedelta(hours=duracion_horas)
        
        print(f"\n✅ Partido programado:")
        print(f"   {formatear_fecha_larga(fecha_inicio)}")
        print(f"   Duración estimada: {duracion_horas} horas")
        
        # Seleccionar árbitros
        print("\n📌 SELECCIÓN DE ÁRBITROS")
        print("-" * 40)
        print("Recuerde: Los árbitros necesitan 7 días de descanso entre partidos.")
        
        # Árbitro principal
        print("\n👨‍⚖️ ÁRBITRO PRINCIPAL (se necesita 1):")
        arbitro_principal = self._seleccionar_arbitro(
            TipoArbitro.PRINCIPAL,
            fecha_inicio,
            fecha_fin
        )
        if not arbitro_principal:
            return
        
        # Árbitros de línea (2)
        print("\n👨‍⚖️ ÁRBITROS DE LÍNEA (se necesitan 2):")
        arbitros_linea = []
        for i in range(2):
            print(f"\n   Seleccione árbitro de línea {i + 1}:")
            arbitro = self._seleccionar_arbitro(
                TipoArbitro.LINEA,
                fecha_inicio,
                fecha_fin,
                excluir=arbitros_linea
            )
            if not arbitro:
                return
            arbitros_linea.append(arbitro)
        
        # Cuarto árbitro
        print("\n👨‍⚖️ CUARTO ÁRBITRO (se necesita 1):")
        cuarto_arbitro = self._seleccionar_arbitro(
            TipoArbitro.CUARTO,
            fecha_inicio,
            fecha_fin
        )
        if not cuarto_arbitro:
            return
        
        # Crear el partido con todos los recursos
        recursos = [arbitro_principal] + arbitros_linea + [cuarto_arbitro]
        
        partido = Partido(
            equipo_local="Manchester City",
            equipo_visitante=equipo_visitante,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            recursos=recursos
        )
        
        # Intentar planificar
        exito, mensaje = self.planificador.planificar_evento(partido)
        
        if exito:
            print("\n" + "=" * 60)
            print("✅ ¡PARTIDO PLANIFICADO EXITOSAMENTE!")
            print("=" * 60)
            print(partido.obtener_detalles())
        else:
            print("\n" + "=" * 60)
            print("❌ NO SE PUDO PLANIFICAR EL PARTIDO")
            print("=" * 60)
            print(f"\nRazón: {mensaje}")
        
        self.pausar()
    
    def _seleccionar_arbitro(self, tipo: TipoArbitro, 
                              fecha_inicio: datetime,
                              fecha_fin: datetime, 
                              excluir: list = None) -> Arbitro:
        """
        Permite al usuario seleccionar un árbitro disponible.
        
        Args:
            tipo: Tipo de árbitro a seleccionar
            fecha_inicio: Fecha de inicio del partido
            fecha_fin: Fecha de fin del partido
            excluir: Lista de árbitros a excluir de la selección
            
        Returns:
            Arbitro seleccionado o None si se cancela
        """
        excluir = excluir or []
        excluir_ids = [a.id for a in excluir]
        
        # Obtener árbitros disponibles del tipo especificado
        arbitros_disponibles = self.planificador.obtener_arbitros_disponibles(
            tipo, fecha_inicio, fecha_fin, excluir_ids
        )
        
        if not arbitros_disponibles:
            print(f"\n❌ No hay árbitros de tipo '{tipo.value}' disponibles para esta fecha.")
            print("   Recuerde: Los árbitros necesitan 7 días de descanso entre partidos.")
            return None
        
        # Mostrar lista de árbitros disponibles
        print(f"\n   Árbitros disponibles ({tipo.value}):")
        for i, arbitro in enumerate(arbitros_disponibles, 1):
            print(f"   [{i}] {arbitro.nombre}")
        print(f"   [0] Cancelar operación")
        
        # Solicitar selección
        seleccion = self.solicitar_entero_positivo(
            "   Seleccione una opción",
            minimo=0,
            maximo=len(arbitros_disponibles)
        )
        
        if seleccion == 0:
            print("\n   ❌ Operación cancelada por el usuario.")
            return None
        
        arbitro_seleccionado = arbitros_disponibles[seleccion - 1]
        print(f"   ✅ Seleccionado: {arbitro_seleccionado.nombre}")
        
        return arbitro_seleccionado
    
    # =========================================================================
    # FUNCIONALIDAD: LISTAR PARTIDOS
    # =========================================================================
    
    def listar_partidos(self):
        """Muestra todos los partidos planificados ordenados por fecha."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         📋 PARTIDOS PLANIFICADOS")
        print("=" * 60)
        
        eventos = self.planificador.obtener_eventos()
        
        if not eventos:
            print("\n📭 No hay partidos planificados actualmente.")
            print("   Use la opción [1] del menú para planificar un nuevo partido.")
        else:
            # Ordenar por fecha
            eventos_ordenados = sorted(eventos, key=lambda e: e.fecha_inicio)
            
            print(f"\n📊 Total de partidos: {len(eventos_ordenados)}")
            print("-" * 60)
            
            for i, partido in enumerate(eventos_ordenados, 1):
                # Determinar estado del partido
                if partido.fecha_inicio > datetime.now():
                    estado = "🟢 PRÓXIMO"
                else:
                    estado = "🔴 PASADO"
                
                print(f"\n┌{'─' * 56}┐")
                print(f"│ {i}. {partido.nombre[:48]:<48} │")
                print(f"│    📅 {formatear_fecha(partido.fecha_inicio):<46} │")
                print(f"│    {estado:<52} │")
                print(f"└{'─' * 56}┘")
        
        self.pausar()
    
    # =========================================================================
    # FUNCIONALIDAD: VER DETALLES DE PARTIDO
    # =========================================================================
    
    def ver_detalles_partido(self):
        """Muestra los detalles completos de un partido específico."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         🔍 DETALLES DE PARTIDO")
        print("=" * 60)
        
        eventos = self.planificador.obtener_eventos()
        
        if not eventos:
            print("\n📭 No hay partidos planificados.")
            self.pausar()
            return
        
        # Mostrar lista de partidos para seleccionar
        eventos_ordenados = sorted(eventos, key=lambda e: e.fecha_inicio)
        
        print("\nPartidos disponibles:")
        print("-" * 40)
        for i, partido in enumerate(eventos_ordenados, 1):
            print(f"   [{i}] {partido.nombre}")
            print(f"       {formatear_fecha(partido.fecha_inicio)}")
        print(f"   [0] Cancelar")
        
        # Solicitar selección
        seleccion = self.solicitar_entero_positivo(
            "\nSeleccione el partido",
            minimo=0,
            maximo=len(eventos_ordenados)
        )
        
        if seleccion == 0:
            return
        
        # Mostrar detalles del partido seleccionado
        partido = eventos_ordenados[seleccion - 1]
        print(partido.obtener_detalles())
        
        self.pausar()
    
    # =========================================================================
    # FUNCIONALIDAD: ELIMINAR PARTIDO
    # =========================================================================
    
    def eliminar_partido(self):
        """Elimina un partido planificado, liberando los árbitros asignados."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         ❌ ELIMINAR PARTIDO")
        print("=" * 60)
        
        eventos = self.planificador.obtener_eventos()
        
        if not eventos:
            print("\n📭 No hay partidos planificados para eliminar.")
            self.pausar()
            return
        
        # Mostrar lista de partidos
        eventos_ordenados = sorted(eventos, key=lambda e: e.fecha_inicio)
        
        print("\nPartidos disponibles:")
        print("-" * 40)
        for i, partido in enumerate(eventos_ordenados, 1):
            print(f"   [{i}] {partido.nombre}")
            print(f"       {formatear_fecha(partido.fecha_inicio)}")
        print(f"   [0] Cancelar")
        
        # Solicitar selección
        seleccion = self.solicitar_entero_positivo(
            "\nSeleccione el partido a eliminar",
            minimo=0,
            maximo=len(eventos_ordenados)
        )
        
        if seleccion == 0:
            print("\n❌ Operación cancelada.")
            self.pausar()
            return
        
        partido = eventos_ordenados[seleccion - 1]
        
        # Confirmar eliminación
        print(f"\n⚠️  ¿Está seguro de eliminar el siguiente partido?")
        print(f"\n   {partido.nombre}")
        print(f"   {formatear_fecha(partido.fecha_inicio)}")
        print(f"\n   Los árbitros asignados quedarán liberados.")
        
        confirmacion = input("\nEscriba 'SI' para confirmar: ").strip().upper()
        
        if confirmacion == 'SI':
            exito, mensaje = self.planificador.eliminar_evento(partido.id)
            if exito:
                print("\n✅ Partido eliminado exitosamente.")
                print("   Los árbitros han sido liberados y pueden ser asignados a otros partidos.")
            else:
                print(f"\n❌ Error: {mensaje}")
        else:
            print("\n❌ Operación cancelada.")
        
        self.pausar()
    
    # =========================================================================
    # FUNCIONALIDAD: BUSCAR HORARIO DISPONIBLE
    # =========================================================================
    
    def buscar_horario_disponible(self):
        """
        Busca el próximo horario disponible para un partido.
        
        Considera:
        - Disponibilidad del estadio (2 días de descanso)
        - Disponibilidad de árbitros de todos los tipos
        """
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         🔎 BUSCAR PRÓXIMO HORARIO DISPONIBLE")
        print("=" * 60)
        
        print("\nEsta función buscará el próximo horario donde se pueda")
        print("realizar un partido cumpliendo todas las restricciones:")
        print("   • Estadio disponible (2 días de descanso)")
        print("   • Árbitros disponibles (7 días de descanso)")
        print("   • Equipo arbitral completo")
        
        # Solicitar fecha de inicio de búsqueda
        print("\n📌 ¿Desde qué fecha desea buscar?")
        fecha_desde = self.solicitar_fecha("Ingrese la fecha de inicio de búsqueda:")
        
        # Buscar horario
        print("\n🔍 Buscando horario disponible...")
        print("   Esto puede tomar unos segundos...\n")
        
        resultado = self.planificador.buscar_proximo_horario(fecha_desde)
        
        if resultado:
            fecha_sugerida, arbitros_disponibles = resultado
            
            print("=" * 60)
            print("✅ ¡HORARIO DISPONIBLE ENCONTRADO!")
            print("=" * 60)
            
            print(f"\n📅 Fecha sugerida: {formatear_fecha_larga(fecha_sugerida)}")
            
            print(f"\n👨‍⚖️ Árbitros disponibles para esta fecha:")
            print("-" * 40)
            
            for tipo, arbitros in arbitros_disponibles.items():
                print(f"\n   {tipo}:")
                if arbitros:
                    # Mostrar máximo 3 árbitros por tipo
                    for arbitro in arbitros[:3]:
                        print(f"      • {arbitro.nombre}")
                    if len(arbitros) > 3:
                        print(f"      ... y {len(arbitros) - 3} más disponibles")
                else:
                    print(f"      (Ninguno disponible)")
        else:
            print("=" * 60)
            print("❌ NO SE ENCONTRÓ HORARIO DISPONIBLE")
            print("=" * 60)
            print("\nNo se encontró un horario disponible en los próximos 60 días.")
            print("Esto puede deberse a que:")
            print("   • Todos los árbitros están ocupados")
            print("   • El estadio tiene muchos partidos programados")
        
        self.pausar()
    
    # =========================================================================
    # FUNCIONALIDAD: VER ÁRBITROS DISPONIBLES
    # =========================================================================
    
    def ver_arbitros_disponibles(self):
        """Muestra todos los árbitros del sistema organizados por tipo."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         👨‍⚖️ ÁRBITROS DEL SISTEMA")
        print("=" * 60)
        
        # Obtener todos los árbitros
        arbitros = [
            r for r in self.planificador.recursos.values() 
            if isinstance(r, Arbitro)
        ]
        
        # Agrupar por tipo
        por_tipo = {}
        for arbitro in arbitros:
            tipo = arbitro.tipo.value
            if tipo not in por_tipo:
                por_tipo[tipo] = []
            por_tipo[tipo].append(arbitro)
        
        # Mostrar árbitros por tipo
        orden_tipos = ['Árbitro Principal', 'Árbitro de Línea', 'Cuarto Árbitro']
        
        for tipo in orden_tipos:
            if tipo in por_tipo:
                lista = por_tipo[tipo]
                
                print(f"\n┌{'─' * 56}┐")
                print(f"│ {tipo.upper():<54} │")
                print(f"│ Total: {len(lista):<47} │")
                print(f"├{'─' * 56}┤")
                
                for arbitro in lista:
                    # Verificar partidos asignados
                    partidos_asignados = self.planificador.obtener_eventos_recurso(arbitro.id)
                    partidos_futuros = [
                        p for p in partidos_asignados 
                        if p.fecha_inicio > datetime.now()
                    ]
                    
                    if partidos_futuros:
                        estado = f"({len(partidos_futuros)} partido(s) asignado(s))"
                    else:
                        estado = "(Disponible)"
                    
                    nombre_truncado = arbitro.nombre[:30]
                    print(f"│   • {nombre_truncado:<25} {estado:<22} │")
                
                print(f"└{'─' * 56}┘")
        
        self.pausar()
    
    # =========================================================================
    # FUNCIONALIDAD: VER AGENDA DE ÁRBITRO
    # =========================================================================
    
    def ver_agenda_arbitro(self):
        """Muestra la agenda completa de un árbitro específico."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         📊 AGENDA DE ÁRBITRO")
        print("=" * 60)
        
        # Obtener todos los árbitros ordenados
        arbitros = [
            r for r in self.planificador.recursos.values() 
            if isinstance(r, Arbitro)
        ]
        arbitros_ordenados = sorted(arbitros, key=lambda a: (a.tipo.value, a.nombre))
        
        # Mostrar lista de árbitros
        print("\nSeleccione un árbitro:")
        print("-" * 40)
        
        tipo_actual = None
        for i, arbitro in enumerate(arbitros_ordenados, 1):
            # Mostrar encabezado de tipo si cambia
            if arbitro.tipo.value != tipo_actual:
                tipo_actual = arbitro.tipo.value
                print(f"\n   --- {tipo_actual} ---")
            
            print(f"   [{i}] {arbitro.nombre}")
        
        print(f"\n   [0] Cancelar")
        
        # Solicitar selección
        seleccion = self.solicitar_entero_positivo(
            "\nSeleccione una opción",
            minimo=0,
            maximo=len(arbitros_ordenados)
        )
        
        if seleccion == 0:
            return
        
        # Mostrar agenda del árbitro seleccionado
        arbitro = arbitros_ordenados[seleccion - 1]
        
        print("\n" + "=" * 60)
        print(f"         📅 AGENDA: {arbitro.nombre.upper()}")
        print("=" * 60)
        
        print(f"\n   Tipo: {arbitro.tipo.value}")
        print(f"   Nacionalidad: {arbitro.nacionalidad}")
        print(f"   Experiencia: {arbitro.experiencia_anios} años")
        print(f"   Descanso requerido: {Arbitro.DIAS_DESCANSO_REQUERIDOS} días entre partidos")
        
        # Obtener partidos asignados
        partidos = self.planificador.obtener_eventos_recurso(arbitro.id)
        
        if not partidos:
            print("\n   📭 Este árbitro no tiene partidos asignados.")
        else:
            partidos_ordenados = sorted(partidos, key=lambda p: p.fecha_inicio)
            
            # Separar en futuros y pasados
            ahora = datetime.now()
            futuros = [p for p in partidos_ordenados if p.fecha_inicio > ahora]
            pasados = [p for p in partidos_ordenados if p.fecha_inicio <= ahora]
            
            print(f"\n   📊 Total de partidos: {len(partidos_ordenados)}")
            print(f"      • Próximos: {len(futuros)}")
            print(f"      • Pasados: {len(pasados)}")
            
            if futuros:
                print(f"\n   🟢 PRÓXIMOS PARTIDOS:")
                print("   " + "-" * 40)
                for partido in futuros:
                    print(f"\n   📅 {formatear_fecha(partido.fecha_inicio)}")
                    print(f"      {partido.nombre}")
            
            if pasados:
                print(f"\n   🔴 PARTIDOS PASADOS:")
                print("   " + "-" * 40)
                for partido in pasados[-5:]:  # Mostrar solo los últimos 5
                    print(f"\n   📅 {formatear_fecha(partido.fecha_inicio)}")
                    print(f"      {partido.nombre}")
                
                if len(pasados) > 5:
                    print(f"\n   ... y {len(pasados) - 5} partidos anteriores")
        
        self.pausar()
    
    # =========================================================================
    # FUNCIONALIDAD: GUARDAR DATOS
    # =========================================================================
    
    def guardar_datos(self):
        """Guarda todos los datos del planificador en un archivo JSON."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         💾 GUARDAR DATOS")
        print("=" * 60)
        
        # Mostrar información actual
        num_eventos = len(self.planificador.eventos)
        num_recursos = len(self.planificador.recursos)
        
        print(f"\n📊 Estado actual del sistema:")
        print(f"   • Partidos planificados: {num_eventos}")
        print(f"   • Árbitros registrados: {num_recursos}")
        
        print(f"\n📁 Archivo de destino: {self.archivo_datos}")
        
        # Confirmar guardado
        confirmacion = input("\n¿Desea guardar los datos? (S/N): ").strip().upper()
        
        if confirmacion == 'S':
            exito, mensaje = self.gestor_persistencia.guardar(
                self.planificador,
                self.archivo_datos
            )
            
            if exito:
                print("\n✅ Datos guardados exitosamente.")
                print(f"   {mensaje}")
            else:
                print(f"\n❌ Error al guardar: {mensaje}")
        else:
            print("\n❌ Operación cancelada.")
        
        self.pausar()
    
    # =========================================================================
    # FUNCIONALIDAD: CARGAR DATOS
    # =========================================================================
    
    def cargar_datos(self):
        """Carga los datos del planificador desde un archivo JSON."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("         📂 CARGAR DATOS")
        print("=" * 60)
        
        print(f"\n📁 Archivo a cargar: {self.archivo_datos}")
        
        # Verificar si el archivo existe
        if not self.gestor_persistencia.existe_archivo(self.archivo_datos):
            print(f"\n⚠️  El archivo '{self.archivo_datos}' no existe.")
            print("   Se utilizarán los datos por defecto del sistema.")
            self.pausar()
            return
        
        # Mostrar información del archivo
        info = self.gestor_persistencia.obtener_info_archivo(self.archivo_datos)
        if info:
            print(f"\n📊 Información del archivo:")
            print(f"   • Versión: {info.get('version', 'Desconocida')}")
            print(f"   • Recursos: {info.get('num_recursos', 0)}")
            print(f"   • Eventos: {info.get('num_eventos', 0)}")
            print(f"   • Tamaño: {info.get('tamanio_bytes', 0)} bytes")
        
        # Advertencia
        print("\n⚠️  ADVERTENCIA: Esto reemplazará todos los datos actuales.")
        print("   Los partidos y configuraciones actuales se perderán.")
        
        # Confirmar carga
        confirmacion = input("\n¿Desea cargar los datos? (S/N): ").strip().upper()
        
        if confirmacion == 'S':
            exito, resultado = self.gestor_persistencia.cargar(self.archivo_datos)
            
            if exito:
                self.planificador = resultado
                print("\n✅ Datos cargados exitosamente.")
                print(f"   • Partidos cargados: {len(self.planificador.eventos)}")
                print(f"   • Recursos cargados: {len(self.planificador.recursos)}")
            else:
                print(f"\n❌ Error al cargar: {resultado}")
        else:
            print("\n❌ Operación cancelada.")
        
        self.pausar()
    
    # =========================================================================
    # BUCLE PRINCIPAL
    # =========================================================================
    
    def ejecutar(self):
        """
        Bucle principal de la aplicación.
        
        Muestra el menú y procesa las opciones del usuario
        hasta que decida salir.
        """
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()
            self.mostrar_menu_principal()
            
            opcion = input("Seleccione una opción: ").strip()
            
            if opcion == '1':
                self.planificar_partido()
            elif opcion == '2':
                self.listar_partidos()
            elif opcion == '3':
                self.ver_detalles_partido()
            elif opcion == '4':
                self.eliminar_partido()
            elif opcion == '5':
                self.buscar_horario_disponible()
            elif opcion == '6':
                self.ver_arbitros_disponibles()
            elif opcion == '7':
                self.ver_agenda_arbitro()
            elif opcion == '8':
                self.guardar_datos()
            elif opcion == '9':
                self.cargar_datos()
            elif opcion == '0':
                self.salir()
                break
            else:
                print("\n❌ Opción no válida. Por favor, seleccione una opción del menú.")
                self.pausar()
    
    def salir(self):
        """Muestra mensaje de despedida y termina la aplicación."""
        self.limpiar_pantalla()
        print("\n" + "=" * 60)
        print("   ¡Gracias por usar el Planificador del Etihad Stadium!")
        print("=" * 60)
        print("""
                    ⚽ ¡Hasta pronto! ⚽
        
           Manchester City FC - Etihad Stadium
              "Superbia in Proelio"
        """)
        print("=" * 60 + "\n")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """Función principal que inicia la aplicación."""
    try:
        app = InterfazConsola()
        app.ejecutar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Aplicación interrumpida por el usuario.")
        print("   ¡Hasta pronto!\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("   Por favor, contacte al administrador del sistema.\n")
        raise


if __name__ == "__main__":
    main()
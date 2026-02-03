"""
=============================================================================
MÓDULO PERSISTENCIA - PLANIFICADOR DE EVENTOS ETIHAD STADIUM
=============================================================================
Servicio de persistencia de datos.
Gestiona el guardado y carga de datos desde archivos JSON.
=============================================================================
"""

import json
import os
from datetime import datetime
from typing import Tuple, Any, Optional, Dict

from models.evento import Evento, Partido
from models.recurso import Recurso, Arbitro, TipoArbitro


class GestorPersistencia:
    """
    Clase encargada de gestionar la persistencia de datos del sistema.
    
    Permite guardar y cargar el estado completo del planificador
    (recursos y eventos) en archivos JSON.
    
    Attributes:
        VERSION (str): Versión del formato de datos
        ENCODING (str): Codificación de archivos
    
    Example:
        >>> gestor = GestorPersistencia()
        >>> exito, mensaje = gestor.guardar(planificador, "datos.json")
        >>> if exito:
        ...     print("Datos guardados correctamente")
        
        >>> exito, resultado = gestor.cargar("datos.json")
        >>> if exito:
        ...     planificador = resultado
    """
    
    VERSION = "1.0"
    ENCODING = "utf-8"
    
    def __init__(self):
        """Inicializa el gestor de persistencia."""
        pass
    
    # =========================================================================
    # GUARDADO DE DATOS
    # =========================================================================
    
    def guardar(self, planificador, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Guarda el estado del planificador en un archivo JSON.
        
        Args:
            planificador: Instancia del PlanificadorEventos a guardar
            ruta_archivo: Ruta del archivo donde guardar
            
        Returns:
            Tuple[bool, str]: (True, mensaje_exito) o (False, mensaje_error)
        
        Example:
            >>> gestor = GestorPersistencia()
            >>> exito, mensaje = gestor.guardar(planificador, "data/partidos.json")
        """
        try:
            # Crear directorio si no existe
            directorio = os.path.dirname(ruta_archivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio)
            
            # Construir estructura de datos
            datos = self._construir_datos_guardado(planificador)
            
            # Guardar en archivo
            with open(ruta_archivo, 'w', encoding=self.ENCODING) as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            
            return True, (
                f"Datos guardados exitosamente en '{ruta_archivo}'. "
                f"Recursos: {len(planificador.recursos)}, "
                f"Eventos: {len(planificador.eventos)}"
            )
            
        except PermissionError:
            return False, f"Error de permisos: No se puede escribir en '{ruta_archivo}'"
        except OSError as e:
            return False, f"Error del sistema de archivos: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado al guardar: {str(e)}"
    
    def _construir_datos_guardado(self, planificador) -> Dict:
        """
        Construye la estructura de datos para guardar.
        
        Args:
            planificador: Instancia del PlanificadorEventos
            
        Returns:
            Dict: Estructura de datos lista para serializar
        """
        return {
            'metadata': {
                'version': self.VERSION,
                'aplicacion': 'Planificador Etihad Stadium',
                'fecha_guardado': datetime.now().isoformat(),
                'descripcion': 'Datos del planificador de eventos'
            },
            'recursos': [
                self._recurso_a_dict(r) 
                for r in planificador.recursos.values()
            ],
            'eventos': [
                self._evento_a_dict(e) 
                for e in planificador.eventos.values()
            ]
        }
    
    def _recurso_a_dict(self, recurso: Recurso) -> Dict:
        """
        Convierte un recurso a diccionario.
        
        Args:
            recurso: Recurso a convertir
            
        Returns:
            Dict: Representación del recurso
        """
        if isinstance(recurso, Arbitro):
            return {
                'id': recurso.id,
                'tipo_clase': 'Arbitro',
                'nombre': recurso.nombre,
                'descripcion': recurso.descripcion,
                'tipo_arbitro': recurso.tipo.value,
                'nacionalidad': recurso.nacionalidad,
                'experiencia_anios': recurso.experiencia_anios
            }
        else:
            return {
                'id': recurso.id,
                'tipo_clase': 'Recurso',
                'nombre': recurso.nombre,
                'descripcion': recurso.descripcion
            }
    
    def _evento_a_dict(self, evento: Evento) -> Dict:
        """
        Convierte un evento a diccionario.
        
        Args:
            evento: Evento a convertir
            
        Returns:
            Dict: Representación del evento
        """
        datos_base = {
            'id': evento.id,
            'tipo': evento.__class__.__name__,
            'nombre': evento.nombre,
            'fecha_inicio': evento.fecha_inicio.isoformat(),
            'fecha_fin': evento.fecha_fin.isoformat(),
            'recursos_ids': [r.id for r in evento.recursos]
        }
        
        if isinstance(evento, Partido):
            datos_base['equipo_local'] = evento.equipo_local
            datos_base['equipo_visitante'] = evento.equipo_visitante
        
        return datos_base
    
    # =========================================================================
    # CARGA DE DATOS
    # =========================================================================
    
    def cargar(self, ruta_archivo: str) -> Tuple[bool, Any]:
        """
        Carga el estado del planificador desde un archivo JSON.
        
        Args:
            ruta_archivo: Ruta del archivo a cargar
            
        Returns:
            Tuple[bool, Any]: (True, planificador) si se cargó correctamente,
                              (False, mensaje_error) si hubo error
        
        Example:
            >>> gestor = GestorPersistencia()
            >>> exito, resultado = gestor.cargar("data/partidos.json")
            >>> if exito:
            ...     planificador = resultado
            ... else:
            ...     print(f"Error: {resultado}")
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(ruta_archivo):
                return False, f"El archivo '{ruta_archivo}' no existe"
            
            # Leer archivo
            with open(ruta_archivo, 'r', encoding=self.ENCODING) as archivo:
                datos = json.load(archivo)
            
            # Validar estructura básica
            valido, mensaje = self._validar_estructura_datos(datos)
            if not valido:
                return False, mensaje
            
            # Reconstruir planificador
            planificador = self._reconstruir_planificador(datos)
            
            return True, planificador
            
        except json.JSONDecodeError as e:
            return False, f"Error al leer JSON: El archivo no tiene formato válido. {str(e)}"
        except PermissionError:
            return False, f"Error de permisos: No se puede leer '{ruta_archivo}'"
        except OSError as e:
            return False, f"Error del sistema de archivos: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado al cargar: {str(e)}"
    
    def _validar_estructura_datos(self, datos: Dict) -> Tuple[bool, str]:
        """
        Valida que los datos tengan la estructura correcta.
        
        Args:
            datos: Diccionario con los datos cargados
            
        Returns:
            Tuple[bool, str]: (True, "") si es válido, (False, error) si no
        """
        if not isinstance(datos, dict):
            return False, "El archivo no contiene un objeto JSON válido"
        
        if 'recursos' not in datos:
            return False, "El archivo no contiene la sección 'recursos'"
        
        if 'eventos' not in datos:
            return False, "El archivo no contiene la sección 'eventos'"
        
        if not isinstance(datos['recursos'], list):
            return False, "La sección 'recursos' debe ser una lista"
        
        if not isinstance(datos['eventos'], list):
            return False, "La sección 'eventos' debe ser una lista"
        
        return True, ""
    
    def _reconstruir_planificador(self, datos: Dict):
        """
        Reconstruye un planificador desde los datos cargados.
        
        Args:
            datos: Diccionario con los datos
            
        Returns:
            PlanificadorEventos: Instancia reconstruida
        """
        # Importación local para evitar dependencia circular
        from services.planificador import PlanificadorEventos
        
        planificador = PlanificadorEventos()
        
        # Cargar recursos primero
        recursos_map = {}
        for recurso_data in datos.get('recursos', []):
            recurso = self._dict_a_recurso(recurso_data)
            if recurso:
                planificador.recursos[recurso.id] = recurso
                recursos_map[recurso.id] = recurso
        
        # Cargar eventos
        for evento_data in datos.get('eventos', []):
            evento = self._dict_a_evento(evento_data, recursos_map)
            if evento:
                planificador.eventos[evento.id] = evento
        
        return planificador
    
    def _dict_a_recurso(self, datos: Dict) -> Optional[Recurso]:
        """
        Convierte un diccionario a recurso.
        
        Args:
            datos: Diccionario con los datos del recurso
            
        Returns:
            Recurso o None si hay error
        """
        try:
            tipo_clase = datos.get('tipo_clase', 'Recurso')
            
            if tipo_clase == 'Arbitro':
                # Mapear tipo de árbitro
                tipo_map = {t.value: t for t in TipoArbitro}
                tipo = tipo_map.get(
                    datos.get('tipo_arbitro'), 
                    TipoArbitro.PRINCIPAL
                )
                
                arbitro = Arbitro(
                    nombre=datos['nombre'],
                    tipo=tipo,
                    nacionalidad=datos.get('nacionalidad', 'Inglaterra'),
                    experiencia_anios=datos.get('experiencia_anios', 0)
                )
                arbitro.id = datos['id']
                return arbitro
            else:
                recurso = Recurso(
                    nombre=datos['nombre'],
                    descripcion=datos.get('descripcion', '')
                )
                recurso.id = datos['id']
                return recurso
                
        except KeyError as e:
            print(f"Advertencia: Recurso incompleto, falta campo {e}")
            return None
        except Exception as e:
            print(f"Advertencia: Error al cargar recurso: {e}")
            return None
    
    def _dict_a_evento(self, datos: Dict, recursos_map: Dict) -> Optional[Evento]:
        """
        Convierte un diccionario a evento.
        
        Args:
            datos: Diccionario con los datos del evento
            recursos_map: Mapa de recursos {id: recurso}
            
        Returns:
            Evento o None si hay error
        """
        try:
            tipo = datos.get('tipo', 'Evento')
            
            # Recuperar recursos asignados
            recursos = []
            for rid in datos.get('recursos_ids', []):
                if rid in recursos_map:
                    recursos.append(recursos_map[rid])
            
            # Parsear fechas
            fecha_inicio = datetime.fromisoformat(datos['fecha_inicio'])
            fecha_fin = datetime.fromisoformat(datos['fecha_fin'])
            
            if tipo == 'Partido':
                partido = Partido(
                    equipo_local=datos['equipo_local'],
                    equipo_visitante=datos['equipo_visitante'],
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    recursos=recursos
                )
                partido.id = datos['id']
                return partido
            else:
                evento = Evento(
                    nombre=datos['nombre'],
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    recursos=recursos
                )
                evento.id = datos['id']
                return evento
                
        except KeyError as e:
            print(f"Advertencia: Evento incompleto, falta campo {e}")
            return None
        except ValueError as e:
            print(f"Advertencia: Error en formato de fecha: {e}")
            return None
        except Exception as e:
            print(f"Advertencia: Error al cargar evento: {e}")
            return None
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    
    def existe_archivo(self, ruta_archivo: str) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            ruta_archivo: Ruta del archivo a verificar
            
        Returns:
            bool: True si existe, False si no
        """
        return os.path.exists(ruta_archivo)
    
    def obtener_info_archivo(self, ruta_archivo: str) -> Optional[Dict]:
        """
        Obtiene información sobre un archivo de datos.
        
        Args:
            ruta_archivo: Ruta del archivo
            
        Returns:
            Dict con información o None si no existe
        """
        if not self.existe_archivo(ruta_archivo):
            return None
        
        try:
            with open(ruta_archivo, 'r', encoding=self.ENCODING) as archivo:
                datos = json.load(archivo)
            
            metadata = datos.get('metadata', {})
            
            return {
                'ruta': ruta_archivo,
                'version': metadata.get('version', 'Desconocida'),
                'fecha_guardado': metadata.get('fecha_guardado', 'Desconocida'),
                'num_recursos': len(datos.get('recursos', [])),
                'num_eventos': len(datos.get('eventos', [])),
                'tamanio_bytes': os.path.getsize(ruta_archivo)
            }
            
        except Exception:
            return None
    
    def crear_backup(self, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Crea una copia de respaldo de un archivo.
        
        Args:
            ruta_archivo: Ruta del archivo a respaldar
            
        Returns:
            Tuple[bool, str]: (True, ruta_backup) o (False, error)
        """
        if not self.existe_archivo(ruta_archivo):
            return False, "El archivo no existe"
        
        try:
            # Generar nombre de backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_base = os.path.splitext(ruta_archivo)[0]
            ruta_backup = f"{nombre_base}_backup_{timestamp}.json"
            
            # Leer archivo original
            with open(ruta_archivo, 'r', encoding=self.ENCODING) as archivo:
                contenido = archivo.read()
            
            # Escribir backup
            with open(ruta_backup, 'w', encoding=self.ENCODING) as archivo:
                archivo.write(contenido)
            
            return True, ruta_backup
            
        except Exception as e:
            return False, f"Error al crear backup: {str(e)}"
    
    def listar_archivos_datos(self, directorio: str = "data") -> list:
        """
        Lista todos los archivos JSON en un directorio.
        
        Args:
            directorio: Directorio a explorar (default: "data")
            
        Returns:
            list: Lista de rutas de archivos JSON encontrados
        """
        archivos = []
        
        if not os.path.exists(directorio):
            return archivos
        
        try:
            for archivo in os.listdir(directorio):
                if archivo.endswith('.json'):
                    ruta_completa = os.path.join(directorio, archivo)
                    archivos.append(ruta_completa)
            
            return sorted(archivos)
            
        except Exception:
            return archivos
    
    def eliminar_archivo(self, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Elimina un archivo de datos.
        
        Args:
            ruta_archivo: Ruta del archivo a eliminar
            
        Returns:
            Tuple[bool, str]: (True, mensaje) o (False, error)
        """
        if not self.existe_archivo(ruta_archivo):
            return False, "El archivo no existe"
        
        try:
            os.remove(ruta_archivo)
            return True, f"Archivo '{ruta_archivo}' eliminado exitosamente"
            
        except PermissionError:
            return False, "Error de permisos: No se puede eliminar el archivo"
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"
    
    def exportar_resumen(self, planificador, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Exporta un resumen legible del estado del planificador.
        
        Args:
            planificador: Instancia del PlanificadorEventos
            ruta_archivo: Ruta del archivo de salida (.txt)
            
        Returns:
            Tuple[bool, str]: (True, mensaje) o (False, error)
        """
        try:
            # Crear directorio si no existe
            directorio = os.path.dirname(ruta_archivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio)
            
            lineas = self._generar_resumen(planificador)
            
            with open(ruta_archivo, 'w', encoding=self.ENCODING) as archivo:
                archivo.write('\n'.join(lineas))
            
            return True, f"Resumen exportado a '{ruta_archivo}'"
            
        except Exception as e:
            return False, f"Error al exportar resumen: {str(e)}"
    
    def _generar_resumen(self, planificador) -> list:
        """
        Genera las líneas del resumen del planificador.
        
        Args:
            planificador: Instancia del PlanificadorEventos
            
        Returns:
            list: Lista de líneas del resumen
        """
        lineas = [
            "=" * 60,
            "RESUMEN DEL PLANIFICADOR - ETIHAD STADIUM",
            "=" * 60,
            f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            "-" * 60,
            "ESTADÍSTICAS GENERALES",
            "-" * 60,
            f"Total de recursos: {len(planificador.recursos)}",
            f"Total de eventos: {len(planificador.eventos)}",
            ""
        ]
        
        # Árbitros por tipo
        from models.recurso import TipoArbitro
        
        lineas.append("-" * 60)
        lineas.append("ÁRBITROS POR TIPO")
        lineas.append("-" * 60)
        
        for tipo in TipoArbitro:
            arbitros = planificador.obtener_recursos_por_tipo(tipo)
            lineas.append(f"{tipo.value}: {len(arbitros)}")
            for arbitro in arbitros:
                lineas.append(f"   • {arbitro.nombre}")
        
        lineas.append("")
        
        # Eventos
        lineas.append("-" * 60)
        lineas.append("PARTIDOS PROGRAMADOS")
        lineas.append("-" * 60)
        
        eventos = sorted(
            planificador.obtener_eventos(), 
            key=lambda e: e.fecha_inicio
        )
        
        if eventos:
            for evento in eventos:
                estado = "PRÓXIMO" if evento.fecha_inicio > datetime.now() else "PASADO"
                lineas.append(f"\n[{estado}] {evento.nombre}")
                lineas.append(f"   Fecha: {evento.fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
                lineas.append(f"   Árbitros asignados:")
                for recurso in evento.recursos:
                    lineas.append(f"      • {recurso}")
        else:
            lineas.append("No hay partidos programados.")
        
        lineas.append("")
        lineas.append("=" * 60)
        lineas.append("FIN DEL RESUMEN")
        lineas.append("=" * 60)
        
        return lineas
    
    def __str__(self) -> str:
        """Representación en cadena del gestor."""
        return f"GestorPersistencia(version={self.VERSION})"
    
    def __repr__(self) -> str:
        """Representación técnica del gestor."""
        return self.__str__()
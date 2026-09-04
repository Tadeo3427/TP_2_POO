import json
import os
from typing import List
from modelos import Tarea, Supervisor, Tecnico, Equipo
from excepciones import ( 
    MantenimientoError,CampoVacioError, TareaNoEncontradaError, TareaNoModificableError,
)


class GestorTareas:
    def __init__(
        self,
        archivo_equipos: str = "equipos.json",
        archivo_personas: str = "personas.json",
         archivo_json: str = "tareas.json",
    ):
        self._archivo_json = archivo_json
        self._archivo_equipos = archivo_equipos
        self._archivo_personas = archivo_personas

        # Inicializar listas vacías para almacenar tareas, supervisores, técnicos y equipos
        self._tareas: List[Tarea] = []
        self._supervisores: List[Supervisor] = []
        self._tecnicos: List[Tecnico] = []
        self._equipos: List[Equipo] = []


        # Cargar datos al instanciar
        self.cargar_personas_desde_json()
        self.cargar_desde_json()
        self.cargar_equipos_desde_json()

    # -------------------------------------------------------------------
    # PROPERTIES DE ACCESO PÚBLICO (READ-ONLY)
    # -------------------------------------------------------------------
    @property
    def tareas(self) -> List[Tarea]:
        """Retorna una copia de la lista de tareas para evitar modificación directa."""
        return list(self._tareas)

    @property
    def equipos(self) -> List[Equipo]:
        """Retorna una copia de la lista de equipos."""
        return list(self._equipos)

    @property
    def supervisores(self) -> List[Supervisor]:
        """Retorna una copia de la lista de supervisores."""
        return list(self._supervisores)

    @property
    def tecnicos(self) -> List[Tecnico]:
        """Retorna una copia de la lista de técnicos."""
        return list(self._tecnicos)

# -------------------------------------------------------------------
# GESTIÓN DE PERSONAL (SUPERVISORES Y TÉCNICOS)
# -------------------------------------------------------------------
    def registrar_supervisor(self, dni: str, nombre: str, sector_cargo: str, legajo: str) -> Supervisor:
        campos = {
            "DNI": dni,
            "Nombre": nombre,
            "Legajo": legajo,
            "Sector / Cargo": sector_cargo,
        }
        for nombre_campo, valor in campos.items():
            if not valor or not valor.strip():
                raise CampoVacioError(f"El campo '{nombre_campo}' no puede estar vacío.")

        dni_limpio = dni.strip()
        legajo_limpio = legajo.strip()

        #Validar DNI estrictamente numérico
        if not dni_limpio.isdigit() or not (7 <= len(dni_limpio) <= 8):
            raise CampoVacioError("El DNI debe ser numérico y tener entre 7 y 8 dígitos.")

        # Validar duplicados contra Supervisores
        for s in self._supervisores:
            if s.dni == dni_limpio:
                raise CampoVacioError(f"Ya existe un supervisor ({s.nombre}) registrado con DNI {dni_limpio}.")
            if s.legajo == legajo_limpio:
                raise CampoVacioError(f"Ya existe un supervisor ({s.nombre}) registrado con Legajo {legajo_limpio}.")

        # Validar duplicados contra Técnicos (Cruce)
        for t in self._tecnicos:
            if t.dni == dni_limpio:
                raise CampoVacioError(f"El DNI {dni_limpio} ya pertenece al técnico {t.nombre}.")
            if t.legajo == legajo_limpio:
                raise CampoVacioError(f"El Legajo {legajo_limpio} ya pertenece al técnico {t.nombre}.")

        sup = Supervisor(
            dni=dni_limpio,
            nombre=nombre.strip(),
            legajo=legajo_limpio,
            sector_cargo=sector_cargo.strip(),
        )
        self._supervisores.append(sup)
        self.guardar_personas_en_json()
        return sup

    def registrar_tecnico(self, dni: str, nombre: str, especialidad: str, legajo: str) -> Tecnico:
        campos = {
            "DNI": dni,
            "Nombre": nombre,
            "Especialidad": especialidad,
            "Legajo": legajo,
        }
        for nombre_campo, valor in campos.items():
            if not valor or not valor.strip():
                raise CampoVacioError(f"El campo '{nombre_campo}' no puede estar vacío.")

        dni_limpio = dni.strip()
        legajo_limpio = legajo.strip()

        #Validar DNI estrictamente numérico
        if not dni_limpio.isdigit() or not (7 <= len(dni_limpio) <= 8):
            raise CampoVacioError("El DNI debe ser numérico y tener entre 7 y 8 dígitos.")

        # Validar duplicados contra Técnicos
        for t in self._tecnicos:
            if t.dni == dni_limpio:
                raise CampoVacioError(f"Ya existe un técnico ({t.nombre}) registrado con DNI {dni_limpio}.")
            if t.legajo == legajo_limpio:
                raise CampoVacioError(f"Ya existe un técnico ({t.nombre}) registrado con Legajo {legajo_limpio}.")

        # Validar duplicados contra Supervisores (Cruce)
        for s in self._supervisores:
            if s.dni == dni_limpio:
                raise CampoVacioError(f"El DNI {dni_limpio} ya pertenece al supervisor {s.nombre}.")
            if s.legajo == legajo_limpio:
                raise CampoVacioError(f"El Legajo {legajo_limpio} ya pertenece al supervisor {s.nombre}.")

        tec = Tecnico(
            dni=dni_limpio,
            nombre=nombre.strip(),
            especialidad=especialidad.strip(),
            legajo=legajo_limpio,
        )
        self._tecnicos.append(tec)
        self.guardar_personas_en_json()
        return tec


    # --- Cambio de estado a técnicos y supervisores (Baja / Alta lógica) ---
    def cambiar_estado_supervisor(self, legajo:str, activo:bool):
        for s in self._supervisores:
            if s.legajo == legajo:
                s.activo = activo
                self.guardar_personas_en_json()
                return True
        raise MantenimientoError(f"No se encontró Supervisor con N° de Legajo: {legajo}")

    def cambiar_estado_tecnico(self, legajo:str, activo:bool):
        for t in self._tecnicos:
            if t.legajo == legajo:
                t.activo = activo
                self.guardar_personas_en_json()
                return True
        raise MantenimientoError(f"No se encontró Técnico con N° de Legajo: {legajo}")
                

    def listar_supervisores(self) -> List[Supervisor]:
        return list(self._supervisores)


    def listar_tecnicos(self) -> List[Tecnico]:
        return list(self._tecnicos)

#-----------------------------------------------------------------------
# Gestión de Equipos 
#-----------------------------------------------------------------------
    def registrar_equipo(self, tag: str, descripcion: str, sector: str) -> Equipo:
        campos = {
            "Tag de equipo": tag,
            "Descripción de equipo": descripcion,
            "Sector": sector,
        }
        for nombre_campo, valor in campos.items():
            if not valor or not valor.strip():
                raise CampoVacioError(f"El campo '{nombre_campo}' no puede estar vacío.")

        tag_limpio = tag.strip().upper()

        # Validar duplicados
        for e in self._equipos:
            if e.tag == tag_limpio:
                raise CampoVacioError(f"Ya existe un equipo registrado con Tag {tag_limpio}.")

        equipo = Equipo(
            tag=tag_limpio,
            descripcion=descripcion.strip(),
            sector=sector.strip(),
        )
        self._equipos.append(equipo)
        self.guardar_equipos_en_json()
        return equipo

    def listar_equipos(self) -> List[Equipo]:
        return list(self._equipos)  

    # --- Cambio de estado a equipo (Baja / Alta lógica) ---
    def cambiar_estado_equipo(self, tag: str, activo: bool):
        for e in self._equipos:
            if e.tag == tag:
                e.activo = activo
                self.guardar_equipos_en_json()
                return True 
        raise MantenimientoError(f"No se encontré el equipo con TAG {tag}")



    # -------------------------------------------------------------------
    # 1. ALTA DE TAREA
    # -------------------------------------------------------------------
    def registrar_tarea(
        self,
        supervisor: Supervisor,
        tecnico: Tecnico,
        equipo: Equipo,
        detalle_tarea: str,
        fecha: str,
    ) -> Tarea:
        # Validación de campos vacíos
        campos = {
            "Tag de equipo": equipo.tag,
            "Descripción de equipo": equipo.descripcion,
            "Sector": equipo.sector,
            "Detalle de tarea": detalle_tarea,
            "Fecha": fecha,
        }
        for nombre_campo, valor in campos.items():
            if not valor or not valor.strip():
                raise CampoVacioError(f"El campo '{nombre_campo}' no puede estar vacío.")

        nueva_tarea = Tarea(
            supervisor=supervisor,
            tecnico=tecnico,
            equipo=equipo,
            detalle_tarea=detalle_tarea.strip(),
            fecha=fecha.strip(),
            estado="pendiente",
        )

        supervisor.agregar_tarea(nueva_tarea.id)
        self._tareas.append(nueva_tarea)
        self.guardar_en_json()
        return nueva_tarea

    # -------------------------------------------------------------------
    # 2. CONSULTA Y BÚSQUEDA
    # -------------------------------------------------------------------
    def buscar_por_ot(self, ot: int) -> Tarea:
        for t in self._tareas:
            if t.id == ot:
                return t
        raise TareaNoEncontradaError(f"No se encontró ninguna tarea con N° de OT: {ot}")

    def buscar_por_equipo_o_sector(self, criterio: str) -> List[Tarea]:
        criterio_lower = criterio.lower().strip()
        resultados = [
            t for t in self._tareas
            if criterio_lower in t.equipo.tag.lower() or criterio_lower in t.equipo.sector.lower()
        ]
        if not resultados:
            raise TareaNoEncontradaError(f"No se encontraron tareas asociadas a: '{criterio}'")
        return resultados

    # -------------------------------------------------------------------
    # 3. MODIFICACIÓN DE ESTADO
    # -------------------------------------------------------------------
    def cambiar_estado_tarea(
        self,
        ot: int,
        nuevo_estado: str,
        fecha_realizado: str = "",
        tarea_realizada: str = "",
    ) -> Tarea:
        tarea = self.buscar_por_ot(ot)

        if tarea.estado in ["finalizado", "cancelado"]:
            raise TareaNoModificableError(
                f"No se puede modificar una tarea que ya está '{tarea.estado}'."
            )

        nuevo_estado = nuevo_estado.lower().strip()

        if tarea.estado == "pendiente" and nuevo_estado == "finalizado":
            raise TareaNoModificableError(
                "ERROR: No se puede pasar de 'pendiente' a 'finalizado' directamente."
                " Debe estar 'en progreso'."
            )

        if nuevo_estado == "finalizado":
            if not fecha_realizado.strip() or not tarea_realizada.strip():
                raise CampoVacioError(
                    "Debe ingresar la fecha de realización y el detalle del trabajo realizado."
                )
            tarea.fecha_realizado = fecha_realizado.strip()
            tarea.tarea_realizada = tarea_realizada.strip()

        tarea.estado = nuevo_estado
        self.guardar_en_json()
        return tarea

    # -------------------------------------------------------------------
    # 4. BAJA / CANCELACIÓN
    # -------------------------------------------------------------------
    def cancelar_tarea(self, ot: int) -> Tarea:
        tarea = self.buscar_por_ot(ot)

        if tarea.estado in ["finalizado", "cancelado"]:
            raise TareaNoModificableError(
                f"No se puede cancelar una tarea que ya está '{tarea.estado}'."
            )

        tarea.estado = "cancelado"
        self.guardar_en_json()
        return tarea

    # -------------------------------------------------------------------
    # 5. LISTADOS
    # -------------------------------------------------------------------
    def listar_todas(self) -> List[Tarea]:
        return list(self._tareas)

    def listar_por_estado(self, estado_buscado: str) -> List[Tarea]:
        estado_buscado = estado_buscado.lower().strip()
        filtradas = [t for t in self._tareas if t.estado == estado_buscado]
        return filtradas

    #--- MÉTODOS DE LISTADO FILTRADO (Uso exlcusivo en interfaz de usuario para altas) ---

    def Listar_equipos_activos(self) -> List[Equipo]:
        return [e for e in self._equipos if e.activo]

    def Listar_supervisores_activos(self) -> List[Supervisor]:
            return [s for s in self._supervisores if s.activo]

    def Listar_tecnicos_activos(self) -> List[Tecnico]:
            return [t for t in self._tecnicos if t.activo]
    

    # -------------------------------------------------------------------
    # 6. PERSISTENCIA EN ARCHIVOS JSON
    # -------------------------------------------------------------------

    # Guardar y cargar equipos
    def guardar_equipos_en_json(self):
        datos = [
            {
                "tag_equipo": e.tag,
                "descripcion_equipo": e.descripcion,
                "sector": e.sector,
                "activo": e.activo
            }
            for e in self._equipos
        ]
        with open(self._archivo_equipos, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def cargar_equipos_desde_json(self):
        if not os.path.exists(self._archivo_equipos):
            self._equipos = []
            return

        try:
            with open(self._archivo_equipos, "r", encoding="utf-8") as f:
                datos = json.load(f)
                self._equipos = [
                    Equipo(
                        tag=e["tag_equipo"],
                        descripcion=e["descripcion_equipo"],
                        sector=e["sector"],
                        activo=e.get("activo", True) # Carga la variable privada a través de __init__
                    )
                    for e in datos
                ]
        except Exception:
            self._equipos = []

    # Guardar y cargar supervisores y técnicos
    
    def guardar_personas_en_json(self):
        datos = {
            "supervisores": [
                {
                    "dni": s.dni,
                    "nombre": s.nombre,
                    "sector_cargo": s.sector_cargo,
                    "legajo": s.legajo,
                    "activo": s.activo
                }
                for s in self._supervisores
            ],
            "tecnicos": [
                {
                    "dni": t.dni,
                    "nombre": t.nombre,
                    "especialidad": t.especialidad,
                    "legajo": t.legajo,
                    "activo": t.activo
                }
                for t in self._tecnicos
            ],
        }
        with open(self._archivo_personas, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def cargar_personas_desde_json(self):
        if not os.path.exists(self._archivo_personas):
            self._supervisores = []
            self._tecnicos = []
            return

        try:
            with open(self._archivo_personas, "r", encoding="utf-8") as f:
                datos = json.load(f)
                self._supervisores = [
                    Supervisor(
                        dni=s["dni"],
                        nombre=s["nombre"],
                        sector_cargo=s["sector_cargo"],
                        legajo=s["legajo"],
                        activo=s.get("activo", True)
                    )
                    for s in datos.get("supervisores", [])
                ]
                self._tecnicos = [
                    Tecnico(
                        dni=t["dni"],
                        nombre=t["nombre"],
                        especialidad=t["especialidad"],
                        legajo=t["legajo"],
                        activo=t.get("activo", True)
                    )
                    for t in datos.get("tecnicos", [])
                ]
        except Exception:
            self._supervisores = []
            self._tecnicos = []

    # Guardar y cargar tareas.        

    def guardar_en_json(self):
        datos = []
        for t in self._tareas:
            datos.append({
                "id": t.id,
                "equipo": {
                    "tag": t.equipo.tag,
                    "descripcion": t.equipo.descripcion,
                    "sector": t.equipo.sector
                },
                "detalle_tarea": t.detalle_tarea,
                "fecha": t.fecha,
                "estado": t.estado,
                "fecha_realizado": t.fecha_realizado,
                "tarea_realizada": t.tarea_realizada,
                "supervisor": {
                    "dni": t.supervisor.dni,
                    "nombre": t.supervisor.nombre,
                    "sector_cargo": t.supervisor.sector_cargo,
                    "legajo": t.supervisor.legajo,
                },
                "tecnico": {
                    "dni": t.tecnico.dni,
                    "nombre": t.tecnico.nombre,
                    "especialidad": t.tecnico.especialidad,
                    "legajo": t.tecnico.legajo, 
                },
            })

        with open(self._archivo_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def cargar_desde_json(self):
        if not os.path.exists(self._archivo_json):
            self._tareas = []
            return

        try:
            with open(self._archivo_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
                self._tareas = []
                for d in datos:
                    sup_d = d["supervisor"]
                    tec_d = d["tecnico"]
                    eq_d = d["equipo"]

                    supervisor = Supervisor(
                        dni=sup_d["dni"],
                        nombre=sup_d["nombre"],
                        sector_cargo=sup_d["sector_cargo"],
                        legajo=sup_d["legajo"]
                    )

                    tecnico = Tecnico(
                        dni=tec_d["dni"],
                        nombre=tec_d["nombre"],
                        especialidad=tec_d["especialidad"],
                        legajo=tec_d["legajo"],
                    )

                    equipo = Equipo(
                        tag=eq_d["tag"],
                        descripcion=eq_d["descripcion"],
                        sector=eq_d["sector"],
                    )

                    tarea = Tarea(
                        supervisor=supervisor,
                        tecnico=tecnico,
                        equipo=equipo,
                        detalle_tarea=d["detalle_tarea"],
                        fecha=d["fecha"],
                        estado=d["estado"],
                        fecha_realizado=d.get("fecha_realizado", ""),
                        tarea_realizada=d.get("tarea_realizada", ""),
                        id=d["id"],
                    )
                    self._tareas.append(tarea)
        except Exception:
            self._tareas = []

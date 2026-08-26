import json
import os
from typing import List, Optional
from modelos import Tarea, Supervisor, Tecnico
from excepciones import (
    CampoVacioError,
    TareaNoEncontradaError,
    TareaNoModificableError,
)


class GestorTareas:
    def __init__(
        self,
        archivo_json: str = "tareas.json",
        archivo_personas: str = "personas.json",
    ):
        self._archivo_json = archivo_json
        self._archivo_personas = archivo_personas
        
        self._tareas: List[Tarea] = []
        self._supervisores: List[Supervisor] = []
        self._tecnicos: List[Tecnico] = []

        # Cargar datos al instanciar
        self.cargar_personas_desde_json()
        self.cargar_desde_json()

    # -------------------------------------------------------------------
    # PROPERTIES DE ACCESO PÚBLICO (READ-ONLY)
    # -------------------------------------------------------------------
    @property
    def tareas(self) -> List[Tarea]:
        """Retorna una copia de la lista de tareas para evitar modificación directa."""
        return list(self._tareas)

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

    def listar_supervisores(self) -> List[Supervisor]:
        return list(self._supervisores)

    def listar_tecnicos(self) -> List[Tecnico]:
        return list(self._tecnicos)

    # -------------------------------------------------------------------
    # 1. ALTA DE TAREA
    # -------------------------------------------------------------------
    def registrar_tarea(
        self,
        supervisor: Supervisor,
        tecnico: Tecnico,
        tag_equipo: str,
        descripcion_equipo: str,
        sector: str,
        detalle_tarea: str,
        fecha: str,
    ) -> Tarea:
        # Validación de campos vacíos
        campos = {
            "Tag de equipo": tag_equipo,
            "Descripción de equipo": descripcion_equipo,
            "Sector": sector,
            "Detalle de tarea": detalle_tarea,
            "Fecha": fecha,
        }
        for nombre_campo, valor in campos.items():
            if not valor or not valor.strip():
                raise CampoVacioError(f"El campo '{nombre_campo}' no puede estar vacío.")

        nueva_tarea = Tarea(
            supervisor=supervisor,
            tecnico=tecnico,
            tag_equipo=tag_equipo.strip(),
            descripcion_equipo=descripcion_equipo.strip(),
            sector=sector.strip(),
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
            if criterio_lower in t.tag_equipo.lower() or criterio_lower in t.sector.lower()
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

    # -------------------------------------------------------------------
    # 6. PERSISTENCIA EN ARCHIVOS JSON
    # -------------------------------------------------------------------
    def guardar_personas_en_json(self):
        datos = {
            "supervisores": [
                {
                    "dni": s.dni,
                    "nombre": s.nombre,
                    "sector_cargo": s.sector_cargo,
                    "legajo": s.legajo
                }
                for s in self._supervisores
            ],
            "tecnicos": [
                {
                    "dni": t.dni,
                    "nombre": t.nombre,
                    "especialidad": t.especialidad,
                    "legajo": t.legajo,
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
                        legajo=s["legajo"]
                    )
                    for s in datos.get("supervisores", [])
                ]
                self._tecnicos = [
                    Tecnico(
                        dni=t["dni"],
                        nombre=t["nombre"],
                        especialidad=t["especialidad"],
                        legajo=t["legajo"],
                    )
                    for t in datos.get("tecnicos", [])
                ]
        except Exception:
            self._supervisores = []
            self._tecnicos = []

    def guardar_en_json(self):
        datos = []
        for t in self._tareas:
            datos.append({
                "id": t.id,
                "tag_equipo": t.tag_equipo,
                "descripcion_equipo": t.descripcion_equipo,
                "sector": t.sector,
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

                    tarea = Tarea(
                        supervisor=supervisor,
                        tecnico=tecnico,
                        tag_equipo=d["tag_equipo"],
                        descripcion_equipo=d["descripcion_equipo"],
                        sector=d["sector"],
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
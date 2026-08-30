from abc import ABC, abstractmethod

# Clase abstracta Persona
class Persona(ABC):
    def __init__(self, dni: str, nombre: str):
        self._dni = dni
        self._nombre = nombre

    @property
    def dni(self):
        return self._dni

    @dni.setter
    def dni(self, value):
        self._dni = value

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @abstractmethod
    def presentacion(self):
        raise NotImplementedError

# Clase Supervisor que hereda de Persona
class Supervisor(Persona):
    def __init__(self, dni: str, nombre: str, sector_cargo: str, legajo: str):
        super().__init__(dni, nombre)
        self._sector_cargo = sector_cargo
        self._legajo = legajo
        self._historial_tareas = []

    @property
    def sector_cargo(self):
        return self._sector_cargo

    @sector_cargo.setter
    def sector_cargo(self, value):
        self._sector_cargo = value

    @property
    def legajo(self):
        return self._legajo

    @legajo.setter
    def legajo(self, value):
        self._legajo = value

    @property
    def historial_tareas(self):
        return list(self._historial_tareas)

    def agregar_tarea(self, tarea_id: int):
        self._historial_tareas.append(tarea_id)

    def presentacion(self):
        return f"Supervisor: {self.nombre} (Legajo: {self.legajo}) , ({self.sector_cargo})"
    
    def __str__(self):
        return f"{self.nombre} - Legajo: {self.legajo} ({self.sector_cargo})"

# Clase Tecnico que hereda de Persona
class Tecnico(Persona):
    def __init__(self, dni: str, nombre: str, especialidad: str, legajo: str):
        super().__init__(dni, nombre)
        self._especialidad = especialidad
        self._legajo = legajo

    @property
    def especialidad(self):
        return self._especialidad

    @especialidad.setter
    def especialidad(self, value):
        self._especialidad = value

    @property
    def legajo(self):
        return self._legajo

    @legajo.setter
    def legajo(self, value):
        self._legajo = value

    def presentacion(self):
        return f"Técnico: {self.nombre} , ({self.especialidad})"
    
# Clase Equipo para representar los equipos de trabajo
class Equipo:
    def __init__(self,
            tag:str,
            descripcion:str,
            sector:str
    ):
        self._tag = tag.strip().upper()
        self._descripcion = descripcion.strip()
        self._sector = sector.strip()

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value.strip().upper()

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, value):
        self._descripcion = value.strip()
 
    @property
    def sector(self):
        return self._sector

    @sector.setter
    def sector(self, value):
        self._sector = value.strip()

    def __str__(self):
        return f"[{self.tag}] {self.descripcion} ({self.sector})"

# Clase Tarea para representar las tareas asignadas a los técnicos
class Tarea:
    _ultimo_id = 0

    def __init__(
        self,
        supervisor: Supervisor, # Recibe la instancia completa de Supervisor
        tecnico: Tecnico,       # Recibe la instancia completa de Tecnico
        equipo: Equipo,         # Recibe la instancia completa de Equipo
        detalle_tarea: str,
        fecha: str,
        estado: str = "pendiente",
        fecha_realizado: str = "",
        tarea_realizada: str = "",
        id: int = None,
    ):
        if id is None:
            Tarea._ultimo_id += 1
            self._id = Tarea._ultimo_id
        else:
            self._id = id
            if id > Tarea._ultimo_id:
                Tarea._ultimo_id = id

        self._supervisor = supervisor
        self._tecnico = tecnico
        self._equipo = equipo
        self._detalle_tarea = detalle_tarea
        self._fecha = fecha
        self._estado = estado
        self._fecha_realizado = fecha_realizado
        self._tarea_realizada = tarea_realizada

    @property
    def id(self):
        return self._id

    @property
    def supervisor(self):
        return self._supervisor

    @property
    def tecnico(self):
        return self._tecnico

    @property
    def equipo(self) -> Equipo:
        return self._equipo


    @property
    def detalle_tarea(self):
        return self._detalle_tarea

    @detalle_tarea.setter
    def detalle_tarea(self, value):
        self._detalle_tarea = value

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, value):
        self._fecha = value

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, value):
        self._estado = value

    @property
    def fecha_realizado(self):
        return self._fecha_realizado

    @fecha_realizado.setter
    def fecha_realizado(self, value):
        self._fecha_realizado = value

    @property
    def tarea_realizada(self):
        return self._tarea_realizada

    @tarea_realizada.setter
    def tarea_realizada(self, value):
        self._tarea_realizada = value

    def mostrar_detalle(self):
        detalle = (
            f"OT / ID: {self.id}\n"
            f"Tag Equipo: {self.equipo.tag}\n"
            f"Descripción Equipo: {self.equipo.descripcion}\n"
            f"Sector: {self.equipo.sector}\n"
            f"Detalle Tarea: {self.detalle_tarea}\n"
            f"Supervisor: {self.supervisor.nombre}\n"
            f"Técnico Asignado: {self.tecnico.nombre}\n"
            f"Fecha Alta: {self.fecha}\n"
            f"Estado: {self.estado}"
        )
        if self.estado == "finalizado":
            detalle += (
                f"\nFecha Realización: {self.fecha_realizado}\n"
                f"Trabajo Realizado: {self.tarea_realizada}"
            )
        return detalle

    def __str__(self):
        return self.mostrar_detalle()
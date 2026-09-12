# Sistema de Gestión de Mantenimiento
Sistema para la gestión y seguimiento de Órdenes de Trabajo (OT) de mantenimiento industrial, desarrollado en Python
bajo el paradigma de Programación Orientada a Objetos (POO) e implementado con una interfaz web interactiva en **Streamlit** 
y almacenamiento local en archivos JSON.

---

## Requisitos Previos 
**Python 3.9** o superior.
**Git** (Para la clonación del repositorio).

---

## 📦 Bibliotecas y Dependencias

El proyecto utiliza Python estándar junto con la biblioteca **Streamlit** para renderizar la interfaz web.

### 1. Clonar el repositorio
```bash
git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
cd TU_REPOSITORIO
```

---

### 2. Crear y activar entorno virtual (Recomendado)

*En Windows:*

```Bash
python -m venv venv
venv\Scripts\activate
```
*En Linux / macOS:*
```Bash
python3 -m venv venv
source venv/bin/activate
```
---

### 3. Instalar bibliotecas requeridas

```Bash
pip install streamlit
```
---

### 4. Ejecutar el proyecto

**Opción 1: Interfaz Web con Streamlit (Recomendado)**
Para iniciar la aplicación web en el navegador:
```Bash
streamlit run app_web.py
```
El sistema abrirá automáticamente la aplicación en ``` http://localhost:8501.```

**Opción 2: Ejecución por Terminal (Consola / CLI)**
Para correr las pruebas o el flujo interactivo desde la consola:
```Bash
python main.py
```

---

# Arquitectura y Patrones de Diseño
El proyecto está diseñado siguiendo la separación de responsabilidades en capas independientes:

### Capa de Dominio (modelos.py):

- **Abstracción y Herencia:** Clase base abstracta ``Persona(ABC)`` de la cual heredan ``Supervisor`` y ``Técnico``.

- **Clase Entidad (``Equipo``):** Representa los activos físicos de la planta (``tag, descripción, sector, activo``).

- **Polimorfismo:** Método obligatorio ``@abstractmethod def presentacion()`` con comportamientos específicos según el rol.

- **Encapsulamiento:** Decoradores ``@property`` y ``@setter`` para la gestión segura de los atributos.

- **Atributo de Clase:** Control autoincremental de identificadores en ``Tarea._ultimo_id``.

### Capa de Control y Negocio (gestor.py):

- **Patrón Controller/Manager:** La clase ``GestorTareas`` administra el estado en memoria, la máquina de estados de las OTs y la persistencia.

- **Encapsulamiento Defensivo:** Retorno de copias de listas (``list(...)``) en las propiedades para proteger el estado interno.

- **Filtrado de Entidades:** Métodos específicos (``obtener_*_activos()``) para alimentar la UI exclusivamente con elementos disponibles.

- **Validaciones Robustas:** Prevención de campos vacíos, control de DNI/Legajo duplicados entre roles y control estricto del flujo de estados.

### Capa de Excepciones (excepciones.py):

****Excepciones personalizadas derivadas de ``MantenimientoError`` (``CampoVacioError, TareaNoEncontradaError, TareaNoModificableError``).****

### Capa de Interfaz (UI):

- **``app_web.py``:** Interfaz Web moderna estructurada en pestañas (Altas, Baja/Alta Lógica, Filtros de OTs, Padrón General).

- **``main.py``:** Punto de entrada secundario por consola (CLI) para depuración.

# Reglas de Negocio Destacadas

- **Gestión de Personal:**

- **DNI estrictamente  numérico (7 u 8 dígitos).**

- **Unicidad Cruzada:** Garantía de identificadores únicos para DNI/Legajo (entre técnicos y supervisores) y TAGs de equipos.

- **Baja y Alta Lógica (``activo``):**

  - Los **Técnicos, Supervisores** y **Equipos** no se eliminan físicamente de la base de datos.

  - Al dar de baja una entidad (``activo = False``), esta deja de aparecer en los desplegables de alta de nuevas tareas.

  - Se conservan de forma íntegra en las consultas del padrón general y en el historial de tareas previas para no romper la trazabilidad.

  - Cualquier entidad desactivada puede ser reactivada en cualquier momento desde el panel de gestión.

- **Ciclo de Vida de una Orden de Trabajo:**

- **Transiciones permitidas:** pendiente ➡️ en progreso ➡️ finalizado.

- **Cierre obligatorio:** Al pasar a finalizado, exige la fecha de realización y la tarea ejecutada.

- Las tareas en estado finalizado o cancelado son inmutables.

## Estructura del Proyecto y Persistencia
```Plaintext
├── app_web.py          # Interfaz de usuario Web (Streamlit)
├── main.py             # Interfaz de consola (CLI) / Debug
├── gestor.py           # Controlador principal y Lógica de Negocio
├── modelos.py          # Clases del dominio (Persona, Supervisor, Tecnico, Equipo, Tarea)
├── excepciones.py      # Excepciones personalizadas del sistema
├── personas.json       # Persistencia de supervisores y técnicos (generado autom.)
├── equipos.json        # Persistencia de equipos de la planta (generado autom.)
└── tareas.json         # Persistencia de órdenes de trabajo (generado autom.)


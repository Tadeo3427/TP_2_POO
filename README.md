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


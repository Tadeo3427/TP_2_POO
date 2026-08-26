import streamlit as st
from gestor import GestorTareas
from modelos import Supervisor, Tecnico
from excepciones import MantenimientoError
# ... imports ...

st.set_page_config(page_title="Gestión de Mantenimiento", layout="wide")

gestor = GestorTareas()

# Initialize session state para guardar el rol
if "rol" not in st.session_state:
    st.session_state["rol"] = "Técnico"  # Rol por defecto

# --- BARRA LATERAL: CONTROL DE ACCESO ---
st.sidebar.title("🔐 Control de Acceso")

rol_seleccionado = st.sidebar.selectbox("Ingresar como:", ["Técnico", "Supervisor"])

if rol_seleccionado == "Supervisor":
    clave = st.sidebar.text_input("Contraseña de Administrador:", type="password")
    if clave == "admin123":  # Clave hardcodeada simple para el TP
        st.session_state["rol"] = "Supervisor"
        st.sidebar.success("🔑 Acceso Supervisor Concedido")
    else:
        st.session_state["rol"] = "Técnico"
        if clave != "":
            st.sidebar.error("❌ Contraseña incorrecta")
else:
    st.session_state["rol"] = "Técnico"

# --- MENÚ DE OPCIONES SEGÚN ROL ---
st.sidebar.divider()

if st.session_state["rol"] == "Supervisor":
    # El supervisor tiene acceso total
    opciones_menu = [
        "📋 Listar Tareas",
        "➕ Registrar Nueva Tarea",
        "👤 Gestión de Personal",  
        "✏️ Modificar Estado",
        "🚫 Cancelar Tarea"
    ]
else:
    # El técnico solo consulta y modifica el estado
    opciones_menu = [
        "📋 Listar Tareas",
        "✏️ Modificar Estado"
    ]

opcion = st.sidebar.radio("Menú de Opciones", opciones_menu)

# -------------------------------------------------------------------
# 1. LISTAR Y BUSCAR TAREAS
# -------------------------------------------------------------------
if opcion == "📋 Listar Tareas":
    st.header("📋 Listado y Búsqueda de Tareas")

    col_filtro1, col_filtro2 = st.columns([1, 2])

    with col_filtro1:
        criterio_busqueda = st.radio(
            "Modo de consulta:",
            ["Ver todas / Por estado", "Buscar por OT"]
        )

    tareas_a_mostrar = []

    if criterio_busqueda == "Ver todas / Por estado":
        with col_filtro2:
            estado_filtro = st.selectbox(
                "Filtrar por estado:",
                ["Todas", "pendiente", "en progreso", "finalizado", "cancelado"]
            )
        if estado_filtro == "Todas":
            tareas_a_mostrar = gestor.listar_todas()
        else:
            tareas_a_mostrar = gestor.listar_por_estado(estado_filtro)

    else:
        with col_filtro2:
            ot_input = st.number_input("Ingrese el número de OT:", min_value=1, step=1)
            if st.button("Buscar OT"):
                try:
                    tarea_hallada = gestor.buscar_por_ot(int(ot_input))
                    tareas_a_mostrar = [tarea_hallada]
                except MantenimientoError as e:
                    st.error(f"⚠️ {e}")

    # --- listado de tareas ---
    if not tareas_a_mostrar:
        st.info("No se encontraron tareas con el criterio seleccionado.")
    else:
        st.write(f"Mostrando **{len(tareas_a_mostrar)}** tarea(s):")
        
        # Mapeo de estados con colores nativos de Streamlit (:orange[], :green[], :red[])
        for t in tareas_a_mostrar:
            estado_str = t.estado.lower()
            if estado_str == "pendiente":
                estado_fmt = ":orange[🟡 PENDIENTE]"
            elif estado_str == "en progreso":
                estado_fmt = ":yellow[🟠 EN PROGRESO]"
            elif estado_str == "finalizado":
                estado_fmt = ":green[🟢 FINALIZADO]"
            elif estado_str == "cancelado":
                estado_fmt = ":red[🔴 CANCELADO]"
            else:
                estado_fmt = t.estado.upper()

            # Desplegable/Tarjeta para cada tarea
            with st.expander(f"OT N° {t.id} - {t.tag_equipo} | Estado: {estado_fmt}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Sector:** {t.sector}")
                    st.markdown(f"**Solicitante:** {t.supervisor.nombre}")
                    st.markdown(f"**Técnico:** {t.tecnico.nombre}")
                    st.markdown(f"**Fecha Alta:** {t.fecha}")
                with col2:
                    st.markdown(f"**Detalle de Tarea:**")
                    # Al ser markdown puro, hace wrap (renglón abajo) automáticamente si es largo
                    st.write(t.detalle_tarea) 

                if t.tarea_realizada:
                    st.success(f"**Trabajo Realizado ({t.fecha_realizado}):** {t.tarea_realizada}")

# -------------------------------------------------------------------
# 2. REGISTRAR NUEVA TAREA
# -------------------------------------------------------------------
elif opcion == "➕ Registrar Nueva Tarea":
    st.header("➕ Formulario de Alta de Tarea")
    
    supervisores_cargados = gestor.listar_supervisores()
    tecnicos_cargados = gestor.listar_tecnicos()

    if not supervisores_cargados or not tecnicos_cargados:
        st.warning("⚠️ Para registrar una tarea, primero debe haber al menos un Supervisor y un Técnico registrados en el sistema.")
        st.info("Por favor, diríjase al menú **'👤 Gestión de Personal'** para dar de alta al personal.")
    else:
        with st.form("form_alta", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("***Datos del Trabajo***")
                tag = st.text_input("Tag del Equipo")
                desc_eq = st.text_input("Descripción del Equipo")
                sector = st.text_input("Sector")
                detalle = st.text_area("Detalle de la Tarea a Realizar")
                fecha_obj = st.date_input("Fecha de Alta", format="DD/MM/YYYY")
                fecha = fecha_obj.strftime("%d/%m/%Y")

            with col2:
                st.subheader("*Asignación de Personal*")
                
                # Desplegable para seleccionar Supervisor existente
                dict_sup = {f"{s.nombre} ({s.sector_cargo})": s for s in supervisores_cargados}
                sup_label = st.selectbox("Seleccione el Supervisor *(Solicitante)*:", list(dict_sup.keys()))
                supervisor_seleccionado = dict_sup[sup_label]

                # Desplegable para seleccionar Técnico existente
                dict_tec = {f"{t.nombre} ({t.especialidad})": t for t in tecnicos_cargados}
                tec_label = st.selectbox("Seleccione el Técnico Asignado:", list(dict_tec.keys()))
                tecnico_seleccionado = dict_tec[tec_label]

            submitted = st.form_submit_button("💾 Guardar Tarea")

            if submitted:
                try:
                    nueva = gestor.registrar_tarea(
                        supervisor=supervisor_seleccionado,
                        tecnico=tecnico_seleccionado,
                        tag_equipo=tag,
                        descripcion_equipo=desc_eq,
                        sector=sector,
                        detalle_tarea=detalle,
                        fecha=fecha
                    )
                    st.success(f"✅ ¡Tarea registrada con éxito! OT N° asignado: {nueva.id}")
                except MantenimientoError as e:
                    st.error(f"⚠️ Error de negocio: {e}")

# -------------------------------------------------------------------
# 3. MODIFICAR ESTADO
# -------------------------------------------------------------------
elif opcion == "✏️ Modificar Estado":
    st.header("✏️ Modificar Estado de Orden de Trabajo")

    tareas_existentes = gestor.listar_todas()
    if not tareas_existentes:
        st.info("No hay tareas en el sistema para modificar.")
    else:
        # Selector desplegable de OTs disponibles
        dict_ots = {f"OT N° {t.id} - {t.tag_equipo} ({t.estado})": t.id for t in tareas_existentes}
        ot_seleccionada_label = st.selectbox("Seleccione la Orden de Trabajo:", list(dict_ots.keys()))
        ot_id = dict_ots[ot_seleccionada_label]

        tarea = gestor.buscar_por_ot(ot_id)

        st.write(f"**Estado Actual:** `{tarea.estado.upper()}`")
        st.write(f"**Detalle de Tarea Solicitada:** {tarea.detalle_tarea}")

        nuevo_estado = st.selectbox(
            "Seleccione el nuevo estado:",
            ["en progreso", "finalizado"],
        )

        fecha_realizado = ""
        tarea_realizada = ""

        if nuevo_estado == "finalizado":
            st.subheader("Datos del Trabajo Realizado")
            fecha_real_obj = st.date_input("Fecha de Realización", format="DD/MM/YYYY")
            fecha_realizado = fecha_real_obj.strftime("%d/%m/%Y")
            tarea_realizada = st.text_area("Detalle del Trabajo Realizado")

        if st.button("Actualizar Estado"):
            try:
                tarea_mod = gestor.cambiar_estado_tarea(
                    ot=ot_id,
                    nuevo_estado=nuevo_estado,
                    fecha_realizado=fecha_realizado,
                    tarea_realizada=tarea_realizada,
                )
                st.success(f"✅ Tarea OT N° {ot_id} actualizada correctamente a estado: '{tarea_mod.estado}'")
            except MantenimientoError as e:
                st.error(f"⚠️ Error de negocio: {e}")

# -------------------------------------------------------------------
# 4. CANCELAR TAREA
# -------------------------------------------------------------------
elif opcion == "🚫 Cancelar Tarea":
    st.header("🚫 Cancelación de Orden de Trabajo")

    tareas_existentes = gestor.listar_todas()
    if not tareas_existentes:
        st.info("No hay tareas en el sistema para cancelar.")
    else:
        dict_ots = {f"OT N° {t.id} - {t.tag_equipo} ({t.estado})": t.id for t in tareas_existentes}
        ot_seleccionada_label = st.selectbox("Seleccione la Orden de Trabajo a cancelar:", list(dict_ots.keys()))
        ot_id = dict_ots[ot_seleccionada_label]

        tarea = gestor.buscar_por_ot(ot_id)

        st.warning(f"⚠️ Está por cancelar la **OT N° {ot_id}** del equipo **{tarea.tag_equipo}**.")

        if st.button("Confirmar Cancelación de OT"):
            try:
                gestor.cancelar_tarea(ot_id)
                st.success(f"✅ La OT N° {ot_id} fue cancelada exitosamente.")
            except MantenimientoError as e:
                st.error(f"⚠️ Error de negocio: {e}")

# -------------------------------------------------------------------
# 5. GESTIÓN DE PERSONAL
# -------------------------------------------------------------------
elif opcion == "👤 Gestión de Personal":
    st.header("👤 Alta y Gestión de Personal")

    tab1, tab2 = st.tabs(["👔 Supervisores", "🔧 Técnicos"])

    # --- PESTAÑA SUPERVISORES ---
    with tab1:
        st.subheader("Registrar Nuevo Supervisor")
        with st.form("form_alta_supervisor"):
            dni_s = st.text_input("DNI del Supervisor")
            nom_s = st.text_input("Nombre y Apellido")
            sec_s = st.text_input("Sector / Cargo", value="Mantenimiento General")
            leg_s = st.text_input(" N° de Legajo")
            sub_sup = st.form_submit_button("💾 Guardar Supervisor")

            if sub_sup:
                try:
                    gestor.registrar_supervisor(dni_s, nom_s, sec_s, leg_s)
                    st.success(f"✅ Supervisor **{nom_s}** (Legajo {leg_s}) registrado correctamente.")
                    st.rerun()
                except MantenimientoError as e:
                    st.error(f"⚠️ {e}")

        st.divider()
        st.subheader("📋 Supervisores Registrados")
        sups = gestor.listar_supervisores()
        if sups:
            tabla_sups = [
                {"DNI": s.dni, "Nombre": s.nombre, "Legajo": s.legajo, "Sector / Cargo": s.sector_cargo}
                for s in sups
            ]
            st.table(tabla_sups)
        else:
            st.info("No hay supervisores registrados en el sistema.")

    # --- PESTAÑA TÉCNICOS ---
    with tab2:
        st.subheader("Registrar Nuevo Técnico")
        with st.form("form_alta_tecnico"):
            dni_t = st.text_input("DNI del Técnico")
            nom_t = st.text_input("Nombre y Apellido")
            esp_t = st.text_input("Especialidad (ej: Mecánica, Electricidad, Instrumentación)")
            leg_t = st.text_input("N° de Legajo")
            sub_tec = st.form_submit_button("💾 Guardar Técnico")

            if sub_tec:
                try:
                    gestor.registrar_tecnico(dni_t, nom_t, esp_t, leg_t)
                    st.success(f"✅ Técnico **{nom_t}** registrado correctamente.")
                    st.rerun()
                except MantenimientoError as e:
                    st.error(f"⚠️ {e}")

        st.divider()
        st.subheader("📋 Técnicos Registrados")
        tecs = gestor.listar_tecnicos()
        if tecs:
            tabla_tecs = [
                {
                    "Legajo": t.legajo,
                    "Nombre": t.nombre,
                    "Especialidad": t.especialidad,
                    "DNI": t.dni,
                }
                for t in tecs
            ]
            st.table(tabla_tecs)
        else:
            st.info("No hay técnicos registrados en el sistema.")
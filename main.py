import sys
from gestor import GestorTareas
from modelos import Supervisor, Tecnico
from excepciones import MantenimientoError, TareaNoEncontradaError


def mostrar_separador():
    print("-" * 80)


def mostrar_encabezado_tabla():
    mostrar_separador()
    print(
        f"| {'OT':<4} | {'Tag Equipo':<12} | {'Sector':<12} | {'Fecha':<10} | {'Estado':<12} | {'Técnico':<18} |"
    )
    mostrar_separador()


def mostrar_fila_tabla(tarea):
    print(
        f"| {tarea.id:<4} | {tarea.tag_equipo:<12} | {tarea.sector:<12} | {tarea.fecha:<10} | {tarea.estado:<12} | {tarea.tecnico.nombre:<18} |"
    )
    if tarea.estado == "finalizado":
        print(
            f"   └─> REALIZADO ({tarea.fecha_realizado}): {tarea.tarea_realizada}"
        )


def mostrar_menu():
    print("\n" + "=" * 50)
    print(" === SISTEMA DE GESTIÓN DE TAREAS (POO Python) ===")
    print("=" * 50)
    print("1. Registrar nueva tarea")
    print("2. Consultar tarea por N° de OT")
    print("3. Modificar estado de tarea")
    print("4. Cancelar tarea")
    print("5. Listar todas las tareas")
    print("6. Listar tareas por estado")
    print("0. Salir")
    print("-" * 50)


def main():
    gestor = GestorTareas()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        try:
            # ---------------------------------------------------------------
            # 1. ALTA DE TAREA
            # ---------------------------------------------------------------
            if opcion == "1":
                print("\n--- DATOS DEL TRABAJO ---")
                tag_equipo = input("Tag del equipo: ")
                descripcion_equipo = input("Descripción del equipo: ")
                sector = input("Sector de la planta: ")
                detalle_tarea = input("Detalle de la tarea a realizar: ")
                fecha = input("Fecha actual (DD/MM/AAAA): ")

                print("\n--- DATOS DEL SUPERVISOR (Solicitante) ---")
                dni_sup = input("DNI del supervisor: ")
                nom_sup = input("Nombre del supervisor: ")
                sec_sup = input("Sector a cargo [General]: ") or "General"
                leg_sup = input(" N° de Legajo :")
                supervisor = Supervisor(dni_sup, nom_sup, sec_sup, leg_sup)

                print("\n--- DATOS DEL TÉCNICO ASIGNADO ---")
                dni_tec = input("DNI del técnico: ")
                nom_tec = input("Nombre del técnico: ")
                esp_tec = input("Especialidad del técnico: ")
                leg_tec = input("Legajo del técnico: ")
                tecnico = Tecnico(dni_tec, nom_tec, esp_tec, leg_tec)

                nueva_tarea = gestor.registrar_tarea(
                    supervisor=supervisor,
                    tecnico=tecnico,
                    tag_equipo=tag_equipo,
                    descripcion_equipo=descripcion_equipo,
                    sector=sector,
                    detalle_tarea=detalle_tarea,
                    fecha=fecha,
                )
                print(f"\n✅ Tarea registrada con éxito. Número de OT asignado: {nueva_tarea.id}")

            # ---------------------------------------------------------------
            # 2. CONSULTAR TAREA POR OT
            # ---------------------------------------------------------------
            elif opcion == "2":
                ot_input = input("\nIngrese el N° de OT a buscar: ").strip()
                if not ot_input.isdigit():
                    raise ValueError("El número de OT debe ser un número entero.")
                
                ot = int(ot_input)
                tarea = gestor.buscar_por_ot(ot)
                
                print("\n" + "=" * 40)
                print("           DETALLE DE LA TAREA")
                print("=" * 40)
                print(tarea.mostrar_detalle())
                print("=" * 40)

            # ---------------------------------------------------------------
            # 3. MODIFICAR ESTADO DE TAREA
            # ---------------------------------------------------------------
            elif opcion == "3":
                ot_input = input("\nIngrese el N° de OT de la tarea a modificar: ").strip()
                if not ot_input.isdigit():
                    raise ValueError("El número de OT debe ser un número entero.")

                ot = int(ot_input)
                tarea = gestor.buscar_por_ot(ot)

                print(f"\nEstado actual de la OT {ot}: '{tarea.estado}'")
                print("Opciones de nuevo estado: [en progreso / finalizado]")
                nuevo_estado = input("Ingrese nuevo estado: ").strip()

                fecha_realizado = ""
                tarea_realizada = ""

                if nuevo_estado.lower() == "finalizado":
                    fecha_realizado = input("Ingrese fecha de realización (DD/MM/AAAA): ")
                    tarea_realizada = input("Ingrese detalle del trabajo realizado: ")

                tarea_actualizada = gestor.cambiar_estado_tarea(
                    ot=ot,
                    nuevo_estado=nuevo_estado,
                    fecha_realizado=fecha_realizado,
                    tarea_realizada=tarea_realizada,
                )
                print(f"\n✅ Tarea actualizada a estado: '{tarea_actualizada.estado}'.")

            # ---------------------------------------------------------------
            # 4. CANCELAR TAREA
            # ---------------------------------------------------------------
            elif opcion == "4":
                ot_input = input("\nIngrese el N° de OT de la tarea a cancelar: ").strip()
                if not ot_input.isdigit():
                    raise ValueError("El número de OT debe ser un número entero.")

                ot = int(ot_input)
                tarea = gestor.buscar_por_ot(ot)

                confirmacion = input(
                    f"¿Está seguro de cancelar la OT N° {ot} ({tarea.tag_equipo})? (S/N): "
                ).strip().lower()

                if confirmacion == "s":
                    gestor.cancelar_tarea(ot)
                    print("\n✅ Tarea cancelada correctamente.")
                else:
                    print("\nOperación abortada. La tarea no sufrió modificaciones.")

            # ---------------------------------------------------------------
            # 5. LISTAR TODAS LAS TAREAS
            # ---------------------------------------------------------------
            elif opcion == "5":
                listado = gestor.listar_todas()
                if not listado:
                    print("\nNo hay tareas registradas en el sistema.")
                else:
                    print("\n=== LISTADO GENERAL DE TAREAS DE MANTENIMIENTO ===")
                    mostrar_encabezado_tabla()
                    for t in listado:
                        mostrar_fila_tabla(t)
                        mostrar_separador()
                    print(f"Total de tareas registradas: {len(listado)}")

            # ---------------------------------------------------------------
            # 6. LISTAR TAREAS POR ESTADO
            # ---------------------------------------------------------------
            elif opcion == "6":
                print("\nEstados válidos: [pendiente / en progreso / finalizado / cancelado]")
                estado_buscado = input("Ingrese el estado a listar: ").strip()

                filtradas = gestor.listar_por_estado(estado_buscado)
                if not filtradas:
                    print(f"\nNo se encontraron tareas con el estado '{estado_buscado}'.")
                else:
                    print(f"\n=== LISTADO DE TAREAS - ESTADO: '{estado_buscado.upper()}' ===")
                    mostrar_encabezado_tabla()
                    for t in filtradas:
                        mostrar_fila_tabla(t)
                        mostrar_separador()
                    print(f"Total de tareas con estado '{estado_buscado}': {len(filtradas)}")

            # ---------------------------------------------------------------
            # 0. SALIR
            # ---------------------------------------------------------------
            elif opcion == "0":
                print("\n¡Hasta luego! Gracias por utilizar el sistema de mantenimiento.")
                sys.exit(0)

            else:
                print("\n⚠️ Opción no válida. Por favor, intente nuevamente.")

        # -------------------------------------------------------------------
        # MANEJO CENTRALIZADO DE EXCEPCIONES
        # -------------------------------------------------------------------
        except MantenimientoError as e:
            print(f"\n⚠️ ERROR DE NEGOCIO: {e}")
        except ValueError as e:
            print(f"\n⚠️ ERROR DE ENTRADA: {e}")
        except Exception as e:
            print(f"\n⚠️ ERROR INESPERADO: {e}")

        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()
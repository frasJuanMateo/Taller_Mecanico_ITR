import flet as ft
import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        database='taller_mecanico',
    )
    if connection.is_connected():
        cursor = connection.cursor()
        print('Conexión exitosa')
except Exception as ex:
    print("Error al conectar a la base de datos:", ex)


def Herramienta_Empleado(page: ft.Page, volver_callback):
    page.title = "Gestión de Empleados"
    page.scroll = True
    dni = ft.TextField(label="DNI", width=200)
    apellido = ft.TextField(label="Apellido", width=300)
    nombre = ft.TextField(label="Nombre", width=300)
    direccion = ft.TextField(label="Dirección", width=300)
    tele_contac = ft.TextField(label="Teléfono de contacto", width=200)
    legajo = ft.TextField(label="Legajo", width=150)

    def limpiar_campos(e=None):
        dni.value = ""
        apellido.value = ""
        nombre.value = ""
        direccion.value = ""
        tele_contac.value = ""
        legajo.value = ""
        page.update()

    def cargar_empleados_data():
        cursor.execute("""
            SELECT p.dni, p.apellido, p.nombre, p.direccion, p.tele_contac, e.legajo
            FROM persona p
            JOIN empleado e ON p.dni = e.dni
        """)
        data = cursor.fetchall()
        return [
            {
                "dni": row[0],
                "apellido": row[1],
                "nombre": row[2],
                "direccion": row[3],
                "tele_contac": row[4],
                "legajo": row[5]
            }
            for row in data
        ]

    def actualizar_tabla():
        tabla_empleados.rows.clear()
        for emp in cargar_empleados_data():
            tabla_empleados.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(emp["dni"])),
                        ft.DataCell(ft.Text(emp["apellido"])),
                        ft.DataCell(ft.Text(emp["nombre"])),
                        ft.DataCell(ft.Text(emp["direccion"] or "")),
                        ft.DataCell(ft.Text(emp["tele_contac"] or "")),
                        ft.DataCell(ft.Text(str(emp["legajo"]))),
                        ft.DataCell(ft.TextButton("Eliminar", icon=ft.Icons.DELETE,
                                                  on_click=lambda e, dni_val=emp["dni"]: eliminar_empleado(dni_val))),
                        ft.DataCell(ft.TextButton("Editar", icon=ft.Icons.EDIT,
                                                  on_click=lambda e, dni_val=emp["dni"]: editar_empleado(dni_val))),
                    ]
                )
            )
        page.update()

    def guardar_empleado(e):
        dni_val = dni.value.strip()
        apellido_val = apellido.value.strip()
        nombre_val = nombre.value.strip()
        direccion_val = direccion.value.strip()
        tele_val = tele_contac.value.strip()
        legajo_val = legajo.value.strip()

        if not all([dni_val, apellido_val, nombre_val, legajo_val]):
            page.open(ft.SnackBar(ft.Text("DNI, Apellido, Nombre y Legajo son obligatorios")))
            return

        try:
            # Insertar en persona
            cursor.execute(
                "INSERT INTO persona (dni, apellido, nombre, direccion, tele_contac) VALUES (%s, %s, %s, %s, %s)",
                (dni_val, apellido_val, nombre_val, direccion_val or None, tele_val or None)
            )
            # Insertar en empleado
            cursor.execute(
                "INSERT INTO empleado (legajo, dni) VALUES (%s, %s)",
                (legajo_val, dni_val)
            )
            connection.commit()
            actualizar_tabla()
            page.open(ft.SnackBar(ft.Text("Empleado guardado exitosamente")))
            limpiar_campos()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al guardar el empleado: {ex}")))
            cursor.execute("DELETE FROM persona WHERE dni = %s", (dni_val,))
            connection.commit()

    def eliminar_empleado(dni_val):
        try:
            cursor.execute("DELETE FROM empleado WHERE dni = %s", (dni_val,))
            cursor.execute("DELETE FROM persona WHERE dni = %s", (dni_val,))
            connection.commit()
            actualizar_tabla()
            
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}")))

    def editar_empleado(dni_val):
        cursor.execute("""
            SELECT p.dni, p.apellido, p.nombre, p.direccion, p.tele_contac, e.legajo
            FROM persona p
            JOIN empleado e ON p.dni = e.dni
            WHERE p.dni = %s
        """, (dni_val,))
        emp = cursor.fetchone()
        if emp:
            dni.value = emp[0]
            apellido.value = emp[1]
            nombre.value = emp[2]
            direccion.value = emp[3] or ""
            tele_contac.value = emp[4] or ""
            legajo.value = str(emp[5])
            # Borro el registro para reemplazarlo al guardar
            eliminar_empleado(dni_val)
            page.update()

    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar_empleado)
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_campos)
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    tabla_empleados = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("DNI")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Dirección")),
            ft.DataColumn(ft.Text("Teléfono")),
            ft.DataColumn(ft.Text("Legajo")),
            ft.DataColumn(ft.Text("")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[]
    )

    actualizar_tabla()

    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("Empleados registrados:", size=18, weight="bold"),
                tabla_empleados,
                ft.Divider(),
                ft.Text("Gestión de Empleados", size=24, weight="bold"),
                dni, apellido, nombre, direccion, tele_contac, legajo,
                ft.Row([guardar_btn, limpiar_btn, volver_btn], spacing=10),
            ],
            spacing=10,
        )
    )
    page.update()
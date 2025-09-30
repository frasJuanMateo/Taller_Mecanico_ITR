import flet as ft
import mysql.connector
from BuscadorDinamico import BuscadorDinamico

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='461315',
        database='taller_mecanico',
    )
    if connection.is_connected():
        cursor = connection.cursor()
        print('Conexión exitosa')
except Exception as ex:
    print("Error al conectar a la base de datos:", ex)


def Herramienta_Cliente(page: ft.Page, volver_callback):
    page.title = "Gestión de Clientes"
    page.scroll = True
    
    cod_cliente = ft.TextField(label="Código de Cliente", width=200)
    dni = ft.TextField(label="DNI", width=200)
    apellido = ft.TextField(label="Apellido", width=300)
    nombre = ft.TextField(label="Nombre", width=300)
    direccion = ft.TextField(label="Dirección", width=300)
    telefono = ft.TextField(label="Teléfono", width=200)

    def limpiar_campos(e=None):
        cod_cliente.value = ""
        dni.value = ""
        apellido.value = ""
        nombre.value = ""
        direccion.value = ""
        telefono.value = ""
        page.update()

    def cargar_clientes_data():
        cursor.execute("""
            SELECT c.cod_cliente, p.dni, p.apellido, p.nombre, p.direccion, p.telefono
            FROM cliente c
            JOIN persona p ON c.dni = p.dni
        """)
        data = cursor.fetchall()
        return [
            {
                "cod_cliente": row[0],
                "dni": row[1],
                "apellido": row[2],
                "nombre": row[3],
                "direccion": row[4],
                "telefono": row[5]
            }
            for row in data
        ]

    def actualizar_tabla():
        tabla_clientes.rows.clear()
        for cli in cargar_clientes_data():
            tabla_clientes.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cli["cod_cliente"])),
                        ft.DataCell(ft.Text(cli["dni"])),
                        ft.DataCell(ft.Text(cli["apellido"])),
                        ft.DataCell(ft.Text(cli["nombre"])),
                        ft.DataCell(ft.Text(cli["direccion"] or "")),
                        ft.DataCell(ft.Text(cli["telefono"] or "")),
                        ft.DataCell(ft.TextButton("Eliminar", icon=ft.Icons.DELETE,
                                                  on_click=lambda e, cod=cli["cod_cliente"]: eliminar_cliente(cod))),
                        ft.DataCell(ft.TextButton("Editar", icon=ft.Icons.EDIT,
                                                  on_click=lambda e, cod=cli["cod_cliente"]: editar_cliente(cod))),
                    ]
                )
            )
        page.update()

    def guardar_cliente(e):
        cod_val = cod_cliente.value.strip()
        dni_val = dni.value.strip()
        apellido_val = apellido.value.strip()
        nombre_val = nombre.value.strip()
        direccion_val = direccion.value.strip()
        tele_val = telefono.value.strip()

        if not all([cod_val, dni_val, apellido_val, nombre_val]):
            page.open(ft.SnackBar(ft.Text("Código, DNI, Apellido y Nombre son obligatorios")))
            return

        try:
            # Insertar en persona
            cursor.execute(
                "INSERT INTO persona (dni, apellido, nombre, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
                (dni_val, apellido_val, nombre_val, direccion_val or None, tele_val or None)
            )
            # Insertar en cliente
            cursor.execute(
                "INSERT INTO cliente (cod_cliente, dni) VALUES (%s, %s)",
                (cod_val, dni_val)
            )
            connection.commit()
            actualizar_tabla()
            buscador.actualizar_opciones_busqueda()
            page.open(ft.SnackBar(ft.Text("Cliente guardado exitosamente")))
            limpiar_campos()
        except Exception as ex:
            cursor.execute("DELETE FROM persona WHERE dni = %s", (dni_val,))
            connection.commit()
            page.open(ft.SnackBar(ft.Text(f"Error al guardar el cliente: {ex}")))

    def eliminar_cliente(cod_val):
        try:
            cursor.execute("DELETE FROM cliente WHERE cod_cliente = %s", (cod_val,))
            # Eliminamos también la persona si no está asociada a otro cliente
            cursor.execute("""
                DELETE FROM persona 
                WHERE dni NOT IN (SELECT dni FROM cliente)
            """)
            connection.commit()
            actualizar_tabla()
            buscador.actualizar_opciones_busqueda()

        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}")))

    def editar_cliente(cod_val):
        cursor.execute("""
            SELECT c.cod_cliente, p.dni, p.apellido, p.nombre, p.direccion, p.telefono
            FROM cliente c
            JOIN persona p ON c.dni = p.dni
            WHERE c.cod_cliente = %s
        """, (cod_val,))
        cli = cursor.fetchone()
        if cli:
            cod_cliente.value = cli[0]
            dni.value = cli[1]
            apellido.value = cli[2]
            nombre.value = cli[3]
            direccion.value = cli[4] or ""
            telefono.value = cli[5] or ""
            # Borro el registro para reemplazarlo al guardar
            eliminar_cliente(cod_val)
            page.update()

    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar_cliente)
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_campos)
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    tabla_clientes = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código Cliente")),
            ft.DataColumn(ft.Text("DNI")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Dirección")),
            ft.DataColumn(ft.Text("Teléfono")),
            ft.DataColumn(ft.Text("")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[]
    )
    
    column_keys = ['cod_cliente', 'dni', 'apellido', 'nombre', 'direccion', 'telefono']
    buscador = BuscadorDinamico(cursor, "cliente", "taller_mecanico", cargar_clientes_data, tabla_clientes, column_keys=column_keys)

    actualizar_tabla()
    buscador.actualizar_opciones_busqueda()
    page.controls.clear()
    
    page.add(
        ft.Column(
            [
                buscador,
                ft.Text("Clientes registrados:", size=18, weight="bold"),
                tabla_clientes,
                ft.Divider(),
                ft.Text("Gestión de Clientes", size=24, weight="bold"),
                cod_cliente, dni, apellido, nombre, direccion, telefono,
                ft.Row([guardar_btn, limpiar_btn, volver_btn], spacing=10),
            ],
            spacing=10,
        )
    )
    page.update()

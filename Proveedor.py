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


def Herramienta_Proveedor(page: ft.Page, volver_callback):
    page.title = "Gestión de Proveedores"
    page.scroll = True
    
    nombre = ft.TextField(label="Nombre", width=300)
    telefono = ft.TextField(label="Teléfono", width=300)
    email = ft.TextField(label="Email", width=300)
    direccion = ft.TextField(label="Dirección", width=300)

    proveedor_editando = None  # Para saber si estamos editando un registro

    def limpiar_campos(e=None):
        nonlocal proveedor_editando
        nombre.value = ""
        telefono.value = ""
        email.value = ""
        direccion.value = ""
        proveedor_editando = None
        page.update()

    def cargar_proveedores_data():
        cursor.execute("SELECT cod_proveedor, nombre, telefono, email, direccion FROM proveedor")
        proveedores_data = cursor.fetchall()
        return [
            {
                'cod_proveedor': p[0],
                'nombre': p[1],
                'telefono': p[2],
                'email': p[3],
                'direccion': p[4]
            }
            for p in proveedores_data
        ]

    def guardar_proveedor(e):
        nonlocal proveedor_editando
        nombre_val = nombre.value.strip()
        telefono_val = telefono.value.strip()
        email_val = email.value.strip()
        direccion_val = direccion.value.strip()

        if not all([nombre_val, telefono_val, email_val, direccion_val]):
            page.open(ft.SnackBar(ft.Text("Todos los campos son obligatorios")))
            return

        try:
            if proveedor_editando is None:
                # Insertar nuevo
                cursor.execute(
                    "INSERT INTO proveedor (nombre, telefono, email, direccion) VALUES (%s, %s, %s, %s)",
                    (nombre_val, telefono_val, email_val, direccion_val)
                )
            else:
                # Actualizar existente
                cursor.execute(
                    "UPDATE proveedor SET nombre=%s, telefono=%s, email=%s, direccion=%s WHERE cod_proveedor=%s",
                    (nombre_val, telefono_val, email_val, direccion_val, proveedor_editando)
                )

            connection.commit()
            actualizar_tabla()
            buscador.actualizar_opciones_busqueda()
            page.open(ft.SnackBar(ft.Text("Proveedor guardado exitosamente")))
            limpiar_campos()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al guardar el proveedor: {ex}")))

    def eliminar_proveedor(cod_proveedor):
        try:
            cursor.execute("DELETE FROM proveedor WHERE cod_proveedor = %s", (cod_proveedor,))
            connection.commit()
            actualizar_tabla()
            buscador.actualizar_opciones_busqueda()
            page.open(ft.SnackBar(ft.Text("Proveedor eliminado exitosamente")))
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}")))

    def editar_proveedor(cod_proveedor):
        nonlocal proveedor_editando
        cursor.execute("SELECT cod_proveedor, nombre, telefono, email, direccion FROM proveedor WHERE cod_proveedor=%s", (cod_proveedor,))
        prov = cursor.fetchone()
        if prov:
            proveedor_editando = prov[0]
            nombre.value = prov[1]
            telefono.value = prov[2]
            email.value = prov[3]
            direccion.value = prov[4]
            page.update()

    # Tabla
    tabla_proveedores = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Teléfono")),
            ft.DataColumn(ft.Text("Email")),
            ft.DataColumn(ft.Text("Dirección")),
            ft.DataColumn(ft.Text("")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[]
    )

    def actualizar_tabla():
        tabla_proveedores.rows.clear()
        for p in cargar_proveedores_data():
            tabla_proveedores.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p['cod_proveedor']))),
                        ft.DataCell(ft.Text(p['nombre'])),
                        ft.DataCell(ft.Text(p['telefono'])),
                        ft.DataCell(ft.Text(p['email'])),
                        ft.DataCell(ft.Text(p['direccion'])),
                        ft.DataCell(ft.TextButton("Eliminar", icon=ft.Icons.DELETE,
                                                  on_click=lambda e, prov=p: eliminar_proveedor(prov['cod_proveedor']))),
                        ft.DataCell(ft.TextButton("Editar", icon=ft.Icons.EDIT,
                                                  on_click=lambda e, prov=p: editar_proveedor(prov['cod_proveedor']))),
                    ]
                )
            )
        page.update()
    
    column_keys = ['cod_cliente', 'dni', 'apellido', 'nombre', 'direccion', 'telefono']
    buscador = BuscadorDinamico(cursor, "proveedor", "taller_mecanico", cargar_proveedores_data, tabla_proveedores, column_keys=column_keys)

    # Botones
    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar_proveedor)
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_campos)
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    # Layout
    actualizar_tabla()
    buscador.actualizar_opciones_busqueda()
    page.controls.clear()
    
    page.add(
        ft.Column(
            [
                buscador,
                ft.Text("Proveedores registrados:", size=18, weight="bold"),
                tabla_proveedores,
                ft.Divider(),
                ft.Text("Gestión de Proveedores", size=24, weight="bold"),
                nombre,
                telefono,
                email,
                direccion,
                ft.Row([guardar_btn, limpiar_btn, volver_btn], spacing=10),
            ],
            spacing=10,
        )
    )

    
    page.update()
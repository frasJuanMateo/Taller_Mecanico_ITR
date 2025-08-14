import flet as ft
import mysql.connector
from datetime import datetime

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

def Herramienta_Repuestos(page: ft.Page, volver_callback):
    page.title = "Gestión de Repuestos"
    page.scroll = True
    cod_repuesto = ft.TextField(label="Código de repuesto", width=300)
    descripcion = ft.TextField(label="Descripción", width=300)
    ingreso = ft.TextField(label="Ingreso (YYYY-MM-DD HH:MM:SS)", width=300)
    egreso = ft.TextField(label="Egreso (YYYY-MM-DD HH:MM:SS)", width=300)
    pcio_unit = ft.TextField(label="Precio unitario", width=300)

    # Función para limpiar
    def limpiar_campos(e=None):
        cod_repuesto.value = ""
        descripcion.value = ""
        ingreso.value = ""
        egreso.value = ""
        pcio_unit.value = ""
        page.update()

    # Cargar datos
    def cargar_repuestos_data():
        cursor.execute("SELECT cod_repuesto, descripcion, ingreso, egreso, pcio_unit FROM repuestos")
        data = cursor.fetchall()
        if not data:
            return []
        return [
            {
                'cod_repuesto': r[0],
                'descripcion': r[1] or "",
                'ingreso': r[2].strftime("%Y-%m-%d %H:%M:%S") if r[2] else "",
                'egreso': r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else "",
                'pcio_unit': r[4] if r[4] is not None else ""
            }
            for r in data
        ]

    # Guardar repuesto
    def guardar_repuesto(e):
        cod = cod_repuesto.value.strip()
        desc = descripcion.value.strip()
        ing = ingreso.value.strip() or None
        egr = egreso.value.strip() or None
        precio = pcio_unit.value.strip()

        if not cod or not precio:
            page.open(ft.SnackBar(ft.Text("Código y precio son obligatorios")))
            return

        try:
            cursor.execute(
                "INSERT INTO repuestos (cod_repuesto, descripcion, ingreso, egreso, pcio_unit) VALUES (%s, %s, %s, %s, %s)",
                (cod, desc or None, ing, egr, float(precio) if precio else None)
            )
            connection.commit()
            actualizar_tabla()
            page.open(ft.SnackBar(ft.Text("Repuesto guardado exitosamente")))
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al guardar: {ex}")))
        finally:
            limpiar_campos()

    # Eliminar repuesto
    def eliminar_repuesto(codigo):
        try:
            cursor.execute("DELETE FROM repuestos WHERE cod_repuesto = %s", (codigo,))
            connection.commit()
            actualizar_tabla()
            page.open(ft.SnackBar(ft.Text("Repuesto eliminado exitosamente")))
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}")))

    # Editar repuesto
    def editar_repuesto(codigo):
        cursor.execute("SELECT * FROM repuestos WHERE cod_repuesto = %s", (codigo,))
        r = cursor.fetchone()
        if r:
            cod_repuesto.value = r[0]
            descripcion.value = r[1] or ""
            ingreso.value = r[2].strftime("%Y-%m-%d %H:%M:%S") if r[2] else ""
            egreso.value = r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else ""
            pcio_unit.value = str(r[4] if r[4] is not None else "")
            eliminar_repuesto(codigo)  # para luego guardar la versión editada
            page.update()

    # Tabla
    tabla_repuestos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Ingreso")),
            ft.DataColumn(ft.Text("Egreso")),
            ft.DataColumn(ft.Text("Precio unitario")),
            ft.DataColumn(ft.Text("")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[],
    )

    # Actualizar tabla
    def actualizar_tabla():
        tabla_repuestos.rows.clear()
        for r in cargar_repuestos_data():
            tabla_repuestos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r['cod_repuesto'])),
                        ft.DataCell(ft.Text(r['descripcion'])),
                        ft.DataCell(ft.Text(r['ingreso'])),
                        ft.DataCell(ft.Text(r['egreso'])),
                        ft.DataCell(ft.Text(str(r['pcio_unit']))),
                        ft.DataCell(ft.TextButton("Eliminar", icon=ft.Icons.DELETE,
                                                  on_click=lambda e, cod=r['cod_repuesto']: eliminar_repuesto(cod))),
                        ft.DataCell(ft.TextButton("Editar", icon=ft.Icons.EDIT,
                                                  on_click=lambda e, cod=r['cod_repuesto']: editar_repuesto(cod))),
                    ]
                )
            )
        page.update()

    actualizar_tabla()

    # Botones
    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar_repuesto)
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_campos)
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("Repuestos registrados:", size=18, weight="bold"),
                tabla_repuestos,
                ft.Divider(),
                ft.Text("Gestión de Repuestos", size=24, weight="bold"),
                cod_repuesto,
                descripcion,
                ingreso,
                egreso,
                pcio_unit,
                ft.Row([guardar_btn, limpiar_btn, volver_btn], spacing=10),
            ],
            spacing=10,
        )
    )
    page.update()

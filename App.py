import flet as ft
import mysql.connector

from Usuario import Herramienta_Usuario
from Empleado import Herramienta_Empleado
from Cliente import Herramienta_Cliente
from Proveedor import Herramienta_Proveedor
from Repuesto import Herramienta_Repuestos

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='461315',
        database='taller_mecanico',
        #ssl_disabled=True,
    )
    if connection.is_connected():
        cursor = connection.cursor()
        print('Conexión exitosa')

except Exception as ex:
    print("Error al conectar a la base de datos:", ex)

def login(page: ft.Page):
    page.title = "Login"
    page.scroll = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = ft.padding.only(top=300)

    usuario_field = ft.TextField(label="Usuario", width=300)
    contraseña_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)

    def iniciar_sesion(e):
        user_val = usuario_field.value.strip()
        pass_val = contraseña_field.value.strip()

        if user_val and pass_val:
            cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND contraseña=%s", (user_val, pass_val))
            user_data = cursor.fetchone()
            if user_data or (user_val == "admin" and pass_val == "admin"):
                page.clean()
                inicio(page)
            else:
                page.open(ft.SnackBar(ft.Text("Usuario o contraseña incorrectos")))
        else:
            page.open(ft.SnackBar(ft.Text("Por favor, complete todos los campos")))

    login_btn = ft.ElevatedButton("Iniciar Sesión", on_click=iniciar_sesion)

    page.add(
        ft.Text("Inicia Sesion", style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)),
        usuario_field,
        contraseña_field,
        login_btn,
    )

def inicio(page: ft.Page):
    page.title = "Aplicacion de Administración de Taller Mecánico"
    page.padding = ft.padding.only(top=0)
    
    cliente_icono = ft.Icon(ft.Icons.PERSON, size=28)
    cliente_item = ft.Row(
        controls=[cliente_icono, ft.Text("Cliente")],
        alignment=ft.MainAxisAlignment.START,
        spacing=8,
    )

    proveedor_icono = ft.Icon(ft.Icons.BUSINESS, size=28)
    proveedor_item = ft.Row(
        controls=[proveedor_icono, ft.Text("Proveedor")],
        alignment=ft.MainAxisAlignment.START,
        spacing=8,
    )

    repuesto_icono = ft.Icon(ft.Icons.BUILD, size=28)
    repuesto_item = ft.Row(
        controls=[repuesto_icono, ft.Text("Repuesto")],
        alignment=ft.MainAxisAlignment.START,
        spacing=8,
    )

    empleado_icono = ft.Icon(ft.Icons.PEOPLE, size=28)
    empleado_item = ft.Row(
        controls=[empleado_icono, ft.Text("Empleado")],
        alignment=ft.MainAxisAlignment.START,
        spacing=8,
    )

    usuario_icono = ft.Icon(ft.Icons.PERSON_OUTLINE, size=28)
    usuario_item = ft.Row(
        controls=[usuario_icono, ft.Text("Usuario")],
        alignment=ft.MainAxisAlignment.START,
        spacing=8,
    )

    ficha_tecnica_icono = ft.Icon(ft.Icons.DIRECTIONS_CAR, size=28)
    ficha_tecnica_item = ft.Row(
        controls=[ficha_tecnica_icono, ft.Text("Ficha Técnica")],
        alignment=ft.MainAxisAlignment.START,
        spacing=8,
    )

    presupuesto_icono = ft.Icon(ft.Icons.ATTACH_MONEY, size=28)
    presupuesto_icono_item = ft.Row(
        controls=[presupuesto_icono, ft.Text("Presupuesto")]
    )

    archivo_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="Copiar", icon=ft.Icons.COPY, tooltip="Copiar"),
            ft.PopupMenuItem(text="Salir", icon=ft.Icons.EXIT_TO_APP, tooltip="Salir"),
        ],
        content=ft.Text("Archivo"),
        tooltip="Archivo",
    )

    herramientas_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(content=cliente_item, on_click=lambda e: cliente(e, page)),
            ft.PopupMenuItem(content=proveedor_item, on_click=lambda e: proveedor(e, page)),
            ft.PopupMenuItem(content=repuesto_item, on_click=lambda e: repuesto(e, page)),
            ft.PopupMenuItem(content=empleado_item, on_click=lambda e: empleado(e, page)),
            ft.PopupMenuItem(content=usuario_item, on_click=lambda e: usuario(e, page)),
        ],
        content=ft.Text("Herramientas"),
        tooltip="Administrador de archivos maestros",
    )

    administracion = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(content=ficha_tecnica_item),
            ft.PopupMenuItem(content=presupuesto_icono_item),
        ],
        content=ft.Text("Administración"),
        tooltip="Administración de presupuesto y ficha técnica",
    )

    boton_cliente = ft.IconButton(icon=ft.Icons.PERSON, tooltip="Cliente", on_click=lambda e: cliente(e, page))
    boton_usuario = ft.IconButton(icon=ft.Icons.PERSON_OUTLINE, tooltip="Usuario", on_click=lambda e: usuario(e, page))
    boton_repuesto = ft.IconButton(icon=ft.Icons.BUILD, tooltip="Repuesto", on_click=lambda e: repuesto(e, page))
    boton_proveedor = ft.IconButton(icon=ft.Icons.BUSINESS, tooltip="Proveedor", on_click=lambda e: proveedor(e, page))
    boton_empleado = ft.IconButton(icon=ft.Icons.PEOPLE, tooltip="Empleado", on_click=lambda e: empleado(e, page))
    boton_ficha_tecnica = ft.IconButton(ft.Icons.DIRECTIONS_CAR, tooltip="Ficha Técnica")
    boton_presupuesto = ft.IconButton(ft.Icons.ATTACH_MONEY, tooltip="Presupuesto")


    page.controls.clear()
    page.add(
        ft.Row(controls=[archivo_menu, administracion, herramientas_menu], spacing=10,),
        ft.Row(controls=[boton_cliente, boton_usuario, boton_repuesto, boton_proveedor, boton_empleado]),
        ft.Row(controls=[boton_ficha_tecnica, boton_presupuesto,]),
    )


def cliente(e, page: ft.Page):
    Herramienta_Cliente(page, inicio)


def proveedor(e, page: ft.Page):
    Herramienta_Proveedor(page, inicio)


def repuesto(e, page: ft.Page):
    Herramienta_Repuestos(page, inicio)


def empleado(e, page: ft.Page):
    Herramienta_Empleado(page, inicio)


def usuario(e, page: ft.Page):
    Herramienta_Usuario(page, inicio)


def main(page: ft.Page):
    page.window.maximized = True
    login(page)
    #inicio(page)


ft.app(target=main)

import flet as ft
import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        database='taller_mecanico',
        #ssl_disabled=True,
    )
    if connection.is_connected():
        cursor = connection.cursor()
        print('Conexión exitosa')
except Exception as ex:
    print("Error al conectar a la base de datos:", ex)

def Herramienta_Usuario(page: ft.Page, volver_callback):
    #Modificar esto para que se adapte a la estructura de la otra tabla
    page.title = "Gestión de Usuarios"
    page.scroll = True
    
    
    email = ft.TextField(label="Email", width=300)
    usuario = ft.TextField(label="Usuario", width=300)
    contraseña = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)

    def limpiar_campos(e):
        email.value = ""
        usuario.value = ""
        contraseña.value = ""
        page.update()

    def cargar_usuarios_data():
        cursor.execute("SELECT email, usuario, contraseña FROM usuarios")
        usuarios_data = cursor.fetchall()
        if not usuarios_data:
            return []
        else:
            usuarios_data = [{'email': u[0], 'usuario': u[1], 'contraseña': u[2]} for u in usuarios_data]
            page.update()
            return usuarios_data
    

    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda e: guardar_usuario(e))
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=lambda e: limpiar_campos(e))
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    def guardar_usuario(e):
        email_val = email.value.strip()
        usuario_val = usuario.value.strip()
        contraseña_val = contraseña.value.strip()

        if not all([email_val, usuario_val, contraseña_val]):
            page.open(ft.SnackBar(ft.Text("Todos los campos son obligatorios")))
            return

        try:
            cursor.execute(
                "INSERT INTO usuarios (email, usuario, contraseña) VALUES (%s, %s, %s)",
                (email_val, usuario_val, contraseña_val)
            )
            connection.commit()
            actualizar_tabla()  # Recargar la tabla de usuarios
            get_opciones()
            page.open(ft.SnackBar(ft.Text("Usuario guardado exitosamente")))
            page.update()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al guardar el usuario: {ex}")))
        finally:
            limpiar_campos(e)
            page.update()

    

    def eliminar_usuario(email_val):
        try:
            cursor.execute("DELETE FROM usuarios WHERE email = %s", (email_val,))
            connection.commit()
            actualizar_tabla()  # Recargar la tabla de usuarios
            get_opciones()
            page.update()
        except Exception as ex:
            print(f"Error al eliminar el usuario: {ex}")

    def editar_usuario(email_val):
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email_val,))
        user_data = cursor.fetchone()
        if user_data:
            email.value = user_data[0]
            usuario.value = user_data[1]
            contraseña.value = user_data[2]
            eliminar_usuario(email_val)
            page.update()
    
    tabla_usuarios = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Email")),
            ft.DataColumn(ft.Text("Usuario")),
            ft.DataColumn(ft.Text("")),
            ft.DataColumn(ft.Text("")),
        ], rows=[],
    )

    def actualizar_tabla():
        tabla_usuarios.rows.clear()
        for u in cargar_usuarios_data():
            tabla_usuarios.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(u['email'])),
                        ft.DataCell(ft.Text(u['usuario'])),
                        ft.DataCell(ft.TextButton("Eliminar", icon=ft.Icons.DELETE,
                                                on_click=lambda e, user=u: eliminar_usuario(user['email']))),
                        ft.DataCell(ft.TextButton("Editar", icon=ft.Icons.EDIT,
                                                on_click=lambda e, user=u: editar_usuario(user['email']))),
                    ]
                )
            )
        page.update()

    def busqueda_changed(e):
        selected_value = e.control.value
        
        for row in tabla_usuarios.rows:
            email_cell = row.cells[1].content.value
            
            if email_cell == selected_value:
                row.color = ft.Colors.YELLOW_100
                for cell in row.cells:
                    if isinstance(cell.content, ft.Text):
                        cell.content.color = ft.Colors.BLACK

            else:
                row.color = None
                for cell in row.cells:
                    if isinstance(cell.content, ft.Text):
                        cell.content.color = None
        
        page.update()
        
    busqueda = ft.Dropdown(
        border=ft.InputBorder.UNDERLINE,
        editable=True,
        leading_icon=ft.Icons.SEARCH,
        label="Usuarios",
        width=300,
        options=[ft.dropdown.Option(content=ft.Text("Seleccione el usuario"), key="Seleccione el usuario")],
        on_change=busqueda_changed,
        enable_filter=True,
        enable_search=True,
        text_align= ft.TextAlign.CENTER,)
    
    def get_opciones():
        opciones = [
            ft.dropdown.Option(content=ft.Text("Seleccione el usuario"), key="Seleccione el usuario")] + [
            ft.dropdown.Option(
                content=ft.Text(u['usuario']), key=u['usuario']
            ) for u in cargar_usuarios_data()
        ]
        if not cargar_usuarios_data():
            opciones = []
        busqueda.options = opciones

    get_opciones()
    actualizar_tabla()
    
    page.controls.clear()
    page.add(
        ft.Column(
            [
                busqueda,
                ft.Text("Usuarios registrados:", size=18, weight="bold"),
                tabla_usuarios,
                ft.Divider(),
                ft.Text("Gestión de Usuarios", size=24, weight="bold"),
                email,
                usuario,
                contraseña,
                ft.Row([guardar_btn, limpiar_btn, volver_btn], spacing=10),
                
            ],
            spacing=10,
        )
    )
    page.update()
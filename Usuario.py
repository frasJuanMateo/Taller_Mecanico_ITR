import flet as ft
import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='461315',
        database='taller_mecanico',
        #ssl_disabled=True,
    )
    if connection.is_connecteda():
        cursor = connection.cursor()
        print('Conexión exitosa')
except Exception as ex:
    print("Error al conectar a la base de datos:", ex)

def Herramienta_Usuario(page: ft.Page, volver_callback):
    #Modificar esto para que se adapte a la estructura de la otra tabla
    page.title = "Gestión de Usuarios"
    page.scroll = True
    
    nombre = ft.TextField(label="Nombre", width=300)
    apellido = ft.TextField(label="Apellido", width=300)
    email = ft.TextField(label="Email", width=300)
    telefono = ft.TextField(label="Teléfono", width=300)
    usuario = ft.TextField(label="Usuario", width=300)
    contraseña = ft.TextField(label="Contraseña", password=True, width=300)

    def limpiar_campos(e):
        nombre.value = ""
        apellido.value = ""
        email.value = ""
        telefono.value = ""
        usuario.value = ""
        contraseña.value = ""
        page.update()

    def cargar_usuarios_data():
        cursor.execute("SELECT nombre, apellido, email, telefono, usuario, contraseña FROM usuarios")
        usuarios_data = cursor.fetchall()
        if not usuarios_data:
            return []
        else:
            usuarios_data = [{'nombre': u[0], 'apellido': u[1], 'email': u[2], 'telefono': u[3], 'usuario': u[4], 'contraseña': u[5]} for u in usuarios_data]
            page.update()
            return usuarios_data
    

    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda e: guardar_usuario(e))
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=lambda e: limpiar_campos(e))
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    def guardar_usuario(e):
        nombre_val = nombre.value.strip()
        apellido_val = apellido.value.strip()
        email_val = email.value.strip()
        telefono_val = telefono.value.strip()
        usuario_val = usuario.value.strip()
        contraseña_val = contraseña.value.strip()

        if not all([nombre_val, apellido_val, email_val, telefono_val, usuario_val, contraseña_val]):
            page.open(ft.SnackBar(ft.Text("Todos los campos son obligatorios")))
            return

        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, apellido, email, telefono, usuario, contraseña) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre_val, apellido_val, email_val, telefono_val, usuario_val, contraseña_val)
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

    

    def eliminar_usuario(username):
        try:
            cursor.execute("DELETE FROM usuarios WHERE usuario = %s", (username,))
            connection.commit()
            actualizar_tabla()  # Recargar la tabla de usuarios
            get_opciones()
            page.update()
        except Exception as ex:
            print(f"Error al eliminar el usuario: {ex}")

    def editar_usuario(username):
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            nombre.value = user_data[0]
            apellido.value = user_data[1]
            email.value = user_data[2]
            telefono.value = user_data[3]
            usuario.value = user_data[4]
            contraseña.value = user_data[5]
            eliminar_usuario(username)
            page.update()
    
    tabla_usuarios = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("Email")),
            ft.DataColumn(ft.Text("Teléfono")),
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
                        ft.DataCell(ft.Text(u['nombre'])),
                        ft.DataCell(ft.Text(u['apellido'])),
                        ft.DataCell(ft.Text(u['email'])),
                        ft.DataCell(ft.Text(u['telefono'])),
                        ft.DataCell(ft.Text(u['usuario'])),
                        ft.DataCell(ft.TextButton("Eliminar", icon=ft.Icons.DELETE,
                                                on_click=lambda e, user=u: eliminar_usuario(user['usuario']))),
                        ft.DataCell(ft.TextButton("Editar", icon=ft.Icons.EDIT,
                                                on_click=lambda e, user=u: editar_usuario(user['usuario']))),
                    ]
                )
            )
        page.update()

    def busqueda_changed(e):
        selected_value = e.control.value
        page.update()
        
    busqueda = ft.Dropdown(
        border=ft.InputBorder.UNDERLINE,
        editable=True,
        leading_icon=ft.Icons.SEARCH,
        label="Usuarios",
        width=300,
        options=[],
        on_change=busqueda_changed,
        enable_filter=True,
        enable_search=True,
    )
    
    def get_opciones():
        opciones = [
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
                nombre,
                apellido,
                email,
                telefono,
                usuario,
                contraseña,
                ft.Row([guardar_btn, limpiar_btn, volver_btn], spacing=10),
                
            ],
            spacing=10,
        )
    )
    page.update()
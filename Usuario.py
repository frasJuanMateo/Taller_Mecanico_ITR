import flet as ft
import mysql.connector
from BuscadorDinamico import BuscadorDinamico

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


def Herramienta_Usuario(page: ft.Page, volver_callback):
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
            return [{'email': u[0], 'usuario': u[1], 'contraseña': u[2]} for u in usuarios_data]

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
            actualizar_tabla()
            actualizar_opciones_busqueda()
            page.open(ft.SnackBar(ft.Text("Usuario guardado exitosamente")))
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Error al guardar el usuario: {ex}")))
        finally:
            limpiar_campos(e)

    def eliminar_usuario(email_val):
        try:
            cursor.execute("DELETE FROM usuarios WHERE email = %s", (email_val,))
            connection.commit()
            actualizar_tabla()
            actualizar_opciones_busqueda()
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
        ],
        rows=[],
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

    def obtener_columnas(tabla_nombre):
        query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s
        """
        cursor.execute(query, (connection.database, tabla_nombre))
        columnas = [col[0] for col in cursor.fetchall()]
        return columnas

    
    # --- BUSCADOR ---
    columna_selector = ft.Dropdown(
        label="Buscar por",
        options = obtener_columnas("usuarios"),
        width=300,
    )

    valor_selector = ft.Dropdown(
        label="Seleccione valor",
        width=300,
        visible=False,
        on_change=lambda e: aplicar_filtro(e.control.value),
    )

    def actualizar_opciones_busqueda():
        #Recarga las opciones del segundo dropdown según la columna seleccionada
        if not columna_selector.value:
            valor_selector.visible = False
            page.update()
            return

        data = cargar_usuarios_data()
        valores_unicos = sorted(set([u[columna_selector.value] for u in data]))
        valor_selector.options = [ft.dropdown.Option(v) for v in valores_unicos]
        valor_selector.visible = True
        valor_selector.value = None
        page.update()

    def aplicar_filtro(valor):
        #Resalta en la tabla el registro que coincida
        if not columna_selector.value or not valor:
            return

        #col_index = obtener_columnas("usuarios").index(columna_selector.value)
        col_index = 0 if columna_selector.value == "email" else 1

        for row in tabla_usuarios.rows:
            cell_value = row.cells[col_index].content.value
            if cell_value == valor:
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

    columna_selector.on_change = lambda e: actualizar_opciones_busqueda()

    # Botones
    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar_usuario)
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_campos)
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    # Inicializar
    actualizar_tabla()
    actualizar_opciones_busqueda()

    page.controls.clear()
    page.add(
        ft.Column(
            [
                columna_selector,
                valor_selector,
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
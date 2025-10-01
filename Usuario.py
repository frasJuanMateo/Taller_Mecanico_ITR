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


def Herramienta_Usuario(page: ft.Page, volver_callback):
    page.title = "Gestión de Usuarios"
    page.scroll = True

    email = ft.TextField(label="Email", width=300)
    usuario = ft.TextField(label="Usuario", width=300)
    contraseña = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
    empleado_dropdown = ft.Dropdown(
        label="Empleado asignado",
        width=300,
        options=[]
    )

    def limpiar_campos(e):
        email.value = ""
        usuario.value = ""
        contraseña.value = ""
        page.update()
        
    def cargar_empleados():
        cursor.execute("""
            SELECT e.legajo, p.nombre, p.apellido
            FROM empleado e
            JOIN persona p ON e.dni = p.dni
        """)
        empleados = cursor.fetchall()
        return [
            {"legajo": e[0], "nombre": f"{e[1]} {e[2]}"}
            for e in empleados
        ]
        
    def actualizar_empleados_dropdown():
        empleados = cargar_empleados()
        empleado_dropdown.options = [
            ft.dropdown.Option(str(emp["legajo"]), f"{emp['nombre']} (Legajo {emp['legajo']})")
            for emp in empleados
        ]
        page.update()


    def cargar_usuarios_data():
        cursor.execute("""
            SELECT u.email, u.usuario, u.contraseña, u.legajo, p.nombre, p.apellido
            FROM usuarios u
            JOIN empleado e ON u.legajo = e.legajo
            JOIN persona p ON e.dni = p.dni
        """)
        usuarios_data = cursor.fetchall()
        return [
            {
                'email': u[0],
                'usuario': u[1],
                'contraseña': u[2],
                'legajo': u[3],
                'empleado': f"{u[4]} {u[5]}"
            }
            for u in usuarios_data
        ]


    def guardar_usuario(e):
        email_val = email.value.strip()
        usuario_val = usuario.value.strip()
        contraseña_val = contraseña.value.strip()
        legajo_val = empleado_dropdown.value

        if not all([email_val, usuario_val, contraseña_val, legajo_val]):
            page.open(ft.SnackBar(ft.Text("Todos los campos son obligatorios")))
            return

        try:
            cursor.execute(
                "INSERT INTO usuarios (email, usuario, contraseña, legajo) VALUES (%s, %s, %s, %s)",
                (email_val, usuario_val, contraseña_val, legajo_val)
            )
            connection.commit()
            actualizar_tabla()
            buscador.actualizar_opciones_busqueda()
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
            buscador.actualizar_opciones_busqueda()
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
            ft.DataColumn(ft.Text("Empleado")),
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
                        ft.DataCell(ft.Text(u['empleado'])),
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
    column_keys = ['email', 'usuario']
    buscador = BuscadorDinamico(cursor, "usuarios", "taller_mecanico", cargar_usuarios_data, tabla_usuarios, column_keys=column_keys)
    
    # Botones
    guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar_usuario)
    limpiar_btn = ft.ElevatedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_campos)
    volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_callback(page))

    # Inicializar
    actualizar_tabla()
    buscador.actualizar_opciones_busqueda()
    actualizar_empleados_dropdown()
    page.controls.clear()
    
    page.add(
        ft.Column(
            [
                buscador,
                ft.Text("Usuarios registrados:", size=18, weight="bold"),
                tabla_usuarios,
                ft.Divider(),
                ft.Text("Gestión de Usuarios", size=24, weight="bold"),
                email,
                usuario,
                contraseña,
                empleado_dropdown,
                ft.Row([guardar_btn, limpiar_btn, volver_btn], spacing=10),
            ],
            spacing=10,
        )
    )
    page.update()
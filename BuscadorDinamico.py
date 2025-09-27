import flet as ft

class BuscadorDinamico(ft.Column):
    def __init__(self, cursor, tabla_nombre, db_name, cargar_data_fn, tabla_control):
        super().__init__(spacing=10)

        self.cursor = cursor
        self.tabla_nombre = tabla_nombre
        self.db_name = db_name
        self.cargar_data_fn = cargar_data_fn
        self.tabla_control = tabla_control

        # Dropdown para elegir columna
        self.columna_selector = ft.Dropdown(
            label="Buscar por",
            width=300,
            options=[ft.dropdown.Option(c) for c in self.obtener_columnas()],
            on_change=self.actualizar_opciones_busqueda
        )

        # Dropdown para valores de esa columna
        self.valor_selector = ft.Dropdown(
            label="Seleccione valor",
            width=300,
            visible=False,
            on_change=self.aplicar_filtro
        )

        # Agregamos los controles al layout
        self.controls = [self.columna_selector, self.valor_selector]

    def obtener_columnas(self):
        """Devuelve un array con los nombres de columnas de la tabla"""
        query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        self.cursor.execute(query, (self.db_name, self.tabla_nombre))
        return [col[0] for col in self.cursor.fetchall()]

    def actualizar_opciones_busqueda(self, e=None):
        """Carga los valores únicos de la columna seleccionada"""
        if not self.columna_selector.value:
            self.valor_selector.visible = False
            return

        data = self.cargar_data_fn()
        valores_unicos = sorted(set([str(u[self.columna_selector.value]) for u in data]))
        self.valor_selector.options = [ft.dropdown.Option(v) for v in valores_unicos]
        self.valor_selector.visible = True
        self.valor_selector.value = None

    def aplicar_filtro(self, e=None):
        """Resalta en la tabla el registro que coincida"""
        if not self.columna_selector.value or not self.valor_selector.value:
            return

        # Determinar índice de la columna en la DataTable
        col_index = [c.label.value for c in self.tabla_control.columns].index(self.columna_selector.value)

        for row in self.tabla_control.rows:
            cell_value = row.cells[col_index].content.value
            if str(cell_value) == str(self.valor_selector.value):
                row.color = ft.Colors.YELLOW_100
            else:
                row.color = None
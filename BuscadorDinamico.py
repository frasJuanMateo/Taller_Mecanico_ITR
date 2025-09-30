# BuscadorDinamico.py
import flet as ft
import unicodedata

class BuscadorDinamico(ft.Column):
    """
    Buscador dinámico reutilizable.
    - cursor: cursor MySQL ya inicializado
    - tabla_nombre, db_name: para consultar INFORMATION_SCHEMA
    - cargar_data_fn: función que devuelve lista de dicts con los datos (orden de keys preferible)
    - tabla_control: el ft.DataTable que queremos filtrar/resaltar
    - column_keys (opcional): lista explícita de nombres de columnas (ej: ['email','usuario','contraseña'])
    """
    def __init__(self, cursor, tabla_nombre, db_name, cargar_data_fn, tabla_control, column_keys=None, label_columna="Buscar por"):
        super().__init__(spacing=10)

        self.cursor = cursor
        self.tabla_nombre = tabla_nombre
        self.db_name = db_name
        self.cargar_data_fn = cargar_data_fn
        self.tabla_control = tabla_control

        # columnas de la BD
        self.db_columns = self.obtener_columnas()

        # si el usuario da column_keys los usamos, si no intentamos inferir
        self.column_keys = column_keys or self._infer_column_keys()

        # mapeo column_key -> índice en tabla_control.rows (int)
        self.col_key_to_index = self._mapear_columnas()

        # dropdowns
        self.columna_selector = ft.Dropdown(
            label=label_columna,
            width=300,
            options=[ft.dropdown.Option(c) for c in self.column_keys],
            on_change=self.actualizar_opciones_busqueda
        )

        # editable=True para permitir escribir manualmente
        self.valor_selector = ft.Dropdown(
            label="Valor (escriba o seleccione)",
            width=300,
            visible=False,
            editable=True,
            enable_search=True,
            on_change=self.aplicar_filtro
        )

        self.controls = [self.columna_selector, self.valor_selector]

    # ---------------- utilidades ----------------
    def _normalize(self, s):
        s = str(s or "")
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
        return s.lower().strip()

    def obtener_columnas(self):
        q = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """
        self.cursor.execute(q, (self.db_name, self.tabla_nombre))
        return [r[0] for r in self.cursor.fetchall()]

    def _infer_column_keys(self):
        # 1) intentamos tomar la primera fila devuelta por cargar_data_fn y obtener keys en ese orden
        try:
            data = self.cargar_data_fn()
            if isinstance(data, list) and data:
                first = data[0]
                if isinstance(first, dict):
                    return list(first.keys())
        except Exception:
            pass
        # 2) fallback a las columnas de la BD
        return self.db_columns

    def _mapear_columnas(self):
        """
        Construye mapping col_key -> índice de columna en la DataTable.
        Intenta hacer match entre column_keys (nombres de dict/db) y las labels de DataTable (insensible a mayúsculas/acentos).
        Si falla, usa la posición (order) como fallback.
        """
        mapping = {}
        # normalizamos etiquetas de DataTable
        labels_norm = []
        for i, c in enumerate(self.tabla_control.columns):
            label = c.label.value if hasattr(c.label, "value") else str(c.label)
            labels_norm.append((i, label, self._normalize(label)))

        # para cada key tratamos de encontrar mejor índice
        for i_key, key in enumerate(self.column_keys):
            key_norm = self._normalize(key)
            found_idx = None
            # 1) buscar label exacto
            for idx, label, lab_norm in labels_norm:
                if lab_norm == key_norm:
                    found_idx = idx
                    break
            # 2) buscar si el key norm aparece dentro del label norm (ej: "email" vs "email usuario")
            if found_idx is None:
                for idx, label, lab_norm in labels_norm:
                    if key_norm in lab_norm or lab_norm in key_norm:
                        found_idx = idx
                        break
            # 3) fallback por posición (si las longitudes coinciden)
            if found_idx is None and i_key < len(self.tabla_control.columns):
                found_idx = i_key

            if found_idx is not None:
                mapping[key] = found_idx
        return mapping

    # ---------------- lógica ----------------
    def actualizar_opciones_busqueda(self, e=None):
        col = self.columna_selector.value
        if not col:
            self.valor_selector.visible = False
            if self.page:   # 👈 verificar si ya está agregado al page
                self.update()
            return

        data = self.cargar_data_fn() or []
        valores_unicos = sorted({str(row.get(col, "") or "") for row in data if row.get(col, "") is not None})
        valores_unicos = [v for v in valores_unicos if v != ""]

        self.valor_selector.options = [ft.dropdown.Option("(Deseleccionar)")] + [ft.dropdown.Option(v) for v in valores_unicos]
        self.valor_selector.value = None
        self.valor_selector.visible = True

        if self.page:       # 👈 solo hacer update si ya está en el page
            self.update()


        try:
            data = self.cargar_data_fn() or []
        except Exception:
            data = []

        valores_unicos = sorted({str(row.get(col, "") or "") for row in data if row.get(col, "") is not None})
        # opcionales: quitar strings vacíos
        valores_unicos = [v for v in valores_unicos if v != ""]

        self.valor_selector.options = [ft.dropdown.Option("(Deseleccionar)")] + [ft.dropdown.Option(v) for v in valores_unicos]
        self.valor_selector.value = None
        self.valor_selector.visible = True
        self.update()

    def aplicar_filtro(self, e=None):
        """Resalta filas que coincidan con el valor (igual o que contengan, case-insensitive y sin acentos)"""
        col = self.columna_selector.value
        val = self.valor_selector.value
        if not col:
            return

        # si valor vacío -> limpiar resaltados
        if not val:
            for row in self.tabla_control.rows:
                row.color = None
                for cell in row.cells:
                    if isinstance(cell.content, ft.Text):
                        cell.content.color = None
            self.tabla_control.update()
            return

        # obtener índice de columna en la DataTable
        col_index = self.col_key_to_index.get(col, None)
        if col_index is None:
            # intentar encontrar por normalización de labels
            for i, c in enumerate(self.tabla_control.columns):
                label = c.label.value if hasattr(c.label, "value") else str(c.label)
                if self._normalize(label) == self._normalize(col):
                    col_index = i
                    break
        if col_index is None:
            # no encontramos índice -> no hacemos nada
            return

        val_norm = self._normalize(val)
        for row in self.tabla_control.rows:
            # obtener texto de la celda
            try:
                content = row.cells[col_index].content
                if isinstance(content, ft.Text):
                    cell_text = content.value
                else:
                    # intentar sacar atributos comunes si no es ft.Text
                    cell_text = getattr(content, "text", None) or getattr(content, "value", None) or str(content)
            except Exception:
                cell_text = ""

            cell_norm = self._normalize(cell_text)

            # si coincide exactamente o contiene -> resaltar
            if val_norm == cell_norm or val_norm in cell_norm:
                row.color = ft.Colors.YELLOW_100
                for cell in row.cells:
                    if isinstance(cell.content, ft.Text):
                        cell.content.color = ft.Colors.BLACK
            else:
                row.color = None
                for cell in row.cells:
                    if isinstance(cell.content, ft.Text):
                        cell.content.color = None

        self.tabla_control.update()
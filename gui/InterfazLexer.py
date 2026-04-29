"""
gui_tk.py — Interfaz gráfica Tkinter del Analizador Léxico
Compiladores — Entrega 1 | Lenguaje fuente → TypeScript

Ejecutar:  python gui_tk.py
Requiere:  tkinter 
Archivos:  tokens.py  lexer.py  gui_logic.py  (mismo directorio)
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import threading

from lexico.Tokens import TokenType
from lexico.LogicaLexer import EstadoLexer, PROGRAMAS, CategoriaToken
from gui.Estilos import TEMA as T

# Categorías en orden para la leyenda
CATEGORIAS = [
    "reservada", "tipo", "logico", "operador", "delimitador",
    "identificador", "numero", "cadena", "booleano", "error"
]


# ═══════════════════════════════════════════════════════════════════
# APLICACIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

class AplicacionLexer:

    def __init__(self, root: tk.Tk):
        self.root   = root
        self.estado = EstadoLexer()

        # Configurar ventana
        root.title("Analizador Lexico — Lenguaje fuente a TypeScript")
        root.geometry("1360x840")
        root.minsize(1100, 700)
        root.configure(bg=T["bg"])

        # Fuentes
        try:
            self.f_code   = tkfont.Font(family="Consolas",    size=13)
            self.f_code_b = tkfont.Font(family="Consolas",    size=13, weight="bold")
            self.f_code_s = tkfont.Font(family="Consolas",    size=11)
            self.f_ui     = tkfont.Font(family="Segoe UI",    size=11)
            self.f_ui_b   = tkfont.Font(family="Segoe UI",    size=11, weight="bold")
            self.f_ui_s   = tkfont.Font(family="Segoe UI",    size=10)
            self.f_ui_xs  = tkfont.Font(family="Segoe UI",    size=9)
            self.f_title  = tkfont.Font(family="Segoe UI",    size=13, weight="bold")
        except Exception:
            self.f_code   = tkfont.Font(family="Courier New", size=13)
            self.f_code_b = tkfont.Font(family="Courier New", size=13, weight="bold")
            self.f_code_s = tkfont.Font(family="Courier New", size=11)
            self.f_ui     = tkfont.Font(size=11)
            self.f_ui_b   = tkfont.Font(size=11, weight="bold")
            self.f_ui_s   = tkfont.Font(size=10)
            self.f_ui_xs  = tkfont.Font(size=9)
            self.f_title  = tkfont.Font(size=13, weight="bold")

        self._build_ui()
        self._cargar_preset(0)

    # ── Construcción de la UI ─────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_errores()

    # ── Header ────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=T["header_bg"], height=52)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="Analizador Lexico",
                 bg=T["header_bg"], fg=T["text_white"],
                 font=self.f_title).pack(side="left", padx=16, pady=14)

        tk.Label(hdr,
                 text="Compiladores  ·  Entrega 1  |  Lenguaje fuente a TypeScript",
                 bg=T["header_bg"], fg=T["text_header"],
                 font=self.f_ui_s).pack(side="left", pady=14)

        # Stats (derecha)
        self.lbl_stats = tk.Label(
            hdr, text="", bg=T["header_bg"],
            fg=T["text_header"], font=self.f_ui_s)
        self.lbl_stats.pack(side="right", padx=16)

        # Leyenda (debajo del header, fondo bg)
        self._build_leyenda()

    def _build_leyenda(self):
        ley_frame = tk.Frame(self.root, bg=T["bg"], pady=4)
        ley_frame.pack(fill="x", side="top")
        for cat in CATEGORIAS:
            c  = T[cat]
            bg = T[f"{cat}_bg"]
            tk.Label(ley_frame,
                     text=f"  {cat.upper()}  ",
                     bg=bg, fg=c,
                     font=self.f_ui_xs,
                     relief="flat",
                     bd=0,
                     padx=2).pack(side="left", padx=2, pady=0)

    # ── Body — columna izquierda + derecha ────────────────────

    def _build_body(self):
        body = tk.PanedWindow(self.root, orient="horizontal",
                              bg=T["bg"], sashwidth=6,
                              sashrelief="flat", bd=0)
        body.pack(fill="both", expand=True,
                  padx=10, pady=(6,0))

        # ── Columna izquierda ──
        left = tk.Frame(body, bg=T["bg"])
        body.add(left, minsize=420, stretch="always")
        self._build_panel_editor(left)

        # ── Columna derecha ──
        right = tk.Frame(body, bg=T["bg"])
        body.add(right, minsize=500, stretch="always")
        self._build_panel_derecho(right)

        # Proporción inicial: 42% / 58%
        self.root.update_idletasks()
        W = self.root.winfo_width()
        body.sash_place(0, int(W * 0.42), 0)

    # ── Panel izquierdo: editor ───────────────────────────────

    def _build_panel_editor(self, parent):
        # Cabecera del panel
        self._panel_header(parent, "Codigo Fuente", T["accent"])

        # Presets
        pre_frame = tk.Frame(parent, bg=T["bg"], pady=4)
        pre_frame.pack(fill="x", padx=8)
        self.preset_btns = []
        for i, (nombre, _) in enumerate(PROGRAMAS):
            btn = tk.Button(
                pre_frame, text=nombre,
                bg=T["surface"], fg=T["text"],
                font=self.f_ui_s, relief="flat",
                bd=1, padx=6, pady=3, cursor="hand2",
                command=lambda i=i: self._cargar_preset(i))
            btn.pack(side="left", padx=2)
            self.preset_btns.append(btn)

        # Editor de texto
        editor_frame = tk.Frame(parent, bg=T["border"], bd=1)
        editor_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self.editor = tk.Text(
            editor_frame,
            font=self.f_code,
            bg=T["surface2"], fg=T["text_bright"],
            insertbackground=T["accent"],
            selectbackground=T["accent_light"],
            selectforeground=T["text"],
            relief="flat", bd=0,
            padx=8, pady=6,
            undo=True,
            wrap="none")
        self.editor.pack(fill="both", expand=True)

        # Scrollbar editor
        sb_e = ttk.Scrollbar(editor_frame, orient="vertical",
                              command=self.editor.yview)
        self.editor.configure(yscrollcommand=sb_e.set)
        sb_e.pack(side="right", fill="y")

        # Resetear análisis al editar
        self.editor.bind("<<Modified>>", self._on_editor_modified)

        # Botones de acción
        btn_frame = tk.Frame(parent, bg=T["bg"], pady=8)
        btn_frame.pack(fill="x", padx=8)

        self.btn_todo = tk.Button(
            btn_frame, text="Analizar todo",
            bg=T["accent"], fg=T["text_white"],
            font=self.f_ui_b, relief="flat",
            padx=14, pady=6, cursor="hand2",
            activebackground="#1D4ED8",
            activeforeground=T["text_white"],
            command=self._analizar_todo)
        self.btn_todo.pack(side="left", padx=(0,6))

        self.btn_paso = tk.Button(
            btn_frame, text="Paso siguiente",
            bg=T["surface"], fg=T["accent"],
            font=self.f_ui_b, relief="flat",
            bd=1, padx=14, pady=6, cursor="hand2",
            activebackground=T["accent_light"],
            command=self._siguiente_paso)
        self.btn_paso.pack(side="left", padx=(0,6))

        self.btn_reset = tk.Button(
            btn_frame, text="Reiniciar",
            bg=T["surface"], fg=T["text"],
            font=self.f_ui, relief="flat",
            bd=1, padx=14, pady=6, cursor="hand2",
            activebackground=T["surface3"],
            command=self._reiniciar)
        self.btn_reset.pack(side="left")

        # Barra de progreso
        prog_frame = tk.Frame(parent, bg=T["bg"])
        prog_frame.pack(fill="x", padx=8, pady=(0,6))

        self.lbl_progreso = tk.Label(
            prog_frame, text="", bg=T["bg"],
            fg=T["text_dim"], font=self.f_ui_xs)
        self.lbl_progreso.pack(side="right")

        self.progress = ttk.Progressbar(
            prog_frame, orient="horizontal",
            mode="determinate", maximum=100)
        self.progress.pack(fill="x", side="left", expand=True)

        # Estilo de la progressbar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar",
                         troughcolor=T["progress_bg"],
                         background=T["progress_fill"],
                         bordercolor=T["progress_bg"],
                         lightcolor=T["progress_fill"],
                         darkcolor=T["progress_fill"])

    # ── Panel derecho: visualizador + tabla ───────────────────

    def _build_panel_derecho(self, parent):
        pw = tk.PanedWindow(parent, orient="vertical",
                            bg=T["bg"], sashwidth=6,
                            sashrelief="flat", bd=0)
        pw.pack(fill="both", expand=True)
        self.pw_derecho = pw

        # Panel visualizador (arriba)
        viz_frame = tk.Frame(pw, bg=T["bg"])
        pw.add(viz_frame, minsize=180, stretch="always")
        self._build_panel_viz(viz_frame)

        # Panel tabla (abajo)
        tab_frame = tk.Frame(pw, bg=T["bg"])
        pw.add(tab_frame, minsize=140, stretch="always")
        self._build_panel_tabla(tab_frame)

        # Proporción inicial: 58% / 42%
        self.root.after(50, self._set_sash_derecho)

    def _set_sash_derecho(self):
        try:
            H = self.pw_derecho.winfo_height()
            self.pw_derecho.sash_place(0, 0, int(H * 0.58))
        except Exception:
            pass

    # ── Visualizador ──────────────────────────────────────────

    def _build_panel_viz(self, parent):
        self._panel_header(
            parent,
            "Posicion del Analizador  —  Codigo resaltado en tiempo real",
            T["accent2"])

        viz_inner = tk.Frame(parent, bg=T["surface"],
                             relief="flat", bd=1,
                             highlightbackground=T["border"],
                             highlightthickness=1)
        viz_inner.pack(fill="both", expand=True, padx=8, pady=(4,0))

        self.viz = tk.Text(
            viz_inner,
            font=self.f_code,
            bg=T["surface"], fg=T["text_bright"],
            relief="flat", bd=0,
            padx=10, pady=8,
            state="disabled",
            cursor="arrow",
            wrap="none",
            spacing1=2, spacing3=2)
        self.viz.pack(fill="both", expand=True)

        sb_vx = ttk.Scrollbar(viz_inner, orient="horizontal",
                               command=self.viz.xview)
        sb_vy = ttk.Scrollbar(viz_inner, orient="vertical",
                               command=self.viz.yview)
        self.viz.configure(xscrollcommand=sb_vx.set,
                           yscrollcommand=sb_vy.set)
        sb_vy.pack(side="right",  fill="y")
        sb_vx.pack(side="bottom", fill="x")

        # Configurar tags de colores por categoría
        self._setup_viz_tags()

        # Label indicador del token activo (parte inferior)
        self.lbl_tok_activo = tk.Label(
            parent, text="",
            bg=T["bg"], fg=T["text_dim"],
            font=self.f_ui_b,
            relief="flat", padx=10, pady=4)
        self.lbl_tok_activo.pack(fill="x", padx=8, pady=4)

    def _setup_viz_tags(self):
        """Registra todos los tags de colores en el widget viz."""
        for cat in CATEGORIAS:
            self.viz.tag_configure(
                cat,
                foreground=T[cat],
                font=self.f_code)
            self.viz.tag_configure(
                f"{cat}_activo",
                foreground=T[cat],
                background=T[f"{cat}_bg"],
                font=self.f_code_b)

        self.viz.tag_configure(
            "consumido",
            foreground=T["border"],
            font=self.f_code)
        self.viz.tag_configure(
            "linea_activa",
            background=T["accent_light"])
        self.viz.tag_configure(
            "espacio",
            foreground=T["text_dim"],
            font=self.f_code)

    # ── Tabla de símbolos ──────────────────────────────────────

    def _build_panel_tabla(self, parent):
        self._panel_header(parent, "Tabla de Simbolos Lexicos", T["tipo"])

        tabla_frame = tk.Frame(parent, bg=T["surface"])
        tabla_frame.pack(fill="both", expand=True, padx=8, pady=(4,4))

        # Estilo de la tabla
        style = ttk.Style()
        style.configure("Lexer.Treeview",
                         font=("Consolas", 11),
                         rowheight=24,
                         background=T["surface"],
                         fieldbackground=T["surface"],
                         foreground=T["text"],
                         borderwidth=0)
        style.configure("Lexer.Treeview.Heading",
                         font=("Segoe UI", 9, "bold"),
                         background=T["surface2"],
                         foreground=T["text_dim"],
                         borderwidth=0,
                         relief="flat")
        style.map("Lexer.Treeview",
                  background=[("selected", T["row_active"])],
                  foreground=[("selected", T["text"])])

        cols = ("lexema", "categoria", "tokentype", "fila", "columna")
        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=cols,
            show="headings",
            style="Lexer.Treeview",
            selectmode="browse")

        # Configurar columnas
        anchos = {"lexema":150, "categoria":110,
                  "tokentype":150, "fila":50, "columna":60}
        titulos = {"lexema":"Lexema", "categoria":"Categoria",
                   "tokentype":"TokenType",
                   "fila":"Fila", "columna":"Columna"}
        for col in cols:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col],
                              anchor="w" if col not in ("fila","columna")
                              else "center",
                              stretch=(col == "lexema"))

        # Scrollbars de la tabla
        sb_ty = ttk.Scrollbar(tabla_frame, orient="vertical",
                              command=self.tabla.yview)
        sb_tx = ttk.Scrollbar(tabla_frame, orient="horizontal",
                              command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sb_ty.set,
                             xscrollcommand=sb_tx.set)

        sb_ty.pack(side="right",  fill="y")
        sb_tx.pack(side="bottom", fill="x")
        self.tabla.pack(fill="both", expand=True)

        # Tags de color para filas de la tabla
        for cat in CATEGORIAS:
            self.tabla.tag_configure(
                cat,
                foreground=T[cat],
                background=T["surface"])
            self.tabla.tag_configure(
                f"{cat}_alt",
                foreground=T[cat],
                background=T["row_alt"])

    # ── Helper: cabecera de panel ──────────────────────────────

    def _panel_header(self, parent, titulo, pill_color):
        hdr = tk.Frame(parent, bg=T["panel_header"], height=36)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        # Pill de color
        tk.Frame(hdr, bg=pill_color,
                 width=8, height=10).place(x=12, y=13)
        tk.Label(hdr, text=titulo,
                 bg=T["panel_header"], fg=T["text_white"],
                 font=self.f_ui_b).place(x=28, y=9)

    # ── Barra de errores léxicos ──────────────────────────────

    def _build_errores(self):
        self.err_frame = tk.Frame(self.root, bg=T["surface"],
                                  height=30,
                                  highlightbackground=T["border"],
                                  highlightthickness=1)
        self.err_frame.pack(fill="x", side="bottom")
        self.err_frame.pack_propagate(False)

        tk.Label(self.err_frame, text="ERRORES LEXICOS",
                 bg=T["surface"], fg=T["text_dim"],
                 font=self.f_ui_xs).pack(side="left", padx=10)

        self.err_content = tk.Frame(self.err_frame, bg=T["surface"])
        self.err_content.pack(side="left", fill="x", expand=True)

    # ═══════════════════════════════════════════════════════════
    # LÓGICA DE ANÁLISIS
    # ═══════════════════════════════════════════════════════════

    def _cargar_preset(self, idx: int):
        """Carga un programa predefinido en el editor."""
        self.estado.reiniciar()
        _, codigo = PROGRAMAS[idx]

        self.editor.edit_modified(False)
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", codigo)
        self.editor.edit_modified(False)

        # Resaltar botón activo
        for i, btn in enumerate(self.preset_btns):
            btn.configure(
                bg=T["accent_light"] if i == idx else T["surface"],
                fg=T["accent"]       if i == idx else T["text"],
                relief="flat" if i == idx else "flat")

        self._reiniciar_ui()

    def _on_editor_modified(self, event=None):
        if self.editor.edit_modified():
            self.estado.reiniciar()
            self._reiniciar_ui()
            self.editor.edit_modified(False)

    def _get_codigo(self) -> str:
        return self.editor.get("1.0", "end-1c")

    def _analizar_todo(self):
        """Procesa todos los tokens de una vez."""
        self.estado.codigo = self._get_codigo()
        self.estado.analizar_todo()
        self._render_viz_completo()
        self._render_tabla_completa()
        self._render_errores()
        self._actualizar_stats()
        self._actualizar_progreso()

    def _siguiente_paso(self):
        """Avanza un token."""
        if not self.estado.analizado:
            self.estado.codigo = self._get_codigo()
            self.estado.preparar()
            self._render_viz_base()      # dibuja código sin resaltar

        hay_mas = self.estado.siguiente_paso()
        self._render_viz_paso()          # resalta token actual
        self._render_tabla_ultimo()      # añade fila a la tabla
        self._actualizar_stats()
        self._actualizar_progreso()

        if not hay_mas:
            self._render_errores()
            self.btn_paso.configure(state="disabled")

    def _reiniciar(self):
        """Limpia todo el análisis."""
        self.estado.reiniciar()
        self._reiniciar_ui()

    def _reiniciar_ui(self):
        self._limpiar_viz()
        self._limpiar_tabla()
        self._limpiar_errores()
        self.progress["value"] = 0
        self.lbl_progreso.configure(text="")
        self.lbl_stats.configure(text="")
        self.lbl_tok_activo.configure(text="", bg=T["bg"])
        self.btn_paso.configure(state="normal")

    # ═══════════════════════════════════════════════════════════
    # RENDERIZADO DEL VISUALIZADOR
    # ═══════════════════════════════════════════════════════════

    def _limpiar_viz(self):
        self.viz.configure(state="normal")
        self.viz.delete("1.0", "end")
        self.viz.configure(state="disabled")

    def _render_viz_base(self):
        """
        Dibuja el código fuente completo en el visualizador
        con colores por categoría pero sin resaltar ningún token aún.
        """
        self.viz.configure(state="normal")
        self.viz.delete("1.0", "end")

        for seg in self.estado.segmentos:
            tok = seg.token
            if tok is None:
                self.viz.insert("end", seg.texto, "espacio")
            else:
                cat = CategoriaToken(tok)
                self.viz.insert("end", seg.texto, cat)

        self.viz.configure(state="disabled")

    def _render_viz_completo(self):
        """
        Renderiza el código completo con todos los tokens
        coloreados por categoría (modo 'analizar todo').
        """
        self._render_viz_base()
        # En modo completo no hay token activo
        self.lbl_tok_activo.configure(text="Analisis completo",
                                       bg=T["accent_light"],
                                       fg=T["accent"])

    def _render_viz_paso(self):
        """
        Actualiza el visualizador para el paso actual:
        - tokens pasados: atenuados
        - token activo: resaltado con fondo de color + negrita
        - tokens futuros: color normal
        """
        tok_act = self.estado.token_activo
        if not tok_act:
            return

        self.viz.configure(state="normal")

        # Quitar todos los tags de pasos anteriores
        self.viz.tag_remove("linea_activa", "1.0", "end")
        for cat in CATEGORIAS:
            self.viz.tag_remove(f"{cat}_activo", "1.0", "end")
            self.viz.tag_remove(cat, "1.0", "end")
        self.viz.tag_remove("consumido", "1.0", "end")
        self.viz.tag_remove("espacio",   "1.0", "end")

        # Redibujar todos los segmentos con estado correcto
        self.viz.delete("1.0", "end")

        paso_actual = self.estado.paso - 1  # índice del token activo

        for seg in self.estado.segmentos:
            tok = seg.token
            if tok is None:
                self.viz.insert("end", seg.texto, "espacio")
                continue

            cat = CategoriaToken(tok)
            try:
                idx = self.estado.tokens_todos.index(tok)
            except ValueError:
                idx = -1

            if idx < paso_actual:
                # Token ya procesado — atenuar
                tag = "consumido"
            elif idx == paso_actual:
                # Token activo — resaltar
                tag = f"{cat}_activo"
            else:
                # Token futuro — color normal
                tag = cat

            self.viz.insert("end", seg.texto, tag)

        # Resaltar línea completa del token activo
        linea = tok_act.fila
        self.viz.tag_add(
            "linea_activa",
            f"{linea}.0", f"{linea}.end+1c")
        # Llevar el token activo a la vista
        self.viz.see(f"{linea}.{tok_act.columna - 1}")

        self.viz.configure(state="disabled")

        # Actualizar indicador inferior
        cat   = CategoriaToken(tok_act)
        color = T[cat]
        bg    = T[f"{cat}_bg"]
        self.lbl_tok_activo.configure(
            text=(f"  Analizando:  {tok_act.lexema}  |  "
                  f"{tok_act.tipo.name}  |  "
                  f"Fila {tok_act.fila}, Columna {tok_act.columna}  "),
            bg=bg, fg=color)

    # ═══════════════════════════════════════════════════════════
    # RENDERIZADO DE LA TABLA
    # ═══════════════════════════════════════════════════════════

    def _limpiar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def _render_tabla_completa(self):
        """Rellena la tabla con todos los tokens de una vez."""
        self._limpiar_tabla()
        for i, tok in enumerate(self.estado.tabla_rows):
            self._insertar_fila(tok, i)
        # Scroll al final
        hijos = self.tabla.get_children()
        if hijos:
            self.tabla.see(hijos[-1])

    def _render_tabla_ultimo(self):
        """Añade solo la última fila (modo paso a paso)."""
        if not self.estado.tabla_rows:
            return
        tok = self.estado.tabla_rows[-1]
        i   = len(self.estado.tabla_rows) - 1
        iid = self._insertar_fila(tok, i)
        self.tabla.see(iid)

        # Quitar resaltado de selección anterior
        seleccion = self.tabla.selection()
        if seleccion:
            self.tabla.selection_remove(seleccion)
        self.tabla.selection_set(iid)

    def _insertar_fila(self, tok, indice: int) -> str:
        cat = CategoriaToken(tok)
        tag = cat if indice % 2 == 0 else f"{cat}_alt"
        iid = self.tabla.insert(
            "", "end",
            values=(tok.lexema, cat.upper(),
                    tok.tipo.name,
                    tok.fila, tok.columna),
            tags=(tag,))
        # Colorear lexema con negrita — aproximación via tag
        self.tabla.tag_configure(
            tag, foreground=T[cat],
            background=T["surface"] if indice%2==0 else T["row_alt"])
        return iid

    # ═══════════════════════════════════════════════════════════
    # ERRORES LÉXICOS
    # ═══════════════════════════════════════════════════════════

    def _limpiar_errores(self):
        for w in self.err_content.winfo_children():
            w.destroy()
        tk.Label(self.err_content,
                 text="Sin errores lexicos detectados",
                 bg=T["surface"], fg=T["tipo"],
                 font=self.f_ui_s).pack(side="left", padx=6)

    def _render_errores(self):
        for w in self.err_content.winfo_children():
            w.destroy()
        if not self.estado.errores_todos:
            tk.Label(self.err_content,
                     text="Sin errores lexicos detectados",
                     bg=T["surface"], fg=T["tipo"],
                     font=self.f_ui_s).pack(side="left", padx=6)
            return
        for e in self.estado.errores_todos:
            # Formato exacto de BNF.md sección 8
            msg = f"  Fila {e.fila}, columna {e.columna}: {e.mensaje}  "
            tk.Label(self.err_content,
                     text=msg,
                     bg=T["error_bg"], fg=T["error"],
                     font=self.f_ui_s,
                     relief="flat", bd=0,
                     padx=2, pady=1).pack(side="left", padx=4, pady=3)

    # ═══════════════════════════════════════════════════════════
    # STATS Y PROGRESO
    # ═══════════════════════════════════════════════════════════

    def _actualizar_stats(self):
        total = self.estado.total_tokens
        paso  = self.estado.paso
        nerr  = len(self.estado.errores_todos)
        ec    = T["error"] if nerr else "#64D28A"
        self.lbl_stats.configure(
            text=(f"Tokens: {paso} / {total}     "
                  f"Errores lexicos: {nerr}"),
            fg=ec if nerr else T["text_header"])

    def _actualizar_progreso(self):
        pct = int(self.estado.progreso * 100)
        self.progress["value"] = pct
        self.lbl_progreso.configure(text=f"{pct}%")


# Alias de compatibilidad
App = AplicacionLexer


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = AplicacionLexer(root)
    root.mainloop()

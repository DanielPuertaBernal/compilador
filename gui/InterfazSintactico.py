"""
gui_parser_tk.py — Interfaz gráfica de análisis sintáctico
Compiladores — Entrega 2 / 3 | Descendente recursivo y predictivo LL(1)
"""

import tkinter as tk
from tkinter import ttk, font as tkfont

from gui.Programas import PROGRAMAS
from sintactico.TablaLL1 import RenderizarFirstFollow, RenderizarTablaLL1
from sintactico.ControladorParser import SolicitudAnalisis, EjecutarAnalisis
from sintactico.EstadoParser import CONJUNTOS_FIRST, CONJUNTOS_FOLLOW, TABLA_LL1
from sintactico.ArbolSintactico import NodoArbol
from gui.Estilos import TEMA as T


class AplicacionSintactico:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.method_var = tk.StringVar(value="recursivo")
        self.recover_var = tk.BooleanVar(value=False)

        root.title("Analizador Sintáctico — Entregas 2 & 3")
        root.geometry("1440x900")
        root.minsize(1160, 720)
        root.configure(bg=T["bg"])

        try:
            self.f_code = tkfont.Font(family="Consolas", size=12)
            self.f_ui = tkfont.Font(family="Segoe UI", size=10)
            self.f_ui_b = tkfont.Font(family="Segoe UI", size=10, weight="bold")
            self.f_title = tkfont.Font(family="Segoe UI", size=13, weight="bold")
            self.f_err = tkfont.Font(family="Consolas", size=11)
        except Exception:
            self.f_code = tkfont.Font(family="Courier New", size=12)
            self.f_ui = tkfont.Font(size=10)
            self.f_ui_b = tkfont.Font(size=10, weight="bold")
            self.f_title = tkfont.Font(size=13, weight="bold")
            self.f_err = tkfont.Font(family="Courier New", size=11)

        self._build_ui()
        self._load_preset(0)
        self._render_static_docs()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()
        body = tk.PanedWindow(self.root, orient="horizontal", bg=T["bg"], sashwidth=6, bd=0)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        left = tk.Frame(body, bg=T["bg"])
        right = tk.Frame(body, bg=T["bg"])
        body.add(left, minsize=420, stretch="always")
        body.add(right, minsize=560, stretch="always")
        self._build_editor_panel(left)
        self._build_result_panel(right)

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=T["header_bg"], height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Analizador Sintáctico",
            bg=T["header_bg"], fg=T["text_white"], font=self.f_title,
        ).pack(side="left", padx=16, pady=14)
        tk.Label(
            header,
            text="Compiladores · Entregas 2 & 3 · Recursivo + Predictivo LL(1) + Recuperación de Errores",
            bg=T["header_bg"], fg=T["text_header"], font=self.f_ui,
        ).pack(side="left", pady=14)

    def _panel_header(self, parent, title: str) -> None:
        hdr = tk.Frame(parent, bg=T["panel_header"], height=34)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text=title, bg=T["panel_header"], fg=T["text_white"], font=self.f_ui_b,
        ).pack(side="left", padx=12, pady=7)

    def _build_editor_panel(self, parent) -> None:
        self._panel_header(parent, "Entrada del programa")

        presets_frame = tk.Frame(parent, bg=T["bg"])
        presets_frame.pack(fill="x", padx=8, pady=(6, 4))
        self.preset_buttons = []
        for index, (name, _, _valid) in enumerate(PROGRAMAS):
            btn = tk.Button(
                presets_frame, text=name, bg=T["surface"], fg=T["text"],
                font=self.f_ui, relief="flat", bd=1, padx=6, pady=3,
                command=lambda i=index: self._load_preset(i),
            )
            btn.pack(side="left", padx=2, pady=2)
            self.preset_buttons.append(btn)

        controls = tk.Frame(parent, bg=T["bg"])
        controls.pack(fill="x", padx=8, pady=(0, 6))

        tk.Label(controls, text="Método:", bg=T["bg"], fg=T["text_dim"], font=self.f_ui_b).pack(side="left")
        ttk.Radiobutton(controls, text="Recursivo", value="recursivo", variable=self.method_var).pack(side="left", padx=(6, 6))
        ttk.Radiobutton(controls, text="Predictivo LL(1)", value="predictivo", variable=self.method_var).pack(side="left", padx=(0, 12))

        ttk.Checkbutton(
            controls, text="Recuperar errores (E3)",
            variable=self.recover_var,
        ).pack(side="left", padx=(0, 12))

        tk.Button(
            controls, text="Analizar",
            bg=T["accent"], fg=T["text_white"], font=self.f_ui_b,
            relief="flat", padx=12, pady=5, command=self._analyze,
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            controls, text="Limpiar",
            bg=T["surface"], fg=T["text"], font=self.f_ui,
            relief="flat", padx=10, pady=5, command=self._clear_runtime_views,
        ).pack(side="right")

        editor_box = tk.Frame(parent, bg=T["border"], highlightthickness=1, highlightbackground=T["border"])
        editor_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.editor = tk.Text(
            editor_box, font=self.f_code, bg=T["surface2"], fg=T["text"],
            relief="flat", bd=0, wrap="none", padx=8, pady=8, undo=True,
        )
        self.editor.pack(side="left", fill="both", expand=True)

        sb_y = ttk.Scrollbar(editor_box, orient="vertical", command=self.editor.yview)
        sb_x = ttk.Scrollbar(parent, orient="horizontal", command=self.editor.xview)
        self.editor.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side="right", fill="y")
        sb_x.pack(fill="x", padx=8)

    def _build_result_panel(self, parent) -> None:
        self._panel_header(parent, "Resultados del análisis")

        status_frame = tk.Frame(parent, bg=T["surface"], highlightbackground=T["border"], highlightthickness=1)
        status_frame.pack(fill="x", padx=8, pady=(6, 6))
        self.lbl_status = tk.Label(
            status_frame, text="Listo para analizar.",
            bg=T["surface"], fg=T["text"], font=self.f_ui_b,
            padx=10, pady=8, anchor="w",
        )
        self.lbl_status.pack(fill="x")

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.tab_summary = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_errors = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_tree = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_trace = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_ll = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_first_follow = tk.Frame(self.notebook, bg=T["surface"])

        self.notebook.add(self.tab_summary, text="Resumen")
        self.notebook.add(self.tab_errors, text="Errores (E3)")
        self.notebook.add(self.tab_tree, text="Árbol")
        self.notebook.add(self.tab_trace, text="Traza LL(1)")
        self.notebook.add(self.tab_ll, text="Tabla LL(1)")
        self.notebook.add(self.tab_first_follow, text="FIRST/FOLLOW")

        # Resumen
        self.summary = tk.Text(
            self.tab_summary, font=self.f_code, wrap="word",
            relief="flat", bg=T["surface"], fg=T["text"],
        )
        self.summary.pack(fill="both", expand=True, padx=8, pady=8)

        # Errores E3
        self._build_errors_tab()

        # Árbol
        legend = tk.Frame(self.tab_tree, bg=T["surface"])
        legend.pack(fill="x", padx=8, pady=(8, 0))
        tk.Label(legend, text="■ No terminal", bg=T["surface"], fg=T["tree_nt"], font=self.f_ui_b).pack(side="left", padx=(0, 12))
        tk.Label(legend, text="■ Terminal", bg=T["surface"], fg=T["tree_term"], font=self.f_ui_b).pack(side="left", padx=(0, 12))
        tk.Label(legend, text="■ Épsilon", bg=T["surface"], fg=T["tree_eps"], font=self.f_ui_b).pack(side="left")
        tree_frame = tk.Frame(self.tab_tree, bg=T["surface"])
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, show="tree")
        self.tree.tag_configure("nonterminal", foreground=T["tree_nt"])
        self.tree.tag_configure("terminal", foreground=T["tree_term"])
        self.tree.tag_configure("epsilon", foreground=T["tree_eps"])
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        tree_scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

        # Traza
        trace_frame = tk.Frame(self.tab_trace, bg=T["surface"])
        trace_frame.pack(fill="both", expand=True)
        columns = ("paso", "pila", "lookahead", "accion", "celda")
        self.trace = ttk.Treeview(trace_frame, columns=columns, show="headings")
        for col, width in {"paso": 60, "pila": 260, "lookahead": 160, "accion": 340, "celda": 180}.items():
            self.trace.heading(col, text=col.title())
            self.trace.column(col, width=width, anchor="w")
        trace_scroll = ttk.Scrollbar(trace_frame, orient="vertical", command=self.trace.yview)
        self.trace.configure(yscrollcommand=trace_scroll.set)
        self.trace.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        trace_scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

        # Tabla LL(1)
        self.ll_text = tk.Text(
            self.tab_ll, font=("Consolas", 9), wrap="none",
            relief="flat", bg=T["surface"], fg=T["text"],
        )
        self.ll_text.pack(fill="both", expand=True, padx=8, pady=8)

        # FIRST/FOLLOW
        self.first_follow_text = tk.Text(
            self.tab_first_follow, font=("Consolas", 10), wrap="none",
            relief="flat", bg=T["surface"], fg=T["text"],
        )
        self.first_follow_text.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_errors_tab(self) -> None:
        """Panel de errores Entrega 3 con tabla + detalle."""
        top = tk.Frame(self.tab_errors, bg=T["surface"])
        top.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        cols = ("#", "Línea", "Col", "Lexema", "Tipo", "Esperado")
        self.err_tree = ttk.Treeview(top, columns=cols, show="headings", height=8)
        widths = {"#": 40, "Línea": 70, "Col": 60, "Lexema": 120, "Tipo": 160, "Esperado": 300}
        for col in cols:
            self.err_tree.heading(col, text=col)
            self.err_tree.column(col, width=widths.get(col, 100), anchor="w")
        self.err_tree.tag_configure("error_row", background=T["error_bg"], foreground=T["error"])

        err_scroll = ttk.Scrollbar(top, orient="vertical", command=self.err_tree.yview)
        self.err_tree.configure(yscrollcommand=err_scroll.set)
        self.err_tree.pack(side="left", fill="both", expand=True)
        err_scroll.pack(side="right", fill="y")

        self.err_tree.bind("<<TreeviewSelect>>", self._on_error_select)

        detail_frame = tk.Frame(self.tab_errors, bg=T["surface"])
        detail_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        tk.Label(
            detail_frame, text="Detalle del error seleccionado:",
            bg=T["surface"], fg=T["text_dim"], font=self.f_ui_b,
        ).pack(anchor="w")

        self.err_detail = tk.Text(
            detail_frame, font=self.f_err, wrap="word", height=8,
            relief="flat", bg="#FFF7F7", fg=T["text"],
        )
        self.err_detail.pack(fill="both", expand=True)
        self._err_objects = []  # stores SyntaxErrorInfo list

    # ── Lógica de análisis ────────────────────────────────────────────────────

    def _analyze(self) -> None:
        code = self.editor.get("1.0", "end-1c")
        self._clear_runtime_views(keep_message=True)

        recover = self.recover_var.get()
        errors, result = EjecutarAnalisis(SolicitudAnalisis(code, self.method_var.get(), recuperar=recover))

        if errors:
            lines = ["Errores léxicos detectados. Análisis sintáctico no ejecutado.", ""]
            for e in errors:
                lines.append(f"  Fila {e.fila}, col {e.columna}: {e.mensaje}")
            self._set_status("Errores léxicos.", ok=False)
            self._set_text_widget(self.summary, "\n".join(lines))
            return

        self._set_status(result.mensaje, ok=result.valido)

        # Pestaña Resumen
        summary_lines = [
            f"Método       : {result.metodo}",
            f"Recuperación : {'activada' if recover else 'desactivada'}",
            f"Estado       : {'VÁLIDO ✓' if result.valido else f'INVÁLIDO — {len(result.errors)} error(es)'}",
            "",
        ]
        if result.valido:
            summary_lines.append("Cadena aceptada sin errores.")
        else:
            summary_lines.append(result.format_error_report())
        if result.arbol is not None:
            summary_lines.extend(["", "Árbol (ASCII):", result.arbol.to_ascii()])
        self._set_text_widget(self.summary, "\n".join(summary_lines))

        # Pestaña Errores E3
        self._populate_errors_tab(result.errors)

        # Árbol
        if result.arbol is not None:
            self._render_tree(result.arbol)

        # Traza
        if result.trace:
            for step in result.trace:
                self.trace.insert(
                    "", "end",
                    values=(step.paso, step.pila, step.lookahead, step.accion, step.celda),
                )
        else:
            self.trace.insert("", "end", values=("—", "—", "—", "No usa pila explícita.", "—"))

        # Ir a pestaña errores si los hay
        if result.errors:
            self.notebook.select(self.tab_errors)

    def _populate_errors_tab(self, errors) -> None:
        for item in self.err_tree.get_children():
            self.err_tree.delete(item)
        self._set_text_widget(self.err_detail, "")
        self._err_objects = list(errors)

        if not errors:
            self.err_tree.insert(
                "", "end",
                values=("—", "—", "—", "—", "—", "Sin errores"),
            )
            return

        for err in errors:
            esperado_txt = ", ".join(err.esperado[:6])
            if len(err.esperado) > 6:
                esperado_txt += f" (+{len(err.esperado) - 6})"
            self.err_tree.insert(
                "", "end",
                values=(
                    err.numero,
                    err.fila,
                    err.columna,
                    err.recibido_lexema,
                    err.recibido_tipo,
                    esperado_txt,
                ),
                tags=("error_row",),
            )

    def _on_error_select(self, _event) -> None:
        sel = self.err_tree.selection()
        if not sel:
            return
        idx = self.err_tree.index(sel[0])
        if idx < len(self._err_objects):
            err = self._err_objects[idx]
            err.numero = idx + 1
            self._set_text_widget(self.err_detail, err.format_report())

    # ── Utilidades de la UI ───────────────────────────────────────────────────

    def _render_static_docs(self) -> None:
        self._set_text_widget(self.ll_text, RenderizarTablaLL1(TABLA_LL1))
        self._set_text_widget(self.first_follow_text, RenderizarFirstFollow(CONJUNTOS_FIRST, CONJUNTOS_FOLLOW))
        self._set_text_widget(
            self.summary,
            "Selecciona un ejemplo o escribe tu código, elige el método y pulsa Analizar.\n\n"
            "Activa 'Recuperar errores (E3)' para continuar el análisis tras cada error.",
        )

    def _load_preset(self, index: int) -> None:
        _, code, _ = PROGRAMAS[index]
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", code)
        for i, button in enumerate(self.preset_buttons):
            button.configure(
                bg=T["accent_light"] if i == index else T["surface"],
                fg=T["accent"] if i == index else T["text"],
            )
        self._clear_runtime_views(keep_message=True)

    def _clear_runtime_views(self, keep_message: bool = False) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.trace.get_children():
            self.trace.delete(item)
        for item in self.err_tree.get_children():
            self.err_tree.delete(item)
        self._set_text_widget(self.err_detail, "")
        self._err_objects = []
        if not keep_message:
            self._set_status("Listo para analizar.", ok=None)
            self._set_text_widget(self.summary, "")

    def _node_text_and_tag(self, node: NodoArbol):
        if node.symbol == "ε":
            return f"ε  {node.label}", "epsilon"
        if node.is_terminal:
            return f"•  {node.label}", "terminal"
        return f"▸  {node.label}", "nonterminal"

    def _expand_all(self, item: str) -> None:
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_all(child)

    def _render_tree(self, node: NodoArbol) -> None:
        self.tree.delete(*self.tree.get_children())

        def add_node(parent: str, current: NodoArbol) -> None:
            text, tag = self._node_text_and_tag(current)
            item = self.tree.insert(parent, "end", text=text, tags=(tag,))
            for child in current.children:
                add_node(item, child)

        add_node("", node)
        root_items = self.tree.get_children()
        if root_items:
            self._expand_all(root_items[0])

    def _set_status(self, text: str, ok=None) -> None:
        bg = T["surface"]
        fg = T["text"]
        if ok is True:
            bg = T["ok_bg"]
            fg = T["ok"]
        elif ok is False:
            bg = T["error_bg"]
            fg = T["error"]
        self.lbl_status.configure(text=text, bg=bg, fg=fg)

    def _set_text_widget(self, widget: tk.Text, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")


# Alias de compatibilidad
SyntaxApp = AplicacionSintactico


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionSintactico(root)
    root.mainloop()

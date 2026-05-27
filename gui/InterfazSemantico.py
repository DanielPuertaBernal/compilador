"""
InterfazSemantico.py — Interfaz gráfica del analizador semántico
Compiladores — Entrega 4 | Análisis semántico + Tabla de símbolos
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import List, Optional

from gui.Estilos import TEMA as T
from semantico.ControladorSemantico import SolicitudSemantica, EjecutarAnalisisSemantico
from semantico.ErrorSemantico import ErrorSemantico
from sintactico.ArbolSintactico import NodoArbol

# ── Color de acento E4 (ámbar — coincide con el color del PDF para reglas semánticas)
_ACENTO_E4 = "#D97706"
_ACENTO_E4_BG = "#FEF3C7"
_ACENTO_E4_FG = "#92400E"

# ── Programas de demostración ─────────────────────────────────────────────────
# Formato: (nombre, código_fuente, es_válido_semánticamente)

PROGRAMAS_SEM: list[tuple[str, str, bool]] = [
    (
        "Sin errores",
        """// Programa válido — factorial recursivo
funcion factorial(n: entero): entero
  si n == 0 entonces
    retornar 1
  sino
    retornar n * factorial(n - 1)
  fin_si
fin_funcion

var resultado: entero = factorial(5)""",
        True,
    ),
    (
        "Doble declaración",
        """// Regla 1 — doble declaracion de variable en el mismo ambito
var contador: entero = 0
var activo: booleano = verdadero
var contador: real = 1.5""",
        False,
    ),
    (
        "Var no declarada",
        """// Regla 2 — uso de variable no declarada
var resultado: entero = valorDesconocido + 5""",
        False,
    ),
    (
        "Tipo incompatible",
        """// Regla 3 — tipo incompatible en declaracion con inicializacion
var edad: entero = "no es un numero"
var nombre: cadena = 42""",
        False,
    ),
    (
        "Retorno incompat.",
        """// Regla 4 — tipo de retorno incompatible con el declarado
funcion obtenerNombre(): entero
  retornar "Juanito"
fin_funcion""",
        False,
    ),
    (
        "Func no declarada",
        """// Regla 5 — llamada a funcion no declarada
var r: entero = calcularTotal(10, 5)
calcularOtra(r)""",
        False,
    ),
    (
        "Errores mixtos",
        """// Varios errores semanticos en un mismo programa
var x: entero = "tipo_equivocado"
var y: cadena = variableInexistente

funcion procesarDato(): cadena
  retornar 99
fin_funcion

var z: booleano = funcionNoExiste()""",
        False,
    ),
]


# ── Interfaz principal ────────────────────────────────────────────────────────

class AplicacionSemantico:
    """Interfaz gráfica para el analizador semántico — Entrega 4."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.method_var = tk.StringVar(value="recursivo")
        self._err_objects: List[ErrorSemantico] = []

        root.title("Analizador Semántico — Entrega 4")
        root.geometry("1440x900")
        root.minsize(1160, 720)
        root.configure(bg=T["bg"])

        try:
            self.f_code  = tkfont.Font(family="Consolas",  size=12)
            self.f_ui    = tkfont.Font(family="Segoe UI",  size=10)
            self.f_ui_b  = tkfont.Font(family="Segoe UI",  size=10, weight="bold")
            self.f_title = tkfont.Font(family="Segoe UI",  size=13, weight="bold")
            self.f_err   = tkfont.Font(family="Consolas",  size=11)
            self.f_mono  = tkfont.Font(family="Consolas",  size=10)
        except Exception:
            self.f_code  = tkfont.Font(family="Courier New", size=12)
            self.f_ui    = tkfont.Font(size=10)
            self.f_ui_b  = tkfont.Font(size=10, weight="bold")
            self.f_title = tkfont.Font(size=13, weight="bold")
            self.f_err   = tkfont.Font(family="Courier New", size=11)
            self.f_mono  = tkfont.Font(family="Courier New", size=10)

        self._build_ui()
        self._load_preset(0)

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()
        body = tk.PanedWindow(
            self.root, orient="horizontal",
            bg=T["bg"], sashwidth=6, bd=0,
        )
        body.pack(fill="both", expand=True, padx=10, pady=10)
        left  = tk.Frame(body, bg=T["bg"])
        right = tk.Frame(body, bg=T["bg"])
        body.add(left,  minsize=420, stretch="always")
        body.add(right, minsize=560, stretch="always")
        self._build_editor_panel(left)
        self._build_result_panel(right)

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=T["header_bg"], height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Analizador Semántico",
            bg=T["header_bg"], fg=T["text_white"], font=self.f_title,
        ).pack(side="left", padx=16, pady=14)

        tk.Label(
            header,
            text="Compiladores · Entrega 4 · Tabla de símbolos + 5 reglas semánticas",
            bg=T["header_bg"], fg=T["text_header"], font=self.f_ui,
        ).pack(side="left", pady=14)

    def _panel_header(self, parent: tk.Widget, title: str) -> None:
        hdr = tk.Frame(parent, bg=T["panel_header"], height=34)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text=title,
            bg=T["panel_header"], fg=T["text_white"], font=self.f_ui_b,
        ).pack(side="left", padx=12, pady=7)

    # ── Panel izquierdo: editor ───────────────────────────────────────────────

    def _build_editor_panel(self, parent: tk.Frame) -> None:
        self._panel_header(parent, "Entrada del programa")

        # Botones de preset
        presets_frame = tk.Frame(parent, bg=T["bg"])
        presets_frame.pack(fill="x", padx=8, pady=(6, 4))
        self._preset_buttons: list[tk.Button] = []
        for i, (name, _, _valid) in enumerate(PROGRAMAS_SEM):
            btn = tk.Button(
                presets_frame, text=name,
                bg=T["surface"], fg=T["text"],
                font=self.f_ui, relief="flat", bd=1,
                padx=6, pady=3,
                command=lambda idx=i: self._load_preset(idx),
            )
            btn.pack(side="left", padx=2, pady=2)
            self._preset_buttons.append(btn)

        # Controles: método + botones
        controls = tk.Frame(parent, bg=T["bg"])
        controls.pack(fill="x", padx=8, pady=(0, 6))

        tk.Label(
            controls, text="Método:",
            bg=T["bg"], fg=T["text_dim"], font=self.f_ui_b,
        ).pack(side="left")
        ttk.Radiobutton(
            controls, text="Recursivo",
            value="recursivo", variable=self.method_var,
        ).pack(side="left", padx=(6, 6))
        ttk.Radiobutton(
            controls, text="Predictivo LL(1)",
            value="predictivo", variable=self.method_var,
        ).pack(side="left", padx=(0, 12))

        tk.Button(
            controls, text="Analizar",
            bg=_ACENTO_E4, fg=T["text_white"], font=self.f_ui_b,
            relief="flat", padx=12, pady=5,
            command=self._analizar,
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            controls, text="Limpiar",
            bg=T["surface"], fg=T["text"], font=self.f_ui,
            relief="flat", padx=10, pady=5,
            command=self._limpiar,
        ).pack(side="right")

        # Editor de código
        editor_box = tk.Frame(
            parent, bg=T["border"],
            highlightthickness=1, highlightbackground=T["border"],
        )
        editor_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.editor = tk.Text(
            editor_box, font=self.f_code,
            bg=T["surface2"], fg=T["text"],
            relief="flat", bd=0, wrap="none",
            padx=8, pady=8, undo=True,
        )
        self.editor.pack(side="left", fill="both", expand=True)

        sb_y = ttk.Scrollbar(editor_box, orient="vertical",   command=self.editor.yview)
        sb_x = ttk.Scrollbar(parent,     orient="horizontal", command=self.editor.xview)
        self.editor.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side="right", fill="y")
        sb_x.pack(fill="x", padx=8)

    # ── Panel derecho: resultados ─────────────────────────────────────────────

    def _build_result_panel(self, parent: tk.Frame) -> None:
        self._panel_header(parent, "Resultados del análisis semántico")

        # Barra de estado
        status_frame = tk.Frame(
            parent, bg=T["surface"],
            highlightbackground=T["border"], highlightthickness=1,
        )
        status_frame.pack(fill="x", padx=8, pady=(6, 6))
        self.lbl_status = tk.Label(
            status_frame, text="Listo para analizar.",
            bg=T["surface"], fg=T["text"], font=self.f_ui_b,
            padx=10, pady=8, anchor="w",
        )
        self.lbl_status.pack(fill="x")

        # Notebook con pestañas
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.tab_resumen  = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_simbolos = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_errores  = tk.Frame(self.notebook, bg=T["surface"])
        self.tab_arbol    = tk.Frame(self.notebook, bg=T["surface"])

        self.notebook.add(self.tab_resumen,  text="Resumen")
        self.notebook.add(self.tab_simbolos, text="Tabla de Símbolos")
        self.notebook.add(self.tab_errores,  text="Errores Semánticos")
        self.notebook.add(self.tab_arbol,    text="Árbol")

        self._build_tab_resumen()
        self._build_tab_simbolos()
        self._build_tab_errores()
        self._build_tab_arbol()

    # ── Pestaña Resumen ───────────────────────────────────────────────────────

    def _build_tab_resumen(self) -> None:
        self.txt_resumen = tk.Text(
            self.tab_resumen, font=self.f_code, wrap="word",
            relief="flat", bg=T["surface"], fg=T["text"],
        )
        self.txt_resumen.pack(fill="both", expand=True, padx=8, pady=8)
        self._set_widget(
            self.txt_resumen,
            "Selecciona un ejemplo o escribe tu código y pulsa Analizar.\n\n"
            "Pestañas disponibles:\n"
            "  • Tabla de Símbolos — todos los identificadores declarados con su tipo y ámbito\n"
            "  • Errores Semánticos — violaciones de las 5 reglas semánticas\n"
            "  • Árbol — árbol sintáctico producido por el parser\n\n"
            "Reglas semánticas implementadas:\n"
            "  REGLA 1 — No redeclaración de identificadores en el mismo ámbito\n"
            "  REGLA 2 — Uso de variable previamente declarada\n"
            "  REGLA 3 — Compatibilidad de tipos en declaración con inicialización\n"
            "  REGLA 4 — Tipo de retorno compatible con la función contenedora\n"
            "  REGLA 5 — Función o clase invocada debe estar declarada",
        )

    # ── Pestaña Tabla de Símbolos ─────────────────────────────────────────────

    def _build_tab_simbolos(self) -> None:
        # Leyenda de colores por categoría
        leyenda = tk.Frame(self.tab_simbolos, bg=T["surface"])
        leyenda.pack(fill="x", padx=8, pady=(8, 0))
        for cat, color in [
            ("variable",   T["tree_term"]),
            ("funcion",    T["tree_nt"]),
            ("clase",      T["accent3"]),
            ("parametro",  T["text_dim"]),
            ("atributo",   _ACENTO_E4_FG),
        ]:
            tk.Label(
                leyenda, text=f"■ {cat}",
                bg=T["surface"], fg=color, font=self.f_ui_b,
            ).pack(side="left", padx=(0, 12))

        # Treeview para la tabla
        sym_frame = tk.Frame(self.tab_simbolos, bg=T["surface"])
        sym_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        cols = ("Ámbito", "Categoría", "Nombre", "Tipo", "L:C", "Init", "Retorna / Params")
        self.sym_tree = ttk.Treeview(sym_frame, columns=cols, show="headings")
        widths = {
            "Ámbito":            120,
            "Categoría":         100,
            "Nombre":            140,
            "Tipo":               90,
            "L:C":                70,
            "Init":               50,
            "Retorna / Params":  260,
        }
        for col in cols:
            self.sym_tree.heading(col, text=col)
            self.sym_tree.column(col, width=widths.get(col, 100), anchor="w")

        # Tags de color por categoría
        self.sym_tree.tag_configure("variable",  foreground=T["tree_term"])
        self.sym_tree.tag_configure("funcion",   foreground=T["tree_nt"])
        self.sym_tree.tag_configure("clase",     foreground=T["accent3"])
        self.sym_tree.tag_configure("parametro", foreground=T["text_dim"])
        self.sym_tree.tag_configure("atributo",  foreground=_ACENTO_E4_FG)

        sym_scroll = ttk.Scrollbar(sym_frame, orient="vertical", command=self.sym_tree.yview)
        self.sym_tree.configure(yscrollcommand=sym_scroll.set)
        self.sym_tree.pack(side="left", fill="both", expand=True)
        sym_scroll.pack(side="right", fill="y")

    # ── Pestaña Errores Semánticos ────────────────────────────────────────────

    def _build_tab_errores(self) -> None:
        # Tabla superior
        top = tk.Frame(self.tab_errores, bg=T["surface"])
        top.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        cols = ("#", "Línea", "Col", "Lexema", "Regla", "Descripción")
        self.err_tree = ttk.Treeview(top, columns=cols, show="headings", height=8)
        widths = {
            "#":          40,
            "Línea":      70,
            "Col":        60,
            "Lexema":    130,
            "Regla":     160,
            "Descripción": 380,
        }
        for col in cols:
            self.err_tree.heading(col, text=col)
            self.err_tree.column(col, width=widths.get(col, 100), anchor="w")
        self.err_tree.tag_configure("err_row", background=T["error_bg"], foreground=T["error"])

        err_scroll = ttk.Scrollbar(top, orient="vertical", command=self.err_tree.yview)
        self.err_tree.configure(yscrollcommand=err_scroll.set)
        self.err_tree.pack(side="left", fill="both", expand=True)
        err_scroll.pack(side="right", fill="y")
        self.err_tree.bind("<<TreeviewSelect>>", self._on_error_select)

        # Detalle del error seleccionado
        detail = tk.Frame(self.tab_errores, bg=T["surface"])
        detail.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        tk.Label(
            detail, text="Detalle del error seleccionado:",
            bg=T["surface"], fg=T["text_dim"], font=self.f_ui_b,
        ).pack(anchor="w")
        self.err_detail = tk.Text(
            detail, font=self.f_err, wrap="word", height=8,
            relief="flat", bg="#FFF7F7", fg=T["text"],
        )
        self.err_detail.pack(fill="both", expand=True)

    # ── Pestaña Árbol ─────────────────────────────────────────────────────────

    def _build_tab_arbol(self) -> None:
        leyenda = tk.Frame(self.tab_arbol, bg=T["surface"])
        leyenda.pack(fill="x", padx=8, pady=(8, 0))
        tk.Label(leyenda, text="■ No terminal", bg=T["surface"], fg=T["tree_nt"],   font=self.f_ui_b).pack(side="left", padx=(0, 12))
        tk.Label(leyenda, text="■ Terminal",    bg=T["surface"], fg=T["tree_term"], font=self.f_ui_b).pack(side="left", padx=(0, 12))
        tk.Label(leyenda, text="■ Épsilon",     bg=T["surface"], fg=T["tree_eps"],  font=self.f_ui_b).pack(side="left")

        tree_frame = tk.Frame(self.tab_arbol, bg=T["surface"])
        tree_frame.pack(fill="both", expand=True)
        self.tree_widget = ttk.Treeview(tree_frame, show="tree")
        self.tree_widget.tag_configure("nonterminal", foreground=T["tree_nt"])
        self.tree_widget.tag_configure("terminal",    foreground=T["tree_term"])
        self.tree_widget.tag_configure("epsilon",     foreground=T["tree_eps"])

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_widget.yview)
        self.tree_widget.configure(yscrollcommand=tree_scroll.set)
        self.tree_widget.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        tree_scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

    # ── Lógica de análisis ────────────────────────────────────────────────────

    def _analizar(self) -> None:
        codigo = self.editor.get("1.0", "end-1c")
        self._limpiar(keep_status=True)

        errores_lex, resultado_sint, resultado_sem = EjecutarAnalisisSemantico(
            SolicitudSemantica(codigo=codigo, metodo=self.method_var.get())
        )

        # Errores léxicos — no continuar
        if errores_lex:
            self._set_status("Errores léxicos detectados. Análisis semántico no ejecutado.", ok=False)
            lineas = ["Errores léxicos (análisis semántico no ejecutado):", ""]
            for e in errores_lex:
                lineas.append(f"  Fila {e.fila}, col {e.columna}: {e.mensaje}")
            self._set_widget(self.txt_resumen, "\n".join(lineas))
            return

        # Estado global
        sint_ok = resultado_sint.valido if resultado_sint else False
        sem_ok  = resultado_sem.valido  if resultado_sem  else False

        if sem_ok:
            self._set_status(
                "Análisis semántico: programa válido ✓" +
                ("" if sint_ok else "  (con advertencias sintácticas)"),
                ok=True,
            )
        else:
            n = len(resultado_sem.errores) if resultado_sem else 0
            self._set_status(
                f"Análisis semántico: {n} error(es) semántico(s) detectado(s).",
                ok=False,
            )

        # ── Pestaña Resumen ──────────────────────────────────────────────
        resumen_lineas = [
            f"Fase sintáctica : {'VÁLIDO ✓' if sint_ok else f'con errores ({len(resultado_sint.errores)})'}",
            f"Fase semántica  : {'VÁLIDO ✓' if sem_ok  else f'con errores ({len(resultado_sem.errores) if resultado_sem else 0})'}",
            f"Método parser   : {self.method_var.get()}",
            "",
        ]
        if resultado_sem:
            if resultado_sem.valido:
                resumen_lineas.append("El programa es semánticamente correcto.")
            else:
                resumen_lineas.append(resultado_sem.FormatearReporteErrores())

        if resultado_sint and resultado_sint.errores:
            resumen_lineas += [
                "",
                "── Errores sintácticos detectados ──",
                resultado_sint.FormatearReporteErrores(),
            ]
        self._set_widget(self.txt_resumen, "\n".join(resumen_lineas))

        # ── Pestaña Tabla de Símbolos ────────────────────────────────────
        if resultado_sem and resultado_sem.tabla:
            self._poblar_tabla_simbolos(resultado_sem.tabla)

        # ── Pestaña Errores Semánticos ───────────────────────────────────
        if resultado_sem:
            self._poblar_errores(resultado_sem.errores)

        # ── Pestaña Árbol ────────────────────────────────────────────────
        if resultado_sint and resultado_sint.arbol:
            self._renderizar_arbol(resultado_sint.arbol)

        # Navegar a la pestaña más relevante
        if resultado_sem and resultado_sem.errores:
            self.notebook.select(self.tab_errores)
        elif resultado_sem and resultado_sem.tabla:
            self.notebook.select(self.tab_simbolos)

    # ── Pobladores de pestañas ────────────────────────────────────────────────

    def _poblar_tabla_simbolos(self, tabla) -> None:
        for item in self.sym_tree.get_children():
            self.sym_tree.delete(item)

        entradas = tabla.todas_las_entradas()
        if not entradas:
            self.sym_tree.insert("", "end", values=("—", "—", "(vacía)", "—", "—", "—", "—"))
            return

        for ambito_nombre, entrada in entradas:
            extra = ""
            if entrada.categoria == "funcion":
                p_txt = ", ".join(f"{n}: {t}" for n, t in entrada.parametros) or "—"
                ret   = entrada.tipo_retorno or "void"
                extra = f"retorna: {ret}  |  params: {p_txt}"

            self.sym_tree.insert(
                "", "end",
                values=(
                    ambito_nombre,
                    entrada.categoria,
                    entrada.nombre,
                    entrada.tipo,
                    f"L{entrada.fila}:C{entrada.columna}",
                    "sí" if entrada.inicializado else "no",
                    extra,
                ),
                tags=(entrada.categoria,),
            )

    def _poblar_errores(self, errores: List[ErrorSemantico]) -> None:
        for item in self.err_tree.get_children():
            self.err_tree.delete(item)
        self._set_widget(self.err_detail, "")
        self._err_objects = list(errores)

        if not errores:
            self.err_tree.insert(
                "", "end",
                values=("—", "—", "—", "—", "—", "Sin errores semánticos"),
            )
            return

        for err in errores:
            # Truncar descripción para la tabla (el detalle completo está abajo)
            desc_corta = err.mensaje[:60] + "…" if len(err.mensaje) > 60 else err.mensaje
            self.err_tree.insert(
                "", "end",
                values=(
                    err.numero,
                    err.fila,
                    err.columna,
                    err.lexema,
                    err.tipo_error,
                    desc_corta,
                ),
                tags=("err_row",),
            )

    def _on_error_select(self, _event) -> None:
        sel = self.err_tree.selection()
        if not sel:
            return
        idx = self.err_tree.index(sel[0])
        if idx < len(self._err_objects):
            err = self._err_objects[idx]
            self._set_widget(self.err_detail, err.FormatearReporte())

    # ── Árbol sintáctico ──────────────────────────────────────────────────────

    def _nodo_texto_y_tag(self, nodo: NodoArbol):
        if nodo.symbol == "ε":
            return f"ε  {nodo.label}", "epsilon"
        if nodo.is_terminal:
            return f"•  {nodo.label}", "terminal"
        return f"▸  {nodo.label}", "nonterminal"

    def _expandir_todo(self, item: str) -> None:
        self.tree_widget.item(item, open=True)
        for hijo in self.tree_widget.get_children(item):
            self._expandir_todo(hijo)

    def _renderizar_arbol(self, nodo: NodoArbol) -> None:
        self.tree_widget.delete(*self.tree_widget.get_children())

        def agregar(parent_id: str, actual: NodoArbol) -> None:
            texto, tag = self._nodo_texto_y_tag(actual)
            item = self.tree_widget.insert(parent_id, "end", text=texto, tags=(tag,))
            for hijo in actual.children:
                agregar(item, hijo)

        agregar("", nodo)
        raices = self.tree_widget.get_children()
        if raices:
            self._expandir_todo(raices[0])

    # ── Utilidades de UI ──────────────────────────────────────────────────────

    def _load_preset(self, index: int) -> None:
        _, codigo, _ = PROGRAMAS_SEM[index]
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", codigo)
        for i, btn in enumerate(self._preset_buttons):
            btn.configure(
                bg=_ACENTO_E4_BG if i == index else T["surface"],
                fg=_ACENTO_E4_FG if i == index else T["text"],
            )
        self._limpiar(keep_status=True)
        # Restablecer el mensaje inicial en la pestaña Resumen al cambiar preset
        self._set_widget(
            self.txt_resumen,
            "Selecciona un ejemplo o escribe tu código y pulsa Analizar.\n\n"
            "Pestañas disponibles:\n"
            "  • Tabla de Símbolos — todos los identificadores declarados con su tipo y ámbito\n"
            "  • Errores Semánticos — violaciones de las 5 reglas semánticas\n"
            "  • Árbol — árbol sintáctico producido por el parser\n\n"
            "Reglas semánticas implementadas:\n"
            "  REGLA 1 — No redeclaración de identificadores en el mismo ámbito\n"
            "  REGLA 2 — Uso de variable previamente declarada\n"
            "  REGLA 3 — Compatibilidad de tipos en declaración con inicialización\n"
            "  REGLA 4 — Tipo de retorno compatible con la función contenedora\n"
            "  REGLA 5 — Función o clase invocada debe estar declarada",
        )

    def _limpiar(self, keep_status: bool = False) -> None:
        for item in self.sym_tree.get_children():
            self.sym_tree.delete(item)
        for item in self.err_tree.get_children():
            self.err_tree.delete(item)
        self.tree_widget.delete(*self.tree_widget.get_children())
        self._set_widget(self.err_detail, "")
        self._err_objects = []
        if not keep_status:
            self._set_status("Listo para analizar.", ok=None)
            self._set_widget(self.txt_resumen, "")

    def _set_status(self, texto: str, ok=None) -> None:
        bg = T["surface"]
        fg = T["text"]
        if ok is True:
            bg = T["ok_bg"]
            fg = T["ok"]
        elif ok is False:
            bg = T["error_bg"]
            fg = T["error"]
        self.lbl_status.configure(text=texto, bg=bg, fg=fg)

    def _set_widget(self, widget: tk.Text, contenido: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", contenido)
        widget.configure(state="disabled")


# ── Alias de compatibilidad ───────────────────────────────────────────────────
SemanticApp = AplicacionSemantico


if __name__ == "__main__":
    root = tk.Tk()
    AplicacionSemantico(root)
    root.mainloop()

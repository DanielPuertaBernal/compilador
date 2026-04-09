"""
main.py — menú principal del proyecto
Teoría de Compiladores | Entrega 2

Permite elegir entre la interfaz del analizador léxico (Entrega 1)
y la interfaz del analizador sintáctico (Entrega 2).
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Optional

T = {
    "bg": "#F3F4F8",
    "surface": "#FFFFFF",
    "surface2": "#EBECF5",
    "border": "#D0D5E2",
    "header_bg": "#1C2840",
    "text": "#28304A",
    "text_dim": "#6E7A96",
    "text_white": "#FFFFFF",
    "accent": "#2563EB",
    "accent2": "#6366F1",
    "accent_light": "#DBEAFE",
}


class LauncherApp:
    """Menú principal para elegir qué interfaz abrir."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.selection: Optional[str] = None

        root.title("Compilador — Menú principal")
        root.geometry("760x460")
        root.minsize(680, 420)
        root.configure(bg=T["bg"])

        try:
            self.f_title = tkfont.Font(family="Segoe UI", size=16, weight="bold")
            self.f_subtitle = tkfont.Font(family="Segoe UI", size=10)
            self.f_card = tkfont.Font(family="Segoe UI", size=12, weight="bold")
            self.f_hint = tkfont.Font(family="Segoe UI", size=10)
        except Exception:
            self.f_title = tkfont.Font(size=16, weight="bold")
            self.f_subtitle = tkfont.Font(size=10)
            self.f_card = tkfont.Font(size=12, weight="bold")
            self.f_hint = tkfont.Font(size=10)

        self._build_ui()
        self.root.bind("1", lambda _event: self._select("lexer"))
        self.root.bind("2", lambda _event: self._select("parser"))
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg=T["header_bg"], height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Compilador Fuente-a-Fuente",
            bg=T["header_bg"],
            fg=T["text_white"],
            font=self.f_title,
        ).pack(anchor="w", padx=18, pady=(12, 0))

        tk.Label(
            header,
            text="Selecciona la interfaz que deseas usar",
            bg=T["header_bg"],
            fg="#BEC8E6",
            font=self.f_subtitle,
        ).pack(anchor="w", padx=18, pady=(2, 10))

        body = tk.Frame(self.root, bg=T["bg"])
        body.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            body,
            text="Elige un módulo",
            bg=T["bg"],
            fg=T["text"],
            font=self.f_title,
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            body,
            text="Puedes abrir el analizador léxico o el analizador sintáctico desde este menú.",
            bg=T["bg"],
            fg=T["text_dim"],
            font=self.f_subtitle,
        ).pack(anchor="w", pady=(0, 14))

        cards = tk.Frame(body, bg=T["bg"])
        cards.pack(fill="x")

        self._build_card(
            cards,
            title="Analizador Léxico",
            subtitle="Entrega 1 · tokenización, tabla de símbolos y errores léxicos",
            button_text="Abrir vista léxica (1)",
            accent=T["accent"],
            command=lambda: self._select("lexer"),
        ).pack(side="left", fill="both", expand=True, padx=(0, 8))

        self._build_card(
            cards,
            title="Analizador Sintáctico",
            subtitle="Entrega 2 · árbol, parser recursivo y predictivo LL(1)",
            button_text="Abrir vista sintáctica (2)",
            accent=T["accent2"],
            command=lambda: self._select("parser"),
        ).pack(side="left", fill="both", expand=True, padx=(8, 0))

        footer = tk.Frame(body, bg=T["bg"])
        footer.pack(fill="x", pady=(18, 0))

        tk.Label(
            footer,
            text="Atajos: 1 = Léxico · 2 = Sintáctico · Esc = Salir",
            bg=T["bg"],
            fg=T["text_dim"],
            font=self.f_hint,
        ).pack(side="left")

        tk.Button(
            footer,
            text="Salir",
            command=self.root.destroy,
            bg=T["surface2"],
            fg=T["text"],
            activebackground=T["surface"],
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
        ).pack(side="right")

    def _build_card(
        self,
        parent: tk.Widget,
        title: str,
        subtitle: str,
        button_text: str,
        accent: str,
        command,
    ) -> tk.Frame:
        card = tk.Frame(parent, bg=T["surface"], bd=1, relief="solid", highlightthickness=0)

        bar = tk.Frame(card, bg=accent, height=8)
        bar.pack(fill="x")

        content = tk.Frame(card, bg=T["surface"])
        content.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            content,
            text=title,
            bg=T["surface"],
            fg=T["text"],
            font=self.f_card,
        ).pack(anchor="w")

        tk.Label(
            content,
            text=subtitle,
            bg=T["surface"],
            fg=T["text_dim"],
            font=self.f_hint,
            justify="left",
            wraplength=280,
        ).pack(anchor="w", pady=(8, 18))

        tk.Button(
            content,
            text=button_text,
            command=command,
            bg=accent,
            fg=T["text_white"],
            activebackground=accent,
            activeforeground=T["text_white"],
            relief="flat",
            padx=16,
            pady=10,
            cursor="hand2",
        ).pack(anchor="w")

        return card

    def _select(self, option: str) -> None:
        self.selection = option
        self.root.destroy()


def show_launcher() -> Optional[str]:
    """Muestra el menú inicial y devuelve la vista elegida."""
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
    return app.selection


def main() -> None:
    """Lanza la interfaz elegida por el usuario."""
    choice = show_launcher()

    if choice == "lexer":
        from gui_tk import App

        root = tk.Tk()
        App(root)
        root.mainloop()
    elif choice == "parser":
        from gui_parser_tk import SyntaxApp

        root = tk.Tk()
        SyntaxApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()

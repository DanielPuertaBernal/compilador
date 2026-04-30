"""
estilos.py — Paleta de colores unificada para todas las interfaces gráficas
Compiladores — Entrega 1 / 2 / 3 | Lenguaje fuente → TypeScript

Importar con:
    from estilos import TEMA
"""

TEMA: dict[str, str] = {
    # ── Fondos ────────────────────────────────────────────────────────
    "bg":              "#F3F4F8",
    "surface":         "#FFFFFF",
    "surface2":        "#EBECF5",
    "surface3":        "#E0E4EE",
    "header_bg":       "#1C2840",
    "panel_header":    "#2C3A56",

    # ── Bordes y texto ────────────────────────────────────────────────
    "border":          "#D0D5E2",
    "text":            "#28304A",
    "text_dim":        "#6E7A96",
    "text_bright":     "#12182E",
    "text_white":      "#FFFFFF",
    "text_header":     "#BEC8E6",

    # ── Acentos ───────────────────────────────────────────────────────
    "accent":          "#2563EB",
    "accent_light":    "#DBEAFE",
    "accent2":         "#6366F1",
    "accent3":         "#7C3AED",

    # ── Árbol sintáctico ──────────────────────────────────────────────
    "tree_nt":         "#1D4ED8",
    "tree_term":       "#047857",
    "tree_eps":        "#6E7A96",

    # ── Estados de validación ─────────────────────────────────────────
    "ok":              "#047857",
    "ok_bg":           "#D1FAE5",
    "error":           "#B91C1C",
    "error_bg":        "#FEE2E2",
    "warn":            "#92400E",
    "warn_bg":         "#FEF3C7",

    # ── Categorías léxicas — color de texto ───────────────────────────
    "reservada":       "#1D4ED8",
    "tipo":            "#047857",
    "logico":          "#6D28D9",
    "operador":        "#A14508",
    "delimitador":     "#475569",
    "identificador":   "#12182E",
    "numero":          "#AF3A0C",
    "cadena":          "#856E0E",
    "booleano":        "#5B21B6",

    # ── Categorías léxicas — fondos pastel ────────────────────────────
    "reservada_bg":    "#DBEAFE",
    "tipo_bg":         "#D1FAE5",
    "logico_bg":       "#EDE9FE",
    "operador_bg":     "#FEF3C7",
    "delimitador_bg":  "#F1F5F9",
    "identificador_bg":"#E2E8F0",
    "numero_bg":       "#FFEDD5",
    "cadena_bg":       "#FEF9C3",
    "booleano_bg":     "#F3E8FF",
    "error_bg_lexico": "#FEE2E2",

    # ── Tabla ─────────────────────────────────────────────────────────
    "row_alt":         "#F8F9FC",
    "row_active":      "#DBEAFE",

    # ── Barra de progreso ─────────────────────────────────────────────
    "progress_bg":     "#D0D5E2",
    "progress_fill":   "#2563EB",
}

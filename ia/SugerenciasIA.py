"""
suggestion_ai.py — Modelo de IA para sugerencias contextuales de errores
Compiladores — Entrega 3

Implementa un clasificador Naive Bayes Multinomial entrenado sobre ejemplos
de errores del lenguaje fuente. El modelo mapea el contexto de un error
(no-terminal activo, token encontrado, tokens esperados) a una clase de
sugerencia y devuelve un mensaje en lenguaje natural.

Reentrenar el modelo:
    modelo = ModeloSugerencias.Cargar("suggestion_model.json")
    modelo.EntrenarEjemplo("sent_si", "fin_si", ["entonces"], "falta_entonces")
    modelo.Guardar("suggestion_model.json")
"""

from __future__ import annotations

import json
import math
import os
from typing import Dict, List, Optional, Tuple

# ── Clases de sugerencia y sus mensajes ──────────────────────────────────────

MENSAJES_SUGERENCIA: Dict[str, str] = {
    "falta_entonces":    "Falta la palabra reservada `entonces` después de la condición del `si`.",
    "falta_hacer":       "Falta la palabra reservada `hacer` después del encabezado del bucle.",
    "falta_fin_si":      "Falta `fin_si` para cerrar el bloque condicional.",
    "falta_fin_para":    "Falta `fin_para` para cerrar el bucle `para`.",
    "falta_fin_mientras": "Falta `fin_mientras` para cerrar el bucle `mientras`.",
    "falta_fin_funcion": "Falta `fin_funcion` para cerrar la declaración de función.",
    "falta_fin_clase":   "Falta `fin_clase` para cerrar la declaración de clase.",
    "falta_tipo":        "Falta el tipo de dato — escribe `entero`, `real`, `cadena` o `booleano`.",
    "falta_paren_der":   "Falta cerrar el paréntesis `)` en la llamada a función o expresión.",
    "falta_dos_puntos":  "Falta `:` después del identificador para indicar su tipo.",
    "falta_asignacion":  "Usa `=` para asignar un valor a la variable o atributo.",
    "falta_identificador": "Se esperaba un nombre válido de variable, función, parámetro o clase.",
    "falta_expresion":   "Se esperaba una expresión: un literal, identificador o subexpresión entre paréntesis.",
    "operador_invalido": "Usa `y`, `o`, `no` para lógica; `^` para potencia; no uses `&&`, `||` ni `!`.",
    "token_inesperado":  "Token inesperado en este contexto. Revisa la estructura de la sentencia.",
}

_CLASE_POR_DEFECTO = "token_inesperado"

# ── Datos de pre-entrenamiento ────────────────────────────────────────────────
# Formato: (nonterminal, token_encontrado, [tokens_esperados], clase)

DATOS_PREENTRENAMIENTO: List[Tuple[str, str, List[str], str]] = [
    # si / entonces / fin_si
    ("sent_si",          "fin_si",       ["entonces"],                               "falta_entonces"),
    ("sent_si",          "fin_para",     ["entonces"],                               "falta_entonces"),
    ("sent_si",          "fin_mientras", ["entonces"],                               "falta_entonces"),
    ("sent_si",          "fin_funcion",  ["entonces"],                               "falta_entonces"),
    ("sent_si",          "hacer",        ["entonces"],                               "falta_entonces"),
    ("sent_si",          "var",          ["entonces"],                               "falta_entonces"),
    ("sent_si",          "retornar",     ["entonces"],                               "falta_entonces"),
    ("sent_si",          "$",            ["fin_si"],                                 "falta_fin_si"),
    ("sent_si",          "fin_funcion",  ["fin_si"],                                 "falta_fin_si"),
    ("sent_si",          "fin_clase",    ["fin_si"],                                 "falta_fin_si"),
    ("rama_sino",        "$",            ["fin_si"],                                 "falta_fin_si"),
    ("rama_sino",        "fin_funcion",  ["fin_si"],                                 "falta_fin_si"),
    # para / hacer / fin_para
    ("sent_para",        "$",            ["hacer"],                                  "falta_hacer"),
    ("sent_para",        "fin_funcion",  ["hacer"],                                  "falta_hacer"),
    ("sent_para",        "fin_si",       ["hacer"],                                  "falta_hacer"),
    ("sent_para",        "$",            ["fin_para"],                               "falta_fin_para"),
    ("sent_para",        "fin_funcion",  ["fin_para"],                               "falta_fin_para"),
    ("sent_para",        "fin_clase",    ["fin_para"],                               "falta_fin_para"),
    # mientras / hacer / fin_mientras
    ("sent_mientras",    "$",            ["hacer"],                                  "falta_hacer"),
    ("sent_mientras",    "fin_funcion",  ["hacer"],                                  "falta_hacer"),
    ("sent_mientras",    "fin_si",       ["hacer"],                                  "falta_hacer"),
    ("sent_mientras",    "$",            ["fin_mientras"],                           "falta_fin_mientras"),
    ("sent_mientras",    "fin_funcion",  ["fin_mientras"],                           "falta_fin_mientras"),
    ("sent_mientras",    "fin_clase",    ["fin_mientras"],                           "falta_fin_mientras"),
    # funcion / fin_funcion
    ("def_funcion",      "$",            ["fin_funcion"],                            "falta_fin_funcion"),
    ("def_funcion",      "fin_clase",    ["fin_funcion"],                            "falta_fin_funcion"),
    ("def_funcion",      "fin_si",       ["fin_funcion"],                            "falta_fin_funcion"),
    ("bloque",           "$",            ["fin_funcion"],                            "falta_fin_funcion"),
    # clase / fin_clase
    ("def_clase",        "$",            ["fin_clase"],                              "falta_fin_clase"),
    ("def_clase",        "fin_funcion",  ["fin_clase"],                              "falta_fin_clase"),
    ("lista_miembros",   "$",            ["fin_clase"],                              "falta_fin_clase"),
    # tipos
    ("param",            "NUMERO_ENTERO",[":"],                                      "falta_dos_puntos"),
    ("param",            "IDENTIFICADOR",[":"],                                      "falta_dos_puntos"),
    ("param",            "=",            [":"],                                      "falta_dos_puntos"),
    ("decl_atributo",    "NUMERO_ENTERO",[":"],                                      "falta_dos_puntos"),
    ("decl_variable",    "NUMERO_ENTERO",[":"],                                      "falta_dos_puntos"),
    ("decl_variable",    "IDENTIFICADOR",[":"],                                      "falta_dos_puntos"),
    ("decl_variable",    "=",            ["entero", "real", "cadena", "booleano",
                                          "IDENTIFICADOR"],                          "falta_tipo"),
    ("decl_variable",    "$",            ["entero", "real", "cadena", "booleano",
                                          "IDENTIFICADOR"],                          "falta_tipo"),
    ("tipo",             "=",            ["entero", "real", "cadena", "booleano",
                                          "IDENTIFICADOR"],                          "falta_tipo"),
    ("tipo",             "$",            ["entero", "real", "cadena", "booleano",
                                          "IDENTIFICADOR"],                          "falta_tipo"),
    # paréntesis
    ("sufijo_valor_atomico", "NUMERO_ENTERO", [")"],                                 "falta_paren_der"),
    ("sufijo_valor_atomico", "IDENTIFICADOR", [")"],                                 "falta_paren_der"),
    ("argumentos",           "$",            [")"],                                  "falta_paren_der"),
    ("arg_lista",            "$",            [")"],                                  "falta_paren_der"),
    ("arg_lista_cont",       "$",            [")"],                                  "falta_paren_der"),
    # asignación
    ("sent_identificador_cont", "IDENTIFICADOR", ["=", "(", "."],                   "falta_asignacion"),
    ("sent_identificador_cont", "fin_si",     ["=", "(", "."],                      "falta_asignacion"),
    ("sent_identificador_cont", "var",        ["=", "(", "."],                      "falta_asignacion"),
    ("inicializacion_opt",      "IDENTIFICADOR", ["="],                             "falta_asignacion"),
    # expresión esperada
    ("valor_atomico",    ")",            ["NUMERO_ENTERO", "NUMERO_REAL",
                                          "IDENTIFICADOR", "(", "nuevo"],           "falta_expresion"),
    ("valor_atomico",    "fin_si",       ["NUMERO_ENTERO", "NUMERO_REAL",
                                          "IDENTIFICADOR", "(", "nuevo"],           "falta_expresion"),
    ("expresion",        "$",            ["NUMERO_ENTERO", "NUMERO_REAL",
                                          "IDENTIFICADOR", "(", "nuevo"],           "falta_expresion"),
    ("expresion_opt",    "fin_si",       ["NUMERO_ENTERO", "NUMERO_REAL",
                                          "IDENTIFICADOR", "("],                    "falta_expresion"),
    # identificador esperado
    ("def_funcion",      "NUMERO_ENTERO",["IDENTIFICADOR"],                         "falta_identificador"),
    ("def_clase",        "NUMERO_ENTERO",["IDENTIFICADOR"],                         "falta_identificador"),
    ("decl_variable",    "NUMERO_ENTERO",["IDENTIFICADOR"],                         "falta_identificador"),
    # token inesperado genérico
    ("programa",         "fin_si",       ["funcion", "clase", "var", "si",
                                          "mientras", "para", "IDENTIFICADOR",
                                          "este", "$"],                             "token_inesperado"),
    ("programa",         "fin_para",     ["funcion", "clase", "var", "si",
                                          "mientras", "para", "IDENTIFICADOR",
                                          "este", "$"],                             "token_inesperado"),
    ("programa",         "fin_mientras", ["funcion", "clase", "var", "si",
                                          "mientras", "para", "IDENTIFICADOR",
                                          "este", "$"],                             "token_inesperado"),
    ("programa",         "entonces",     ["funcion", "clase", "var", "si",
                                          "mientras", "para", "IDENTIFICADOR",
                                          "este", "$"],                             "token_inesperado"),
]

_RUTA_MODELO = os.path.join(os.path.dirname(__file__), "suggestion_model.json")


def _ExtraerCaracteristicas(
    nonterminal: str,
    token_encontrado: str,
    esperado: List[str],
) -> Tuple[str, ...]:
    caracteristicas = [f"NT:{nonterminal}", f"FOUND:{token_encontrado}"]
    for exp in sorted(esperado):
        caracteristicas.append(f"EXP:{exp}")
    return tuple(caracteristicas)


class ModeloSugerencias:
    """
    Clasificador Naive Bayes Multinomial para sugerencias contextuales.

    Características usadas:
      - NT:<nonterminal>   — no-terminal que se estaba expandiendo
      - FOUND:<token>      — terminal encontrado (inesperado)
      - EXP:<token>        — cada terminal esperado en ese contexto

    Suavizado de Laplace para tratar características no vistas.
    """

    def __init__(self) -> None:
        self._conteos_caracteristicas: Dict[Tuple[str, str], int] = {}
        self._conteos_clases: Dict[str, int] = {}
        self._total: int = 0
        self._vocabulario: set = set()

    # ── Entrenamiento ─────────────────────────────────────────────────

    def EntrenarEjemplo(
        self,
        nonterminal: str,
        token_encontrado: str,
        esperado: List[str],
        clase: str,
    ) -> None:
        """Incorpora un ejemplo de entrenamiento al modelo."""
        for caract in _ExtraerCaracteristicas(nonterminal, token_encontrado, esperado):
            clave = (caract, clase)
            self._conteos_caracteristicas[clave] = self._conteos_caracteristicas.get(clave, 0) + 1
            self._vocabulario.add(caract)
        self._conteos_clases[clase] = self._conteos_clases.get(clase, 0) + 1
        self._total += 1

    # ── Predicción ────────────────────────────────────────────────────

    def PredecirClase(
        self,
        nonterminal: str,
        token_encontrado: str,
        esperado: List[str],
    ) -> str:
        """Predice la clase de sugerencia para el contexto de error dado."""
        if self._total == 0:
            return _CLASE_POR_DEFECTO

        caracteristicas = _ExtraerCaracteristicas(nonterminal, token_encontrado, esperado)
        tam_vocabulario = len(self._vocabulario) + 1

        mejor_clase = _CLASE_POR_DEFECTO
        mejor_puntaje = float("-inf")

        for cls, conteo_cls in self._conteos_clases.items():
            puntaje = math.log(conteo_cls / self._total)
            for caract in caracteristicas:
                conteo = self._conteos_caracteristicas.get((caract, cls), 0)
                puntaje += math.log((conteo + 1) / (conteo_cls + tam_vocabulario))
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_clase = cls

        return mejor_clase

    def Sugerir(
        self,
        nonterminal: str,
        token_encontrado: str,
        esperado: List[str],
    ) -> str:
        """Retorna la sugerencia en lenguaje natural para el contexto dado."""
        clase = self.PredecirClase(nonterminal, token_encontrado, esperado)
        return MENSAJES_SUGERENCIA.get(clase, MENSAJES_SUGERENCIA[_CLASE_POR_DEFECTO])

    # ── Persistencia ─────────────────────────────────────────────────

    def Guardar(self, ruta: str = _RUTA_MODELO) -> None:
        datos = {
            "feature_counts": {f"{k[0]}|||{k[1]}": v for k, v in self._conteos_caracteristicas.items()},
            "class_counts": self._conteos_clases,
            "total": self._total,
            "vocab": list(self._vocabulario),
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    @classmethod
    def Cargar(cls, ruta: str = _RUTA_MODELO) -> "ModeloSugerencias":
        modelo = cls()
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        modelo._conteos_caracteristicas = {
            (raw.split("|||")[0], raw.split("|||")[1]): v
            for raw, v in datos["feature_counts"].items()
        }
        modelo._conteos_clases = datos["class_counts"]
        modelo._total = datos["total"]
        modelo._vocabulario = set(datos["vocab"])
        return modelo

    @classmethod
    def ConstruirPreentrenado(cls) -> "ModeloSugerencias":
        """Construye el modelo con los ejemplos predefinidos."""
        modelo = cls()
        for nt, encontrado, esperado, clase in DATOS_PREENTRENAMIENTO:
            modelo.EntrenarEjemplo(nt, encontrado, esperado, clase)
        return modelo

    # ── Alias de compatibilidad ───────────────────────────────────────
    def train_example(self, nt, found, expected, clase):
        return self.EntrenarEjemplo(nt, found, expected, clase)

    def predict_class(self, nt, found, expected):
        return self.PredecirClase(nt, found, expected)

    def suggest(self, nt, found, expected):
        return self.Sugerir(nt, found, expected)

    def save(self, ruta=_RUTA_MODELO):
        return self.Guardar(ruta)

    @classmethod
    def load(cls, ruta=_RUTA_MODELO):
        return cls.Cargar(ruta)

    @classmethod
    def build_pretrained(cls):
        return cls.ConstruirPreentrenado()


# Alias de clase para compatibilidad
SuggestionModel = ModeloSugerencias


def _CargarOConstruir() -> ModeloSugerencias:
    if os.path.exists(_RUTA_MODELO):
        try:
            return ModeloSugerencias.Cargar(_RUTA_MODELO)
        except Exception:
            pass
    modelo = ModeloSugerencias.ConstruirPreentrenado()
    try:
        modelo.Guardar(_RUTA_MODELO)
    except Exception:
        pass
    return modelo


# Instancia global lista para usar directamente
MODELO_IA: ModeloSugerencias = _CargarOConstruir()

# Alias de compatibilidad hacia atrás
AI_MODEL = MODELO_IA
PRETRAIN_DATA = DATOS_PREENTRENAMIENTO
SUGGESTION_MESSAGES = MENSAJES_SUGERENCIA

"""
AsistenteSemantico.py — Integración de IA para el análisis semántico
Compiladores — Entrega 4 | Bonus Modalidad A + C

Modalidad A: enriquece los errores detectados por las reglas clásicas
             con sugerencias contextualizadas generadas por Claude.
Modalidad C: responde preguntas del usuario sobre un error semántico
             específico, manteniendo el contexto del programa fuente.

Requiere:
    pip install anthropic
    Variable de entorno ANTHROPIC_API_KEY con la clave de API.

Uso:
    from ia.AsistenteSemantico import enriquecer_errores, consultar_error

    # Modalidad A — enriquecimiento automático tras el análisis
    exito, msg = enriquecer_errores(codigo, lista_de_errores)

    # Modalidad C — asistente interactivo
    exito, respuesta = consultar_error(codigo, error_seleccionado, pregunta)
"""

from __future__ import annotations

import json
import os
from typing import List, Optional, Tuple

from semantico.ErrorSemantico import ErrorSemantico


# ── Configuración del modelo ──────────────────────────────────────────────────

_MODELO = "claude-haiku-4-5-20251001"   # rápido y económico para la demo

# ── Prompts de sistema ────────────────────────────────────────────────────────

_SISTEMA_ENRIQUECER = """\
Eres un asistente de compiladores especializado en análisis semántico.
El compilador procesa código en un lenguaje imperativo/OOP con palabras clave
en español y lo traduce a TypeScript.

Se te entregará el código fuente y los errores semánticos que el compilador
detectó aplicando sus reglas clásicas (tabla de símbolos, verificación de tipos,
comprobación de declaraciones, etc.).

Para cada error, genera una sugerencia de corrección CONCISA (máximo 2 oraciones)
en español que explique POR QUÉ ocurre el error y CÓMO corregirlo exactamente.

Responde ÚNICAMENTE con un objeto JSON con este formato exacto:
{"sugerencias": ["sugerencia para error 1", "sugerencia para error 2", ...]}

Sin texto adicional fuera del JSON."""

_SISTEMA_CONSULTAR = """\
Eres un asistente de compiladores especializado en análisis semántico.
El compilador procesa código en un lenguaje imperativo/OOP con palabras clave
en español y lo traduce a TypeScript.

Recibes el código fuente del programa y los detalles de un error semántico
específico detectado por las reglas clásicas del compilador.

Responde de forma clara, concisa y en español las preguntas del usuario sobre
el error. Incluye siempre: la causa raíz del error y el paso exacto para corregirlo."""


# ── Helpers internos ──────────────────────────────────────────────────────────

def _crear_cliente(api_key: Optional[str] = None):
    """
    Crea y retorna un cliente Anthropic, o None si no está disponible.
    Busca la clave en: parámetro → ANTHROPIC_API_KEY → vacío (falla).
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except ImportError:
        return None


def _extraer_json(texto: str) -> Optional[dict]:
    """Extrae el primer objeto JSON del texto aunque haya texto extra alrededor."""
    inicio = texto.find("{")
    fin    = texto.rfind("}") + 1
    if inicio == -1 or fin == 0:
        return None
    try:
        return json.loads(texto[inicio:fin])
    except json.JSONDecodeError:
        return None


# ── API pública ───────────────────────────────────────────────────────────────

def enriquecer_errores(
    codigo_fuente: str,
    errores: List[ErrorSemantico],
    api_key: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Modalidad A — enriquece las sugerencias de los errores con IA.

    Llama a la API de Anthropic/Claude con el código fuente y los errores
    ya detectados por las reglas clásicas, y reemplaza cada
    ErrorSemantico.sugerencia con la versión contextualizada generada por el modelo.

    No reemplaza las reglas clásicas: opera DESPUÉS de que el analizador
    semántico terminó su trabajo y ya se tienen los errores.

    Parámetros:
        codigo_fuente — código fuente completo analizado
        errores       — lista de ErrorSemantico (modificados in-place)
        api_key       — clave de API (opcional; usa ANTHROPIC_API_KEY si no se pasa)

    Retorna:
        (True,  mensaje_informativo)  si el enriquecimiento fue exitoso
        (False, mensaje_de_error)     si falló por cualquier motivo
    """
    if not errores:
        return True, ""

    cliente = _crear_cliente(api_key)
    if cliente is None:
        return (
            False,
            "ANTHROPIC_API_KEY no configurada o librería 'anthropic' no instalada."
            " Ejecuta: pip install anthropic",
        )

    # Construir descripción numerada de los errores
    errores_desc = "\n".join(
        f"Error {i + 1} — L{e.fila}:C{e.columna}  "
        f"lexema='{e.lexema}'  regla={e.tipo_error}:\n  {e.mensaje}"
        for i, e in enumerate(errores)
    )
    prompt = (
        f"Código fuente:\n```\n{codigo_fuente}\n```\n\n"
        f"Errores semánticos detectados por el compilador:\n{errores_desc}"
    )

    try:
        respuesta = cliente.messages.create(
            model=_MODELO,
            max_tokens=1024,
            system=_SISTEMA_ENRIQUECER,
            messages=[{"role": "user", "content": prompt}],
        )
        datos = _extraer_json(respuesta.content[0].text.strip())
        if datos is None:
            return False, "La IA devolvió una respuesta en formato inesperado."

        sugerencias: List[str] = datos.get("sugerencias", [])
        enriquecidos = 0
        for i, err in enumerate(errores):
            if i < len(sugerencias) and sugerencias[i]:
                err.sugerencia = f"[IA] {sugerencias[i]}"
                enriquecidos += 1

        return True, f"✦ {enriquecidos} sugerencia(s) generada(s) por IA"

    except Exception as exc:
        return False, f"Error al consultar la IA: {exc}"


def consultar_error(
    codigo_fuente: str,
    error: ErrorSemantico,
    pregunta: str,
    api_key: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Modalidad C — responde una pregunta sobre un error semántico específico.

    Actúa como asistente de depuración integrado: el usuario selecciona
    un error en la GUI y puede preguntar sobre su causa y corrección.

    Parámetros:
        codigo_fuente — código fuente completo
        error         — el ErrorSemantico seleccionado por el usuario
        pregunta      — pregunta en lenguaje natural del usuario
        api_key       — clave de API (opcional; usa ANTHROPIC_API_KEY si no se pasa)

    Retorna:
        (True,  texto_respuesta)     si la consulta fue exitosa
        (False, mensaje_de_error)    si falló
    """
    cliente = _crear_cliente(api_key)
    if cliente is None:
        return (
            False,
            "ANTHROPIC_API_KEY no configurada o librería 'anthropic' no instalada.\n"
            "Ejecuta: pip install anthropic",
        )

    contexto = (
        f"Código fuente:\n```\n{codigo_fuente}\n```\n\n"
        f"Error semántico seleccionado:\n"
        f"  Línea   : {error.fila}\n"
        f"  Columna : {error.columna}\n"
        f"  Lexema  : '{error.lexema}'\n"
        f"  Regla   : {error.tipo_error}\n"
        f"  Mensaje : {error.mensaje}\n"
        f"  Sugerencia actual: {error.sugerencia or '—'}\n\n"
        f"Pregunta del usuario: {pregunta}"
    )

    try:
        respuesta = cliente.messages.create(
            model=_MODELO,
            max_tokens=512,
            system=_SISTEMA_CONSULTAR,
            messages=[{"role": "user", "content": contexto}],
        )
        return True, respuesta.content[0].text.strip()
    except Exception as exc:
        return False, f"Error al consultar la IA: {exc}"

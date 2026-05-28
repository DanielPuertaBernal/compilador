"""
AsistenteSemantico.py — Integración de IA para el análisis semántico
Compiladores — Entrega 4 | Bonus Modalidad A + C

Usa la API gratuita de Groq (LLaMA 3) para enriquecer los errores semánticos
detectados por las reglas clásicas del compilador.

Modalidad A: tras el análisis, enriquece cada ErrorSemantico.sugerencia
             con una explicación contextual generada por el modelo.
Modalidad C: responde preguntas del usuario sobre un error específico.

Obtener clave gratuita (sin tarjeta de crédito):
    https://console.groq.com  →  "API Keys" → "Create API Key"

Agregar al archivo .env en la raíz del proyecto:
    GROQ_API_KEY=gsk_...

Sin dependencias externas — usa urllib de la librería estándar de Python.
"""

from __future__ import annotations

import json
import os
import pathlib
import urllib.request
import urllib.error
from typing import List, Optional, Tuple

from semantico.ErrorSemantico import ErrorSemantico


# ── Lectura del .env ──────────────────────────────────────────────────────────

def _leer_dotenv() -> dict[str, str]:
    """Lee el archivo .env de la raíz del proyecto sin dependencias externas."""
    raiz = pathlib.Path(__file__).parent.parent   # ia/ → compilador/
    env_path = raiz / ".env"
    valores: dict[str, str] = {}
    if not env_path.exists():
        return valores
    try:
        with open(env_path, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                clave, _, valor = linea.partition("=")
                valores[clave.strip()] = valor.strip().strip('"').strip("'")
    except Exception:
        pass
    return valores


_ENV = _leer_dotenv()   # se carga una vez al importar el módulo


# ── Configuración ─────────────────────────────────────────────────────────────

_MODELO      = "llama-3.1-8b-instant"                             # gratis en Groq
_URL_GROQ    = "https://api.groq.com/openai/v1/chat/completions"  # compatible con OpenAI
_TIMEOUT_SEG = 30

# ── Prompts de sistema ────────────────────────────────────────────────────────

_SISTEMA_ENRIQUECER = (
    "Eres un asistente de compiladores especializado en análisis semántico. "
    "El compilador procesa código en un lenguaje imperativo/OOP con palabras "
    "clave en español y lo traduce a TypeScript. "
    "Para cada error semántico detectado por las reglas clásicas del compilador, "
    "genera una sugerencia de corrección CONCISA (máximo 2 oraciones) en español "
    "que explique POR QUÉ ocurre el error y CÓMO corregirlo exactamente. "
    'Responde ÚNICAMENTE con JSON válido: {"sugerencias": ["sugerencia 1", ...]} '
    "Sin texto adicional fuera del JSON."
)

_SISTEMA_CONSULTAR = (
    "Eres un asistente de compiladores especializado en análisis semántico. "
    "El compilador procesa código con palabras clave en español que compila a TypeScript. "
    "Responde de forma clara, concisa y en español las preguntas sobre errores semánticos. "
    "Incluye siempre: la causa raíz del error y el paso exacto para corregirlo."
)


# ── Comunicación con Groq ─────────────────────────────────────────────────────

def _llamar_groq(
    sistema: str,
    prompt: str,
    api_key: str,
) -> Tuple[bool, str]:
    """Llama a la API de Groq (compatible con OpenAI) y retorna (exito, texto)."""
    cuerpo = json.dumps({
        "model": _MODELO,
        "messages": [
            {"role": "system", "content": sistema},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens":  1024,
    }).encode("utf-8")

    req = urllib.request.Request(
        _URL_GROQ,
        data=cuerpo,
        headers={
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SEG) as resp:
            datos = json.loads(resp.read().decode("utf-8"))
            texto = datos["choices"][0]["message"]["content"].strip()
            return True, texto
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", errors="replace")
        try:
            msg_api = json.loads(detalle).get("error", {}).get("message", detalle)
        except Exception:
            msg_api = detalle[:120]
        return False, f"Error Groq API: {msg_api}"
    except urllib.error.URLError as e:
        return False, f"Sin conexión a internet: {e.reason}"
    except Exception as exc:
        return False, f"Error inesperado: {exc}"


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


def _obtener_key(api_key: Optional[str]) -> Optional[str]:
    """Retorna la clave de API: parámetro → .env → variable de entorno."""
    return (
        api_key
        or _ENV.get("GROQ_API_KEY")
        or os.environ.get("GROQ_API_KEY")
        or None
    )


# ── API pública ───────────────────────────────────────────────────────────────

def enriquecer_errores(
    codigo_fuente: str,
    errores: List[ErrorSemantico],
    api_key: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Modalidad A — enriquece las sugerencias de los errores con Gemini.

    Opera DESPUÉS de que el analizador semántico detectó los errores con
    sus reglas clásicas. Reemplaza ErrorSemantico.sugerencia con texto
    contextualizado generado por el modelo.

    Retorna (True, msg_info) si fue exitoso,
            (False, msg_error) si faltó la clave o hubo error de red.
    """
    if not errores:
        return True, ""

    key = _obtener_key(api_key)
    if not key:
        return (
            False,
            "Configura GROQ_API_KEY en el archivo .env. "
            "Clave gratuita (sin tarjeta) en: console.groq.com",
        )

    errores_desc = "\n".join(
        f"Error {i + 1} — L{e.fila}:C{e.columna}  "
        f"lexema='{e.lexema}'  regla={e.tipo_error}:\n  {e.mensaje}"
        for i, e in enumerate(errores)
    )
    prompt = (
        f"Código fuente:\n```\n{codigo_fuente}\n```\n\n"
        f"Errores semánticos detectados por el compilador:\n{errores_desc}"
    )

    exito, texto = _llamar_groq(_SISTEMA_ENRIQUECER, prompt, key)
    if not exito:
        return False, texto

    datos = _extraer_json(texto)
    if datos is None:
        return False, "Gemini no devolvió JSON válido. Reintenta."

    sugerencias: List[str] = datos.get("sugerencias", [])
    enriquecidos = 0
    for i, err in enumerate(errores):
        if i < len(sugerencias) and sugerencias[i]:
            err.sugerencia = f"[IA] {sugerencias[i]}"
            enriquecidos += 1

    return True, f"✦ {enriquecidos} sugerencia(s) generada(s) por Gemini"


def consultar_error(
    codigo_fuente: str,
    error: ErrorSemantico,
    pregunta: str,
    api_key: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Modalidad C — responde una pregunta sobre un error semántico específico.

    Retorna (True, respuesta) si fue exitoso,
            (False, msg_error) si faltó la clave o hubo error de red.
    """
    key = _obtener_key(api_key)
    if not key:
        return (
            False,
            "Configura GROQ_API_KEY en el archivo .env.\n"
            "Clave gratuita (sin tarjeta) en: console.groq.com",
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
    return _llamar_groq(_SISTEMA_CONSULTAR, contexto, key)

# Compilador Fuente-a-Fuente — Español a TypeScript
**Teoría de Compiladores — Trabajo de curso | Entregas 1, 2 y 3**

Proyecto de curso para un lenguaje fuente con palabras reservadas en español, análisis léxico, sintáctico y recuperación de errores con sugerencias generadas por IA.

---

## Resumen del proyecto

- **Lenguaje fuente:** imperativo y orientado a objetos, sintaxis en español
- **Lenguaje destino:** TypeScript
- **Entrega 1:** analizador léxico con visualización interactiva
- **Entrega 2:** parser recursivo y predictivo LL(1) con árbol sintáctico
- **Entrega 3:** recuperación de errores en modo pánico + sugerencias con IA (Naive Bayes)

## Documentación incluida

| Documento | Contenido |
|---|---|
| [Requisitos del Lenguaje Origen](Documentacion/RequisitosLenguajeOrigen.md) | Vocabulario, operadores, delimitadores y equivalencias con TypeScript |
| [Gramática BNF](Documentacion/BNF.md) | Gramática LL(1) en BNF, conjuntos FIRST/FOLLOW, verificación y ajustes |
| `README.md` | Instalación, ejecución, estructura y descripción del módulo de IA |

---

## Estructura del proyecto

```
compilador/
├── Main.py                        # Menú principal
├── lexico/
│   ├── Tokens.py                  # Enum TokenType (33 tokens) y dataclass Token
│   ├── Lexer.py                   # Analizador léxico reutilizable
│   └── LogicaLexer.py             # EstadoLexer — lógica de estado para la GUI léxica
├── sintactico/
│   ├── Gramatica.py               # Gramática LL(1) factorizada y funciones auxiliares
│   ├── TablaLL1.py                # Cálculo de FIRST, FOLLOW y tabla LL(1)
│   ├── EstadoParser.py            # Instancia global de tabla y conjuntos
│   ├── ArbolSintactico.py         # NodoArbol, ResultadoAnalisis, ErrorSintactico
│   ├── RecuperacionErrores.py     # Tokens de sincronización y salto en modo pánico
│   ├── ParserRecursivo.py         # Analizador descendente recursivo
│   ├── ParserPredictivo.py        # Analizador predictivo LL(1) con pila explícita
│   └── ControladorParser.py      # SolicitudAnalisis / EjecutarAnalisis — API unificada
├── ia/
│   └── SugerenciasIA.py           # Clasificador Naive Bayes para sugerencias de error
└── gui/
    ├── Estilos.py                 # Paleta TEMA unificada para todas las interfaces
    ├── Programas.py               # 5 programas de prueba predefinidos
    ├── InterfazLexer.py           # Interfaz Tkinter — Entrega 1
    └── InterfazSintactico.py      # Interfaz Tkinter — Entregas 2 y 3
```

---

## Requisitos e instalación

- Python 3.9 o superior
- `tkinter` — incluido en Python estándar. En Linux: `sudo apt install python3-tk`
- Sin dependencias externas adicionales

```bash
git clone https://github.com/DanielPuertaBernal/compilador
cd compilador

# Entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate       # Mac / Linux
venv\Scripts\activate          # Windows

# Ejecutar
python Main.py
```

---

## Uso de la aplicación

### Menú principal

`Main.py` muestra tres tarjetas:

| Opción | Atajo | Descripción |
|---|---|---|
| Analizador Léxico | `1` | Interfaz de la Entrega 1 |
| Analizador Sintáctico | `2` | Interfaz de la Entrega 2 |
| Recuperación de Errores + IA | `3` | Interfaz de la Entrega 3 (recuperación activada) |

### Entrega 1 — Analizador léxico

Seleccionar preset o escribir código. Botones disponibles:

| Botón | Función |
|---|---|
| **Analizar todo** | Tokeniza de una sola vez |
| **Paso siguiente** | Avanza un token — modo paso a paso |
| **Reiniciar** | Limpia el análisis |

Panel derecho muestra el código resaltado por categoría y la tabla de símbolos léxicos.

### Entrega 2 — Analizador sintáctico

| Funcionalidad | Descripción |
|---|---|
| Método | Elegir entre **recursivo** y **predictivo LL(1)** |
| Árbol sintáctico | Visualización del árbol generado |
| Traza predictiva | Pila, lookahead y acción paso a paso |
| Tabla LL(1) | Calculada automáticamente desde la gramática |
| FIRST / FOLLOW | Conjuntos mostrados en la propia app |

### Entrega 3 — Recuperación de errores + IA

Activar **"Recuperar errores (E3)"** antes de analizar. El parser no aborta al primer error: salta tokens hasta el siguiente punto de sincronización y sigue. La pestaña **Errores (E3)** muestra todos los errores encontrados con número, fila, columna y la sugerencia generada por el modelo de IA.

---

## Módulo de IA — Sugerencias contextuales

**Archivo:** [`ia/SugerenciasIA.py`](ia/SugerenciasIA.py)

### ¿Qué problema resuelve?

Cuando el parser detecta un error, el mensaje genérico ("token inesperado") no orienta al estudiante. El modelo de IA clasifica el contexto del error y devuelve un mensaje en lenguaje natural específico, por ejemplo:

> *"Falta la palabra reservada `entonces` después de la condición del `si`."*

### Algoritmo: Naive Bayes Multinomial

Se eligió Naive Bayes Multinomial por ser interpretable, liviano (sin dependencias externas), entrenable incrementalmente y apropiado para clasificación de texto con características discretas.

#### Paso 1 — Extracción de características

Cada error se describe con tres tipos de características categóricas:

```
NT:<nonterminal>     →  el no-terminal que se estaba expandiendo
FOUND:<token>        →  el terminal encontrado (inesperado)
EXP:<token>          →  cada terminal esperado en ese contexto (uno por característica)
```

**Ejemplo** — error al parsear `sent_si` con token `fin_si` esperando `entonces`:

```
("NT:sent_si", "FOUND:fin_si", "EXP:entonces")
```

Función: `_ExtraerCaracteristicas(nonterminal, token_encontrado, esperado) → tuple[str, ...]`

#### Paso 2 — Entrenamiento

El modelo se entrena con `DATOS_PREENTRENAMIENTO`: 60+ ejemplos etiquetados de la forma `(nonterminal, token_encontrado, [esperados], clase)`.

Por cada ejemplo, `EntrenarEjemplo` actualiza tres contadores:

| Contador | Qué almacena |
|---|---|
| `_conteos_caracteristicas[(caract, clase)]` | Cuántas veces aparece cada característica en cada clase |
| `_conteos_clases[clase]` | Cuántos ejemplos hay de cada clase |
| `_vocabulario` | Conjunto de todas las características vistas |

Las 15 clases posibles son: `falta_entonces`, `falta_hacer`, `falta_fin_si`, `falta_fin_para`, `falta_fin_mientras`, `falta_fin_funcion`, `falta_fin_clase`, `falta_tipo`, `falta_paren_der`, `falta_dos_puntos`, `falta_asignacion`, `falta_identificador`, `falta_expresion`, `operador_invalido`, `token_inesperado`.

#### Paso 3 — Predicción

Para un nuevo error, `PredecirClase` calcula el puntaje logarítmico de cada clase:

```
score(clase) = log P(clase) + Σ log P(característica | clase)
```

Con **suavizado de Laplace** para características no vistas:

```
P(característica | clase) = (conteo(caract, clase) + 1) / (conteo(clase) + |vocabulario| + 1)
```

Se elige la clase con mayor puntaje.

```python
# Simplificado
for cls, conteo_cls in self._conteos_clases.items():
    puntaje = log(conteo_cls / self._total)             # prior
    for caract in caracteristicas:
        conteo = conteos[(caract, cls)]                 # likelihood + Laplace
        puntaje += log((conteo + 1) / (conteo_cls + vocab_size))
```

#### Paso 4 — Traducción a lenguaje natural

La clase predicha se mapea a un mensaje en `MENSAJES_SUGERENCIA`:

```python
MENSAJES_SUGERENCIA = {
    "falta_entonces":  "Falta la palabra reservada `entonces` después de la condición del `si`.",
    "falta_fin_si":    "Falta `fin_si` para cerrar el bloque condicional.",
    # ... 15 clases en total
}
```

#### Paso 5 — Persistencia del modelo

Al iniciarse, `_CargarOConstruir` intenta cargar `suggestion_model.json`. Si no existe (o falla), construye el modelo desde `DATOS_PREENTRENAMIENTO` y lo guarda. Esto evita reentrenar en cada ejecución.

```
Primera ejecución:  DATOS_PREENTRENAMIENTO → ModeloSugerencias → suggestion_model.json
Siguientes:         suggestion_model.json → ModeloSugerencias (carga rápida)
```

`suggestion_model.json` está en `.gitignore` — se regenera automáticamente.

#### Diagrama de flujo completo

```
Parser detecta error
        │
        ▼
ConstruirError(nonterminal, token_encontrado, esperados)
        │
        ▼
MODELO_IA.Sugerir(nonterminal, encontrado, esperados)
        │
        ▼
_ExtraerCaracteristicas → ["NT:sent_si", "FOUND:fin_si", "EXP:entonces"]
        │
        ▼
PredecirClase → score por cada clase (Naive Bayes + Laplace)
        │
        ▼
clase = "falta_entonces"
        │
        ▼
MENSAJES_SUGERENCIA["falta_entonces"]
        │
        ▼
"Falta la palabra reservada `entonces` después de la condición del `si`."
        │
        ▼
ErrorSintactico.sugerencia → mostrado en pestaña Errores (E3)
```

### Reentrenar o extender el modelo

```python
from ia.SugerenciasIA import ModeloSugerencias

modelo = ModeloSugerencias.Cargar("ia/suggestion_model.json")
modelo.EntrenarEjemplo("sent_si", "fin_clase", ["entonces"], "falta_entonces")
modelo.Guardar("ia/suggestion_model.json")
```

---

## Entregables por entrega

### Entrega 1

| Entregable | Evidencia |
|---|---|
| Código fuente Python | `lexico/Tokens.py`, `lexico/Lexer.py`, `gui/InterfazLexer.py` |
| Interfaz gráfica | `gui/InterfazLexer.py` — resaltado, tabla léxica, modo paso a paso |

### Entrega 2

| Entregable | Evidencia |
|---|---|
| Parser recursivo | `sintactico/ParserRecursivo.py` |
| Parser predictivo LL(1) | `sintactico/ParserPredictivo.py` |
| Tabla LL(1) calculada | `sintactico/TablaLL1.py`, pestaña "Tabla LL(1)" en la GUI |
| FIRST / FOLLOW | `sintactico/TablaLL1.py`, pestaña "FIRST/FOLLOW" en la GUI |
| Árbol sintáctico | Pestaña "Árbol" en `gui/InterfazSintactico.py` |
| Ajustes a la gramática | §8 de `Documentacion/BNF.md` |

### Entrega 3

| Entregable | Evidencia |
|---|---|
| Recuperación en modo pánico | `sintactico/RecuperacionErrores.py`, checkbox "Recuperar errores (E3)" |
| Múltiples errores por análisis | `sintactico/ParserRecursivo.py` y `ParserPredictivo.py` con `recuperar=True` |
| Sugerencias con IA | `ia/SugerenciasIA.py` — Naive Bayes Multinomial con suavizado de Laplace |
| Pestaña de errores detallada | "Errores (E3)" en `gui/InterfazSintactico.py` |

---

## Tecnologías

- **Python 3.9+** con `tkinter` para la GUI
- **Sin dependencias externas** — Naive Bayes implementado desde cero con `math.log`
- **LL(1)** verificado sin conflictos — tabla calculada en `sintactico/TablaLL1.py`

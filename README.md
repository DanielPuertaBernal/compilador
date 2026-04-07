# Compilador Fuente-a-Fuente — Español a TypeScript

Repositorio que contiene la lógica necesaria para la construcción de un compilador capaz de transformar una gramática libre de contexto definida en lenguaje natural (español) hacia código en el lenguaje de destino TypeScript.

---

## Descripción general

El proyecto consiste en diseñar un lenguaje de programación propio con palabras reservadas en español y construir, a lo largo de las entregas del curso, un compilador completo que traduzca programas escritos en ese lenguaje fuente a TypeScript.

---

## Entregas

### Entrega 1 — Análisis Léxico y Gramática BNF

| Documento | Descripción |
|---|---|
| [Requisitos del Lenguaje Origen](Documentacion/RequisitosLenguajeOrigen.md) | Vocabulario completo del lenguaje fuente: palabras reservadas, operadores, delimitadores, ejemplos y tabla de traducción a TypeScript. |
| [Gramática BNF](Documentacion/BNF.md) | Gramática Libre de Contexto en notación BNF: terminales, producciones, verificación LL, cobertura de requisitos y ejemplos de programas válidos e inválidos. |

### Entrega 2 — Análisis Sintáctico Descendente

La segunda entrega amplía el proyecto con dos analizadores sintácticos que reutilizan el `lexer.py` de la Entrega 1:

- **Descendente recursivo** — reconocimiento por funciones recursivas y construcción del árbol sintáctico.
- **Predictivo LL(1)** — cálculo automático de `FIRST`, `FOLLOW`, tabla LL(1), traza de pila y árbol sintáctico.

---

## Entregable práctico — Analizador Léxico

### Archivos

| Archivo | Responsabilidad |
|---|---|
| `tokens.py` | Enum `TokenType` con los 33 tokens del lenguaje y dataclass `Token` |
| `lexer.py` | Clase `Lexer` — analizador léxico independiente y reutilizable |
| `gui_logic.py` | `EstadoLexer` — lógica de estado del análisis léxico (paso a paso, segmentos, errores) |
| `gui_tk.py` | Interfaz gráfica Tkinter de la Entrega 1 — visualización interactiva del análisis léxico |
| `grammar.py` | Gramática LL(1) factorizada y programas de prueba para la Entrega 2 |
| `ll1_table.py` | Cálculo de conjuntos `FIRST`, `FOLLOW` y tabla LL(1) |
| `parse_tree.py` | Nodos del árbol sintáctico, errores y resultados unificados |
| `parser_recursive.py` | Analizador sintáctico descendente recursivo |
| `parser_predictive.py` | Analizador sintáctico predictivo descendente con pila explícita |
| `gui_parser_tk.py` | Interfaz gráfica Tkinter de la Entrega 2 — árbol, traza LL(1) y validación sintáctica |
| `requirements.txt` | Dependencias externas del proyecto |

### Requisitos

- Python 3.10 o superior
- `tkinter` — incluido en Python estándar. En Linux: `sudo apt install python3-tk`
- No requiere dependencias externas adicionales

### Instalación y ejecución

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/compilador
cd compilador

# Crear y activar entorno virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

# Ejecutar la interfaz gráfica de la Entrega 1 (léxico)
python gui_tk.py

# Ejecutar la interfaz gráfica de la Entrega 2 (sintáctico)
python gui_parser_tk.py
```

### Uso de la interfaz

#### Entrega 1 — Analizador léxico

La interfaz ofrece dos modos de ingreso de código fuente:

**Modo A — Ingresar código manualmente:**
Hacer clic en **"Ingresar codigo manualmente"** para abrir un diálogo de texto libre donde se puede escribir o pegar cualquier programa del lenguaje fuente. Confirmar con **"Usar este codigo"** o `Ctrl+Enter`.

**Modo B — Programas predefinidos:**
Seleccionar uno de los 5 programas en la barra superior del editor:

| Preset | Constructos que demuestra |
|---|---|
| Factorial | Funciones recursivas, `si/sino`, `retornar` |
| Busqueda lineal | `para/desde/hasta/paso`, `si`, variables |
| Clase Rectangulo | OOP completo — clases, atributos, métodos, `nuevo` |
| Mientras + Logicos | `mientras`, operadores `y` / `o` / `no` |
| Errores lexicos | Detección de `@`, cadena sin cerrar, comentario sin cerrar |

Una vez cargado el código, usar los botones de análisis:

| Botón | Función |
|---|---|
| **Analizar todo** | Procesa todos los tokens de una sola vez |
| **Paso siguiente** | Avanza un token — muestra el proceso paso a paso |
| **Reiniciar** | Limpia el análisis y vuelve al estado inicial |

#### Entrega 2 — Analizador sintáctico

La nueva interfaz `gui_parser_tk.py` permite:

| Funcionalidad | Descripción |
|---|---|
| Selección de método | Elegir entre **recursivo** y **predictivo LL(1)** |
| Programas predefinidos | Casos válidos e inválidos para probar la gramática |
| Árbol sintáctico | Visualización del árbol generado por ambos métodos |
| Traza predictiva | Tabla paso a paso con pila, lookahead y acción tomada |
| Tabla LL(1) | Vista de la tabla calculada automáticamente desde la gramática |
| FIRST / FOLLOW | Conjuntos calculados y mostrados en la propia app |

### Funcionalidades cubiertas

| Requisito del enunciado | Implementación |
|---|---|
| Ingreso libre de cadena | Botón "Ingresar codigo manualmente" — diálogo modal |
| Selección de cadena predefinida | 5 presets en la barra del editor |
| Visualización gráfica de tokens | Panel "Posicion del Analizador" — colores por categoría, resaltado de línea activa, indicador del token actual |
| Tabla de símbolos léxicos | Panel "Tabla de Simbolos Lexicos" — lexema, categoría, TokenType, fila, columna |
| Manejo de errores léxicos | Barra inferior — fila y columna exactas, análisis continúa sin abortar |
| Independencia del lexer | `lexer.py` — clase autónoma importable directamente en futuras entregas |

### Reutilización del lexer en entregas futuras

```python
from lexer import Lexer

lex = Lexer(codigo_fuente)
tokens, errores = lex.tokenizar()

# tokens: list[Token]       — .tipo, .lexema, .fila, .columna
# errores: list[ErrorLexico] — .mensaje, .fila, .columna
```

---

## Tecnologías

- **Lenguaje fuente:** diseño propio con palabras clave en español
- **Lenguaje de destino:** TypeScript
- **Implementación:** Python 3 + Tkinter

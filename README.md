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

---

## Entregable práctico — Analizador Léxico

### Archivos

| Archivo | Responsabilidad |
|---|---|
| `tokens.py` | Enum `TokenType` con los 33 tokens del lenguaje y dataclass `Token` |
| `lexer.py` | Clase `Lexer` — analizador léxico independiente y reutilizable |
| `gui_logic.py` | `EstadoLexer` — lógica de estado del análisis (paso a paso, segmentos, errores) |
| `gui_tk.py` | Interfaz gráfica Tkinter — visualización interactiva del análisis |

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

# Ejecutar la interfaz gráfica
python gui_tk.py
```

### Uso de la interfaz

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

# Compilador Fuente-a-Fuente — Español a TypeScript
**Teoría de Compiladores — Trabajo de curso | Entrega 2**

Proyecto de curso para un lenguaje fuente con palabras reservadas en español y análisis sintáctico sobre una gramática LL(1), reutilizando el analizador léxico construido en la Entrega 1.

---

## Resumen del proyecto

- **Lenguaje fuente:** imperativo y orientado a objetos, con sintaxis en español
- **Lenguaje de destino:** TypeScript
- **Método 1:** parser descendente recursivo con árbol sintáctico
- **Método 2:** parser predictivo LL(1) con tabla, pila y traza paso a paso

## Documentación incluida

| Documento | Contenido |
|---|---|
| [Requisitos del Lenguaje Origen](Documentacion/RequisitosLenguajeOrigen.md) | Vocabulario, operadores, delimitadores y equivalencias con TypeScript |
| [Gramática BNF](Documentacion/BNF.md) | Gramática final en BNF, conjuntos FIRST/FOLLOW, verificación LL(1) y ajustes realizados |
| `README.md` | Instalación, ejecución y resumen de entregables |

## Entregables de la Entrega 2

| Entregable | Evidencia en el repositorio |
|---|---|
| **E1 — Código fuente Python** | `lexer.py`, `parser_recursive.py`, `parser_predictive.py`, `gui_parser_tk.py` y módulos auxiliares |
| **E2 — Tabla LL(1) calculada** | `ll1_table.py`, pestañas de tabla y FIRST/FOLLOW en `gui_parser_tk.py`, §4 de `Documentacion/BNF.md` |
| **E3 — README actualizado** | Este archivo |
| **E5 — Ajustes a la gramática** | §8 de `Documentacion/BNF.md` |

---

## Código fuente incluido

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

- Python 3.9 o superior
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

### Flujo sugerido para la sustentación

1. Abrir `gui_parser_tk.py`
2. Probar un caso **válido** con el método **recursivo** y mostrar el árbol
3. Probar el mismo caso con **predictivo LL(1)** y mostrar la traza de pila
4. Ejecutar un caso **inválido** para evidenciar el reporte de error

## Uso de la aplicación

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
| Integración con el lexer de la Entrega 1 | `lexer.py` se reutiliza directamente por los parsers y la interfaz, sin duplicar lógica |

---

## Tecnologías

- **Lenguaje fuente:** diseño propio con palabras clave en español
- **Lenguaje de destino:** TypeScript
- **Implementación:** Python 3 + Tkinter

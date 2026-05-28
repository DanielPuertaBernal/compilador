"""
AnalizadorSemantico.py — Analizador semántico por recorrido del árbol sintáctico
Compiladores — Entrega 4 | Lenguaje fuente → TypeScript

Implementa cinco reglas semánticas sobre el NodoArbol producido por el parser:

  REGLA SEM 1 — No redeclaración de identificadores en el mismo ámbito
                Nodos:  <decl_variable>, <def_funcion>, <def_clase>, <decl_atributo>
                Atrib:  id.nombre (sintetizado), id.ambito (heredado del contexto)
                Restr:  id.nombre ∉ tablaSimbolos en el ámbito actual
                Acción: SI ∈ → reportar error con fila/col/lexema

  REGLA SEM 2 — Uso de identificador previamente declarado
                Nodos:  <valor_atomico> → IDENTIFICADOR, <sent_identificador>
                Atrib:  id.tipo (sintetizado desde tablaSimbolos)
                Restr:  id.nombre ∈ tablaSimbolos (búsqueda ascendente)
                Acción: SI ∉ → reportar error

  REGLA SEM 3 — Compatibilidad de tipos en declaración con inicialización
                Nodos:  <decl_variable> con <inicializacion_opt> ≠ ε
                Atrib:  decl.tipo (heredado de <tipo>), expr.tipo (sintetizado)
                Restr:  decl.tipo compatible con expr.tipo
                Acción: SI incompatible → reportar error

  REGLA SEM 4 — Tipo de retorno compatible con la función contenedora
                Nodo:   <sent_retornar>
                Atrib:  expr.tipo (sintetizado), func.tipo_retorno (heredado del contexto)
                Restr:  expr.tipo compatible con func.tipo_retorno
                Acción: SI incompatible → reportar error

  REGLA SEM 5 — Función o clase invocada debe estar declarada
                Nodos:  <valor_atomico> → IDENTIFICADOR (con sufijo '('), nuevo IDENTIFICADOR
                        <sent_identificador> → IDENTIFICADOR (con cont '(')
                Atrib:  func.nombre (sintetizado), func.entrada (desde tablaSimbolos)
                Restr:  func.nombre ∈ tablaSimbolos
                Acción: SI ∉ → reportar error
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from sintactico.ArbolSintactico import NodoArbol
from semantico.TablaSimbolos import TablaSimbolos, EntradaSimbolo
from semantico.ErrorSemantico import (
    ErrorSemantico,
    ResultadoSemantico,
    TIPO_DOBLE_DECLARACION,
    TIPO_NO_DECLARADO,
    TIPO_INCOMPATIBLE,
    TIPO_RETORNO_INCOMP,
    TIPO_LLAMADA_NO_DECL,
)

# Tipos numéricos mutuamente compatibles (entero ↔ real)
_NUMERICOS = frozenset({"entero", "real"})


def _tipos_compatibles(t1: Optional[str], t2: Optional[str]) -> bool:
    """
    Verdadero si t1 y t2 son tipos asignables entre sí.

    Reglas de compatibilidad:
      - Tipos iguales → compatibles
      - entero / real entre sí → compatibles (ambos son 'number' en TypeScript)
      - None (desconocido) → no reportar error (beneficio de la duda)
    """
    if t1 is None or t2 is None:
        return True
    if t1 == t2:
        return True
    if t1 in _NUMERICOS and t2 in _NUMERICOS:
        return True
    return False


# ── Analizador principal ──────────────────────────────────────────────────────

class AnalizadorSemantico:
    """
    Recorre el árbol sintáctico (NodoArbol) de las entregas anteriores
    y aplica las 5 reglas semánticas definidas.

    Uso:
        analizador = AnalizadorSemantico()
        resultado  = analizador.analizar(arbol)
    """

    def __init__(self):
        self.tabla = TablaSimbolos()
        self._errores: List[ErrorSemantico]  = []
        # Contexto heredado para REGLA 4
        self._tipo_retorno_actual: Optional[str] = None
        self._nombre_funcion_actual: Optional[str] = None

    # ── API pública ───────────────────────────────────────────────────────────

    def analizar(self, arbol: Optional[NodoArbol]) -> ResultadoSemantico:
        """
        Punto de entrada: recibe el árbol del parser y produce el resultado.

        Siempre termina (nunca lanza excepción), incluso con un árbol parcial.
        """
        self.tabla = TablaSimbolos()
        self._errores = []
        self._tipo_retorno_actual = None
        self._nombre_funcion_actual = None

        if arbol is not None:
            self._visitar(arbol)

        _numerar_errores(self._errores)
        return ResultadoSemantico(
            valido=len(self._errores) == 0,
            errores=list(self._errores),
            tabla=self.tabla,
        )

    # ── Núcleo del visitor ────────────────────────────────────────────────────

    def _visitar(self, nodo: Optional[NodoArbol]) -> Optional[str]:
        """
        Despacha el nodo al visitador especializado o al genérico.
        Retorna el tipo inferido del nodo (útil para expresiones).
        """
        if nodo is None:
            return None

        # Terminal: inferir tipo si es literal/identificador
        if nodo.es_terminal:
            return self._tipo_de_terminal(nodo)

        simbolo = nodo.simbolo
        if simbolo.startswith("<") and simbolo.endswith(">"):
            nombre_nt = simbolo[1:-1].replace("-", "_")
            metodo    = getattr(self, f"_visitar_{nombre_nt}", self._visitar_generico)
            return metodo(nodo)

        return None

    def _visitar_generico(self, nodo: NodoArbol) -> Optional[str]:
        """
        Visitador de respaldo: recorre todos los hijos en orden.
        Retorna el primer tipo no-None que produzca algún hijo
        (necesario para propagar tipos a través de la jerarquía de expresiones).
        """
        tipo_resultado: Optional[str] = None
        for hijo in nodo.hijos:
            tipo = self._visitar(hijo)
            if tipo_resultado is None and tipo is not None:
                tipo_resultado = tipo
        return tipo_resultado

    # ── REGLA SEM 1+3 — Declaración de variable ──────────────────────────────

    def _visitar_decl_variable(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 1: id.nombre ∉ tabla en el ámbito actual.
        REGLA SEM 3: tipo_declarado compatible con tipo_expresión_init.

        Producción: var IDENTIFICADOR : <tipo> <inicializacion_opt>
        Índices:     [0]  [1]           [2] [3]   [4]
        """
        if len(nodo.hijos) < 5:
            self._visitar_generico(nodo)
            return None

        id_nodo    = nodo.hijos[1]   # IDENTIFICADOR
        tipo_nodo  = nodo.hijos[3]   # <tipo>
        init_nodo  = nodo.hijos[4]   # <inicializacion_opt>

        nombre         = id_nodo.token.lexema  if id_nodo.token  else "?"
        fila           = id_nodo.token.fila    if id_nodo.token  else 0
        col            = id_nodo.token.columna if id_nodo.token  else 0
        tipo_declarado = self._extraer_tipo(tipo_nodo)

        # ── REGLA SEM 3: evaluar expresión ANTES de registrar la variable ──
        # (para que la variable no se vea a sí misma en su propia init)
        tipo_init = self._inferir_tipo_init(init_nodo)

        # ── REGLA SEM 1 ────────────────────────────────────────────────────
        existente = self.tabla.buscar_local(nombre)
        if existente is not None:
            self._registrar_error(
                tipo_error=TIPO_DOBLE_DECLARACION,
                mensaje=(
                    f"La variable '{nombre}' ya fue declarada en el ámbito "
                    f"'{self.tabla.ambito_actual}'"
                ),
                lexema=nombre, fila=fila, col=col,
                sugerencia=(
                    f"Renombra la segunda declaración o elimina la duplicada. "
                    f"Primera declaración en L{existente.fila}:C{existente.columna}."
                ),
            )
        else:
            self.tabla.declarar(EntradaSimbolo(
                nombre=nombre, categoria="variable", tipo=tipo_declarado,
                ambito=self.tabla.ambito_actual, fila=fila, columna=col,
                inicializado=not self._es_epsilon_nodo(init_nodo),
            ))

        # ── REGLA SEM 3: comparar tipos ────────────────────────────────────
        if tipo_init is not None and tipo_declarado not in ("desconocido",):
            if not _tipos_compatibles(tipo_declarado, tipo_init):
                err_fila = fila
                err_col  = col
                # Intentar reportar en la posición del '='
                if init_nodo.hijos and init_nodo.hijos[0].token:
                    err_fila = init_nodo.hijos[0].token.fila
                    err_col  = init_nodo.hijos[0].token.columna
                self._registrar_error(
                    tipo_error=TIPO_INCOMPATIBLE,
                    mensaje=(
                        f"Tipo incompatible: '{nombre}' se declaró como '{tipo_declarado}' "
                        f"pero la expresión de inicialización es de tipo '{tipo_init}'"
                    ),
                    lexema=nombre, fila=err_fila, col=err_col,
                    sugerencia=(
                        f"Asigna una expresión de tipo '{tipo_declarado}' "
                        f"o cambia el tipo declarado a '{tipo_init}'."
                    ),
                )

        return tipo_declarado

    # ── REGLA SEM 1 — Declaración de atributo de clase ───────────────────────

    def _visitar_decl_atributo(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 1: atributo duplicado dentro de la misma clase.

        Producción: IDENTIFICADOR : <tipo> <inicializacion_opt>
        Índices:    [0]             [1] [2]  [3]
        """
        if len(nodo.hijos) < 4:
            self._visitar_generico(nodo)
            return None

        id_nodo    = nodo.hijos[0]
        tipo_nodo  = nodo.hijos[2]
        init_nodo  = nodo.hijos[3]

        nombre         = id_nodo.token.lexema  if id_nodo.token  else "?"
        fila           = id_nodo.token.fila    if id_nodo.token  else 0
        col            = id_nodo.token.columna if id_nodo.token  else 0
        tipo_declarado = self._extraer_tipo(tipo_nodo)

        # ── REGLA SEM 1 ────────────────────────────────────────────────────
        existente = self.tabla.buscar_local(nombre)
        if existente is not None:
            self._registrar_error(
                tipo_error=TIPO_DOBLE_DECLARACION,
                mensaje=(
                    f"El atributo '{nombre}' ya fue declarado en la clase "
                    f"'{self.tabla.ambito_actual}'"
                ),
                lexema=nombre, fila=fila, col=col,
                sugerencia="Renombra el atributo o elimina la declaración duplicada.",
            )
        else:
            self.tabla.declarar(EntradaSimbolo(
                nombre=nombre, categoria="atributo", tipo=tipo_declarado,
                ambito=self.tabla.ambito_actual, fila=fila, columna=col,
                inicializado=not self._es_epsilon_nodo(init_nodo),
            ))

        # Visitar init para detectar errores en ella (sin hacer type-check de atributo)
        self._inferir_tipo_init(init_nodo)
        return tipo_declarado

    # ── REGLA SEM 1 — Declaración de función ─────────────────────────────────

    def _visitar_def_funcion(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 1: función duplicada en el mismo ámbito.
        Gestiona el ámbito y el tipo_retorno heredado para REGLA SEM 4.

        Producción: funcion IDENTIFICADOR ( <parametros> ) <tipo_retorno_opt> <bloque> fin_funcion
        Índices:    [0]     [1]             [2] [3]         [4] [5]            [6]      [7]
        """
        if len(nodo.hijos) < 8:
            self._visitar_generico(nodo)
            return None

        id_nodo      = nodo.hijos[1]   # IDENTIFICADOR
        params_nodo  = nodo.hijos[3]   # <parametros>
        retorno_nodo = nodo.hijos[5]   # <tipo_retorno_opt>
        bloque_nodo  = nodo.hijos[6]   # <bloque>

        nombre       = id_nodo.token.lexema  if id_nodo.token  else "?"
        fila         = id_nodo.token.fila    if id_nodo.token  else 0
        col          = id_nodo.token.columna if id_nodo.token  else 0
        params       = self._extraer_lista_params(params_nodo)
        tipo_retorno = self._extraer_tipo_retorno_opt(retorno_nodo)

        # ── REGLA SEM 1 ────────────────────────────────────────────────────
        existente = self.tabla.buscar_local(nombre)
        if existente is not None:
            self._registrar_error(
                tipo_error=TIPO_DOBLE_DECLARACION,
                mensaje=(
                    f"La función '{nombre}' ya fue declarada en el ámbito "
                    f"'{self.tabla.ambito_actual}'"
                ),
                lexema=nombre, fila=fila, col=col,
                sugerencia=(
                    f"Renombra la función o elimina la declaración duplicada. "
                    f"Primera declaración en L{existente.fila}:C{existente.columna}."
                ),
            )
        else:
            self.tabla.declarar(EntradaSimbolo(
                nombre=nombre, categoria="funcion", tipo="funcion",
                ambito=self.tabla.ambito_actual, fila=fila, columna=col,
                inicializado=True, tipo_retorno=tipo_retorno, parametros=params,
            ))

        # Entrar al ámbito de la función
        prev_retorno = self._tipo_retorno_actual
        prev_func    = self._nombre_funcion_actual
        self._tipo_retorno_actual   = tipo_retorno
        self._nombre_funcion_actual = nombre

        self.tabla.entrar_ambito(nombre)

        # Registrar parámetros como variables en el nuevo ámbito
        for p_nombre, p_tipo in params:
            if not self.tabla.declarar(EntradaSimbolo(
                nombre=p_nombre, categoria="parametro", tipo=p_tipo,
                ambito=self.tabla.ambito_actual, fila=fila, columna=col,
                inicializado=True,
            )):
                # Parámetro duplicado
                self._registrar_error(
                    tipo_error=TIPO_DOBLE_DECLARACION,
                    mensaje=f"El parámetro '{p_nombre}' está duplicado en la función '{nombre}'",
                    lexema=p_nombre, fila=fila, col=col,
                    sugerencia="Usa nombres distintos para cada parámetro.",
                )

        # Visitar el bloque (donde se aplicará REGLA 4 en cada sent_retornar)
        self._visitar(bloque_nodo)

        self.tabla.salir_ambito()
        self._tipo_retorno_actual   = prev_retorno
        self._nombre_funcion_actual = prev_func

        return None

    # ── REGLA SEM 1 — Declaración de clase ───────────────────────────────────

    def _visitar_def_clase(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 1: clase duplicada en el mismo ámbito.

        Producción: clase IDENTIFICADOR <herencia_opt> <lista_miembros> fin_clase
        Índices:    [0]   [1]            [2]            [3]              [4]
        """
        if len(nodo.hijos) < 5:
            self._visitar_generico(nodo)
            return None

        id_nodo       = nodo.hijos[1]
        miembros_nodo = nodo.hijos[3]

        nombre = id_nodo.token.lexema  if id_nodo.token  else "?"
        fila   = id_nodo.token.fila    if id_nodo.token  else 0
        col    = id_nodo.token.columna if id_nodo.token  else 0

        # ── REGLA SEM 1 ────────────────────────────────────────────────────
        existente = self.tabla.buscar_local(nombre)
        if existente is not None:
            self._registrar_error(
                tipo_error=TIPO_DOBLE_DECLARACION,
                mensaje=(
                    f"La clase '{nombre}' ya fue declarada en el ámbito "
                    f"'{self.tabla.ambito_actual}'"
                ),
                lexema=nombre, fila=fila, col=col,
                sugerencia="Renombra la clase o elimina la declaración duplicada.",
            )
        else:
            self.tabla.declarar(EntradaSimbolo(
                nombre=nombre, categoria="clase", tipo="clase",
                ambito=self.tabla.ambito_actual, fila=fila, columna=col,
                inicializado=True,
            ))

        self.tabla.entrar_ambito(nombre)
        self._visitar(miembros_nodo)
        self.tabla.salir_ambito()

        return None

    # ── REGLA SEM 1/2 — Sentencia para (ciclo for) ───────────────────────────

    def _visitar_sent_para(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 1: variable de iteración no redeclarada en el mismo ámbito.
        REGLA SEM 2: registra la variable de iteración para que su uso en el
                     bloque del ciclo no genere un falso error de 'no declarada'.

        Producción: para IDENTIFICADOR desde <expresion> hasta <expresion>
                    [0]  [1]            [2]   [3]          [4]   [5]
                    <paso_opt> hacer <bloque> fin_para
                    [6]        [7]   [8]      [9]

        Atributo sintetizado: id.nombre, id.tipo (siempre 'entero').
        Atributo heredado:    id.ambito (contexto actual de la tabla).
        """
        if len(nodo.hijos) < 9:
            self._visitar_generico(nodo)
            return None

        id_nodo     = nodo.hijos[1]  # IDENTIFICADOR — variable contadora
        expr_desde  = nodo.hijos[3]  # <expresion>   — límite inferior
        expr_hasta  = nodo.hijos[5]  # <expresion>   — límite superior
        paso_nodo   = nodo.hijos[6]  # <paso_opt>
        bloque_nodo = nodo.hijos[8]  # <bloque>      — cuerpo del ciclo

        nombre = id_nodo.token.lexema  if id_nodo.token  else "?"
        fila   = id_nodo.token.fila    if id_nodo.token  else 0
        col    = id_nodo.token.columna if id_nodo.token  else 0

        # ── REGLA SEM 1: verificar que no esté ya declarada en este ámbito ──
        existente = self.tabla.buscar_local(nombre)
        if existente is not None:
            self._registrar_error(
                tipo_error=TIPO_DOBLE_DECLARACION,
                mensaje=(
                    f"La variable de iteración '{nombre}' ya fue declarada "
                    f"en el ámbito '{self.tabla.ambito_actual}'"
                ),
                lexema=nombre, fila=fila, col=col,
                sugerencia=(
                    f"Usa un nombre diferente para la variable del 'para'. "
                    f"Primera declaración en L{existente.fila}:C{existente.columna}."
                ),
            )
        else:
            # Registrar la variable contadora como tipo 'entero'
            # (los rangos desde/hasta siempre son enteros en este lenguaje)
            self.tabla.declarar(EntradaSimbolo(
                nombre=nombre, categoria="variable", tipo="entero",
                ambito=self.tabla.ambito_actual, fila=fila, columna=col,
                inicializado=True,
            ))

        # Visitar expresiones de rango y paso para detectar errores dentro de ellos
        self._visitar(expr_desde)
        self._visitar(expr_hasta)
        self._visitar(paso_nodo)

        # Visitar el bloque del cuerpo del ciclo
        # (la variable de iteración ya está registrada, no habrá falso REGLA 2)
        self._visitar(bloque_nodo)

        return None

    # ── REGLA SEM 4 — Sentencia retornar ─────────────────────────────────────

    def _visitar_sent_retornar(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 4: tipo de la expresión retornada compatible con
        el tipo de retorno declarado de la función contenedora.

        Producción: retornar <expresion_opt>
        Índices:    [0]      [1]
        """
        if len(nodo.hijos) < 2:
            return None

        retornar_nodo = nodo.hijos[0]   # terminal 'retornar'
        expr_opt      = nodo.hijos[1]   # <expresion_opt>

        fila = retornar_nodo.token.fila    if retornar_nodo.token else 0
        col  = retornar_nodo.token.columna if retornar_nodo.token else 0

        tipo_expr = self._inferir_tipo_expresion_opt(expr_opt)

        # ── REGLA SEM 4 ────────────────────────────────────────────────────
        tipo_esperado = self._tipo_retorno_actual
        if tipo_esperado is not None and tipo_expr is not None:
            if not _tipos_compatibles(tipo_esperado, tipo_expr):
                func = self._nombre_funcion_actual or "la función"
                self._registrar_error(
                    tipo_error=TIPO_RETORNO_INCOMP,
                    mensaje=(
                        f"Tipo de retorno incompatible en '{func}': "
                        f"se declaró retornar '{tipo_esperado}' "
                        f"pero la expresión es de tipo '{tipo_expr}'"
                    ),
                    lexema="retornar", fila=fila, col=col,
                    sugerencia=(
                        f"Cambia la expresión de retorno para que sea de tipo '{tipo_esperado}', "
                        f"o modifica el tipo de retorno declarado de la función."
                    ),
                )

        return tipo_expr

    # ── REGLAS SEM 2+5 — Valor atómico (expresiones) ─────────────────────────

    def _visitar_valor_atomico(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 2: variable usada debe estar declarada.
        REGLA SEM 5: función/clase invocada debe estar declarada.

        Producciones del no-terminal:
          NUMERO_ENTERO | NUMERO_REAL | CADENA_LITERAL | verdadero | falso | nulo
          nuevo IDENTIFICADOR ( <argumentos> )
          este . IDENTIFICADOR <sufijo_valor_atomico>
          IDENTIFICADOR <sufijo_valor_atomico>
          ( <expresion> )
        """
        if not nodo.hijos:
            return None

        primer = nodo.hijos[0]

        # ── Literales directos ──────────────────────────────────────────────
        if primer.simbolo == "NUMERO_ENTERO":   return "entero"
        if primer.simbolo == "NUMERO_REAL":     return "real"
        if primer.simbolo == "CADENA_LITERAL":  return "cadena"
        if primer.simbolo in ("verdadero", "falso"): return "booleano"
        if primer.simbolo == "nulo":            return "nulo"

        # ── ( <expresion> ) ─────────────────────────────────────────────────
        if primer.simbolo == "(":
            expr = nodo.hijos[1] if len(nodo.hijos) >= 2 else None
            return self._visitar(expr)

        # ── nuevo IDENTIFICADOR ( <argumentos> ) ────────────────────────────
        if primer.simbolo == "nuevo":
            return self._verificar_instanciacion(nodo)

        # ── este . IDENTIFICADOR <sufijo_valor_atomico> ─────────────────────
        if primer.simbolo == "este":
            # Acceso a miembro propio: no validamos profundamente (nivel básico)
            return None

        # ── IDENTIFICADOR <sufijo_valor_atomico> ────────────────────────────
        if primer.simbolo == "IDENTIFICADOR" and primer.token:
            return self._verificar_identificador_en_expresion(nodo, primer)

        return None

    def _verificar_instanciacion(self, nodo: NodoArbol) -> Optional[str]:
        """nuevo IDENTIFICADOR ( <argumentos> ) — REGLA SEM 5."""
        if len(nodo.hijos) < 2:
            return None
        id_nodo = nodo.hijos[1]
        if not id_nodo.token:
            return None

        nombre = id_nodo.token.lexema
        fila   = id_nodo.token.fila
        col    = id_nodo.token.columna

        entrada = self.tabla.buscar(nombre)
        if entrada is None:
            self._registrar_error(
                tipo_error=TIPO_LLAMADA_NO_DECL,
                mensaje=f"La clase '{nombre}' no ha sido declarada",
                lexema=nombre, fila=fila, col=col,
                sugerencia=(
                    f"Declara la clase '{nombre}' con "
                    f"'clase {nombre} ... fin_clase' antes de instanciarla."
                ),
            )
            return None

        # Visitar argumentos para detectar errores dentro de ellos
        if len(nodo.hijos) >= 4:
            self._visitar(nodo.hijos[3])  # <argumentos>
        return nombre   # el tipo de 'nuevo Animal(...)' es 'Animal'

    def _verificar_identificador_en_expresion(
        self,
        nodo: NodoArbol,
        id_nodo: NodoArbol,
    ) -> Optional[str]:
        """
        Maneja IDENTIFICADOR <sufijo_valor_atomico> en el contexto de expresión.
        Aplica REGLA 2 (variable no declarada) o REGLA 5 (función no declarada).
        """
        nombre = id_nodo.token.lexema   # type: ignore[union-attr]
        fila   = id_nodo.token.fila     # type: ignore[union-attr]
        col    = id_nodo.token.columna  # type: ignore[union-attr]

        sufijo     = nodo.hijos[1] if len(nodo.hijos) > 1 else None
        es_llamada = self._sufijo_es_llamada(sufijo)

        if es_llamada:
            # ── REGLA SEM 5 ──────────────────────────────────────────────
            entrada = self.tabla.buscar(nombre)
            if entrada is None:
                self._registrar_error(
                    tipo_error=TIPO_LLAMADA_NO_DECL,
                    mensaje=f"La función '{nombre}' no ha sido declarada",
                    lexema=nombre, fila=fila, col=col,
                    sugerencia=(
                        f"Declara la función '{nombre}' con "
                        f"'funcion {nombre}(...) ... fin_funcion' antes de llamarla."
                    ),
                )
                # Visitar argumentos igualmente para detectar más errores
                if sufijo and len(sufijo.hijos) >= 2:
                    self._visitar(sufijo.hijos[1])
                return None

            # Visitar argumentos para detectar errores dentro de ellos
            if sufijo and len(sufijo.hijos) >= 2:
                self._visitar(sufijo.hijos[1])
            return entrada.tipo_retorno if entrada.categoria == "funcion" else entrada.tipo

        else:
            # ── REGLA SEM 2 ──────────────────────────────────────────────
            entrada = self.tabla.buscar(nombre)
            if entrada is None:
                self._registrar_error(
                    tipo_error=TIPO_NO_DECLARADO,
                    mensaje=f"La variable '{nombre}' no ha sido declarada",
                    lexema=nombre, fila=fila, col=col,
                    sugerencia=(
                        f"Declara la variable '{nombre}' con "
                        f"'var {nombre}: <tipo>' antes de usarla."
                    ),
                )
                return None
            return entrada.tipo

    # ── REGLAS SEM 2+3+5 — Sentencia identificador (asignación/llamada) ───────

    def _visitar_sent_identificador(self, nodo: NodoArbol) -> Optional[str]:
        """
        REGLA SEM 2: el identificador al que se asigna debe estar declarado.
        REGLA SEM 3: tipo de la expresión asignada debe ser compatible.
        REGLA SEM 5: si es llamada, la función debe estar declarada.

        Producciones:
          IDENTIFICADOR <sent_identificador_cont>
          este . IDENTIFICADOR <sent_post_punto>
        """
        if not nodo.hijos:
            return None

        primer = nodo.hijos[0]

        # este . IDENTIFICADOR … — no validamos profundamente
        if primer.simbolo == "este":
            # Visitar la parte de la expresión si existe
            if len(nodo.hijos) >= 4:
                self._visitar(nodo.hijos[3])
            return None

        if primer.simbolo != "IDENTIFICADOR" or not primer.token:
            return self._visitar_generico(nodo)

        nombre = primer.token.lexema
        fila   = primer.token.fila
        col    = primer.token.columna
        entrada = self.tabla.buscar(nombre)

        cont = nodo.hijos[1] if len(nodo.hijos) > 1 else None
        if cont is None or not cont.hijos:
            # No hay continuación — solo verificar que existe (REGLA 2)
            if entrada is None:
                self._registrar_error(
                    tipo_error=TIPO_NO_DECLARADO,
                    mensaje=f"El identificador '{nombre}' no ha sido declarado",
                    lexema=nombre, fila=fila, col=col,
                    sugerencia=f"Declara '{nombre}' antes de usarlo.",
                )
            return None

        prim_cont = cont.hijos[0]

        # ── Asignación: = <expresion> ────────────────────────────────────────
        if prim_cont.simbolo == "=":
            # ── REGLA SEM 2 ────────────────────────────────────────────────
            if entrada is None:
                self._registrar_error(
                    tipo_error=TIPO_NO_DECLARADO,
                    mensaje=f"El identificador '{nombre}' no ha sido declarado",
                    lexema=nombre, fila=fila, col=col,
                    sugerencia=f"Declara '{nombre}' con 'var {nombre}: <tipo>' antes de asignarle.",
                )

            expr_nodo = cont.hijos[1] if len(cont.hijos) > 1 else None
            tipo_expr = self._visitar(expr_nodo) if expr_nodo else None

            # ── REGLA SEM 3 ────────────────────────────────────────────────
            if (
                entrada is not None
                and tipo_expr is not None
                and entrada.tipo not in ("funcion", "clase")
            ):
                if not _tipos_compatibles(entrada.tipo, tipo_expr):
                    self._registrar_error(
                        tipo_error=TIPO_INCOMPATIBLE,
                        mensaje=(
                            f"Tipo incompatible en asignación: '{nombre}' es de tipo "
                            f"'{entrada.tipo}' pero la expresión es de tipo '{tipo_expr}'"
                        ),
                        lexema=nombre, fila=fila, col=col,
                        sugerencia=f"Asigna una expresión de tipo '{entrada.tipo}'.",
                    )

        # ── Llamada a función como sentencia: ( <argumentos> ) ──────────────
        elif prim_cont.simbolo == "(":
            # ── REGLA SEM 5 ────────────────────────────────────────────────
            if entrada is None:
                self._registrar_error(
                    tipo_error=TIPO_LLAMADA_NO_DECL,
                    mensaje=f"La función '{nombre}' no ha sido declarada",
                    lexema=nombre, fila=fila, col=col,
                    sugerencia=(
                        f"Declara la función '{nombre}' con "
                        f"'funcion {nombre}(...) ... fin_funcion' antes de llamarla."
                    ),
                )
            # Visitar argumentos para detectar errores en ellos
            if len(cont.hijos) >= 2:
                self._visitar(cont.hijos[1])

        # ── Acceso a miembro: . IDENTIFICADOR <sent_post_punto> ─────────────
        else:
            self._visitar(cont)

        return None

    # ── Helpers de extracción ─────────────────────────────────────────────────

    def _extraer_tipo(self, nodo_tipo: Optional[NodoArbol]) -> str:
        """
        Extrae el string de tipo de un nodo <tipo>.

        <tipo> → entero | real | cadena | booleano | IDENTIFICADOR
        El atributo es sintetizado: se toma directamente del terminal hijo.
        """
        if nodo_tipo is None or not nodo_tipo.hijos:
            return "desconocido"
        hijo = nodo_tipo.hijos[0]
        if hijo.token:
            return hijo.token.lexema
        return hijo.simbolo

    def _extraer_tipo_retorno_opt(self, nodo: Optional[NodoArbol]) -> Optional[str]:
        """
        Extrae el tipo de retorno de <tipo_retorno_opt> (: <tipo>) | ε.

        Retorna None si la producción es ε (función void).
        """
        if nodo is None or not nodo.hijos:
            return None
        primer = nodo.hijos[0]
        if self._es_epsilon_nodo(primer):
            return None
        # : <tipo>  →  hijos[0]=":", hijos[1]=<tipo>
        if len(nodo.hijos) >= 2:
            return self._extraer_tipo(nodo.hijos[1])
        return None

    def _extraer_lista_params(self, nodo_params: Optional[NodoArbol]) -> List[Tuple[str, str]]:
        """
        Extrae [(nombre, tipo)] de un nodo <parametros>.

        <parametros> → <param_lista> | ε
        """
        resultado: List[Tuple[str, str]] = []
        if nodo_params is None or not nodo_params.hijos:
            return resultado
        if self._es_epsilon_nodo(nodo_params.hijos[0]):
            return resultado
        self._recolectar_params(nodo_params.hijos[0], resultado)
        return resultado

    def _recolectar_params(
        self,
        nodo: Optional[NodoArbol],
        resultado: List[Tuple[str, str]],
    ) -> None:
        """Recorre recursivamente <param_lista> y <param_lista_cont>."""
        if nodo is None or not nodo.hijos:
            return

        simbolo = nodo.simbolo

        if simbolo == "<param_lista>":
            if nodo.hijos:
                self._recolectar_params(nodo.hijos[0], resultado)   # <param>
            if len(nodo.hijos) > 1:
                self._recolectar_params(nodo.hijos[1], resultado)   # <param_lista_cont>

        elif simbolo == "<param>":
            # IDENTIFICADOR : <tipo>
            if len(nodo.hijos) >= 3:
                id_n   = nodo.hijos[0]
                tipo_n = nodo.hijos[2]
                nombre = id_n.token.lexema if id_n.token else "?"
                tipo   = self._extraer_tipo(tipo_n)
                resultado.append((nombre, tipo))

        elif simbolo == "<param_lista_cont>":
            # , <param> <param_lista_cont> | ε
            if nodo.hijos and not self._es_epsilon_nodo(nodo.hijos[0]):
                if len(nodo.hijos) >= 3:
                    self._recolectar_params(nodo.hijos[1], resultado)   # <param>
                    self._recolectar_params(nodo.hijos[2], resultado)   # <param_lista_cont>

    def _es_epsilon_nodo(self, nodo: Optional[NodoArbol]) -> bool:
        """Verdadero si el nodo es el terminal épsilon (ε)."""
        return nodo is not None and nodo.es_terminal and nodo.simbolo == "ε"

    def _sufijo_es_llamada(self, nodo_sufijo: Optional[NodoArbol]) -> bool:
        """Verdadero si <sufijo_valor_atomico> comienza con '(' (es llamada a función)."""
        if nodo_sufijo is None or not nodo_sufijo.hijos:
            return False
        primer = nodo_sufijo.hijos[0]
        if self._es_epsilon_nodo(primer):
            return False
        return primer.simbolo == "("

    # ── Inferencia de tipos en expresiones ───────────────────────────────────

    def _inferir_tipo_init(self, nodo: Optional[NodoArbol]) -> Optional[str]:
        """
        Infiere el tipo de <inicializacion_opt> (= <expresion> | ε).

        Retorna None si es epsilon (sin inicialización).
        La visita propaga errores (REGLA 2, 5) dentro de la expresión.
        """
        if nodo is None or not nodo.hijos:
            return None
        if self._es_epsilon_nodo(nodo.hijos[0]):
            return None
        # = <expresion>  →  hijos[0]="=", hijos[1]=<expresion>
        if len(nodo.hijos) >= 2:
            return self._visitar(nodo.hijos[1])
        return None

    def _inferir_tipo_expresion_opt(self, nodo: Optional[NodoArbol]) -> Optional[str]:
        """
        Infiere el tipo de <expresion_opt> (<expresion> | ε).

        Retorna None si es epsilon (retornar sin expresión).
        """
        if nodo is None or not nodo.hijos:
            return None
        if self._es_epsilon_nodo(nodo.hijos[0]):
            return None
        return self._visitar(nodo.hijos[0])

    def _tipo_de_terminal(self, nodo: NodoArbol) -> Optional[str]:
        """
        Retorna el tipo semántico de un nodo terminal.

        Para literales, el tipo es fijo (sintetizado desde el lexema).
        Para IDENTIFICADOR, se consulta la tabla de símbolos (heredado del entorno).
        """
        s = nodo.simbolo
        if s == "NUMERO_ENTERO":              return "entero"
        if s == "NUMERO_REAL":                return "real"
        if s == "CADENA_LITERAL":             return "cadena"
        if s in ("verdadero", "falso"):       return "booleano"
        if s == "nulo":                       return "nulo"
        if s == "IDENTIFICADOR" and nodo.token:
            entrada = self.tabla.buscar(nodo.token.lexema)
            return entrada.tipo if entrada else None
        return None

    # ── Registro de errores ───────────────────────────────────────────────────

    def _registrar_error(
        self,
        tipo_error: str,
        mensaje:    str,
        lexema:     str,
        fila:       int,
        col:        int,
        sugerencia: str = "",
    ) -> None:
        """Agrega un ErrorSemantico evitando duplicados en la misma posición y tipo."""
        for e in self._errores:
            if e.fila == fila and e.columna == col and e.tipo_error == tipo_error:
                return
        self._errores.append(ErrorSemantico(
            mensaje=mensaje, fila=fila, columna=col,
            lexema=lexema, tipo_error=tipo_error, sugerencia=sugerencia,
        ))


# ── Utilidad interna ──────────────────────────────────────────────────────────

def _numerar_errores(errores: List[ErrorSemantico]) -> None:
    """Asigna número secuencial (1-based) a cada error."""
    for i, e in enumerate(errores, start=1):
        e.numero = i

"""
lexer.py — Analizador léxico reutilizable
Compiladores — Entrega 1 | Lenguaje fuente → TypeScript

Uso:
    from lexer import Lexer
    lex = Lexer(codigo_fuente)
    tokens, errores = lex.tokenizar()
"""

from tokens import Token, TokenType, PALABRAS_RESERVADAS


class ErrorLexico:
    """Representa un error léxico con posición y descripción."""

    def __init__(self, mensaje: str, fila: int, columna: int):
        self.mensaje = mensaje
        self.fila    = fila
        self.columna = columna

    def __repr__(self) -> str:
        return f"ErrorLexico(fila={self.fila}, col={self.columna}: {self.mensaje})"


class Lexer:
    """
    Analizador léxico del lenguaje fuente.

    Diseñado para ser independiente del parser — se puede importar
    directamente en entregas futuras sin modificaciones.

    Parámetros
    ----------
    fuente : str
        Código fuente completo a tokenizar.

    Resultado de tokenizar()
    ------------------------
    tokens  : list[Token]       — lista de tokens reconocidos
    errores : list[ErrorLexico] — errores encontrados (análisis continúa)
    """

    # Caracteres válidos en identificadores además de letras y dígitos
    LETRAS_VALIDAS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
                         "áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöüÄËÏÖÜñÑ")
    DIGITOS        = set("0123456789")

    def __init__(self, fuente: str):
        self.fuente  = fuente
        self.pos     = 0          # posición actual en la cadena
        self.fila    = 1          # fila actual (base 1)
        self.columna = 1          # columna actual (base 1)
        self._tokens : list[Token]       = []
        self._errores: list[ErrorLexico] = []

    # ─────────────────────────────────────────────────────────────────
    # API pública
    # ─────────────────────────────────────────────────────────────────

    def tokenizar(self) -> tuple[list[Token], list[ErrorLexico]]:
        """Recorre toda la fuente y devuelve (tokens, errores)."""
        while not self._fin():
            self._saltar_espacios_y_comentarios()
            if self._fin():
                break
            self._siguiente_token()

        self._tokens.append(
            Token(TokenType.EOF, "", self.fila, self.columna)
        )
        return self._tokens, self._errores

    # ─────────────────────────────────────────────────────────────────
    # Helpers de navegación
    # ─────────────────────────────────────────────────────────────────

    def _fin(self) -> bool:
        """Verdadero si se consumió toda la entrada."""
        return self.pos >= len(self.fuente)

    def _actual(self) -> str:
        """Carácter en la posición actual."""
        return self.fuente[self.pos] if not self._fin() else ""

    def _siguiente(self) -> str:
        """Carácter siguiente sin avanzar (lookahead 1)."""
        return self.fuente[self.pos + 1] if self.pos + 1 < len(self.fuente) else ""

    def _avanzar(self) -> str:
        """Consume el carácter actual y actualiza fila/columna."""
        c = self.fuente[self.pos]
        self.pos += 1
        if c == "\n":
            self.fila    += 1
            self.columna  = 1
        else:
            self.columna += 1
        return c

    # ─────────────────────────────────────────────────────────────────
    # Espacios y comentarios
    # ─────────────────────────────────────────────────────────────────

    def _saltar_espacios_y_comentarios(self):
        """Avanza sobre espacios en blanco y comentarios // y /* */."""
        while not self._fin():
            c = self._actual()

            # Espacios en blanco y saltos de línea
            if c in " \t\r\n":
                self._avanzar()

            # Comentario de línea //
            elif c == "/" and self._siguiente() == "/":
                while not self._fin() and self._actual() != "\n":
                    self._avanzar()

            # Comentario de bloque /* … */
            elif c == "/" and self._siguiente() == "*":
                fila_inicio = self.fila
                col_inicio  = self.columna
                self._avanzar()  # /
                self._avanzar()  # *
                cerrado = False
                while not self._fin():
                    if self._actual() == "*" and self._siguiente() == "/":
                        self._avanzar()  # *
                        self._avanzar()  # /
                        cerrado = True
                        break
                    self._avanzar()
                if not cerrado:
                    self._errores.append(ErrorLexico(
                        f"Comentario de bloque abierto en fila {fila_inicio}, "
                        f"columna {col_inicio} sin '*/' de cierre.",
                        fila_inicio, col_inicio
                    ))
            else:
                break

    # ─────────────────────────────────────────────────────────────────
    # Despacho principal
    # ─────────────────────────────────────────────────────────────────

    def _siguiente_token(self):
        """Reconoce y retorna el siguiente token desde la posición actual."""
        fila = self.fila
        col  = self.columna
        c    = self._actual()

        # Números
        if c in self.DIGITOS:
            self._leer_numero(fila, col)

        # Cadenas de texto
        elif c == '"':
            self._leer_cadena(fila, col)

        # Identificadores y palabras reservadas
        elif c in self.LETRAS_VALIDAS:
            self._leer_identificador(fila, col)

        # Operadores de dos caracteres primero
        elif c == "=" and self._siguiente() == "=":
            self._avanzar(); self._avanzar()
            self._agregar(TokenType.IGUAL, "==", fila, col)

        elif c == "!" and self._siguiente() == "=":
            self._avanzar(); self._avanzar()
            self._agregar(TokenType.DISTINTO, "!=", fila, col)

        elif c == "<" and self._siguiente() == "=":
            self._avanzar(); self._avanzar()
            self._agregar(TokenType.MENOR_IGUAL, "<=", fila, col)

        elif c == ">" and self._siguiente() == "=":
            self._avanzar(); self._avanzar()
            self._agregar(TokenType.MAYOR_IGUAL, ">=", fila, col)

        # Operadores ajenos al lenguaje — error guiado
        elif c == "&" and self._siguiente() == "&":
            self._avanzar(); self._avanzar()
            self._errores.append(ErrorLexico(
                "Operador '&&' no válido en este lenguaje. Use la palabra reservada 'y'.",
                fila, col
            ))
            self._agregar(TokenType.ERROR, "&&", fila, col)

        elif c == "|" and self._siguiente() == "|":
            self._avanzar(); self._avanzar()
            self._errores.append(ErrorLexico(
                "Operador '||' no válido en este lenguaje. Use la palabra reservada 'o'.",
                fila, col
            ))
            self._agregar(TokenType.ERROR, "||", fila, col)

        elif c == "*" and self._siguiente() == "*":
            self._avanzar(); self._avanzar()
            self._errores.append(ErrorLexico(
                "Operador '**' no válido en este lenguaje. Para potencia use '^'.",
                fila, col
            ))
            self._agregar(TokenType.ERROR, "**", fila, col)

        elif c == "!":
            self._avanzar()
            self._errores.append(ErrorLexico(
                "Operador '!' no válido en este lenguaje. Use la palabra reservada 'no'.",
                fila, col
            ))
            self._agregar(TokenType.ERROR, "!", fila, col)

        # Operadores de un carácter
        elif c == "<":
            self._avanzar()
            self._agregar(TokenType.MENOR, "<", fila, col)

        elif c == ">":
            self._avanzar()
            self._agregar(TokenType.MAYOR, ">", fila, col)

        elif c == "=":
            self._avanzar()
            self._agregar(TokenType.ASIGNACION, "=", fila, col)

        elif c == "+":
            self._avanzar()
            self._agregar(TokenType.SUMA, "+", fila, col)

        elif c == "-":
            self._avanzar()
            self._agregar(TokenType.RESTA, "-", fila, col)

        elif c == "*":
            self._avanzar()
            self._agregar(TokenType.MULT, "*", fila, col)

        elif c == "/":
            self._avanzar()
            self._agregar(TokenType.DIV, "/", fila, col)

        elif c == "%":
            self._avanzar()
            self._agregar(TokenType.MODULO, "%", fila, col)

        elif c == "^":
            self._avanzar()
            self._agregar(TokenType.POTENCIA, "^", fila, col)

        # Delimitadores
        elif c == "(":
            self._avanzar()
            self._agregar(TokenType.PAREN_IZQ, "(", fila, col)

        elif c == ")":
            self._avanzar()
            self._agregar(TokenType.PAREN_DER, ")", fila, col)

        elif c == ",":
            self._avanzar()
            self._agregar(TokenType.COMA, ",", fila, col)

        elif c == ":":
            self._avanzar()
            self._agregar(TokenType.DOS_PUNTOS, ":", fila, col)

        elif c == ".":
            self._avanzar()
            self._agregar(TokenType.PUNTO, ".", fila, col)

        # Carácter no reconocido → error léxico, continúa
        else:
            self._avanzar()
            self._errores.append(ErrorLexico(
                f"Carácter '{c}' no reconocido.", fila, col
            ))
            self._agregar(TokenType.ERROR, c, fila, col)

    # ─────────────────────────────────────────────────────────────────
    # Lectores especializados
    # ─────────────────────────────────────────────────────────────────

    def _leer_numero(self, fila: int, col: int):
        """Lee NUMERO_ENTERO o NUMERO_REAL."""
        inicio = self.pos
        while not self._fin() and self._actual() in self.DIGITOS:
            self._avanzar()

        if not self._fin() and self._actual() == "." and self._siguiente() in self.DIGITOS:
            self._avanzar()  # punto decimal
            while not self._fin() and self._actual() in self.DIGITOS:
                self._avanzar()
            lexema = self.fuente[inicio:self.pos]
            self._agregar(TokenType.NUMERO_REAL, lexema, fila, col)
        else:
            lexema = self.fuente[inicio:self.pos]
            self._agregar(TokenType.NUMERO_ENTERO, lexema, fila, col)

    def _leer_cadena(self, fila: int, col: int):
        """Lee CADENA_LITERAL entre comillas dobles."""
        self._avanzar()  # comilla de apertura
        inicio = self.pos
        cerrada = False

        while not self._fin():
            c = self._actual()
            if c == '"':
                lexema = self.fuente[inicio:self.pos]
                self._avanzar()  # comilla de cierre
                self._agregar(TokenType.CADENA_LITERAL, f'"{lexema}"', fila, col)
                cerrada = True
                break
            if c == "\n":
                # Cadena sin cerrar en esta línea
                break
            self._avanzar()

        if not cerrada:
            lexema = self.fuente[inicio:self.pos]
            self._errores.append(ErrorLexico(
                f"Cadena de texto sin cerrar: \"{lexema}\"", fila, col
            ))
            self._agregar(TokenType.ERROR, f'"{lexema}', fila, col)

    def _leer_identificador(self, fila: int, col: int):
        """Lee IDENTIFICADOR o palabra reservada."""
        inicio = self.pos
        while not self._fin() and (
            self._actual() in self.LETRAS_VALIDAS or
            self._actual() in self.DIGITOS
        ):
            self._avanzar()

        lexema = self.fuente[inicio:self.pos]
        tipo   = PALABRAS_RESERVADAS.get(lexema, TokenType.IDENTIFICADOR)
        self._agregar(tipo, lexema, fila, col)

    # ─────────────────────────────────────────────────────────────────
    # Helper de registro
    # ─────────────────────────────────────────────────────────────────

    def _agregar(self, tipo: TokenType, lexema: str, fila: int, col: int):
        self._tokens.append(Token(tipo, lexema, fila, col))

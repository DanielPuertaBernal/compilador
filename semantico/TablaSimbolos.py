"""
TablaSimbolos.py — Tabla de símbolos con soporte de ámbitos anidados
Compiladores — Entrega 4 | Lenguaje fuente → TypeScript

Estructura:
  EntradaSimbolo  — atributos de un identificador (tipo, categoría, ámbito, posición…)
  AmbitoTabla     — ámbito individual con puntero al padre
  TablaSimbolos   — gestor de pila de ámbitos con API declarar/buscar
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Entrada individual en la tabla ────────────────────────────────────────────

@dataclass
class EntradaSimbolo:
    """
    Registro de un identificador en la tabla de símbolos.

    Atributos sintetizados (calculados en el nodo de declaración):
      nombre, categoria, tipo, ambito, fila, columna, inicializado

    Atributos extra para funciones (sintetizados de sus producciones hijas):
      tipo_retorno, parametros
    """

    nombre:       str               # lexema declarado
    categoria:    str               # "variable" | "funcion" | "clase" | "parametro" | "atributo"
    tipo:         str               # "entero" | "real" | "cadena" | "booleano" | <nombre_clase>
    ambito:       str               # nombre del ámbito donde fue declarado
    fila:         int               # línea de la declaración
    columna:      int               # columna de la declaración
    inicializado: bool = False      # verdadero si tiene inicialización explícita

    # Solo para funciones
    tipo_retorno: Optional[str] = None                      # tipo de retorno declarado
    parametros:   List[Tuple[str, str]] = field(            # [(nombre, tipo), …]
        default_factory=list
    )

    def __str__(self) -> str:
        base = (
            f"{self.categoria:<12} '{self.nombre}' : {self.tipo:<12}"
            f"  @ {self.ambito}  L{self.fila}:C{self.columna}"
        )
        if self.categoria == "funcion":
            p_txt = ", ".join(f"{n}: {t}" for n, t in self.parametros) or "—"
            ret   = self.tipo_retorno or "void"
            base += f"  [{p_txt}] → {ret}"
        return base


# ── Ámbito individual ─────────────────────────────────────────────────────────

class AmbitoTabla:
    """
    Nodo de la jerarquía de ámbitos.

    Cada ámbito conoce a su padre (para la búsqueda ascendente) y mantiene
    una lista de hijos para poder recorrer toda la tabla al renderizarla.
    """

    def __init__(self, nombre: str, padre: Optional[AmbitoTabla] = None):
        self.nombre:   str                       = nombre
        self.padre:    Optional[AmbitoTabla]     = padre
        self.simbolos: Dict[str, EntradaSimbolo] = {}
        self.hijos:    List[AmbitoTabla]         = []

    # ── Declaración ───────────────────────────────────────────────────

    def declarar(self, entrada: EntradaSimbolo) -> bool:
        """
        Registra la entrada en este ámbito.

        Retorna False si el nombre ya existía (sin sobreescribir).
        Atributo sintetizado: la entrada queda almacenada bajo su nombre.
        """
        if entrada.nombre in self.simbolos:
            return False
        self.simbolos[entrada.nombre] = entrada
        return True

    # ── Búsqueda ──────────────────────────────────────────────────────

    def buscar_local(self, nombre: str) -> Optional[EntradaSimbolo]:
        """Busca únicamente en este ámbito (sin ascender)."""
        return self.simbolos.get(nombre)

    def buscar(self, nombre: str) -> Optional[EntradaSimbolo]:
        """
        Búsqueda ascendente: este ámbito → padre → abuelo … → global.

        Atributo heredado: el nombre buscado se propaga hacia los padres
        hasta que se encuentra o se agota la jerarquía.
        """
        resultado = self.buscar_local(nombre)
        if resultado is not None:
            return resultado
        if self.padre is not None:
            return self.padre.buscar(nombre)
        return None


# ── Tabla principal ───────────────────────────────────────────────────────────

class TablaSimbolos:
    """
    Gestiona la jerarquía de ámbitos durante el análisis semántico.

    Uso típico:
        tabla = TablaSimbolos()
        tabla.declarar(EntradaSimbolo(...))   # ámbito global
        tabla.entrar_ambito("miFunc")
        tabla.declarar(EntradaSimbolo(...))   # parámetro en ámbito miFunc
        tabla.salir_ambito()
    """

    def __init__(self):
        self._raiz:  AmbitoTabla            = AmbitoTabla("global")
        self._actual: AmbitoTabla           = self._raiz
        self._pila:  List[AmbitoTabla]      = [self._raiz]

    # ── Gestión de ámbitos ────────────────────────────────────────────

    def entrar_ambito(self, nombre: str) -> None:
        """Crea un nuevo ámbito hijo y lo activa."""
        nuevo = AmbitoTabla(nombre, self._actual)
        self._actual.hijos.append(nuevo)
        self._actual = nuevo
        self._pila.append(nuevo)

    def salir_ambito(self) -> None:
        """Vuelve al ámbito padre."""
        if len(self._pila) > 1:
            self._pila.pop()
            self._actual = self._pila[-1]

    # ── Declaración y búsqueda ────────────────────────────────────────

    def declarar(self, entrada: EntradaSimbolo) -> bool:
        """Declara en el ámbito actual. Retorna False si ya existía."""
        return self._actual.declarar(entrada)

    def buscar(self, nombre: str) -> Optional[EntradaSimbolo]:
        """Busca en el ámbito actual y todos sus padres."""
        return self._actual.buscar(nombre)

    def buscar_local(self, nombre: str) -> Optional[EntradaSimbolo]:
        """Busca SOLO en el ámbito actual (sin ascender)."""
        return self._actual.buscar_local(nombre)

    # ── Consulta ──────────────────────────────────────────────────────

    @property
    def ambito_actual(self) -> str:
        return self._actual.nombre

    def todas_las_entradas(self) -> List[Tuple[str, EntradaSimbolo]]:
        """Devuelve [(nombre_ambito, entrada)] de todos los símbolos declarados."""
        resultado: List[Tuple[str, EntradaSimbolo]] = []
        self._recolectar(self._raiz, resultado)
        return resultado

    def _recolectar(
        self,
        ambito: AmbitoTabla,
        resultado: List[Tuple[str, EntradaSimbolo]],
    ) -> None:
        for entrada in ambito.simbolos.values():
            resultado.append((ambito.nombre, entrada))
        for hijo in ambito.hijos:
            self._recolectar(hijo, resultado)

    # ── Renderizado ───────────────────────────────────────────────────

    def renderizar(self) -> str:
        """Genera texto plano con el contenido completo de la tabla."""
        entradas = self.todas_las_entradas()
        if not entradas:
            return "(Tabla vacía — no se declaró ningún identificador)"

        lineas = ["TABLA DE SÍMBOLOS", "=" * 72, ""]
        ambito_anterior: Optional[str] = None

        for ambito_nombre, entrada in entradas:
            if ambito_nombre != ambito_anterior:
                if ambito_anterior is not None:
                    lineas.append("")
                lineas.append(f"Ámbito: {ambito_nombre}")
                lineas.append("-" * 40)
                ambito_anterior = ambito_nombre

            extra = ""
            if entrada.categoria == "funcion":
                p_txt = ", ".join(f"{n}: {t}" for n, t in entrada.parametros) or "(sin parámetros)"
                ret   = entrada.tipo_retorno or "void"
                extra = f"   params=[{p_txt}]  retorna={ret}"

            lineas.append(
                f"  {entrada.categoria:<12} {entrada.nombre:<20} : {entrada.tipo:<14}"
                f" L{entrada.fila}:C{entrada.columna}{extra}"
            )

        return "\n".join(lineas)

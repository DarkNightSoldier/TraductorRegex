"""
Módulo `utils.py`

Agrupa funciones utilitarias para:

- Validar si una expresión regular es sintácticamente correcta.
- Aplicar una serie de simplificaciones / optimizaciones locales sobre la regex,
  con el objetivo de:
    * Hacerla más legible.
    * Eliminar redundancias.
    * Ponerla en una forma “canónica” donde sea posible.
"""

import re


# ===============================================================
#  VALIDACIÓN
# ===============================================================

def validate_regex(regex: str) -> bool:
<<<<<<< HEAD
    """Valida si una expresión regular es sintácticamente correcta."""
=======
    """
    Verifica si una expresión regular es sintácticamente válida
    para el motor `re` de Python.

    Parameters
    ----------
    regex : str
        Expresión regular a validar.

    Returns
    -------
    bool
        True si `re.compile` no lanza excepción; False en caso contrario.
    """
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    try:
        re.compile(regex)
        return True
    except Exception:
        return False


# ===============================================================
<<<<<<< HEAD
#  OPTIMIZADORES INTERNOS
=======
#  OPTIMIZADORES INTERNOS (NIVEL SINTÁCTICO)
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
# ===============================================================

def simplify_parentheses(regex: str) -> str:
    """
<<<<<<< HEAD
    Elimina paréntesis innecesarios como:
      (a) → a
      ([0-9]) → [0-9]
    """
    # (X) where X has no operators that require grouping
    regex = re.sub(r'\((\[[^\]]+\])\)', r'\1', regex)
=======
    Elimina paréntesis que no aportan agrupación real.

    Casos tratados:
      - ([...]) → [...]
      - (a)     → a

    Es decir, solo se eliminan si en su interior hay un token simple
    o una clase de caracteres, sin operadores adicionales.
    """
    # Clase de caracteres entre paréntesis → la clase sola
    regex = re.sub(r'\((\[[^\]]+\])\)', r'\1', regex)
    # Literal alfanumérico simple entre paréntesis → literal solo
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    regex = re.sub(r'\(([a-zA-Z0-9])\)', r'\1', regex)
    return regex


def collapse_repetitions(regex: str) -> str:
    """
<<<<<<< HEAD
    Convierte secuencias repetidas en {n}
    Ej: [0-9][0-9][0-9] → [0-9]{3}
    """
    pattern = r'(\[[^\]]+\])\1+'
    def replacer(match):
        token = match.group(1)
        count = len(match.group(0)) // len(token)
        return f"{token}{{{count}}}"
=======
    Colapsa repeticiones consecutivas idénticas de la misma clase de caracteres
    en un cuantificador `{n}`.

    Ejemplo:
      [0-9][0-9][0-9]  →  [0-9]{3}
    """
    pattern = r'(\[[^\]]+\])\1+'

    def replacer(match: re.Match) -> str:
        token = match.group(1)          # la clase de caracteres, p.ej. [0-9]
        total_length = len(match.group(0))
        count = total_length // len(token)
        return f"{token}{{{count}}}"

>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    return re.sub(pattern, replacer, regex)


def simplify_or(regex: str) -> str:
    """
<<<<<<< HEAD
    Convierte (a|b|c) en [abc] cuando sea posible.
    Convierte ([0-9]|[1-9]) en [0-9]
    """
    # Primer caso: literales simples
    regex = re.sub(
        r'\((?:([a-zA-Z0-9])\|)+([a-zA-Z0-9])\)',
        lambda m: "[" + "".join(m.group(0).replace("(", "").replace(")", "").split("|")) + "]",
        regex
    )

    # Segundo caso: clases de dígitos
    regex = re.sub(
        r'\(\[0-9\]\|\[1-9\]\)',
        r"[0-9]",
        regex
=======
    Simplifica algunas expresiones OR en clases de caracteres.

    Casos principales:
      - (a|b|c)    → [abc]  (cuando todos son literales alfanuméricos)
      - ([0-9]|[1-9]) → [0-9]
    """
    # Literales simples entre paréntesis separados por '|'
    regex = re.sub(
        r'\((?:([a-zA-Z0-9])\|)+([a-zA-Z0-9])\)',
        lambda m: "[" + "".join(
            m.group(0).replace("(", "").replace(")", "").split("|")
        ) + "]",
        regex,
    )

    # Caso especial de dígitos
    regex = re.sub(
        r'\(\[0-9\]\|\[1-9\]\)',
        r"[0-9]",
        regex,
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    )

    return regex


def reorder_char_classes(regex: str) -> str:
    """
<<<<<<< HEAD
    Ordena caracteres dentro de clases:
    Ej: [zaq] → [aqz]
    """
    def repl(m):
        chars = list(m.group(1))
=======
    Ordena alfabéticamente los caracteres dentro de una clase de caracteres
    siempre que sean letras o dígitos (sin rangos).

    Ejemplo:
      [zaq]   → [aqz]
      [31A3]  → [13A]
    """

    def repl(m: re.Match) -> str:
        chars = list(m.group(1))
        # set(...) elimina duplicados; sorted(...) los ordena
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        chars = sorted(set(chars))
        return "[" + "".join(chars) + "]"

    return re.sub(r'\[([a-zA-Z0-9]+)\]', repl, regex)


# ===============================================================
#  OPTIMIZACIONES SEMÁNTICAS
# ===============================================================

def collapse_A_Astar(regex: str) -> str:
    """
<<<<<<< HEAD
    Simplifica A A* → A+
    """
    # Caso clase de caracteres: [a-z][a-z]*
    regex = re.sub(r'(\[[^\]]+\])\1\*', r'\1+', regex)

    # Caso literal/grupo simple: (X)(X)*
    regex = re.sub(r'(\([^\)]+\))\1\*', r'\1+', regex)

    # Caso token simple: a a*
=======
    Simplifica patrones del tipo: A A* → A+

    Casos contemplados:
      - [class][class]*  → [class]+
      - (grupo)(grupo)*  → (grupo)+
      - x x*             → x+
    """
    # Clase de caracteres repetida seguida de su '*'
    regex = re.sub(r'(\[[^\]]+\])\1\*', r'\1+', regex)
    # Grupo completo repetido y luego con '*'
    regex = re.sub(r'(\([^\)]+\))\1\*', r'\1+', regex)
    # Literal simple seguido de su '*'
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    regex = re.sub(r'([a-zA-Z0-9])\1\*', r'\1+', regex)

    return regex


def collapse_A_Aplus(regex: str) -> str:
    """
<<<<<<< HEAD
    Simplifica A A+ → A{2,}
    """
    # Caso clase de caracteres
    regex = re.sub(r'(\[[^\]]+\])\1\+', r'\1{2,}', regex)

    # Caso grupo simple
    regex = re.sub(r'(\([^\)]+\))\1\+', r'\1{2,}', regex)

=======
    Simplifica patrones del tipo: A A+ → A{2,}

    Casos contemplados:
      - [class][class]+  → [class]{2,}
      - (grupo)(grupo)+  → (grupo){2,}
    """
    regex = re.sub(r'(\[[^\]]+\])\1\+', r'\1{2,}', regex)
    regex = re.sub(r'(\([^\)]+\))\1\+', r'\1{2,}', regex)
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    return regex


def collapse_Aexact_Aexact(regex: str) -> str:
    """
<<<<<<< HEAD
    Simplifica A{m} A{n} → A{m+n}
    """
    def repl(m):
        token = m.group(1)
        m1 = int(m.group(2))
        m2 = int(m.group(3))
        return f"{token}{{{m1+m2}}}"
=======
    Une dos cuantificadores exactos consecutivos sobre la misma clase
    de caracteres: A{m} A{n} → A{m+n}.

    Ejemplo:
      [0-9]{2}[0-9]{3} → [0-9]{5}
    """

    def repl(m: re.Match) -> str:
        token = m.group(1)
        m1 = int(m.group(2))
        m2 = int(m.group(3))
        return f"{token}{{{m1 + m2}}}"
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593

    return re.sub(r'(\[[^\]]+\])\{(\d+)\}\1\{(\d+)\}', repl, regex)


def collapse_Aexact_Astar(regex: str) -> str:
    """
<<<<<<< HEAD
    Simplifica A{m} A* → A{m,}
=======
    Combina un cuantificador exacto seguido del mismo token con '*':
    A{m} A* → A{m,}

    Ejemplo:
      [a-z]{2}[a-z]* → [a-z]{2,}
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    """
    return re.sub(r'(\[[^\]]+\])\{(\d+)\}\1\*', r'\1{\2,}', regex)


def remove_redundant_one(regex: str) -> str:
    """
<<<<<<< HEAD
    Quita {1} → vacío.
    """
    regex = re.sub(r'\{1\}', '', regex)
    return regex
=======
    Elimina cuantificadores triviales {1}, que no cambian la semántica.

    Ejemplo:
      a{1} → a
    """
    return re.sub(r'\{1\}', '', regex)
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593


def collapse_group_plus(regex: str) -> str:
    """
<<<<<<< HEAD
    Simplifica (X)+ → X+  cuando X es simple.
    """
    # si es un token simple o clase de caracteres
=======
    Simplifica (X)+ a X+ cuando X es suficientemente simple:

      - Una clase de caracteres: ([...])+ → [...] +
      - Un literal simple:      (a)+     → a+

    De esta forma se reduce el número de paréntesis innecesarios.
    """
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    regex = re.sub(r'\((\[[^\]]+\])\)\+', r'\1+', regex)
    regex = re.sub(r'\(([a-zA-Z0-9])\)\+', r'\1+', regex)
    return regex


<<<<<<< HEAD

=======
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
# ===============================================================
#  OPTIMIZADOR PRINCIPAL
# ===============================================================

def simplify_regex(regex: str) -> str:
<<<<<<< HEAD

    old = None
    new = regex

    while new != old:
        old = new

        
        new = simplify_parentheses(new)
        new = collapse_repetitions(new)
        new = simplify_or(new)
        new = reorder_char_classes(new)

       
        new = collapse_A_Astar(new)
        new = collapse_A_Aplus(new)
        new = collapse_Aexact_Aexact(new)
        new = collapse_Aexact_Astar(new)
        new = remove_redundant_one(new)
        new = collapse_group_plus(new)

    return new

=======
    """
    Aplica iterativamente todas las simplificaciones definidas arriba
    hasta alcanzar un punto fijo (cuando ya no hay cambios).

    Orden aproximado:
      1. Simplificaciones sintácticas básicas (paréntesis, repeticiones).
      2. Normalización de ciertas clases de letras con '+'.
      3. Simplificación de OR y ordenamiento de clases.
      4. Simplificaciones semánticas (A A* → A+, etc.).

    Parameters
    ----------
    regex : str
        Expresión regular generada por el traductor.

    Returns
    -------
    str
        Expresión regular simplificada.
    """
    old = None
    new = regex

    # Repetimos el ciclo mientras alguna transformación cambie la cadena
    while new != old:
        old = new

        # Simplificaciones sintácticas locales
        new = simplify_parentheses(new)
        new = collapse_repetitions(new)

        # Forma canónica para la clase de letras con '+'
        # Caso específico: [a-zA-Z]+ se reescribe como [A-Za-z]+
        new = re.sub(r"\[a-zA-Z\]\+", "[A-Za-z]+", new)

        # Transformaciones de OR y reordenamiento de clases de caracteres
        new = simplify_or(new)
        new = reorder_char_classes(new)

        # Simplificaciones semánticas sobre cuantificadores
        new = collapse_A_Astar(new)
        new = collapse_A_Aplus(new)
        new = collapse_Aexact_Aexact(new)
        new = collapse_Aexact_Astar(new)
        new = remove_redundant_one(new)
        new = collapse_group_plus(new)

    return new
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593

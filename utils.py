import re

def validate_regex(regex: str) -> bool:
    """Valida si una expresión regular es sintácticamente correcta."""
    try:
        re.compile(regex)
        return True
    except:
        return False


# ===============================================================
#  OPTIMIZADORES INTERNOS
# ===============================================================

def simplify_parentheses(regex: str) -> str:
    """
    Elimina paréntesis innecesarios como:
      (a) → a
      ([0-9]) → [0-9]
    """
    # (X) where X has no operators that require grouping
    regex = re.sub(r'\((\[[^\]]+\])\)', r'\1', regex)
    regex = re.sub(r'\(([a-zA-Z0-9])\)', r'\1', regex)
    return regex


def collapse_repetitions(regex: str) -> str:
    """
    Convierte secuencias repetidas en {n}
    Ej: [0-9][0-9][0-9] → [0-9]{3}
    """
    pattern = r'(\[[^\]]+\])\1+'
    def replacer(match):
        token = match.group(1)
        count = len(match.group(0)) // len(token)
        return f"{token}{{{count}}}"
    return re.sub(pattern, replacer, regex)


def simplify_or(regex: str) -> str:
    """
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
    )

    return regex


def reorder_char_classes(regex: str) -> str:
    """
    Ordena caracteres dentro de clases:
    Ej: [zaq] → [aqz]
    """
    def repl(m):
        chars = list(m.group(1))
        chars = sorted(set(chars))
        return "[" + "".join(chars) + "]"

    return re.sub(r'\[([a-zA-Z0-9]+)\]', repl, regex)


# ===============================================================
#  OPTIMIZACIONES SEMÁNTICAS
# ===============================================================

def collapse_A_Astar(regex: str) -> str:
    """
    Simplifica A A* → A+
    """
    # Caso clase de caracteres: [a-z][a-z]*
    regex = re.sub(r'(\[[^\]]+\])\1\*', r'\1+', regex)

    # Caso literal/grupo simple: (X)(X)*
    regex = re.sub(r'(\([^\)]+\))\1\*', r'\1+', regex)

    # Caso token simple: a a*
    regex = re.sub(r'([a-zA-Z0-9])\1\*', r'\1+', regex)

    return regex


def collapse_A_Aplus(regex: str) -> str:
    """
    Simplifica A A+ → A{2,}
    """
    # Caso clase de caracteres
    regex = re.sub(r'(\[[^\]]+\])\1\+', r'\1{2,}', regex)

    # Caso grupo simple
    regex = re.sub(r'(\([^\)]+\))\1\+', r'\1{2,}', regex)

    return regex


def collapse_Aexact_Aexact(regex: str) -> str:
    """
    Simplifica A{m} A{n} → A{m+n}
    """
    def repl(m):
        token = m.group(1)
        m1 = int(m.group(2))
        m2 = int(m.group(3))
        return f"{token}{{{m1+m2}}}"

    return re.sub(r'(\[[^\]]+\])\{(\d+)\}\1\{(\d+)\}', repl, regex)


def collapse_Aexact_Astar(regex: str) -> str:
    """
    Simplifica A{m} A* → A{m,}
    """
    return re.sub(r'(\[[^\]]+\])\{(\d+)\}\1\*', r'\1{\2,}', regex)


def remove_redundant_one(regex: str) -> str:
    """
    Quita {1} → vacío.
    """
    regex = re.sub(r'\{1\}', '', regex)
    return regex


def collapse_group_plus(regex: str) -> str:
    """
    Simplifica (X)+ → X+  cuando X es simple.
    """
    # si es un token simple o clase de caracteres
    regex = re.sub(r'\((\[[^\]]+\])\)\+', r'\1+', regex)
    regex = re.sub(r'\(([a-zA-Z0-9])\)\+', r'\1+', regex)
    return regex



# ===============================================================
#  OPTIMIZADOR PRINCIPAL
# ===============================================================

def simplify_regex(regex: str) -> str:

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


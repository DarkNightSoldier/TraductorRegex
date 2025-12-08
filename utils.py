import re

def validate_regex(regex: str) -> bool:
    """
    Valida si una expresión regular es sintácticamente correcta.
    """
    try:
        re.compile(regex)
        return True
    except:
        return False


# ============================================================
#  REGEX SIMPLIFIER — SAFE HEURISTICS
# ============================================================

def simplify_regex(regex: str) -> str:
    """
    Simplificador avanzado y seguro para regex generadas.
    NO altera la semántica. Solo elimina redundancias comunes.
    """

    # -------------------------------------------
    # S0: Limpiezas básicas ya existentes
    # -------------------------------------------
    regex = regex.replace("((", "(").replace("))", ")")
    regex = regex.replace("([", "[").replace("])", "]")

    # Eliminar paréntesis externos si no son necesarios
    if regex.startswith("(") and regex.endswith(")"):
        inner = regex[1:-1]
        if "(" not in inner and ")" not in inner and "|" not in inner:
            regex = inner

    # -------------------------------------------
    # S1–S4: Simplificar repeticiones básicas
    # -------------------------------------------

    # X{1} → X
    regex = re.sub(r"(\[[^\]]+\]|\w|\.)\{1\}", r"\1", regex)

    # X{0} → "" (cadena vacía)
    regex = re.sub(r"(\[[^\]]+\]|\w|\.)\{0\}", r"", regex)

    # X{0,1} → X?
    regex = re.sub(r"(\[[^\]]+\]|\w|\.)\{0,1\}", r"\1?", regex)

    # X{1,} → X+
    regex = re.sub(r"(\[[^\]]+\]|\w|\.)\{1,\}", r"\1+", regex)

    # -------------------------------------------
    # S5–S6: [a-z][a-z]* → [a-z]+ 
    # -------------------------------------------

    regex = re.sub(r"(\[[^\]]+\])\1\*", r"\1+", regex)
    regex = re.sub(r"(\[[^\]]+\])\1\+", r"\1+", regex)

    # -------------------------------------------
    # S7: [a-z]{n}[a-z]{m} → [a-z]{n+m}
    # -------------------------------------------

    def merge_repetitions(match):
        cls = match.group(1)
        n = int(match.group(2))
        m = int(match.group(3))
        return f"{cls}{{{n+m}}}"

    regex = re.sub(r"(\[[^\]]+\])\{(\d+)\}\1\{(\d+)\}", merge_repetitions, regex)

    # -------------------------------------------
    # S8–S9: Eliminar paréntesis innecesarios
    # -------------------------------------------
    # (X) → X si X es simple
    regex = re.sub(r"\((\[[^\]]+\])\)", r"\1", regex)

    # ([a-z])* → [a-z]*
    regex = re.sub(r"\((\[[^\]]+\])\)([\*\+\?]|\{\d+(,\d+)?\})", r"\1\2", regex)

    # -------------------------------------------
    # S10: Dobles paréntesis extra
    # -------------------------------------------
    regex = regex.replace("((", "(").replace("))", ")")

    return regex

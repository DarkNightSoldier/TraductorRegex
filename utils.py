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


def simplify_regex(regex: str) -> str:
    """
    Simplificador básico para limpiar regex generadas.
    No elimina lógica — solo limpia redundancias simples.
    """
    # eliminar dobles paréntesis
    regex = regex.replace("((", "(").replace("))", ")")

    # eliminar paréntesis innecesarios sobre términos simples
    if regex.startswith("(") and regex.endswith(")"):
        inner = regex[1:-1]
        if "(" not in inner and ")" not in inner:
            regex = inner

    # eliminar grupos tontos como ([a-z]) -> [a-z]
    regex = regex.replace("([", "[").replace("])", "]")

    return regex
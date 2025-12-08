from lark import Lark, UnexpectedInput
from translator import RegexTranslator
from normalizer import Normalizer

# Instancia global del normalizador
normalizer = Normalizer()

# Cargar parser Lark con la gramática actualizada
try:
    parser = Lark.open(
        "grammar.lark",
        rel_to=__file__,
        start="start",
        parser="lalr"
    )
except Exception as e:
    print("ERROR cargando grammar.lark:", e)
    parser = None


# ============================================================
#  FUNCIONES INTERNAS (útiles para depuración y CLI)
# ============================================================

def normalize_text(text: str) -> str:
    """Retorna el DSL normalizado sin intentar parsearlo."""
    return normalizer.normalize(text)


def parse_normalized(normalized: str):
    """Parsea DSL normalizado y retorna el AST."""
    if parser is None:
        raise RuntimeError("ERROR: No se pudo cargar grammar.lark")

    return parser.parse(normalized)


def translate_tree(tree):
    """Convierte el AST en una regex cruda."""
    return RegexTranslator().transform(tree)


# ============================================================
#  API PRINCIPAL
# ============================================================

def translate_to_regex(text: str):
    """
    Función principal usada por el CLI y test.py.
    Retorna solo la regex final (o error).
    """
    if parser is None:
        return "ERROR: No se pudo cargar la gramática."

    try:
        # 1. Normalizar entrada natural → DSL
        normalized = normalize_text(text)

        # 2. Parsear DSL
        tree = parse_normalized(normalized)

        # 3. Traducir AST → regex cruda
        regex = translate_tree(tree)

        return regex

    except UnexpectedInput:
        return f"ERROR: La frase no coincide con el DSL."

    except Exception as e:
        return f"ERROR interno: {e}"

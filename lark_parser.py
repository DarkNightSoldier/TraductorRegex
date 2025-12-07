from lark import Lark, UnexpectedInput
from translator import RegexTranslator
from normalizer import Normalizer

# Crear instancia del normalizador
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


def translate_to_regex(text):
    if parser is None:
        return "ERROR: No se pudo cargar la gramática."

    try:
        # 1. Normalizar entrada natural → DSL
        normalized = normalizer.normalize(text)
        print("NORM >>>", normalized)

        # 2. Parsear DSL
        tree = parser.parse(normalized)

        # 3. Transformar AST → regex
        regex = RegexTranslator().transform(tree)

        return regex

    except UnexpectedInput as e:
        return f"ERROR: La frase no coincide con el DSL."

    except Exception as e:
        return f"ERROR interno: {e}"
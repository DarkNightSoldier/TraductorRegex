"""
Módulo `lark_parser.py`

Centraliza:

- La carga de la gramática `grammar.lark` usando Lark.
- El normalizador de texto (pseudolenguaje → DSL interno).
- El parseo del DSL normalizado a un árbol de sintaxis (AST).
- La traducción del AST a regex usando `RegexTranslator`.
- Un helper de alto nivel `translate_to_regex(text)` que encapsula
  todo el pipeline y maneja los errores más comunes.
"""

from lark import Lark, UnexpectedInput
from translator import RegexTranslator
from normalizer import Normalizer

<<<<<<< HEAD
# Instancia global del normalizador
=======
# Instancia global del normalizador que se reutiliza en todo el proyecto.
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
normalizer = Normalizer()

# ----------------------------------------------------------------------
# CARGA DE LA GRAMÁTICA
# ----------------------------------------------------------------------
try:
    # Lark.open permite cargar el archivo grammar.lark relativo a este módulo.
    # - start="start": regla inicial de la gramática.
    # - parser="lalr": usa el parser LALR(1) (rápido y adecuado para gramáticas grandes).
    parser = Lark.open("grammar.lark", rel_to=__file__, start="start", parser="lalr")
except Exception as e:
    # Si hay algún problema (archivo no encontrado, error de sintaxis en la gramática, etc.),
    # lo reportamos en consola y dejamos `parser = None` para notificar en tiempo de ejecución.
    print("ERROR cargando grammar.lark:", e)
    parser = None


<<<<<<< HEAD
# ============================================================
#  FUNCIONES INTERNAS (útiles para depuración y CLI)
# ============================================================

def normalize_text(text: str) -> str:
    """Retorna el DSL normalizado sin intentar parsearlo."""
=======
# ----------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normaliza una frase en pseudolenguaje / lenguaje natural ligero
    al DSL interno que entiende `grammar.lark`.

    Esta función delega en la instancia global de `Normalizer`.
    Se usa tanto en el pipeline principal como en el modo explicación.
    """
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    return normalizer.normalize(text)


def parse_normalized(normalized: str):
<<<<<<< HEAD
    """Parsea DSL normalizado y retorna el AST."""
    if parser is None:
        raise RuntimeError("ERROR: No se pudo cargar grammar.lark")

=======
    """
    Parsea una cadena ya normalizada usando la gramática de Lark y devuelve el AST.

    Parámetros
    ----------
    normalized : str
        Texto que ya está en el DSL que la gramática reconoce.

    Retorna
    -------
    lark.Tree
        Árbol de sintaxis generado por Lark.

    Lanza
    -----
    RuntimeError
        Si el parser no pudo cargarse (grammar.lark no se cargó correctamente).
    lark.UnexpectedInput
        Si el texto no coincide con la gramática.
    """
    if parser is None:
        raise RuntimeError("ERROR: No se pudo cargar grammar.lark")
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    return parser.parse(normalized)


def translate_tree(tree):
<<<<<<< HEAD
    """Convierte el AST en una regex cruda."""
    return RegexTranslator().transform(tree)


# ============================================================
#  API PRINCIPAL
# ============================================================

def translate_to_regex(text: str):
    """
    Función principal usada por el CLI y test.py.
    Retorna solo la regex final (o error).
=======
    """
    Traduce un AST de Lark a una expresión regular.

    Parámetros
    ----------
    tree : lark.Tree
        Árbol producido por `parse_normalized`.

    Retorna
    -------
    str
        Expresión regular generada por `RegexTranslator`.
    """
    return RegexTranslator().transform(tree)


def translate_to_regex(text: str):
    """
    Función de alto nivel que traduce una frase de entrada a una regex.

    Pipeline:
      1. Verifica que la gramática haya cargado correctamente.
      2. Normaliza el texto de entrada.
      3. Parsea el texto normalizado a un AST.
      4. Traduce el AST a regex con `RegexTranslator`.

    Manejo de errores:
      - Si la gramática no se cargó → devuelve un mensaje de ERROR.
      - Si el texto no coincide con el DSL → "ERROR: La frase no coincide con el DSL."
      - Para cualquier otra excepción → "ERROR interno: <detalle>"

    Parámetros
    ----------
    text : str
        Frase original escrita por el usuario.

    Retorna
    -------
    str
        Regex generada o un mensaje de error que empieza por "ERROR".
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    """
    if parser is None:
        return "ERROR: No se pudo cargar la gramática."
    try:
<<<<<<< HEAD
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
=======
        # 1) Normalizar
        normalized = normalize_text(text)
        # 2) Parsear a AST
        tree = parse_normalized(normalized)
        # 3) Traducir AST a regex
        regex = translate_tree(tree)
        return regex
    except UnexpectedInput:
        # Lark lanza UnexpectedInput cuando el texto normalizado
        # no encaja con ninguna producción de la gramática.
        return "ERROR: La frase no coincide con el DSL."
    except Exception as e:
        # Cualquier otro error interno (bug en transformer, etc.)
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        return f"ERROR interno: {e}"

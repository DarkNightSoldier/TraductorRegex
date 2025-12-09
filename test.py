"""
Módulo `test.py`

Este archivo agrupa un pequeño “test runner” para el traductor
DSL → regex. Permite:

- Ejecutar pruebas unitarias sobre frases del DSL.
- Verificar que la regex generada:
    * no sea un error,
    * sea sintácticamente válida,
    * y (cuando aplique) coincida con una regex esperada.
- Ejecutar todas las pruebas desde la línea de comandos con `--verbose`
  para ver el detalle de cada caso.
"""

import argparse
from lark_parser import translate_to_regex
from utils import validate_regex, simplify_regex


def test_case(phrase: str, expected: str | None = None, verbose: bool = False) -> bool:
    """
    Ejecuta una prueba unitaria para una frase del DSL.

    Parámetros
    ----------
    phrase : str
        Frase de entrada en el DSL.
    expected : str | None
        Regex esperada. Si es:
          - str: se compara estrictamente contra la regex obtenida.
          - None: se espera que la traducción falle (cadena que empieza por "ERROR").
    verbose : bool
        Si es True, imprime siempre el detalle del caso.
        Si es False, solo imprime detalles cuando la prueba falla.

    Retorna
    -------
    bool
        True si la prueba pasa, False si falla.
    """
    raw = translate_to_regex(phrase)

    # Caso 1: la traducción devolvió un error
    if raw.startswith("ERROR"):
        if expected is None:
            ok = True
            msg = "Error esperado."
        else:
            ok = False
            msg = raw
        regex = raw
    else:
        # Caso 2: la traducción produjo una regex
        regex = simplify_regex(raw)

        if not validate_regex(regex):
            ok = False
            msg = "Regex inválida sintácticamente."
        elif expected is not None and regex != expected:
            ok = False
            msg = f"Esperado: {expected}, obtenido: {regex}"
        else:
            ok = True
            msg = "OK"

    # Salida por consola según modo verbose o resultado de la prueba
    if verbose or not ok:
        print()
        print("Frase:", phrase)
        print("Regex:", regex)
        if expected is not None:
            print("Esperado:", expected)
        print("Resultado:", "OK" if ok else f"FALLÓ – {msg}")

    return ok


def probar(frase: str) -> None:
    """
    Función de ayuda para uso interactivo.

    Imprime directamente la regex generada (o el error),
    emulando el comportamiento de la herramienta principal.
    """
    test_case(frase, expected=None, verbose=True)


# -------------------------------------------------------------------
#  GRUPOS DE PRUEBAS
# -------------------------------------------------------------------

# Pruebas básicas (coinciden con ejemplos típicos del README)
BASIC_TESTS = [
    ("digits that appear three times", "[0-9]{3}"),
    ("a lowercase letter optionally followed by three digits", "[a-z]?[0-9]{3}"),
    ("letters then digits", "[A-Za-z]+[0-9]+"),
    ("any character except digits", "[^0-9]"),
    ("uppercase letters that repeat twice next lowercase letters", "[A-Z]{2}[a-z]+"),
    ("'hello' then digits that appear between 2 and 5 times", "hello[0-9]{2,5}"),
    ("group digit followed by letter end group repeated twice", "([0-9][a-zA-Z]){2}"),
]

# Pruebas específicas para rangos textuales (range 'a' to 'z', etc.)
RANGE_TESTS = [
    ("range 'a' to 'f'", "[a-f]"),
    ("range '0' to '9'", "[0-9]"),
    ("range 'A' to 'Z'", "[A-Z]"),
]

# Pruebas para clases semánticas predefinidas
CLASS_TESTS = [
    ("vowel one or more", "[AEIOUaeiou]+"),
    ("consonant one or more", "[BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz]+"),
    ("hex digit one or more", "[0-9A-Fa-f]+"),
    ("word character one or more", r"\w+"),
    ("non whitespace one or more", r"\S+"),
]

# Pruebas centradas en distintos cuantificadores
QUANTIFIER_TESTS = [
    ("digit one or more", "[0-9]+"),
    ("digit zero or more", "[0-9]*"),
    ("digit optional", "[0-9]?"),
    ("digit 3 times", "[0-9]{3}"),
    ("digit between 2 and 5 times", "[0-9]{2,5}"),
    ("digit at least 2 times", "[0-9]{2,}"),
    ("digit at most 4 times", "[0-9]{0,4}"),
]

# Pruebas para números en inglés “ilimitados” (más allá del 10)
ENGLISH_NUMBER_TESTS = [
    ("digit twenty times", "[0-9]{20}"),
    ("letter seventy two times", "[a-zA-Z]{72}"),
    ("digit one hundred and five times", "[0-9]{105}"),
    ("digit two thousand and eight times", "[0-9]{2008}"),
    ("hex digit three hundred forty one times", "[0-9A-Fa-f]{341}"),
]

# Frases que deberían fallar (el parser debe rechazarlas)
ERROR_TESTS = [
    ("digit followedby letter", None),  # falta el espacio en "followed by"
]


if __name__ == "__main__":
    """
    Punto de entrada cuando se ejecuta:

        python test.py [--verbose]

    Recorre todos los grupos de pruebas y muestra el resultado
    de cada bloque. Si se pasa `--verbose`, imprime el detalle
    completo de cada test_case (haya pasado o no).
    """
    parser = argparse.ArgumentParser(
        description="Pruebas para el traductor DSL → regex"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra el detalle de cada prueba.",
    )
    args = parser.parse_args()

    print("\n=== PRUEBAS BÁSICAS (README) ===")
    for phrase, expected in BASIC_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE RANGOS ===")
    for phrase, expected in RANGE_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE CLASES PREDEFINIDAS ===")
    for phrase, expected in CLASS_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE CUANTIFICADORES ===")
    for phrase, expected in QUANTIFIER_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE NÚMEROS EN INGLÉS ===")
    for phrase, expected in ENGLISH_NUMBER_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE ERRORES ESPERADOS ===")
    for phrase, expected in ERROR_TESTS:
        test_case(phrase, expected, args.verbose)

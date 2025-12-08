import argparse
from lark_parser import translate_to_regex
from utils import validate_regex, simplify_regex


def test_case(phrase: str, expected: str | None = None, verbose: bool = False) -> bool:
    """
    Ejecuta una prueba sobre una frase del DSL.

    - Si expected es una regex, comprueba que:
      * la traducción no sea un error,
      * la regex sea sintácticamente válida,
      * y coincida exactamente con expected.

    - Si expected es None, se espera que la traducción falle
      (devuelva una cadena que empieza por 'ERROR').
    """
    raw = translate_to_regex(phrase)

    if raw.startswith("ERROR"):
        if expected is None:
            ok = True
            msg = "Error esperado."
        else:
            ok = False
            msg = raw
        regex = raw
    else:
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
    Atajo de uso interactivo que imprime la regex generada,
    similar al comportamiento de la versión original.
    """
    test_case(frase, expected=None, verbose=True)


# Pruebas básicas
BASIC_TESTS = [
    ("digits that appear three times", "[0-9]{3}"),
    ("a lowercase letter optionally followed by three digits", "[a-z]?[0-9]{3}"),
    ("letters then digits", "[A-Za-z]+[0-9]+"),
    ("any character except digits", "[^0-9]"),
    ("uppercase letters that repeat twice next lowercase letters", "[A-Z]{2}[a-z]+"),
    ("'hello' then digits that appear between 2 and 5 times", "hello[0-9]{2,5}"),
    ("group digit followed by letter end group repeated twice", "([0-9][a-zA-Z]){2}"),
]

# Pruebas para rangos textuales
RANGE_TESTS = [
    ("range 'a' to 'f'", "[a-f]"),
    ("range '0' to '9'", "[0-9]"),
    ("range 'A' to 'Z'", "[A-Z]"),
]

# Pruebas para clases predefinidas
CLASS_TESTS = [
    ("vowel one or more", "[AEIOUaeiou]+"),
    ("consonant one or more", "[BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz]+"),
    ("hex digit one or more", "[0-9A-Fa-f]+"),
    ("word character one or more", r"\w+"),
    ("non whitespace one or more", r"\S+"),
]

# Pruebas para distintos cuantificadores
QUANTIFIER_TESTS = [
    ("digit one or more", "[0-9]+"),
    ("digit zero or more", "[0-9]*"),
    ("digit optional", "[0-9]?"),
    ("digit 3 times", "[0-9]{3}"),
    ("digit between 2 and 5 times", "[0-9]{2,5}"),
    ("digit at least 2 times", "[0-9]{2,}"),
    ("digit at most 4 times", "[0-9]{0,4}"),
]

# Pruebas específicas de números en inglés ilimitados
ENGLISH_NUMBER_TESTS = [
    ("digit twenty times", "[0-9]{20}"),
    ("letter seventy two times", "[a-zA-Z]{72}"),
    ("digit one hundred and five times", "[0-9]{105}"),
    ("digit two thousand and eight times", "[0-9]{2008}"),
    ("hex digit three hundred forty one times", "[0-9A-Fa-f]{341}"),
]

# Frases que deberían fallar (errores esperados)
ERROR_TESTS = [
    ("digit followedby letter", None),  # falta el espacio en "followed by"
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pruebas para el traductor DSL → regex"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra el detalle de cada prueba."
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

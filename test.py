import argparse
from lark_parser import translate_to_regex, normalize_text
from utils import validate_regex, simplify_regex


def test_case(phrase, expected=None, verbose=False):
    """
    Ejecuta un caso de prueba:
    - Traduce frase → regex
    - Verifica sintaxis
    - Compara con regex esperada (si se proporciona)
    """

    regex = translate_to_regex(phrase)

    ok = True
    msg = ""

    if regex.startswith("ERROR"):
        ok = False
        msg = regex
    elif not validate_regex(regex):
        ok = False
        msg = "Regex inválida generada."
    elif expected is not None and simplif(regex) != simplify_regex(expected):
        ok = False
        msg = f"Esperado: {expected}, obtenido: {regex}"

    if ok:
        print(f"✓ PASSED  →  '{phrase}'   =>   {regex}")
    else:
        print(f"✗ FAILED  →  '{phrase}'")
        print("   Motivo:", msg)

    if verbose:
        print("   Normalizado:", normalize_text(phrase))
        print("   Regex final:", regex)
        print()


# ============================================================
# PRUEBAS DEFINIDAS
# ============================================================

BASIC_TESTS = [
    ("digits that appear three times", "[0-9]{3}"),
    ("a lowercase letter optionally followed by three digits", "[a-z]?[0-9]{3}"),
    ("letters then digits", "[a-zA-Z]+[0-9]+"),
    ("any character except digits", "[^0-9]"),
    ("uppercase letters that repeat twice next lowercase letters", "[A-Z]{2}[a-z]+"),
    ("'hello' then digits that appear between 2 and 5 times", "hello[0-9]{2,5}"),
    ("digit or letter followed by space optional", "([0-9]|[a-zA-Z])\\s?")
]

RANGE_TESTS = [
    ("letter between 'a' and 'f'", "[a-f]"),
    ("character between 'm' and 'z' one or more", "[m-z]+"),
    ("digit followed by letter between 'a' and 'c' times", "[0-9][a-c]{1}")  # expected revisable
]

GROUP_TESTS = [
    ("group digit followed by digit end group 3 times", "([0-9][0-9]){3}"),
    ("group 'a' followed by digit end group or 'hello'", "(a[0-9]|hello)")
]

ERROR_TESTS = [
    ("digit followedby letter", None),  # error esperado
    ("3 times digit", None),
    ("letter between 'z' and 'a'", None),  # rango invertido → error futuro
]

VOWEL_TESTS = [
    ("vowel", "[aeiouAEIOU]"),
    ("vowels", "[aeiouAEIOU]+"),
    ("vowel followed by consonant", "[aeiouAEIOU][b-df-hj-np-tv-zB-DF-HJ-NP-TV-Z]"),
]

HEX_TESTS = [
    ("hex digit", "[0-9A-Fa-f]"),
    ("hex digits", "[0-9A-Fa-f]+"),
]

WORD_TESTS = [
    ("word character one or more", r"\w+"),
]

ALNUM_TESTS = [
    ("alphanumeric 3 times", "[A-Za-z0-9]{3}"),
]

NONSPACE_TESTS = [
    ("non whitespace one or more", r"\S+"),
]



# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    print("\n=== PRUEBAS BÁSICAS ===")
    for phrase, expected in BASIC_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE RANGO ===")
    for phrase, expected in RANGE_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE GRUPOS ===")
    for phrase, expected in GROUP_TESTS:
        test_case(phrase, expected, args.verbose)

    print("\n=== PRUEBAS DE ERRORES ESPERADOS ===")
    for phrase, expected in ERROR_TESTS:
        test_case(phrase, expected, args.verbose)
    
    print("\n=== PRUEBAS DE NUMEROS EN INGLES ===")
    tests_num = [
        ("digit twenty times", "[0-9]{20}"),
        ("letter seventy two times", "[a-zA-Z]{72}"),
        ("digit one hundred and five times", "[0-9]{105}"),
        ("digit two thousand and eight times", "[0-9]{2008}"),
        ("hex digit three hundred forty one times", "[0-9A-Fa-f]{341}"),
    ]   

    for phrase, expected in tests_num:
        test_case(phrase, expected, args.verbose)


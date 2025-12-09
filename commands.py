"""
Módulo `commands.py`

Define funciones auxiliares para el modo interactivo del CLI:

- show_help()    → imprime la lista de comandos disponibles del REPL.
- show_examples()→ imprime ejemplos de frases válidas del DSL.
- show_tokens()  → imprime el “vocabulario” básico del DSL (tokens soportados).

Estas funciones solo devuelven cadenas ya coloreadas con colorama (no imprimen).
El CLI (`cli.py`) se encarga de llamarlas y hacer `print(...)`.
"""

from colorama import Fore


def show_help():
    """
    Devuelve un texto corto con los comandos disponibles en el modo interactivo.

    Se usa cuando el usuario escribe `help` en el REPL.
    No realiza ningún I/O por sí mismo, solo retorna el string coloreado.
    """
    return (
        Fore.CYAN + "Comandos disponibles:\n"
        "  help       - Muestra esta ayuda\n"
        "  examples   - Ejemplos de frases válidas del DSL\n"
        "  tokens     - Lista de palabras clave del DSL\n"
        "  exit       - Salir del modo interactivo\n"
    )


def show_examples():
    """
    Devuelve una lista de ejemplos de frases válidas del DSL.

    Está organizada en secciones:
    - Básicos
    - Clases avanzadas
    - Rangos
    - Grupos
    - Negaciones

    El modo interactivo la muestra cuando el usuario escribe `examples`.
    """
    return (
        Fore.GREEN + "Ejemplos de frases válidas:\n"
        "\n--- Básicos ---\n"
        "  letter followed by digit\n"
        "  uppercase letter followed by digit zero or more\n"
        "  'hello' followed by digit between 2 and 4 times\n"
        "  letter one or more or digit one or more\n"
        "\n--- Clases avanzadas ---\n"
        "  vowel followed by consonant\n"
        "  word character one or more\n"
        "  alphanumeric at least 3 times\n"
        "  whitespace at most 2 times\n"
        "  non whitespace one or more\n"
        "\n--- Rangos ---\n"
        "  range 'a' to 'z' one or more\n"
        "\n--- Grupos ---\n"
        "  group digit followed by letter end group 3 times\n"
        "\n--- Negaciones ---\n"
        "  letter except 'a'\n"
    )


def show_tokens():
    """
    Devuelve una lista de los tokens / palabras clave del DSL.

    Está separada en:
    - Términos básicos: clases simples (letter, digit, space, etc.) y literales.
    - Clases avanzadas: categorías semánticas más ricas (vowel, consonant, etc.).
    - Rangos: sintaxis para rangos de caracteres.
    - Repeticiones: cuantificadores soportados (optional, one or more, X times...).
    - Conectores: formas de combinar elementos (followed by, or).

    El modo interactivo la muestra cuando el usuario escribe `tokens`.
    """
    return (
        Fore.YELLOW + "Tokens válidos del DSL:\n"
        "\n--- Términos básicos ---\n"
        "  letter\n"
        "  digit\n"
        "  space\n"
        "  any character\n"
        "  uppercase letter\n"
        "  lowercase letter\n"
        "  'a', 'b', '1', '@'\n"
        "\n--- Clases avanzadas ---\n"
        "  vowel\n"
        "  consonant\n"
        "  word character\n"
        "  alphanumeric\n"
        "  hex digit\n"
        "  whitespace\n"
        "  non whitespace\n"
        "\n--- Rangos ---\n"
        "  range 'x' to 'y'\n"
        "\n--- Repeticiones ---\n"
        "  optional\n"
        "  one or more\n"
        "  zero or more\n"
        "  X times\n"
        "  between X and Y times\n"
        "  at least X times\n"
        "  at most X times\n"
        "\n--- Conectores ---\n"
        "  followed by\n"
        "  or\n"
    )

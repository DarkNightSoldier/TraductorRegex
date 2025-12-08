import argparse
import re
from colorama import Fore, init

from lark_parser import translate_to_regex, normalizer, parser
from translator import RegexTranslator
from completer import DSLCompleter
from commands import show_help, show_tokens, show_examples
from explain import explain_phrase_and_regex
from utils import validate_regex, simplify_regex

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory

init(autoreset=True)


def main():
    parser_arg = argparse.ArgumentParser(
        description="TraductorRegex – DSL para generar expresiones regulares."
    )

    parser_arg.add_argument("phrase", nargs="?", help="Frase pseudonatural a convertir.")
    parser_arg.add_argument("--test", help="Cadena para validar contra la Regex.")
    parser_arg.add_argument("--explain", action="store_true", help="Explica paso a paso la conversión.")
    parser_arg.add_argument("--debug", action="store_true", help="Muestra DSL normalizado, AST y regex sin simplificar.")
    parser_arg.add_argument("--interactive", action="store_true", help="Modo interactivo con autocompletado.")

    args = parser_arg.parse_args()

    if args.interactive:
        run_interactive(args)
        return

    if not args.phrase:
        print(Fore.YELLOW + "ERROR: No ingresaste ninguna frase.")
        return

    run_conversion(args.phrase, args)


def run_conversion(phrase, args):

    # --------------------------------------
    # MODO DEBUG → mostrar salida detallada
    # --------------------------------------
    if args.debug:
        print(Fore.CYAN + "\n=== DEBUG MODE ACTIVADO ===\n")

        print(Fore.GREEN + "Frase original:")
        print(" ", phrase, "\n")

        # 1. Normalización
        normalized = normalizer.normalize(phrase)
        print(Fore.GREEN + "DSL normalizado:")
        print(" ", normalized, "\n")

        # 2. AST
        try:
            tree = parser.parse(normalized)
            print(Fore.GREEN + "AST generado:")
            print(tree.pretty(), "\n")
        except Exception as e:
            print(Fore.RED + "Error al generar AST:", e)
            return

        # 3. Regex cruda
        try:
            raw_regex = RegexTranslator().transform(tree)
            print(Fore.GREEN + "Regex cruda generada:")
            print(" ", raw_regex, "\n")
        except Exception as e:
            print(Fore.RED + "Error durante traducción a regex:", e)
            return

        # 4. Regex final (simplificada)
        final_regex = simplify_regex(raw_regex)
        print(Fore.GREEN + "Regex simplificada (final):")
        print(" ", final_regex, "\n")

        if args.test:
            test_regex(final_regex, args.test)

        return

    # --------------------------------------
    # MODO NORMAL
    # --------------------------------------
    regex = translate_to_regex(phrase)
    regex = simplify_regex(regex)

    if regex.startswith("ERROR"):
        print(Fore.YELLOW + regex)
        return

    if not validate_regex(regex):
        print(Fore.RED + "ERROR: La regex generada no es válida.")
        return

    print(Fore.GREEN + "Regex generada:", regex)

    if args.explain:
        print(explain_phrase_and_regex(phrase, regex))

    if args.test:
        test_regex(regex, args.test)


def run_interactive(args):
    print(Fore.CYAN + "Modo interactivo (TAB = autocompletar).")
    print(Fore.CYAN + "Comandos: help, examples, tokens, exit.\n")

    completer = DSLCompleter()
    history = FileHistory(".traductorregex_history")

    while True:
        phrase = prompt("Frase > ", completer=completer, history=history)
        cleaned = phrase.strip().lower()

        if cleaned == "exit":
            print(Fore.CYAN + "Saliendo del modo interactivo.")
            break

        if cleaned == "help":
            print(show_help())
            continue

        if cleaned == "examples":
            print(show_examples())
            continue

        if cleaned == "tokens":
            print(show_tokens())
            continue

        if not phrase.strip():
            print(Fore.YELLOW + "No escribiste ninguna frase.")
            continue

        run_conversion(phrase, args)


def test_regex(pattern, text):
    try:
        if re.fullmatch(pattern, text):
            print(Fore.GREEN + f"✓ '{text}' coincide.")
        else:
            print(Fore.RED + f"✗ '{text}' NO coincide.")
    except Exception as e:
        print(Fore.YELLOW + f"Error usando regex: {e}")


if __name__ == "__main__":
    main()

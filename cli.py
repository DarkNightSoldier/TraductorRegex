import argparse
import re
from colorama import Fore, init

from lark_parser import translate_to_regex
from completer import DSLCompleter
from commands import show_help, show_tokens, show_examples
from explain import explain_phrase_and_regex
from utils import validate_regex, simplify_regex

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory

init(autoreset=True)


def main():
    parser = argparse.ArgumentParser(
        description="TraductorRegex – DSL para generar expresiones regulares."
    )

    parser.add_argument("phrase", nargs="?", help="Frase pseudonatural a convertir.")
    parser.add_argument("--test", help="Cadena para validar contra la Regex.")
    parser.add_argument("--explain", action="store_true", help="Explica paso a paso la conversión.")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo con autocompletado.")

    args = parser.parse_args()

    # ---------------------------------------------------------
    # MODO INTERACTIVO
    # ---------------------------------------------------------
    if args.interactive:
        run_interactive(args)
        return

    # ---------------------------------------------------------
    # MODO NORMAL
    # ---------------------------------------------------------
    if not args.phrase:
        print(Fore.YELLOW + "ERROR: No ingresaste ninguna frase.")
        return

    run_conversion(args.phrase, args)


def run_conversion(phrase, args):
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

        # ---------------------------------
        # DETECCIÓN DE COMANDOS INTERNOS
        # ---------------------------------
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

        # ---------------------------------
        # Si no es comando, procesar frase
        # ---------------------------------
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
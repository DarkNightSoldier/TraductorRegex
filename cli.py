"""
CLI principal de TraductorRegex.

Este archivo define la interfaz de línea de comandos del proyecto.
Permite:

- Ejecutar el traductor en modo “una sola frase”.
- Activar modo debug para ver DSL normalizado, AST y regex cruda.
- Probar la regex generada contra una cadena de prueba.
- Entrar en modo interactivo con autocompletado del DSL.
- (Opcional) Mostrar una explicación paso a paso de cómo se construye la regex.
"""

import argparse
import re

<<<<<<< HEAD
=======
from colorama import Fore, init
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
from lark_parser import translate_to_regex, normalizer, parser
from translator import RegexTranslator
from completer import DSLCompleter
from commands import show_help, show_tokens, show_examples
from explain import explain_phrase_and_regex
from utils import validate_regex, simplify_regex
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory

# Inicializa colorama para que los colores se “reset” automáticamente
# después de cada impresión, evitando tener que resetear manualmente.
init(autoreset=True)


def main():
<<<<<<< HEAD
=======
    """
    Punto de entrada del programa cuando se ejecuta `python cli.py`.

    - Define los argumentos de línea de comandos.
    - Decide si se usa modo interactivo o de una sola frase.
    - Llama a `run_conversion` o `run_interactive` según corresponda.
    """
    # Parser de argumentos para la CLI
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    parser_arg = argparse.ArgumentParser(
        description="TraductorRegex – DSL para generar expresiones regulares."
    )

<<<<<<< HEAD
    parser_arg.add_argument("phrase", nargs="?", help="Frase pseudonatural a convertir.")
    parser_arg.add_argument("--test", help="Cadena para validar contra la Regex.")
    parser_arg.add_argument("--explain", action="store_true", help="Explica paso a paso la conversión.")
    parser_arg.add_argument("--debug", action="store_true", help="Muestra DSL normalizado, AST y regex sin simplificar.")
    parser_arg.add_argument("--interactive", action="store_true", help="Modo interactivo con autocompletado.")

    args = parser_arg.parse_args()

=======
    # Argumento posicional: la frase en pseudolenguaje natural a convertir
    parser_arg.add_argument(
        "phrase",
        nargs="?",
        help="Frase pseudonatural a convertir.",
    )

    # Opción: cadena de prueba para validar la regex generada
    parser_arg.add_argument(
        "--test",
        help="Cadena para validar contra la Regex.",
    )

    # Opción: explicar paso a paso el proceso (normalización, AST, etc.)
    parser_arg.add_argument(
        "--explain",
        action="store_true",
        help="Explica paso a paso la conversión.",
    )

    # Opción: modo debug – imprime DSL normalizado, AST, regex cruda y simplificada
    parser_arg.add_argument(
        "--debug",
        action="store_true",
        help="Muestra DSL normalizado, AST y regex sin simplificar.",
    )

    # Opción: modo interactivo (REPL) con autocompletado
    parser_arg.add_argument(
        "--interactive",
        action="store_true",
        help="Modo interactivo con autocompletado.",
    )

    # Parseo final de los argumentos
    args = parser_arg.parse_args()

    # Si se pidió modo interactivo, delegamos a `run_interactive`
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    if args.interactive:
        run_interactive(args)
        return

<<<<<<< HEAD
=======
    # Si no hay frase y no estamos en interactivo, es un error de uso
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    if not args.phrase:
        print(Fore.YELLOW + "ERROR: No ingresaste ninguna frase.")
        return

    # Flujo normal: convertir una sola frase
    run_conversion(args.phrase, args)


def run_conversion(phrase, args):
<<<<<<< HEAD

    # --------------------------------------
    # MODO DEBUG → mostrar salida detallada
    # --------------------------------------
    if args.debug:
        print(Fore.CYAN + "\n=== DEBUG MODE ACTIVADO ===\n")

        print(Fore.GREEN + "Frase original:")
        print(" ", phrase, "\n")

        # 1. Normalización
=======
    """
    Ejecuta el flujo de conversión para una frase dada.

    - Si `args.debug` está activo, entra en modo diagnóstico:
        * Muestra la frase original.
        * Muestra el DSL normalizado.
        * Construye y muestra el AST con Lark.
        * Traduce el AST a regex cruda (sin optimizaciones).
        * Simplifica la regex y la muestra.
    - Si no está en debug:
        * Usa `translate_to_regex` (pipeline normal).
        * Simplifica la regex final.
        * Valida que la regex sea sintácticamente correcta.
        * Imprime la regex generada.
        * Opcionalmente explica el proceso (`--explain`).
        * Opcionalmente prueba la regex contra una cadena (`--test`).
    """
    # ------------------ MODO DEBUG ------------------
    if args.debug:
        print(Fore.CYAN + "\n=== DEBUG MODE ACTIVADO ===\n")

        # 1) Mostrar frase original
        print(Fore.GREEN + "Frase original:")
        print(" ", phrase, "\n")

        # 2) Normalizar con el normalizador global de lark_parser
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        normalized = normalizer.normalize(phrase)
        print(Fore.GREEN + "DSL normalizado:")
        print(" ", normalized, "\n")

<<<<<<< HEAD
        # 2. AST
=======
        # 3) Construir AST con el parser de Lark
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        try:
            tree = parser.parse(normalized)
            print(Fore.GREEN + "AST generado:")
            print(tree.pretty(), "\n")
        except Exception as e:
<<<<<<< HEAD
            print(Fore.RED + "Error al generar AST:", e)
            return

        # 3. Regex cruda
=======
            # Si algo falla en el parsing, lo reportamos y salimos
            print(Fore.RED + "Error al generar AST:", e)
            return

        # 4) Traducir AST a regex con el Transformer de `translator.py`
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        try:
            raw_regex = RegexTranslator().transform(tree)
            print(Fore.GREEN + "Regex cruda generada:")
            print(" ", raw_regex, "\n")
        except Exception as e:
<<<<<<< HEAD
            print(Fore.RED + "Error durante traducción a regex:", e)
            return

        # 4. Regex final (simplificada)
=======
            # Si falla la transformación (regla no manejada, etc.), se reporta
            print(Fore.RED + "Error durante traducción a regex:", e)
            return

        # 5) Simplificar/optimizar la regex resultante
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        final_regex = simplify_regex(raw_regex)
        print(Fore.GREEN + "Regex simplificada (final):")
        print(" ", final_regex, "\n")

<<<<<<< HEAD
        if args.test:
            test_regex(final_regex, args.test)

        return

    # --------------------------------------
    # MODO NORMAL
    # --------------------------------------
=======
        # 6) Si se pasó `--test`, probamos la regex contra la cadena dada
        if args.test:
            test_regex(final_regex, args.test)

        # En modo debug nunca llegamos al flujo normal de `translate_to_regex`
        return

    # ------------------ MODO NORMAL ------------------
    # 1) Usa el pipeline completo (normalización + parseo + traducción)
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    regex = translate_to_regex(phrase)

    # 2) Aplica las simplificaciones de regex (optimización, forma canónica, etc.)
    regex = simplify_regex(regex)

    # 3) Manejo de errores provenientes del pipeline (mensajes tipo "ERROR: ...")
    if regex.startswith("ERROR"):
        print(Fore.YELLOW + regex)
        return

    # 4) Validar que la regex generada sea compilable por `re`
    if not validate_regex(regex):
        print(Fore.RED + "ERROR: La regex generada no es válida.")
        return

    # 5) Imprimir regex final
    print(Fore.GREEN + "Regex generada:", regex)

    # 6) Si se pide explicación estructural, la imprimimos
    if args.explain:
        print(explain_phrase_and_regex(phrase, regex))

    # 7) Si se pasó `--test`, probamos la regex contra la cadena
    if args.test:
        test_regex(regex, args.test)


def run_interactive(args):
    """
    Lanza un pequeño REPL (modo interactivo) con autocompletado del DSL.

    Características:
    - Se mantiene un historial en disco (`.traductorregex_history`).
    - Soporta comandos especiales:
        * help     → muestra descripción del DSL.
        * examples → muestra ejemplos de frases soportadas.
        * tokens   → muestra los tokens/clases básicos.
        * exit     → sale del modo interactivo.
    - Para cualquier otra entrada, ejecuta `run_conversion` con los mismos `args`.
    """
    print(Fore.CYAN + "Modo interactivo (TAB = autocompletar).")
    print(Fore.CYAN + "Comandos: help, examples, tokens, exit.\n")

    # Autocompletador específico del DSL
    completer = DSLCompleter()

    # Historial de entradas del usuario, persistente entre ejecuciones
    history = FileHistory(".traductorregex_history")

    # Bucle principal del REPL
    while True:
        # prompt_toolkit se encarga de:
        # - mostrar el prompt
        # - gestionar autocompletado (TAB)
        # - registrar en el historial
        phrase = prompt("Frase > ", completer=completer, history=history)
<<<<<<< HEAD
        cleaned = phrase.strip().lower()

=======

        # Versión “limpia” de la entrada para detectar comandos
        cleaned = phrase.strip().lower()

        # Comando: salir del modo interactivo
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        if cleaned == "exit":
            print(Fore.CYAN + "Saliendo del modo interactivo.")
            break

        # Comando: ayuda general del DSL
        if cleaned == "help":
            print(show_help())
            continue

        # Comando: ejemplos de uso
        if cleaned == "examples":
            print(show_examples())
            continue

        # Comando: lista de tokens/clases semánticas
        if cleaned == "tokens":
            print(show_tokens())
            continue

<<<<<<< HEAD
=======
        # Entrada vacía → advertimos y pedimos de nuevo
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        if not phrase.strip():
            print(Fore.YELLOW + "No escribiste ninguna frase.")
            continue

        # Cualquier otra cosa se trata como frase a traducir
        run_conversion(phrase, args)


def test_regex(pattern, text):
    """
    Prueba si la cadena `text` coincide completamente con el patrón `pattern`.

    - Usa `re.fullmatch` para requerir coincidencia total.
    - Imprime ✓ si coincide.
    - Imprime ✗ si no coincide.
    - Si hay un error al compilar/usar la regex, se informa.
    """
    try:
        # `fullmatch` exige que la regex cubra toda la cadena de prueba
        if re.fullmatch(pattern, text):
            print(Fore.GREEN + f"✓ '{text}' coincide.")
        else:
            print(Fore.RED + f"✗ '{text}' NO coincide.")
    except Exception as e:
        # Por ejemplo, si el patrón es inválido para `re`
        print(Fore.YELLOW + f"Error usando regex: {e}")


# Solo se ejecuta `main()` si este archivo se corre directamente,
# no cuando se importa como módulo desde otro archivo.
if __name__ == "__main__":
    main()

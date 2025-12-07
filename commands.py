from colorama import Fore

def show_help():
    return (
        Fore.CYAN + "Comandos disponibles:\n"
        "  help       - Muestra esta ayuda\n"
        "  examples   - Ejemplos de frases válidas\n"
        "  tokens     - Palabras clave del DSL\n"
        "  exit       - Salir del modo interactivo\n"
    )

def show_examples():
    return (
        Fore.GREEN + "Ejemplos:\n"
        "  letter followed by digit\n"
        "  uppercase letter followed by digit zero or more\n"
        "  'hello' followed by digit between 2 and 4 times\n"
        "  letter one or more or digit one or more\n"
    )

def show_tokens():
    return (
        Fore.YELLOW + "Tokens válidos:\n"
        "letter\n"
        "digit\n"
        "space\n"
        "any character\n"
        "uppercase letter\n"
        "lowercase letter\n"
        "'a', 'b', '1', '@'\n"
        "optional, one or more, zero or more\n"
        "X times, between X and Y times\n"
        "followed by, or\n"
    )
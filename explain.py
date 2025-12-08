from colorama import Fore

def explain_phrase_and_regex(phrase, regex):
    """
    Explica de manera simple cómo se construyó la regex.
    (No perfecto, pero útil para usuarios principiantes.)
    """

    explanation = Fore.CYAN + "Explicación:\n"

    explanation += Fore.GREEN + f"Frase: {phrase}\n"
    explanation += Fore.GREEN + f"Regex: {regex}\n\n"

    # Nuevas interpretaciones agregadas al diccionario
    parts = {
        "letter": "[a-zA-Z]",
        "digit": "[0-9]",
        "space": r"\s",
        "any character": ".",
        "uppercase letter": "[A-Z]",
        "lowercase letter": "[a-z]",

        # Nuevos tokens
        "vowel": "[aeiouAEIOU]",
        "consonant": "[b-df-hj-np-tv-zB-DF-HJ-NP-TV-Z]",
        "word character": r"\w",
        "alphanumeric": "[A-Za-z0-9]",
        "hex digit": "[0-9A-Fa-f]",
        "whitespace": r"\s",
        "range": "rango de caracteres",
    }

    explanation += Fore.YELLOW + "Interpretación:\n"

    for word, exp in parts.items():
        if word in phrase:
            explanation += f"  {word} → {exp}\n"

    # Repeticiones básicas
    if "one or more" in phrase:
        explanation += "  one or more → +\n"
    if "zero or more" in phrase:
        explanation += "  zero or more → *\n"
    if "optional" in phrase:
        explanation += "  optional → ?\n"
    if "times" in phrase and "at least" not in phrase and "at most" not in phrase:
        explanation += "  X times → {X}\n"
    if "between" in phrase:
        explanation += "  between X and Y times → {X,Y}\n"

    # Nuevas repeticiones
    if "at least" in phrase:
        explanation += "  at least X times → {X,}\n"
    if "at most" in phrase:
        explanation += "  at most X times → {0,X}\n"

    # Explicación del range
    if "range" in phrase:
        explanation += "  range 'a' to 'z' → [a-z]\n"

    explanation += "\n" + Fore.CYAN + "Regex final: " + Fore.GREEN + regex
    return explanation

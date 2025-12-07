from colorama import Fore

def explain_phrase_and_regex(phrase, regex):
    """
    Explica de manera simple cómo se construyó la regex.
    (No perfecto, pero útil para usuarios principiantes.)
    """

    explanation = Fore.CYAN + "Explicación:\n"

    explanation += Fore.GREEN + f"Frase: {phrase}\n"
    explanation += Fore.GREEN + f"Regex: {regex}\n\n"

    parts = {
        "letter": "[a-zA-Z]",
        "digit": "[0-9]",
        "space": r"\s",
        "any character": ".",
        "uppercase letter": "[A-Z]",
        "lowercase letter": "[a-z]",
    }

    explanation += Fore.YELLOW + "Interpretación:\n"

    for word, exp in parts.items():
        if word in phrase:
            explanation += f"  {word} → {exp}\n"

    if "one or more" in phrase:
        explanation += "  one or more → +\n"
    if "zero or more" in phrase:
        explanation += "  zero or more → *\n"
    if "optional" in phrase:
        explanation += "  optional → ?\n"
    if "times" in phrase:
        explanation += "  X times → {X}\n"
    if "between" in phrase:
        explanation += "  between X and Y times → {X,Y}\n"

    explanation += "\n" + Fore.CYAN + "Regex final: " + Fore.GREEN + regex
    return explanation
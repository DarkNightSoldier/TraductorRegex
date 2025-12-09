import re

# ===========================================================
#   NÚMEROS EN INGLÉS → ENTEROS (SIN LÍMITE DE TAMAÑO)
# ===========================================================

# Palabras básicas de número en inglés y su valor numérico
NUMWORDS_SIMPLE = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19,
}

# Decenas “largas” (twenty, thirty, ...)
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

# Escalas multiplicativas (hundred, thousand, ...)
SCALES = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1000000,
    "billion": 1000000000,
}


def words_to_number(words):
    """
    Convierte una secuencia de palabras de número en inglés a un entero.

    Parameters
    ----------
    words : list[str]
        Lista de tokens como ["one", "hundred", "twenty", "three"].

    Returns
    -------
    int | None
        Entero resultante si la secuencia es completamente numérica;
        en caso contrario devuelve None para indicar que no se pudo convertir.
    """
    current = 0      # acumulador local de la “parte actual”
    total = 0        # acumulador global cuando aparece una escala
    seen_numeric = False  # indica si alguna palabra fue reconocida como número

    for w in words:
        if w in NUMWORDS_SIMPLE:
            current += NUMWORDS_SIMPLE[w]
            seen_numeric = True

        elif w in TENS:
            current += TENS[w]
            seen_numeric = True

        elif w in SCALES:
            # Si aparece una escala sin parte previa (p. ej. "hundred"),
            # se interpreta como 1 * escala (100, 1000, etc.).
            if current == 0:
                current = 1
            current *= SCALES[w]
            total += current
            current = 0
            seen_numeric = True

        elif w == "and":
            # Conector típico de números en inglés ("one hundred and two");
            # no aporta valor numérico directo.
            continue

        else:
            # Alguna palabra no es parte de un número bien formado.
            return None

    # Si no se reconoció ninguna palabra como número, se considera fallo.
    if not seen_numeric:
        return None

    return total + current


def convert_numwords(text):
    """
    Reemplaza secuencias de palabras numéricas en inglés por su valor entero.

    Ejemplo:
        "one hundred twenty three times"
        → "123 times"

    Parameters
    ----------
    text : str
        Cadena de entrada con palabras y posibles números en inglés.

    Returns
    -------
    str
        Cadena donde cada bloque numérico reconocible se sustituye por un entero.
    """
    tokens = text.split()
    result = []   # tokens de salida
    buffer = []   # tokens numéricos pendientes de convertir

    def flush_buffer():
        """
        Convierte el contenido del buffer a número (si es posible).
        Si la secuencia no es puramente numérica, se devuelve tal cual.
        """
        if not buffer:
            return None
        number = words_to_number(buffer)
        return str(number) if number is not None else " ".join(buffer)

    i = 0
    while i < len(tokens):
        w = tokens[i]

        # Identificar si el token pertenece a un bloque numérico
        if w in NUMWORDS_SIMPLE or w in TENS or w in SCALES or w == "and":
            buffer.append(w)
        else:
            # Si veníamos acumulando un número, lo volcamos al resultado
            if buffer:
                result.append(flush_buffer())
                buffer = []
            result.append(w)
        i += 1

    # Procesar cualquier resto numérico al final del texto
    if buffer:
        result.append(flush_buffer())

    return " ".join(result)


def lowercase_outside_quotes(text: str) -> str:
    """
    Convierte a minúsculas solo la parte del texto que está fuera de comillas.

    Sirve para:
      - Normalizar frases del usuario sin perder la distinción de mayúsculas
        en rangos y literales (p.ej. 'A', 'Z').
    Las comillas simples y dobles se respetan y el contenido interno se deja igual.
    """
    result = []
    in_single = False  # estamos dentro de comillas simples
    in_double = False  # estamos dentro de comillas dobles

    for ch in text:
        if ch == "'" and not in_double:
            in_single = not in_single
            result.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            result.append(ch)
        else:
            if in_single or in_double:
                # Dentro de comillas no se toca el caso
                result.append(ch)
            else:
                # Fuera de comillas se pasa a minúscula
                result.append(ch.lower())

    return "".join(result)


# ===========================================================
#   NORMALIZADOR PRINCIPAL (PSEUDOLENGUAJE → DSL)
# ===========================================================

class Normalizer:
    """
    Encapsula todas las transformaciones de texto:
    - Limpieza de palabras irrelevantes.
    - Expansión de sinónimos.
    - Normalización de conectores y frases de repetición.
    - Conversión de números en inglés a dígitos.
    - Reescrituras estructurales para ajustarse a `grammar.lark`.
    """

    # Palabras frecuentes que no aportan estructura al DSL
    STOPWORDS = {
        "the", "a", "an", "this", "that", "which", "who", "whom",
        "pattern", "sequence", "find", "match", "should", "be",
        "like", "consisting", "made", "up", "into", "of",
        "string", "strings", "regex", "regular", "expression", "expressions",
        "please",
    }

    # Frases equivalentes a combinaciones ya soportadas en el DSL
    SYNONYMS = {
        "digits": "digit one or more",
        "numbers": "digit one or more",
        "letters": "letter one or more",
        "characters": "any character one or more",

        "lowercase letters": "lowercase letter one or more",
        "uppercase letters": "uppercase letter one or more",

        "spaces": "space one or more",
        "space characters": "space one or more",

        "whitespace": "whitespace",
        "whitespaces": "whitespace one or more",

        "vowels": "vowel one or more",
        "consonants": "consonant one or more",

        "alphanumerics": "alphanumeric one or more",
        "hex digits": "hex digit one or more",

        "non whitespaces": "non whitespace one or more",

        "word characters": "word character one or more",
        "non whitespace characters": "non whitespace one or more",
    }

    def normalize(self, text):
        """
        Aplica la cadena completa de normalización sobre la frase de entrada.

        Orden aproximado de pasos:
          1. Minúsculas fuera de comillas.
          2. Eliminación de stopwords.
          3. Manejo de "once"/"twice"/"thrice".
          4. Expansión de sinónimos.
          5. Normalización de conectores y opcionales.
          6. Reglas de repetición verbal.
          7. Conversión de números en inglés a dígitos.
          8. Ajustes específicos para expresiones como "zero or more".
          9. Reescrituras estructurales para las construcciones del DSL.
         10. Limpieza final de espacios.
        """
        # Mantener literales y rangos exactamente como se escriben
        text = lowercase_outside_quotes(text)

        # Eliminación de términos irrelevantes para la estructura
        words = [w for w in text.split() if w not in self.STOPWORDS]
        text = " ".join(words)

        # Normalización de "once", "twice", "thrice" a contadores explícitos
        text = re.sub(r"\bonce\b", "1 times", text)
        text = re.sub(r"\btwice\b", "2 times", text)
        text = re.sub(r"\bthrice\b", "3 times", text)

        # Expansión de sinónimos según el diccionario anterior
        for src, tgt in self.SYNONYMS.items():
            text = text.replace(src, tgt)

        # Unificación de conectores que implican secuencia
        text = text.replace(" then ", " followed by ")
        text = text.replace(" next ", " followed by ")

        # Manejo de frases opcionales básicas
        text = text.replace(" optionally ", " optional ")

        # Frases verbales que implican repetición
        text = re.sub(r"appear (\d+) times", r"\1 times", text)
        text = re.sub(r"repeat (\d+) times", r"\1 times", text)
        text = re.sub(r"appear(ed)?", "one or more", text)
        text = re.sub(r"repeat(ed)?", "one or more", text)

        # Conversión de palabras de número a dígitos
        text = convert_numwords(text)

        # Caso especial: "0 or more" debería mapear a "zero or more"
        text = re.sub(r"\b0 or more\b", "zero or more", text)

        # Corrección de variantes como "1 or more" → "one or more"
        text = text.replace("1 or more", "one or more")

        # Normalización de la forma "between X and Y times"
        text = re.sub(
            r"between (\d+) and (\d+) times",
            r"between \1 and \2 times",
            text,
        )

        # Patrón de clases soportadas por el DSL (para reescrituras posteriores)
        cls = (
            r"(digit|letter|lowercase letter|uppercase letter|any character|"
            r"space|vowel|consonant|alphanumeric|word character|whitespace|"
            r"non whitespace|hex digit)"
        )

        # Evitar duplicidad de "one or more one or more"
        text = text.replace("one or more one or more", "one or more")

        # "3 digit one or more" → "digit 3 times"
        text = re.sub(
            rf"\b(\d+)\s+{cls}\s+one or more\b",
            r"\2 \1 times",
            text,
        )

        # "digit one or more N times" → "digit N times"
        text = re.sub(
            rf"{cls} one or more (\d+) times",
            r"\1 \2 times",
            text,
        )

        # "digit one or more between X and Y times" → "digit between X and Y times"
        text = re.sub(
            rf"{cls} one or more between (\d+) and (\d+) times",
            r"\1 between \2 and \3 times",
            text,
        )

        # "except digit one or more" → "except digit"
        text = text.replace(" except digit one or more", " except digit")

        # "X one or more twice" → "X 2 times"
        text = re.sub(
            rf"{cls} one or more twice",
            r"\1 2 times",
            text,
        )

        # "group ... end group one or more twice" → "group ... end group 2 times"
        text = re.sub(
            r"(group .*? end group) one or more twice",
            r"\1 2 times",
            text,
        )

        # "group ... end group one or more N times" → "group ... end group N times"
        text = re.sub(
            r"(group .*? end group) one or more (\d+) times",
            r"\1 \2 times",
            text,
        )

        # Limpieza final de espacios repetidos y bordes
        text = re.sub(r"\s+", " ", text).strip()

        return text

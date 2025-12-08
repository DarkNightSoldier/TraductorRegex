import re

# ===========================================================
#   NÚMEROS EN INGLÉS → ENTEROS (ILIMITADOS)
# ===========================================================

NUMWORDS_SIMPLE = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19
}

TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
}

SCALES = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1000000,
    "billion": 1000000000
}


def words_to_number(words):
    """
    Convierte una lista de palabras de número en inglés a un entero.
    Ejemplo: ["one","hundred","twenty","three"] → 123
    """
    current = 0
    total = 0

    for w in words:

        if w in NUMWORDS_SIMPLE:
            current += NUMWORDS_SIMPLE[w]
        elif w in TENS:
            current += TENS[w]
        elif w in SCALES:
            current *= SCALES[w]
            total += current
            current = 0
        elif w == "and":
            continue
        else:
            return None  # palabra no numérica → abortar

    return total + current

def convert_numwords(text):
    """
    Busca secuencias numéricas en inglés y las reemplaza por enteros.
    Ejemplo: "one hundred twenty three times" → "123 times"
    """

    tokens = text.split()
    result = []
    buffer = []

    def flush_buffer():
        if not buffer:
            return None
        number = words_to_number(buffer)
        return str(number) if number is not None else " ".join(buffer)

    i = 0
    while i < len(tokens):
        w = tokens[i]

        # ¿Es parte de un número?
        if w in NUMWORDS_SIMPLE or w in TENS or w in SCALES or w == "and":
            buffer.append(w)
        else:
            if buffer:
                result.append(flush_buffer())
                buffer = []
            result.append(w)
        i += 1

    # vaciar buffer final
    if buffer:
        result.append(flush_buffer())

    return " ".join(result)


class Normalizer:
    """
    NLP-lite estructural final — COMPLETAMENTE COMPATIBLE
    con grammar.lark y translator.py
    """

    STOPWORDS = {
        "the","a","an","this","that","which","who","whom",
        "pattern","sequence","find","match","should","be",
        "like","consisting","made","up","into","of",
        "string","strings","regex","regular","expression","expressions",
        "please"
    }

    SYNONYMS = {
        "digits": "digit one or more",
        "numbers": "digit one or more",
        "letters": "letter one or more",
        "characters": "any character one or more",
        "lowercase letters": "lowercase letter one or more",
        "uppercase letters": "uppercase letter one or more",
        "spaces": "space one or more",
        "whitespace": "space one or more",
        "whitespaces": "space one or more",
        "space character": "space",
        "space characters": "space one or more",
        "vowels": "vowel one or more",
        "consonants": "consonant one or more",
        "alphanumerics": "alphanumeric one or more",
        "hex digits": "hex digit one or more",
        "whitespaces": "whitespace one or more",
        "non whitespaces": "non whitespace one or more",
    }

    NUMWORDS = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    def normalize(self, text):
        text = text.lower()

        # ---------------- STOPWORDS ----------------
        words = [w for w in text.split() if w not in self.STOPWORDS]
        text = " ".join(words)

        # ---------------- ONCE / TWICE / THRICE ----------------
        text = re.sub(r"\bonce\b", "1 times", text)
        text = re.sub(r"\btwice\b", "2 times", text)
        text = re.sub(r"\bthrice\b", "3 times", text)

        # ---------------- SYNONYMS -----------------
        for src, tgt in self.SYNONYMS.items():
            text = text.replace(src, tgt)

        # ---------------- NUMWORDS -----------------
        for w, n in self.NUMWORDS.items():
            text = re.sub(fr"\b{w}\b", str(n), text)

        # ---------------- CONNECTORS ----------------
        text = text.replace(" then ", " followed by ")
        text = text.replace(" next ", " followed by ")

        # ---------------- OPTIONAL -------------------
        text = text.replace(" optionally ", " optional ")

        # ---------------- VERBAL REPETITION ----------
        text = re.sub(r"appear (\d+) times", r"\1 times", text)
        text = re.sub(r"repeat (\d+) times", r"\1 times", text)
        text = re.sub(r"appear(ed)?", "one or more", text)
        text = re.sub(r"repeat(ed)?", "one or more", text)

        # --- REEMPLAZAR NÚMEROS EN INGLÉS POR ENTEROS ---
        text = convert_numwords(text)

        # ---------------- SANITY CLEANUP ------------
        text = text.replace("1 or more", "one or more")

        # ---------------- BETWEEN --------------------
        text = re.sub(
            r"between (\d+) and (\d+) times",
            r"between \1 and \2 times",
            text
        )

        #  FIX 1 — "3 digit one or more" → "digit 3 times"
        text = re.sub(
            r"\b(\d+)\s+(digit|letter|lowercase letter|uppercase letter|any character|space)\s+one or more\b",
            r"\2 \1 times",
            text
        )

        #  FIX 2 — "digit one or more N times" → "digit N times"
        text = re.sub(
            r"(digit|letter|lowercase letter|uppercase letter|any character|space) one or more (\d+) times",
            r"\1 \2 times",
            text
        )

        #  FIX 3 — "digit one or more between X and Y times"
        text = re.sub(
            r"(digit|letter|lowercase letter|uppercase letter|any character|space) one or more between (\d+) and (\d+) times",
            r"\1 between \2 and \3 times",
            text
        )

        #  FIX 4 — "one or more one or more" → "one or more"
        text = text.replace("one or more one or more", "one or more")

        #  FIX 5 — "except digit one or more" → "except digit"
        text = text.replace(" except digit one or more", " except digit")

        #  FIX 6 — "X one or more twice" → "X 2 times"
        text = re.sub(
            r"(digit|letter|lowercase letter|uppercase letter|any character|space) one or more twice",
            r"\1 2 times",
            text
        )

        #  FIX 7 — "group ... end group one or more twice"
        text = re.sub(
            r"(group .*? end group) one or more twice",
            r"\1 2 times",
            text
        )

        # FIX 8 — "X one or more between A and B times" → "X between A and B times"
        text = re.sub(
            r"(digit|letter|lowercase letter|uppercase letter|any character|space) one or more between (\d+) and (\d+) times",
            r"\1 between \2 and \3 times",
            text
        )

        # ---------------- FINAL CLEANUP --------------
        text = re.sub(r"\s+", " ", text).strip()

        return text
    
    

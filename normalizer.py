import re

class Normalizer:
    """
    NLP-lite estructural final — COMPLETAMENTE COMPATIBLE
    con grammar.lark y translator.py
    """

    STOPWORDS = {
        "the","a","an","this","that","which","who","whom",
        "pattern","sequence","find","match","should","be",
        "like","consisting","made","up","into","of"
    }

    SYNONYMS = {
        "digits": "digit one or more",
        "numbers": "digit one or more",
        "letters": "letter one or more",
        "characters": "any character one or more",
        "lowercase letters": "lowercase letter one or more",
        "uppercase letters": "uppercase letter one or more"
    }

    NUMWORDS = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    def normalize(self, text):
        text = text.lower()

        # ---------------- STOPWORDS ----------------
        words = [w for w in text.split() if w not in self.STOPWORDS]
        text = " ".join(words)

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
            r"\b(\d+)\s+(digit|letter|lowercase letter|uppercase letter|any character)\s+one or more\b",
            r"\2 \1 times",
            text
        )

        
        #  FIX 2 — "digit one or more N times" → "digit N times"
        text = re.sub(
            r"(digit|letter|lowercase letter|uppercase letter|any character) one or more (\d+) times",
            r"\1 \2 times",
            text
        )

        #  FIX 3 — "digit one or more between X and Y times"
        text = re.sub(
            r"(digit|letter|lowercase letter|uppercase letter|any character) one or more between (\d+) and (\d+) times",
            r"\1 between \2 and \3 times",
            text
        )

        #  FIX 4 — "one or more one or more" → "one or more"
        text = text.replace("one or more one or more", "one or more")

        #  FIX 5 — "except digit one or more" → "except digit"
        text = text.replace(" except digit one or more", " except digit")

        #  FIX 6 — "X one or more twice" → "X 2 times"
        text = re.sub(
            r"(digit|letter|lowercase letter|uppercase letter|any character) one or more twice",
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
            r"(digit|letter|lowercase letter|uppercase letter|any character) one or more between (\d+) and (\d+) times",
            r"\1 between \2 and \3 times",
            text
        )

        # ---------------- FINAL CLEANUP --------------
        text = re.sub(r"\s+", " ", text).strip()

        return text
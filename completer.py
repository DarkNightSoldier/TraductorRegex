from prompt_toolkit.completion import Completer, Completion

# Palabras del DSL
TERMS = [
    # clases básicas
    "letter", "digit", "space", "any character",
    "uppercase letter", "lowercase letter",

    # clases extendidas
    "vowel", "consonant",
    "word character",
    "alphanumeric",
    "hex digit",
    "whitespace",
    "non whitespace",

    # literales simples de ejemplo
    "'a'", "'b'", "'c'", "'@'", "'1'",

    # range
    "range",   # permite sugerir "range" como palabra clave
]

REPETITIONS = [
    "optional", "one or more", "zero or more",
    "times", "between", "and",
    "at least", "at most"
]

CONNECTORS = [
    "followed by", "or"
]


class DSLCompleter(Completer):
    """
    Autocompletado contextual del DSL.
    Sugiere términos, repeticiones o conectores dependiendo
    de la última palabra escrita por el usuario.
    """

    def get_completions(self, document, complete_event):

        text = document.text_before_cursor.strip()
        last = text.split()[-1] if text else ""

        # Si no hay nada escrito → ofrecer todo
        if not text:
            for w in TERMS + REPETITIONS + CONNECTORS:
                yield Completion(w, start_position=0)
            return

        # Si se acaba de poner un término → sugerir repeticiones o conectores
        if text in TERMS or last in TERMS:
            for w in REPETITIONS + CONNECTORS:
                yield Completion(w, start_position=0)
            return

        # Si se puso una repetición → sugerir conectores
        if last in ["optional", "one", "zero", "times", "more",
                    "between", "and", "at", "least", "most"]:
            for w in CONNECTORS:
                yield Completion(w, start_position=0)
            return

        # Autocompletado básico por prefijo
        for w in TERMS + REPETITIONS + CONNECTORS:
            if w.startswith(last):
                yield Completion(w, start_position=-len(last))

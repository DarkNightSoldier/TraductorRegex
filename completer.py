"""
Módulo `completer.py`

Define el autocompletador del DSL para el modo interactivo del CLI,
usando `prompt_toolkit`.

La idea es sugerir:

- TÉRMINOS (clases de caracteres, literales, etc.)
- REPETICIONES (cuantificadores como "one or more", "between X and Y times", etc.)
- CONECTORES ("followed by", "or")

en función de lo que el usuario vaya escribiendo.
"""

from prompt_toolkit.completion import Completer, Completion

# ----------------------------------------------------------------------
# LISTAS DE PALABRAS CLAVE DEL DSL
# ----------------------------------------------------------------------

# Términos básicos y avanzados que describen clases de caracteres
TERMS = [
<<<<<<< HEAD
    # clases básicas
    "letter", "digit", "space", "any character",
    "uppercase letter", "lowercase letter",

    # clases extendidas
    "vowel", "consonant",
=======
    "letter",
    "digit",
    "space",
    "any character",
    "uppercase letter",
    "lowercase letter",
    "vowel",
    "consonant",
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
    "word character",
    "alphanumeric",
    "hex digit",
    "whitespace",
    "non whitespace",
<<<<<<< HEAD

    # literales simples de ejemplo
    "'a'", "'b'", "'c'", "'@'", "'1'",

    # range
    "range",   # permite sugerir "range" como palabra clave
=======
    # Algunos literales de ejemplo / uso frecuente
    "'a'",
    "'b'",
    "'c'",
    "'@'",
    "'1'",
    # Palabra clave para rangos
    "range",
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
]

# Palabras relacionadas con cuantificadores y repeticiones
REPETITIONS = [
<<<<<<< HEAD
    "optional", "one or more", "zero or more",
    "times", "between", "and",
    "at least", "at most"
=======
    "optional",
    "one or more",
    "zero or more",
    "times",
    "between",
    "and",
    "at least",
    "at most",
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
]

# Conectores para encadenar términos y grupos
CONNECTORS = [
    "followed by",
    "or",
]


class DSLCompleter(Completer):
    """
    Autocompletador para el DSL de TraductorRegex.

    Implementa la interfaz de `prompt_toolkit.completion.Completer`,
    devolviendo objetos `Completion` según el contexto:

    - Si el usuario no ha escrito nada → sugerir TODO (TERMS + REPETITIONS + CONNECTORS).
    - Si lo último que escribió es un TÉRMINO → sugerir REPETITIONS + CONNECTORS.
    - Si lo último que escribió parece parte de una repetición (ej: "between", "times") →
      sugerir CONNECTORS (para seguir la frase).
    - En cualquier otro caso → sugerencias por prefijo, comparando el "último token"
      con los TERMS + REPETITIONS + CONNECTORS.
    """

    def get_completions(self, document, complete_event):
        """
        Genera sugerencias de autocompletado en función del texto antes del cursor.

        Parámetros:
        - document: objeto de prompt_toolkit con el estado actual de la edición.
        - complete_event: evento de completado (no se usa aquí, pero la interfaz lo exige).
        """

        # Texto completo que el usuario ha escrito antes del cursor
        text = document.text_before_cursor.strip()

        # Última "palabra" (token) según espacios; sirve para decidir el contexto
        last = text.split()[-1] if text else ""

        # ------------------------------------------------------------------
        # CASO 1: No hay texto todavía → ofrecemos TODO el vocabulario
        # ------------------------------------------------------------------
        if not text:
            for w in TERMS + REPETITIONS + CONNECTORS:
                # start_position=0 → insertar desde el inicio de la línea
                yield Completion(w, start_position=0)
            return

        # ------------------------------------------------------------------
        # CASO 2: El texto completo o la última palabra coincide con un TÉRMINO
        #         Ejemplo: "letter", "digit", "uppercase letter"
        #         → lo natural es sugerir una repetición o un conector.
        # ------------------------------------------------------------------
        if text in TERMS or last in TERMS:
            for w in REPETITIONS + CONNECTORS:
                # start_position=0 → se añade al final, no reemplaza nada
                yield Completion(w, start_position=0)
            return

<<<<<<< HEAD
        # Si se puso una repetición → sugerir conectores
        if last in ["optional", "one", "zero", "times", "more",
                    "between", "and", "at", "least", "most"]:
=======
        # ------------------------------------------------------------------
        # CASO 3: El último token forma parte de expresiones de repetición
        #         (ej: "optional", "one", "zero", "times", "between", etc.)
        #         → sugerimos conectores ("followed by", "or") para seguir la frase.
        # ------------------------------------------------------------------
        if last in ["optional", "one", "zero", "times", "more", "between", "and", "at", "least", "most"]:
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
            for w in CONNECTORS:
                yield Completion(w, start_position=0)
            return

        # ------------------------------------------------------------------
        # CASO 4: Búsqueda por prefijo
        #
        # Si ninguno de los casos anteriores aplica, buscamos todas las palabras
        # (TERMS + REPETITIONS + CONNECTORS) que empiecen por `last`.
        #
        # Ejemplo: el usuario ha escrito "upp" → sugerimos "uppercase letter".
        # ------------------------------------------------------------------
        for w in TERMS + REPETITIONS + CONNECTORS:
            if w.startswith(last):
<<<<<<< HEAD
=======
                # start_position negativo: número de caracteres a reemplazar
                # desde la posición actual (el prefijo ya escrito).
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
                yield Completion(w, start_position=-len(last))

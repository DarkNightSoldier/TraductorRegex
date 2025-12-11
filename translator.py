"""
Módulo `translator.py`

Contiene la clase `RegexTranslator`, un `Transformer` de Lark que
recorre el AST producido por `grammar.lark` y lo convierte en una
expresión regular.

Regla de oro:
- Cada método con nombre de regla/token en la gramática devuelve
  un fragmento de regex (str).
- El árbol completo se traduce combinando esos fragmentos.
"""

from lark import Transformer, Tree


class RegexTranslator(Transformer):
    """
    Transformer de Lark que convierte cada nodo del AST en un fragmento de regex.

<<<<<<< HEAD
    # ---------- BASE TERMS ----------
    def t_letter(self, _):
        return "[a-zA-Z]"

    def t_digit(self, _):
        return "[0-9]"

    def t_space(self, _):
        # "space" en tu DSL lo tratamos como whitespace genérico
        return r"\s"

    def t_any(self, _):
        return "."

    def t_upper(self, _):
        return "[A-Z]"

    def t_lower(self, _):
        return "[a-z]"

    def t_vowel(self, _):
        return "[AEIOUaeiou]"

    def t_consonant(self, _):
        # Todas las consonantes inglesas explícitas
        return "[BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz]"

    def t_alphanumeric(self, _):
        return "[A-Za-z0-9]"

    def t_word(self, _):
        # Aquí sí queremos \w explícitamente para "word character"
        return r"\w"

    def t_hex(self, _):
        return "[0-9A-Fa-f]"

    def t_whitespace(self, _):
        return r"\s"

    def t_non_whitespace(self, _):
        return r"\S"

    def t_range(self, children):
        # children son dos CHAR_LITERAL tipo "'a'", "'z'"
        c1 = children[0][1:-1]
        c2 = children[1][1:-1]
        return f"[{c1}-{c2}]"

    def t_char(self, tok):
        # tok es un Token con valor "'a'" → nos quedamos con a
        return tok[0][1:-1]

    def t_string(self, tok):
        # "'hello'" → "hello"
        return tok[0][1:-1]
=======
    La firma de cada método coincide con el nombre de la regla o token en
    `grammar.lark`. Lark llama automáticamente a estos métodos al recorrer
    el árbol.
    """

    # ------------------------------------------------------------------
    #  CLASES BÁSICAS DE CARACTERES (BASE TERMS)
    # ------------------------------------------------------------------

    def t_letter(self, _):
        """
        Regla: t_letter
        Representa cualquier letra (mayúscula o minúscula).
        """
        return "[a-zA-Z]"

    def t_digit(self, _):
        """
        Regla: t_digit
        Representa cualquier dígito decimal.
        """
        return "[0-9]"

    def t_space(self, _):
        """
        Regla: t_space
        Un espacio según el DSL; se mapea a whitespace genérico.
        """
        return r"\s"

    def t_any(self, _):
        """
        Regla: t_any
        Cualquier carácter (.) en regex.
        """
        return "."

    def t_upper(self, _):
        """
        Regla: t_upper
        Letra mayúscula.
        """
        return "[A-Z]"

    def t_lower(self, _):
        """
        Regla: t_lower
        Letra minúscula.
        """
        return "[a-z]"

    def t_vowel(self, _):
        """
        Regla: t_vowel
        Vocal (mayúscula o minúscula).
        """
        return "[AEIOUaeiou]"

    def t_consonant(self, _):
        """
        Regla: t_consonant
        Consonantes inglesas explícitas (mayúsculas y minúsculas).
        """
        return "[BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz]"

    def t_alphanumeric(self, _):
        """
        Regla: t_alphanumeric
        Carácter alfanumérico.
        """
        return "[A-Za-z0-9]"

    def t_word(self, _):
        """
        Regla: t_word
        Carácter de palabra tal como lo entiende regex: \w
        """
        return r"\w"

    def t_hex(self, _):
        """
        Regla: t_hex
        Dígito hexadecimal.
        """
        return "[0-9A-Fa-f]"

    def t_whitespace(self, _):
        """
        Regla: t_whitespace
        Carácter de espacio en blanco (incluye tabs, saltos de línea, etc.).
        """
        return r"\s"

    def t_non_whitespace(self, _):
        """
        Regla: t_non_whitespace
        Cualquier carácter que NO sea whitespace.
        """
        return r"\S"

    # ------------------------------------------------------------------
    #  RANGOS DE CARACTERES
    # ------------------------------------------------------------------

    def t_range(self, children):
        """
        Regla: t_range

        Traduce algo como:
            range 'a' to 'z'
        a la regex:
            [a-z]

        Estructura típica en el AST:

            t_range
              range_expr
                'a'
                'z'
        """
        flat = []
        for ch in children:
            # Si el hijo es un subárbol (p.ej. `range_expr`),
            # añadimos sus hijos directamente.
            if isinstance(ch, Tree):
                flat.extend(ch.children)
            else:
                flat.append(ch)

        if len(flat) < 2:
            # Si por alguna razón no hay dos extremos de rango, devolvemos vacío.
            return ""

        def _unquote(tok):
            """
            Quita comillas simples o dobles de un token literal.
            Ej: "'a'" → "a", '"Z"' → "Z".
            """
            s = str(tok)
            if len(s) >= 2 and (s[0] in ("'", '"')) and s[-1] == s[0]:
                return s[1:-1]
            return s

        c1 = _unquote(flat[0])
        c2 = _unquote(flat[1])
        return f"[{c1}-{c2}]"

    # ------------------------------------------------------------------
    #  LITERALES
    # ------------------------------------------------------------------

    def t_char(self, children):
        """
        Regla: t_char

        Literal de un solo carácter, p.ej.:
            'a' → a
        """
        tok = children[0]
        s = str(tok)
        if len(s) >= 2 and (s[0] in ("'", '"')) and s[-1] == s[0]:
            return s[1:-1]
        return s

    def t_string(self, children):
        """
        Regla: t_string

        Literal de cadena, p.ej.:
            'hello' → hello
        """
        tok = children[0]
        s = str(tok)
        if len(s) >= 2 and (s[0] in ("'", '"')) and s[-1] == s[0]:
            return s[1:-1]
        return s

    # ------------------------------------------------------------------
    #  NEGACIÓN / EXCEPT
    # ------------------------------------------------------------------
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593

    def t_except(self, children):
        """
        Regla: t_except

        Representa construcciones tipo:
            letter except 'a'

        En el AST viene como:
            t_except
              base
              conjunto_a_excluir

        Aquí tomamos el complemento del segundo argumento:
          [abc] → [^abc]
        """
        base, neg = children
<<<<<<< HEAD
        # Por ahora ignoramos 'base' y tomamos el complemento de 'neg'
        neg_inside = str(neg).strip("[]")
        return f"[^{neg_inside}]"

    # ---------- REPETITIONS ----------
    def r_optional(self, _):
        return "?"

    def r_one_or_more(self, _):
        return "+"

    def r_zero_or_more(self, _):
        return "*"

    def r_exact(self, children):
        return f"{{{children[0]}}}"

    def r_range(self, children):
        return f"{{{children[0]},{children[1]}}}"

    def r_at_least(self, children):
        return f"{{{children[0]},}}"

    def r_at_most(self, children):
        return f"{{0,{children[0]}}}"
=======
        neg_inside = str(neg).strip("[]")
        return f"[^{neg_inside}]"

    # ------------------------------------------------------------------
    #  CUANTIFICADORES (REPETITIONS)
    # ------------------------------------------------------------------

    def r_optional(self, _):
        """
        Regla: r_optional
        Cuantificador "optional" → ?
        """
        return "?"

    def r_one_or_more(self, _):
        """
        Regla: r_one_or_more
        Cuantificador "one or more" → +
        """
        return "+"

    def r_zero_or_more(self, _):
        """
        Regla: r_zero_or_more
        Cuantificador "zero or more" → *
        """
        return "*"

    def r_exact(self, children):
        """
        Regla: r_exact
        "exactly N times" → {N}
        """
        return f"{{{children[0]}}}"

    def r_range(self, children):
        """
        Regla: r_range
        "between N and M times" → {N,M}
        """
        return f"{{{children[0]},{children[1]}}}"

    def r_at_least(self, children):
        """
        Regla: r_at_least
        "at least N times" → {N,}
        """
        return f"{{{children[0]},}}"

    def r_at_most(self, children):
        """
        Regla: r_at_most
        "at most N times" → {0,N}
        """
        return f"{{0,{children[0]}}}"

    # ------------------------------------------------------------------
    #  TÉRMINOS BÁSICOS (ENVOLTORIOS)
    # ------------------------------------------------------------------
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593

    def term(self, children):
        """
        Regla: term
        Envoltorio que delega directamente en su único hijo.
        """
        return children[0]

    def base_term(self, children):
        """
        Regla: base_term
        Otro envoltorio que solo retorna su hijo.
        """
        return children[0]

    # ------------------------------------------------------------------
    #  TÉRMINOS REPETIDOS
    # ------------------------------------------------------------------

    def repeated_term(self, children):
        """
<<<<<<< HEAD
        children puede ser:
=======
        Regla: repeated_term

        Combina un término con uno o dos cuantificadores posibles.

        Casos típicos:
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
          [term]
          [rep_before, term]
          [term, rep_after]
          [rep_before, term, rep_after]
<<<<<<< HEAD
        """
=======

        Donde cada cuantificador puede ser:
          ?, +, *, {N}, {N,M}, {N,}, {0,N}
        """
        # Convertimos todo a string para simplificar la combinación final
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        children = [str(c) for c in children]

        if len(children) == 1:
            # Solo un término sin repetición explícita
            return children[0]

        if len(children) == 2:
            # Dos elementos: o bien [rep, term] o [term, rep]
            a, b = children
            rep_symbols = ["?", "+", "*"]
<<<<<<< HEAD
            # a = repetición antes del término
            if a.startswith("{") or a in rep_symbols:
                return b + a
            # a = término, b = repetición
=======
            # Si `a` parece ser un cuantificador, lo aplicamos después de `b`
            if a.startswith("{") or a in rep_symbols:
                return b + a
            # En caso contrario, asumimos que `b` es el cuantificador de `a`
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
            return a + b

        if len(children) == 3:
            # Tres elementos: cuantificador antes y después de un mismo término
            rep_before, term, rep_after = children
            return term + rep_before + rep_after

        # Cualquier caso raro con más de tres elementos: concatenación directa
        return "".join(children)

    # ------------------------------------------------------------------
    #  AGRUPACIÓN (GRUPOS)
    # ------------------------------------------------------------------

    def group(self, children):
        """
        Regla: group

        Formas:
          (sequence)
          (sequence)repetition

        children[0] → parte agrupada
        children[1] → cuantificador opcional
        """
        children = [str(c) for c in children]
        if len(children) == 1:
            return "(" + children[0] + ")"
        # children[1] suele ser la repetición (ej. {2}, +, ?, etc.)
        return "(" + children[0] + ")" + children[1]

    # ------------------------------------------------------------------
    #  SECUENCIAS
    # ------------------------------------------------------------------

    def sequence(self, children):
        """
        Regla: sequence
        Concatenación directa de todos los elementos.
        """
        return "".join(str(c) for c in children)

    # ------------------------------------------------------------------
    #  ALTERNATIVAS (OR)
    # ------------------------------------------------------------------

    def or_expr(self, children):
        """
        Regla: or_expr
        Alternativa entre dos expresiones: (A|B).
        """
        return "(" + str(children[0]) + "|" + str(children[1]) + ")"

    # ------------------------------------------------------------------
    #  ELEMENTOS (ENVOLTORIO)
    # ------------------------------------------------------------------

    def element(self, children):
        """
        Regla: element
        Envoltorio sencillo que devuelve su único hijo.
        """
        return children[0]

    # ------------------------------------------------------------------
    #  NODO INICIAL (START)
    # ------------------------------------------------------------------

    def start(self, children):
<<<<<<< HEAD
=======
        """
        Regla: start
        Punto de entrada de la gramática; devuelve la expresión raíz.
        """
>>>>>>> c2e13238c6ee0f0eebeed2a6b7618046035fb593
        return children[0]

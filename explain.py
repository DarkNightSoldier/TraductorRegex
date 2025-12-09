"""
Módulo `explain.py`

Se encarga de generar una explicación textual paso a paso de cómo
se construye la expresión regular a partir de la frase en DSL:

1. Muestra la frase original y su versión normalizada.
2. Construye el AST usando `parse_normalized` (Lark).
3. Recorre el AST con `explain_tree` para ir armando la regex
   y acumulando mensajes explicativos.
4. Muestra la regex final (ya generada por el traductor principal).
"""

from colorama import Fore
from lark_parser import normalize_text, parse_normalized


def explain_phrase_and_regex(phrase, final_regex):
    """
    Punto de entrada de la explicación.

    Parámetros
    ----------
    phrase : str
        Frase original que el usuario escribió en el DSL/pseudolenguaje.
    final_regex : str
        Regex que ya fue generada por el pipeline principal
        (normalizer + parser + translator + optimizaciones).

    Retorna
    -------
    str
        Cadena con varias secciones:
          - Normalización
          - AST generado
          - Explicación estructural
          - Regex final
    """
    explanation = []

    # 1) Normalizar la frase con el mismo normalizador usado por el traductor
    normalized = normalize_text(phrase)

    explanation.append(Fore.CYAN + "=== Normalización ===")
    explanation.append(Fore.GREEN + f"Frase original: {phrase}")
    explanation.append(Fore.GREEN + f"DSL normalizado: {normalized}\n")

    # 2) Construir el AST a partir del DSL normalizado
    try:
        tree = parse_normalized(normalized)
    except Exception as e:
        # Si el parser falla, devolvemos un mensaje de error
        return Fore.RED + f"ERROR al generar AST: {e}"

    explanation.append(Fore.CYAN + "=== AST generado ===")
    # `pretty()` dibuja el árbol de forma legible
    explanation.append(tree.pretty() + "\n")

    # 3) Recorrer recursivamente el AST para explicar la estructura
    explanation.append(Fore.CYAN + "=== Explicación estructural ===")
    built_regex, steps = explain_tree(tree)
    explanation.extend(steps)

    # 4) Mostrar la regex final (la que realmente se usa)
    explanation.append("\n" + Fore.CYAN + "=== Regex final ===")
    explanation.append(Fore.GREEN + final_regex)

    return "\n".join(explanation)


def explain_tree(tree):
    """
    Función recursiva que explica un nodo del AST y todos sus hijos.

    Parámetros
    ----------
    tree : lark.Tree o lark.Token
        Nodo actual del AST.

    Retorna
    -------
    (regex, steps) : (str, list[str])
        - regex : fragmento de expresión regular producido por este nodo.
        - steps : lista de líneas de explicación (con colores) sobre cómo
                  se construyó ese fragmento.
    """
    # `data` es el nombre de la regla (para Tree); para Token no existe
    nodetype = getattr(tree, "data", None)

    # ------------------------------------------------------------------
    # CASO 1: TERMINALES (Tokens)
    # Si `nodetype` es None, Lark nos ha dado un Token (valor textual).
    # ------------------------------------------------------------------
    if nodetype is None:
        token = str(tree)
        return token, [Fore.YELLOW + f"Terminal literal → '{token}'"]

    # ------------------------------------------------------------------
    # CASO 2: Nodo raíz 'start'
    # Representa el punto de entrada de la gramática.
    # ------------------------------------------------------------------
    if nodetype == "start":
        if not tree.children:
            return "", [Fore.RED + "Árbol vacío en 'start'."]
        # Por diseño asumimos un único hijo que contiene toda la expresión
        regex, steps = explain_tree(tree.children[0])
        steps.append(Fore.YELLOW + f"start → expresión completa: {regex}")
        return regex, steps

    # ------------------------------------------------------------------
    # CASO 3: Nodos envoltorio simples ('element', 'term')
    # Solo concatenan lo que producen sus hijos.
    # ------------------------------------------------------------------
    if nodetype in ("element", "term"):
        parts = []
        steps = []
        for ch in tree.children:
            r, s = explain_tree(ch)
            parts.append(r)
            steps.extend(s)
        regex = "".join(parts)
        steps.append(Fore.YELLOW + f"{nodetype} → {regex}")
        return regex, steps

    # ------------------------------------------------------------------
    # CASO 4: Términos base (clases de caracteres y atajos)
    # Cada entrada mapea una regla de la gramática a:
    #    (regex, descripción legible)
    # ------------------------------------------------------------------
    base_map = {
        "t_digit": ("[0-9]", "digit → [0-9]"),
        "t_letter": ("[a-zA-Z]", "letter → [a-zA-Z]"),
        "t_space": (r"\s", "space → \\s"),
        "t_any": (".", "any character → ."),
        "t_upper": ("[A-Z]", "uppercase letter → [A-Z]"),
        "t_lower": ("[a-z]", "lowercase letter → [a-z]"),
        "t_vowel": ("[AEIOUaeiou]", "vowel → [AEIOUaeiou]"),
        "t_consonant": (
            "[BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz]",
            "consonant → all consonants",
        ),
        "t_word": (r"\w", "word character → \\w"),
        "t_alphanumeric": ("[A-Za-z0-9]", "alphanumeric → [A-Za-z0-9]"),
        "t_hex": ("[0-9A-Fa-f]", "hex digit → [0-9A-Fa-f]"),
        "t_whitespace": (r"\s", "whitespace → \\s"),
        "t_non_whitespace": (r"\S", "non whitespace → \\S"),
    }

    if nodetype in base_map:
        regex, desc = base_map[nodetype]
        return regex, [Fore.YELLOW + desc]

    # ------------------------------------------------------------------
    # CASO 5: Rango explícito (t_range)
    #
    # Estructura esperada en el AST:
    #   t_range
    #     range_expr
    #       'a'
    #       'z'
    #
    # De aquí construimos [a-z] o [A-Z], respetando comillas/literal.
    # ------------------------------------------------------------------
    if nodetype == "t_range":
        if not tree.children:
            return "", [Fore.RED + "Árbol de rango sin hijos."]

        range_node = tree.children[0]

        # Si el primer hijo es un sub-árbol (p.ej. range_expr), tomamos sus hijos
        if hasattr(range_node, "children") and len(range_node.children) >= 2:
            raw1 = str(range_node.children[0])
            raw2 = str(range_node.children[1])
        else:
            # Fallback: asumimos que los hijos de t_range son directamente 'a', 'z'
            raw1 = str(tree.children[0])
            raw2 = str(tree.children[1]) if len(tree.children) > 1 else ""

        # Función auxiliar para quitar comillas de 'a', "A", etc.
        def _unquote(s: str) -> str:
            if len(s) >= 2 and (s[0] in ("'", '"')) and s[-1] == s[0]:
                return s[1:-1]
            return s

        c1 = _unquote(raw1)
        c2 = _unquote(raw2)
        r = f"[{c1}-{c2}]"
        return r, [Fore.YELLOW + f"range '{c1}' to '{c2}' → {r}"]

    # ------------------------------------------------------------------
    # CASO 6: Literal de carácter (t_char)
    #   Ej: 'a' → a
    # ------------------------------------------------------------------
    if nodetype == "t_char":
        tok = str(tree.children[0])
        # Quitamos las comillas externas
        ch = tok[1:-1]
        r = ch
        return r, [Fore.YELLOW + f"literal char {tok} → '{ch}'"]

    # ------------------------------------------------------------------
    # CASO 7: Literal de cadena (t_string)
    #   Ej: 'hello' → hello
    # ------------------------------------------------------------------
    if nodetype == "t_string":
        tok = str(tree.children[0])
        s = tok[1:-1]
        return s, [Fore.YELLOW + f"literal string {tok} → '{s}'"]

    # ------------------------------------------------------------------
    # CASO 8: Except (t_except)
    #
    # Algo como "letter except 'a'" se espera como:
    #   t_except
    #     (base)
    #     (conjunto a excluir)
    #
    # Construimos una clase negada: [^...] a partir del segundo hijo.
    # ------------------------------------------------------------------
    if nodetype == "t_except":
        base_r, base_steps = explain_tree(tree.children[0])
        neg_r, neg_steps = explain_tree(tree.children[1])

        # Asumimos que neg_r es algo tipo "[...]" → extraemos el interior
        inside = neg_r.strip("[]")
        r = f"[^{inside}]"
        steps = base_steps + neg_steps
        steps.append(Fore.YELLOW + f"except → negación → {r}")
        return r, steps

    # ------------------------------------------------------------------
    # CASO 9: sequence
    #
    # Representa concatenación de varios elementos.
    # ------------------------------------------------------------------
    if nodetype == "sequence":
        parts = []
        steps = []
        for ch in tree.children:
            r, s = explain_tree(ch)
            parts.append(r)
            steps.extend(s)
        joined = "".join(parts)
        steps.append(Fore.YELLOW + f"sequence → concatenación: {joined}")
        return joined, steps

    # ------------------------------------------------------------------
    # CASO 10: OR / OR_EXPR
    #
    # Representa alternativas: (A|B).
    # ------------------------------------------------------------------
    if nodetype in ("or", "or_expr"):
        left, s1 = explain_tree(tree.children[0])
        right, s2 = explain_tree(tree.children[1])
        r = f"({left}|{right})"
        return r, s1 + s2 + [Fore.YELLOW + f"or → alternativa: {r}"]

    # ------------------------------------------------------------------
    # CASO 11: Nodos de repetición / cuantificadores
    #
    # Estos nodos solo devuelven el símbolo de repetición que luego
    # será aplicado por `repeated_term`.
    # ------------------------------------------------------------------
    if nodetype == "r_optional":
        return "?", [Fore.YELLOW + "optional → ?"]

    if nodetype == "r_one_or_more":
        return "+", [Fore.YELLOW + "one or more → +"]

    if nodetype == "r_zero_or_more":
        return "*", [Fore.YELLOW + "zero or more → *"]

    if nodetype == "r_exact":
        # exactly N times
        n = str(tree.children[0])
        r = f"{{{n}}}"
        return r, [Fore.YELLOW + f"exactly {n} times → {r}"]

    if nodetype == "r_range":
        # between N and M times
        n1 = str(tree.children[0])
        n2 = str(tree.children[1])
        r = f"{{{n1},{n2}}}"
        return r, [Fore.YELLOW + f"between {n1} and {n2} times → {r}"]

    if nodetype == "r_at_least":
        # at least N times
        n = str(tree.children[0])
        r = f"{{{n},}}"
        return r, [Fore.YELLOW + f"at least {n} times → {r}"]

    if nodetype == "r_at_most":
        # at most N times → {0,N}
        n = str(tree.children[0])
        r = f"{{0,{n}}}"
        return r, [Fore.YELLOW + f"at most {n} times → {r}"]

    # ------------------------------------------------------------------
    # CASO 12: repeated_term
    #
    # Estructura típica:
    #   repeated_term: term
    #                | term repetition
    #                | repetition term
    #                | repetition term repetition
    #
    # Donde "repetition" es alguno de los nodos r_* anteriores.
    # ------------------------------------------------------------------
    if nodetype == "repeated_term":
        children = list(tree.children)

        # Solo un hijo → sin cuantificador explícito
        if len(children) == 1:
            return explain_tree(children[0])

        # Dos hijos:
        #   o bien (term, repetition) o (repetition, term)
        if len(children) == 2:
            c1, c2 = children
            r1, s1 = explain_tree(c1)
            r2, s2 = explain_tree(c2)
            steps = s1 + s2

            quantifiers = ["?", "+", "*"]
            # Si el primer fragmento es cuantificador → va después del término
            if r1.startswith("{") or r1 in quantifiers:
                regex = r2 + r1
                steps.append(
                    Fore.YELLOW
                    + f"repeated_term → aplicamos cuantificador '{r1}' al término '{r2}': {regex}"
                )
            else:
                regex = r1 + r2
                steps.append(
                    Fore.YELLOW
                    + f"repeated_term → aplicamos cuantificador '{r2}' al término '{r1}': {regex}"
                )
            return regex, steps

        # Tres hijos:
        #   repetición antes, término en medio, repetición después.
        if len(children) == 3:
            rep_before, term_node, rep_after = children
            r_before, s_before = explain_tree(rep_before)
            r_term, s_term = explain_tree(term_node)
            r_after, s_after = explain_tree(rep_after)

            regex = r_term + r_before + r_after
            steps = s_before + s_term + s_after
            steps.append(
                Fore.YELLOW
                + f"repeated_term → cuantificador doble alrededor de '{r_term}': {regex}"
            )
            return regex, steps

        # Más de tres hijos (caso muy raro) → concatenamos todo sin más
        parts = []
        steps = []
        for ch in children:
            r, s = explain_tree(ch)
            parts.append(r)
            steps.extend(s)
        regex = "".join(parts)
        steps.append(Fore.YELLOW + f"repeated_term → {regex}")
        return regex, steps

    # ------------------------------------------------------------------
    # CASO 13: group
    #
    #   group: "(" sequence ")"
    #        | "(" sequence ")" repetition
    #
    #   → (seq) o (seq)repetition
    # ------------------------------------------------------------------
    if nodetype == "group":
        # Primero explicamos la secuencia interna
        seq_r, seq_steps = explain_tree(tree.children[0])
        steps = seq_steps.copy()

        # Sin repetición → solo agrupamos
        if len(tree.children) == 1:
            r = f"({seq_r})"
            steps.append(Fore.YELLOW + f"group → {r}")
            return r, steps

        # Con repetición → (expr)quantifier
        rep_r, rep_steps = explain_tree(tree.children[1])
        steps.extend(rep_steps)
        r = f"({seq_r}){rep_r}"
        steps.append(Fore.YELLOW + f"group with repetition → {r}")
        return r, steps

    # ------------------------------------------------------------------
    # CASO 14: Fallback
    #
    # Si llega un nodo no contemplado explíticamente, no fallamos en seco:
    # - Recorrermos recursivamente sus hijos para no perder la estructura.
    # - Anotamos un mensaje de advertencia con el tipo de nodo.
    # ------------------------------------------------------------------
    regex_parts = []
    steps = [Fore.RED + f"⚠ nodo no reconocido: {nodetype}, se recorren hijos."]
    for ch in getattr(tree, "children", []):
        r, s = explain_tree(ch)
        regex_parts.append(r)
        steps.extend(s)

    regex = "".join(regex_parts)
    return regex, steps

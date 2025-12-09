from colorama import Fore
from lark_parser import normalize_text, parse_normalized


def explain_phrase_and_regex(phrase, final_regex):
    explanation = []

    normalized = normalize_text(phrase)

    explanation.append(Fore.CYAN + "=== Normalización ===")
    explanation.append(Fore.GREEN + f"Frase original: {phrase}")
    explanation.append(Fore.GREEN + f"DSL normalizado: {normalized}\n")

    try:
        tree = parse_normalized(normalized)
    except Exception as e:
        return Fore.RED + f"ERROR al generar AST: {e}"

    explanation.append(Fore.CYAN + "=== AST generado ===")
    explanation.append(tree.pretty() + "\n")

    explanation.append(Fore.CYAN + "=== Explicación estructural ===")
    built_regex, steps = explain_tree(tree)
    explanation.extend(steps)

    explanation.append("\n" + Fore.CYAN + "=== Regex final ===")
    explanation.append(Fore.GREEN + final_regex)

    return "\n".join(explanation)


def explain_tree(tree):
    nodetype = getattr(tree, "data", None)

    if nodetype is None:
        token = str(tree)
        return token, [Fore.YELLOW + f"Terminal literal → '{token}'"]

    if nodetype == "start":
        if not tree.children:
            return "", [Fore.RED + "Árbol vacío en 'start'."]
        regex, steps = explain_tree(tree.children[0])
        steps.append(Fore.YELLOW + f"start → expresión completa: {regex}")
        return regex, steps

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

    base_map = {
        "t_digit": ("[0-9]", "digit → [0-9]"),
        "t_letter": ("[a-zA-Z]", "letter → [a-zA-Z]"),
        "t_space": (r"\s", "space → \\s"),
        "t_any": (".", "any character → ."),
        "t_upper": ("[A-Z]", "uppercase letter → [A-Z]"),
        "t_lower": ("[a-z]", "lowercase letter → [a-z]"),
        "t_vowel": ("[AEIOUaeiou]", "vowel → [AEIOUaeiou]"),
        "t_consonant": ("[BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz]",
                        "consonant → all consonants"),
        "t_word": (r"\w", "word character → \\w"),
        "t_alphanumeric": ("[A-Za-z0-9]", "alphanumeric → [A-Za-z0-9]"),
        "t_hex": ("[0-9A-Fa-f]", "hex digit → [0-9A-Fa-f]"),
        "t_whitespace": (r"\s", "whitespace → \\s"),
        "t_non_whitespace": (r"\S", "non whitespace → \\S"),
    }

    if nodetype in base_map:
        regex, desc = base_map[nodetype]
        return regex, [Fore.YELLOW + desc]
    
        # ---------- RANGO ----------
    if nodetype == "t_range":
        # Estructura esperada:
        #   t_range
        #     range_expr
        #       'a'
        #       'z'
        if not tree.children:
            return "", [Fore.RED + "Árbol de rango sin hijos."]

        range_node = tree.children[0]

        if hasattr(range_node, "children") and len(range_node.children) >= 2:
            raw1 = str(range_node.children[0])
            raw2 = str(range_node.children[1])
        else:
            raw1 = str(tree.children[0])
            raw2 = str(tree.children[1]) if len(tree.children) > 1 else ""

        def _unquote(s: str) -> str:
            if len(s) >= 2 and (s[0] in ("'", '"')) and s[-1] == s[0]:
                return s[1:-1]
            return s

        c1 = _unquote(raw1)
        c2 = _unquote(raw2)
        r = f"[{c1}-{c2}]"
        return r, [Fore.YELLOW + f"range '{c1}' to '{c2}' → {r}"]

    if nodetype == "t_char":
        tok = str(tree.children[0])
        ch = tok[1:-1]
        r = ch
        return r, [Fore.YELLOW + f"literal char {tok} → '{ch}'"]

    if nodetype == "t_string":
        tok = str(tree.children[0])
        s = tok[1:-1]
        return s, [Fore.YELLOW + f"literal string {tok} → '{s}'"]

    if nodetype == "t_except":
        base_r, base_steps = explain_tree(tree.children[0])
        neg_r, neg_steps = explain_tree(tree.children[1])
        inside = neg_r.strip("[]")
        r = f"[^{inside}]"
        steps = base_steps + neg_steps
        steps.append(Fore.YELLOW + f"except → negación → {r}")
        return r, steps

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

    if nodetype in ("or", "or_expr"):
        left, s1 = explain_tree(tree.children[0])
        right, s2 = explain_tree(tree.children[1])
        r = f"({left}|{right})"
        return r, s1 + s2 + [Fore.YELLOW + f"or → alternativa: {r}"]

    if nodetype == "r_optional":
        return "?", [Fore.YELLOW + "optional → ?"]

    if nodetype == "r_one_or_more":
        return "+", [Fore.YELLOW + "one or more → +"]

    if nodetype == "r_zero_or_more":
        return "*", [Fore.YELLOW + "zero or more → *"]

    if nodetype == "r_exact":
        n = str(tree.children[0])
        r = f"{{{n}}}"
        return r, [Fore.YELLOW + f"exactly {n} times → {r}"]

    if nodetype == "r_range":
        n1 = str(tree.children[0])
        n2 = str(tree.children[1])
        r = f"{{{n1},{n2}}}"
        return r, [Fore.YELLOW + f"between {n1} and {n2} times → {r}"]

    if nodetype == "r_at_least":
        n = str(tree.children[0])
        r = f"{{{n},}}"
        return r, [Fore.YELLOW + f"at least {n} times → {r}"]

    if nodetype == "r_at_most":
        n = str(tree.children[0])
        r = f"{{0,{n}}}"
        return r, [Fore.YELLOW + f"at most {n} times → {r}"]

    if nodetype == "repeated_term":
        children = list(tree.children)

        if len(children) == 1:
            return explain_tree(children[0])

        if len(children) == 2:
            c1, c2 = children
            r1, s1 = explain_tree(c1)
            r2, s2 = explain_tree(c2)
            steps = s1 + s2
            quantifiers = ["?", "+", "*"]
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

        parts = []
        steps = []
        for ch in children:
            r, s = explain_tree(ch)
            parts.append(r)
            steps.extend(s)
        regex = "".join(parts)
        steps.append(Fore.YELLOW + f"repeated_term → {regex}")
        return regex, steps

    if nodetype == "group":
        seq_r, seq_steps = explain_tree(tree.children[0])
        steps = seq_steps.copy()
        if len(tree.children) == 1:
            r = f"({seq_r})"
            steps.append(Fore.YELLOW + f"group → {r}")
            return r, steps
        rep_r, rep_steps = explain_tree(tree.children[1])
        steps.extend(rep_steps)
        r = f"({seq_r}){rep_r}"
        steps.append(Fore.YELLOW + f"group with repetition → {r}")
        return r, steps

    regex_parts = []
    steps = [Fore.RED + f"⚠ nodo no reconocido: {nodetype}, se recorren hijos."]
    for ch in getattr(tree, "children", []):
        r, s = explain_tree(ch)
        regex_parts.append(r)
        steps.extend(s)
    regex = "".join(regex_parts)
    return regex, steps

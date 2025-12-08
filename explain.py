from colorama import Fore
from lark_parser import normalize_text, parse_normalized, translate_tree


def explain_phrase_and_regex(phrase, final_regex):
    """
    Explica paso a paso:
    1. Normalización del DSL
    2. AST generado por Lark
    3. Construcción paso por paso de la regex
    """

    explanation = []

    # ============================================================
    # 1. NORMALIZACIÓN
    # ============================================================
    normalized = normalize_text(phrase)

    explanation.append(Fore.CYAN + "=== Normalización ===")
    explanation.append(Fore.GREEN + f"Frase original: {phrase}")
    explanation.append(Fore.GREEN + f"DSL normalizado: {normalized}\n")

    # ============================================================
    # 2. PARSING → AST
    # ============================================================
    try:
        tree = parse_normalized(normalized)
    except Exception as e:
        return Fore.RED + f"ERROR al generar AST: {e}"

    explanation.append(Fore.CYAN + "=== AST generado ===")
    explanation.append(tree.pretty() + "\n")

    # ============================================================
    # 3. EXPLICACIÓN ESTRUCTURAL BASADA EN EL AST
    # ============================================================
    explanation.append(Fore.CYAN + "=== Explicación estructural ===")
    built_regex, steps = explain_tree(tree)
    explanation.extend(steps)

    # ============================================================
    # 4. REGEX FINAL
    # ============================================================
    explanation.append("\n" + Fore.CYAN + "=== Regex final ===")
    explanation.append(Fore.GREEN + final_regex)

    return "\n".join(explanation)


# ============================================================
# FUNCIÓN CENTRAL DE EXPLICACIÓN DEL AST
# ============================================================

def explain_tree(tree):
    """
    Explica recursivamente la construcción de la regex.
    Retorna:
       (regex_generada, lista_de_explicaciones)
    """
    nodetype = tree.data if hasattr(tree, "data") else None

    # Casos atómicos (terminales)
    if nodetype is None:
        token = str(tree)
        return token, [Fore.YELLOW + f"Terminal: {token}"]

    # Despachar según tipo
    if nodetype == "t_digit":
        return "[0-9]", [Fore.YELLOW + "digit → [0-9]"]

    if nodetype == "t_letter":
        return "[a-zA-Z]", [Fore.YELLOW + "letter → [a-zA-Z]"]

    if nodetype == "t_space":
        return r"\s", [Fore.YELLOW + "space → \\s"]

    if nodetype == "t_any":
        return ".", [Fore.YELLOW + "any character → ."]

    if nodetype == "t_upper":
        return "[A-Z]", [Fore.YELLOW + "uppercase letter → [A-Z]"]

    if nodetype == "t_lower":
        return "[a-z]", [Fore.YELLOW + "lowercase letter → [a-z]"]

    if nodetype == "t_char":
        val = tree.children[0].value[1:-1]
        return val, [Fore.YELLOW + f"char '{val}' → {val}"]

    if nodetype == "t_string":
        val = tree.children[0].value[1:-1]
        return val, [Fore.YELLOW + f"string \"{val}\" → {val}"]

    # ------------------------------------------------------------
    # except: base except base
    # ------------------------------------------------------------
    if nodetype == "t_except":
        base, steps_base = explain_tree(tree.children[0])
        neg, steps_neg = explain_tree(tree.children[1])

        neg_inside = neg.strip("[]")
        regex = f"[^{neg_inside}]"

        steps = []
        steps.extend(steps_base)
        steps.extend(steps_neg)
        steps.append(Fore.YELLOW + f"except → Negación: [^{neg_inside}]")

        return regex, steps

    # ------------------------------------------------------------
    # repetition nodes
    # ------------------------------------------------------------
    rep_map = {
        "r_optional": "?",
        "r_one_or_more": "+",
        "r_zero_or_more": "*",
        "r_exact": lambda c: f"{{{c[0]}}}",
        "r_range": lambda c: f"{{{c[0]},{c[1]}}}",
    }

    if nodetype in rep_map:
        raw = tree.children
        if callable(rep_map[nodetype]):
            rep = rep_map[nodetype]([str(x) for x in raw])
        else:
            rep = rep_map[nodetype]

        return rep, [Fore.YELLOW + f"repetition → {rep}"]

    # ------------------------------------------------------------
    # sequence: concatenación
    # ------------------------------------------------------------
    if nodetype == "sequence":
        regex_parts = []
        steps = []

        for child in tree.children:
            sub_r, sub_steps = explain_tree(child)
            regex_parts.append(sub_r)
            steps.extend(sub_steps)

        final = "".join(regex_parts)
        steps.append(Fore.YELLOW + f"sequence → concatenación: {final}")

        return final, steps

    # ------------------------------------------------------------
    # or_expr: X or Y
    # ------------------------------------------------------------
    if nodetype == "or_expr":
        left_r, left_steps = explain_tree(tree.children[0])
        right_r, right_steps = explain_tree(tree.children[1])

        regex = f"({left_r}|{right_r})"

        steps = []
        steps.extend(left_steps)
        steps.extend(right_steps)
        steps.append(Fore.YELLOW + f"or → alternativa: {regex}")

        return regex, steps

    # ------------------------------------------------------------
    # repeated_term → combinación de term + repetición
    # ------------------------------------------------------------
    if nodetype == "repeated_term":
        children = tree.children

        # sin repetición
        if len(children) == 1:
            return explain_tree(children[0])

        steps = []
        parts = []

        for c in children:
            r, s = explain_tree(c)
            parts.append(r)
            steps.extend(s)

        regex = "".join(parts)
        steps.append(Fore.YELLOW + f"repeated term → {regex}")

        return regex, steps

    # ------------------------------------------------------------
    # group → (contenido)rep?
    # ------------------------------------------------------------
    if nodetype == "group":
        seq_tree = tree.children[0]
        seq_r, seq_steps = explain_tree(seq_tree)

        steps = list(seq_steps)

        # grupo sin repetición
        if len(tree.children) == 1:
            regex = f"({seq_r})"
            steps.append(Fore.YELLOW + f"group → ({seq_r})")
            return regex, steps

        # con repetición
        rep_tree = tree.children[1]
        rep_r, rep_steps = explain_tree(rep_tree)
        steps.extend(rep_steps)

        regex = f"({seq_r}){rep_r}"
        steps.append(Fore.YELLOW + f"group repeated → {regex}")

        return regex, steps

    if nodetype == "t_vowel":
        return "[aeiouAEIOU]", ["vowel → [aeiouAEIOU]"]

    if nodetype == "t_consonant":
        return "[b-df-hj-np-tv-zB-DF-HJ-NP-TV-Z]", ["consonant → (all consonants)"]

    if nodetype == "t_word":
        return r"\w", ["word character → \\w"]

    if nodetype == "t_alnum":
        return "[A-Za-z0-9]", ["alphanumeric → [A-Za-z0-9]"]

    if nodetype == "t_hex":
        return "[0-9A-Fa-f]", ["hex digit → [0-9A-Fa-f]"]

    if nodetype == "t_nonspace":
        return r"\S", ["non whitespace → \\S"]

    # fallback (no debería ocurrir)
    return "", [Fore.RED + f"No sé explicar nodo: {nodetype}"]  

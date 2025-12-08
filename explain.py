from colorama import Fore
from lark_parser import normalize_text, parse_normalized, translate_tree


def explain_phrase_and_regex(phrase, final_regex):
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
    # 3. EXPLICACIÓN ESTRUCTURAL
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
# FUNCIÓN RECURSIVA PRINCIPAL
# ============================================================

def explain_tree(tree):
    nodetype = getattr(tree, "data", None)

    # -------------------- TERMINALES --------------------
    if nodetype is None:
        token = str(tree)
        return token, [Fore.YELLOW + f"Terminal literal → '{token}'"]

    # ---------- BASE TERMS ----------
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
        regex, msg = base_map[nodetype]
        return regex, [Fore.YELLOW + msg]

    # ---------- LITERALES ----------
    if nodetype == "t_char":
        val = tree.children[0].value[1:-1]
        return val, [Fore.YELLOW + f"character literal '{val}' → {val}"]

    if nodetype == "t_string":
        val = tree.children[0].value[1:-1]
        return val, [Fore.YELLOW + f"string literal \"{val}\" → {val}"]

    # ---------- RANGO ----------
    if nodetype == "t_range":
        c1 = tree.children[0][1:-1]
        c2 = tree.children[1][1:-1]
        r = f"[{c1}-{c2}]"
        return r, [Fore.YELLOW + f"range '{c1}' to '{c2}' → {r}"]

    # ---------- NEGACIÓN ----------
    if nodetype == "t_except":
        base_r, base_steps = explain_tree(tree.children[0])
        neg_r, neg_steps = explain_tree(tree.children[1])

        inside = neg_r.strip("[]")
        r = f"[^{inside}]"

        steps = base_steps + neg_steps
        steps.append(Fore.YELLOW + f"except → negación → {r}")
        return r, steps

    # ---------- REPETICIONES ----------
    if nodetype == "r_optional":
        return "?", ["optional → ?"]

    if nodetype == "r_one_or_more":
        return "+", ["one or more → +"]

    if nodetype == "r_zero_or_more":
        return "*", ["zero or more → *"]

    if nodetype == "r_exact":
        n = tree.children[0]
        return f"{{{n}}}", [f"{n} times → {{{n}}}"]

    if nodetype == "r_range":
        a, b = tree.children
        return f"{{{a},{b}}}", [f"between {a} and {b} times → {{{a},{b}}}"]

    if nodetype == "r_at_least":
        n = tree.children[0]
        return f"{{{n},}}", [f"at least {n} times → {{{n},}}"]

    if nodetype == "r_at_most":
        n = tree.children[0]
        return f"{{0,{n}}}", [f"at most {n} times → {{0,{n}}}"]

    # ---------- SEQUENCE ----------
    if nodetype == "sequence":
        parts = []
        steps = []
        for ch in tree.children:
            r, s = explain_tree(ch)
            parts.append(r)
            steps.extend(s)
        final = "".join(parts)
        steps.append(Fore.YELLOW + f"sequence → concatenación: {final}")
        return final, steps

    # ---------- OR ----------
    if nodetype == "or_expr":
        left, s1 = explain_tree(tree.children[0])
        right, s2 = explain_tree(tree.children[1])
        r = f"({left}|{right})"
        return r, s1 + s2 + [Fore.YELLOW + f"or → alternativa: {r}"]

    # ---------- REPEATED TERM ----------
    if nodetype == "repeated_term":
        steps = []
        parts = []
        for ch in tree.children:
            r, s = explain_tree(ch)
            parts.append(r)
            steps.extend(s)
        r = "".join(parts)
        steps.append(Fore.YELLOW + f"repeated term → {r}")
        return r, steps

    # ---------- GROUP ----------
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

    # Fallback
    return "", [Fore.RED + f"⚠ nodo no reconocido: {nodetype}"]

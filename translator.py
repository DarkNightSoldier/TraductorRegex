from lark import Transformer

class RegexTranslator(Transformer):

    # ---------- BASE TERMS ----------
    def t_letter(self, _): return "[a-zA-Z]"
    def t_digit(self, _): return "[0-9]"
    def t_space(self, _): return r"\s"
    def t_any(self, _):   return "."

    def t_upper(self, _): return "[A-Z]"
    def t_lower(self, _): return "[a-z]"

    def t_vowel(self, _): 
        return "[aeiouAEIOU]"

    def t_consonant(self, _):
        # Todas las consonantes inglesas
        return "[b-df-hj-np-tv-zB-DF-HJ-NP-TV-Z]"

    def t_word(self, _):
        return r"\w"

    def t_alnum(self, _):
        return "[A-Za-z0-9]"

    def t_hex(self, _):
        return "[0-9A-Fa-f]"

    def t_ws(self, _):
        return r"\s"

    def t_range(self, children):
        c1 = children[0][1:-1]
        c2 = children[1][1:-1]
        return f"[{c1}-{c2}]"

    def t_char(self, tok):
        return tok[0][1:-1]

    def t_string(self, tok):
        return tok[0][1:-1]

    # ---------- NEGATION ----------
    def t_except(self, children):
        base, neg = children
        neg_inside = neg.strip("[]")
        return f"[^{neg_inside}]"

    # ---------- REPETITIONS ----------
    def r_optional(self, _):     return "?"
    def r_one_or_more(self, _): return "+"
    def r_zero_or_more(self, _): return "*"
    def r_exact(self, children): return f"{{{children[0]}}}"
    def r_range(self, children): return f"{{{children[0]},{children[1]}}}"

    def r_at_least(self, children):
        return f"{{{children[0]},}}"

    def r_at_most(self, children):
        return f"{{0,{children[0]}}}"

    # ---------- TERM ----------
    def term(self, children):
        return children[0]

    def base_term(self, children):
        return children[0]

    # ---------- REPEATED TERM ----------
    def repeated_term(self, children):
        # Convert Trees to strings
        children = [str(c) for c in children]

        if len(children) == 1:
            return children[0]

        if len(children) == 2:
            a, b = children
            rep_symbols = ["?", "+", "*"]
            if a.startswith("{") or a in rep_symbols:
                return b + a
            return a + b

        if len(children) == 3:
            rep_before, term, rep_after = children
            return term + rep_before + rep_after

        return "".join(children)

    # ---------- GROUP ----------
    def group(self, children):
        children = [str(c) for c in children]
        if len(children) == 1:
            return "(" + children[0] + ")"
        return "(" + children[0] + ")" + children[1]

    # ---------- SEQUENCE ----------
    def sequence(self, children):
        return "".join(str(c) for c in children)

    # ---------- OR ----------
    def or_expr(self, children):
        return "(" + str(children[0]) + "|" + str(children[1]) + ")"

    # ---------- ELEMENT ----------
    def element(self, children):
        return children[0]

    # ---------- START ----------
    def start(self, children):
        return children[0]

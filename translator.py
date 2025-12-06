from lark import Transformer

class RegexTranslator(Transformer):
    """
    Transforma el Árbol de Sintaxis Abstracta (AST) de la gramática
    en la expresión regular final.
    """

    # --- Mapeo de Términos Base a Regex ---
    
    # Convierte los tokens terminales del lenguaje natural a su equivalente Regex
    def t_letra(self, _):
        # "[a-zA-Z]"
        return "[a-zA-Z]"

    def t_digito(self, _):
        # "[0-9]"
        return "[0-9]"
        
    def t_espacio(self, _):
        # "\s" (o " ")
        return r"\s"
        
    def t_cualquier(self, _):
        # "."
        return "."
        
    # --- Manejo de Repeticiones (Modificadores) ---
    
    def r_opcional(self, _):
        # "?"
        return "?"
        
    def r_mas(self, _):
        # "+"
        return "+"

    # --- Manejo de la Estructura (Nodos del AST) ---

    def term(self, children):
        # Un término base sin modificadores es solo el valor del hijo
        return children[0]
    
    def element(self, children):
        # Si tiene repetición, agrega el modificador al final
        if len(children) == 2:
            base_regex = children[0]
            modifier = children[1]
            return f"{base_regex}{modifier}"
        # Si no, es solo el término base
        return children[0]

    def pattern(self, children):
        # Maneja la elección ("o"). Une los elementos con el operador "|"
        if len(children) > 1:
            # Los patrones de elección se deben encerrar en paréntesis
            return f"({'|'.join(children)})"
        return children[0]

    def sequence(self, children):
        # Maneja la concatenación ("seguido de"). Une los patrones
        # El conector "seguido de" se ignora en la transformación
        return "".join(c for c in children if isinstance(c, str))
        
    def start(self, children):
        # El resultado final es la secuencia
        return children[0]
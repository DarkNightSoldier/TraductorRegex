from lark import Lark
from translator import RegexTranslator


def translate_to_regex(natural_language_phrase):
    """
    Inicializa el parser, analiza la frase y la transforma en una Regex.
    """
    
    # 1. Inicializar el Parser con la Gramática
    # 'lalr' es rápido y es adecuado para gramáticas de izquierda a derecha.
    # Se carga la Gramática Usando Lark.open()
    # Lark buscará el archivo en la ubicación especificada.
    # El 'rel_to=__file__' asegura que busque el archivo relativo a la ubicación
    # del script de Python actual, lo cual es muy útil.
    try:
        parser = Lark.open(
            "grammar.lark",  # El nombre del archivo de gramática
            rel_to=__file__,       # Ubicación relativa al archivo Python actual
            start='start',         # El nombre de la regla inicial
            parser='lalr'          # El algoritmo de análisis
        )
    except FileNotFoundError:
        return "Error: No se encontró el archivo 'grammar.lark'. Asegúrate de que esté en el mismo directorio."

    try:
        # 2. Analizar la frase para crear el AST
        tree = parser.parse(natural_language_phrase)
        
        # 3. Transformar el AST en la Regex
        regex = RegexTranslator().transform(tree)
        
        return regex
        
    except Exception as e:
        return f"Error de análisis para '{natural_language_phrase}': {e}"
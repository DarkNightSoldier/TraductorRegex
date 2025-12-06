from lark_parser import translate_to_regex

#frase = "letter or digit followed by space optional"
frase = "letter one or more followed by digit optional or any character"
resultado = translate_to_regex(frase)
print(f"La frase: '{frase}'\nLa Regex generada: '{resultado}'")
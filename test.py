from lark_parser import translate_to_regex

def probar(frase):
    regex = translate_to_regex(frase)
    print("\nFrase:", frase)
    print("Regex:", regex)

print("=== PRUEBAS NATURALES ===")

probar("match a sequence of digits that appear three times")
probar("a lowercase letter optionally followed by three digits")
probar("letters then digits")
probar("any character except digits")
probar("uppercase letters that repeat twice next lowercase letters")
probar("'hello' then digits that appear between 2 and 5 times")
probar("digit or letter followed by space optional")

print("\n=== PRUEBAS AVANZADAS ===")

probar("a group of digit then letter end group repeated twice")
probar("group digit followed by digit end group optional")
probar("lowercase letter then group digit end group between 2 and 4 times")
probar("group 'a' followed by digit end group or 'hello'")
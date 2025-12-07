# TraductorRegex  
### DSL Natural → Expresiones Regulares  
Proyecto de Compiladores – Traductor de Lenguaje Pseudonatural a Regex

TraductorRegex es una herramienta capaz de transformar frases en inglés pseudonatural 
("natural‑like DSL") en expresiones regulares reales y válidas.  

Este proyecto combina:

- Análisis sintáctico con **Lark**  
- Normalización lingüística (“NLP‑lite”)  
- Traducción estructural mediante un **AST Transformer**  
- Un CLI profesional con modo interactivo, autocompletado y pruebas  

Es un ejemplo completo de diseño e implementación de un **lenguaje específico de dominio (DSL)**.

---

#  Características

✔ Soporte para frases naturales como:

- `match a sequence of digits that appear three times`
- `a lowercase letter optionally followed by three digits`
- `uppercase letters that repeat twice next lowercase letters`
- `'hello' then digits that appear between 2 and 5 times`
- `any character except digits`
- `group digit followed by digit end group optional`

✔ DSL formal, limpio y sin ambigüedades  
✔ Gramática robusta y extendible  
✔ Normalizador avanzado (NLP-lite estructural)  
✔ Soporte completo para:  
  - `one or more`, `zero or more`, `optional`  
  - `3 times`, `between 2 and 5 times`  
  - `except`  
  - grupos (`group … end group`)  
  - `or`  
  - literales `'a'`, `'hello'`  
✔ CLI con:  
  - modo normal  
  - modo interactivo con autocompletado (TAB)  
  - `--test` para validar cadenas  
  - `--explain` para mostrar el análisis  

---

#  Arquitectura
Frase natural → Normalizer → DSL limpio → Lark Parser → AST → Transformer → Regex final

text

Componentes:

- **normalizer.py**  
  Traduce frases naturales en frases formales del DSL.

- **grammar.lark**  
  Gramática del DSL (sin ambigüedades).

- **translator.py**  
  Transformer que convierte el AST en la regex final.

- **lark_parser.py**  
  Junta normalizador + parser + translator.

- **cli.py**  
  Interfaz de línea de comandos, con modo interactivo y autocompletado.

---

#  Ejemplos de uso

### Modo directo:
python cli.py "lowercase letter optional followed by digit 3 times"

text

Salida:
Regex: [a-z]?[0-9]{3}

text

### Probar cadenas:
python cli.py "digit one or more" --test "12345"

text

### Explicar la traducción:
python cli.py "letter one or more" --explain

text

### Modo interactivo con autocompletado (TAB):
python cli.py --interactive

text

---

#  Ejemplos traducidos

| Frase natural | Regex |
|---------------|-------|
| digits that appear three times | `[0-9]{3}` |
| a lowercase letter optionally followed by three digits | `[a-z]?[0-9]{3}` |
| letters then digits | `[A-Za-z]+[0-9]+` |
| any character except digits | `[^0-9]` |
| uppercase letters that repeat twice next lowercase letters | `[A-Z]{2}[a-z]+` |
| 'hello' then digits that appear between 2 and 5 times | `hello[0-9]{2,5}` |
| group digit followed by letter end group repeated twice | `([0-9][a-zA-Z]){2}` |

---

#  Pruebas

Ejecutar:
python test.py

text

---

#  Requisitos
pip install lark prompt_toolkit colorama

text

---

#  Extensiones futuras

- Soporte para ranges textuales:  
  `letter between 'a' and 'f'`
- Nombres de clases predefinidas: `vowel`, `consonant`, `hex digit`
- Inversión del traductor (regex → frase natural)
- Simplificador más inteligente

---

#  Créditos

Proyecto realizado para el curso de Compiladores.  
Incluye análisis, diseño e implementación completa de un DSL real y un traductor funcional.  
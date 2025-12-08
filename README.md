# TraductorRegex 
### DSL pseudonatural en inglés → Expresiones Regulares

**Integrantes:** Juan Antonio Rodríguez Rubio, Manuel Fernando Valle Amorteguí, Ivan Gabriel Aranguren Rengifo, Alejandro Higuera Castro

Proyecto del curso de Compiladores

Universidad Nacional de Colombia

TraductorRegex es una herramienta capaz de transformar frases en inglés pseudonatural ("natural‑like DSL") en expresiones regulares reales y válidas.


Ejemplo:

> `a lowercase letter optionally followed by three digits`  
> ⟶ `[a-z]?[0-9]{3}`

Está pensado como un **mini lenguaje específico de dominio (DSL)** que combina:

- Análisis sintáctico con **Lark**  
- Normalización lingüística (“NLP‑lite”)  
- Traducción estructural mediante un **AST Transformer**  
- Un CLI profesional con modo interactivo, autocompletado y pruebas  

---

## 1. Instalación

Requisitos:

- Python 3.10+  
- Librerías (incluidas en `requirements.txt`):

```txt
lark==1.3.1
prompt_toolkit==3.0.52
colorama==0.4.6
```
Clonar el repositorio:
```bash
git clone https://github.com/DarkNightSoldier/TraductorRegex.git
```

Instalar:

```bash
pip install -r requirements.txt
```

---

## 2. Uso rápido

### 2.1 Conversión directa

```bash
python cli.py "lowercase letter optional followed by digit 3 times"
```

Salida:

```text
Regex generada: [a-z]?[0-9]{3}
```

### 2.2 Probar una cadena contra la regex (`--test`)

```bash
python cli.py "digit one or more" --test "12345"
# ✓ '12345' coincide.
```

### 2.3 Explicar la traducción paso a paso (`--explain`)

```bash
python cli.py "letter one or more" --explain
```

Muestra:

1. Frase original  
2. DSL normalizado  
3. AST  
4. Regex cruda  
5. Regex optimizada  
6. Explicación texto a texto de cómo se construyó la regex.

### 2.4 Modo interactivo con autocompletado (`--interactive`)

```bash
python cli.py --interactive
```

Comandos dentro del modo interactivo:

- `help`     – ayuda rápida  
- `examples` – ejemplos de frases válidas  
- `tokens`   – lista de palabras clave del DSL  
- `exit`     – salir

Autocompletado con `TAB` para palabras del DSL.

### 2.5 Modo debug (`--debug`)

```bash
python cli.py "vowel followed by digit three times" --debug
```

Muestra explícitamente:

1. Frase original  
2. DSL normalizado  
3. AST de Lark  
4. Regex cruda  
5. Regex final simplificada

---

## 3. Arquitectura del proyecto

Pipeline de la herramienta:

```text
Frase natural
  ↓
Normalizer (normalizer.py)
  ↓
DSL limpio en texto
  ↓
Parser Lark (grammar.lark, lark_parser.py)
  ↓
AST
  ↓
Transformer (translator.py)
  ↓
Regex cruda
  ↓
Simplificador (utils.py)
  ↓
Regex final
```

Archivos principales:

- **normalizer.py**  
  Traduce frases naturales a un DSL limpio:
  - elimina *stopwords* (“match”, “regex”, “string”, “the”, …)
  - maneja **números en inglés ilimitados** (“one hundred and five” → `105`)
  - aplica sinónimos y conectores (“then” → `followed by`, “vowels” → `vowel one or more`, etc.)

- **grammar.lark**  
  Gramática formal del DSL:  
  secuencias, `or`, `followed by`, `group … end group`, `except`, repeticiones, rangos, literales…

- **translator.py**  
  Transformer Lark → regex:
  - mapea los términos del DSL a clases de caracteres regex
  - implementa `optional`, `one or more`, `between X and Y times`, `at least`, `at most`, etc.
  - soporta `range 'a' to 'z'`, `vowel`, `consonant`, `hex digit`, etc.

- **utils.py**  
  - `validate_regex(regex)`  
  - `simplify_regex(regex)` con un conjunto de reglas de optimización.

- **lark_parser.py**  
  Funciones de alto nivel:
  - `normalize_text(text)`
  - `parse_normalized(normalized)`
  - `translate_tree(tree)`
  - `translate_to_regex(text)`

- **cli.py**  
  CLI, flags y modo interactivo, pruebas (`--test`) y explicación (`--explain`).

- **completer.py** / **commands.py** / **explain.py**  
  Autocompletado, ayuda integrada y explicación detallada de cada fase.

---

## 4. Especificación del DSL

Todo el DSL está en **inglés**. Las frases finales que se parsean son las **frases normalizadas**, es decir: lo que queda después de que el normalizador limpie sinónimos, plurales y palabras de relleno.

### 4.1 Términos básicos (clases de caracteres)

| Token DSL           | Significado                  | Regex generada         |
|---------------------|-----------------------------|------------------------|
| `letter`            | Cualquier letra              | `[a-zA-Z]`            |
| `digit`             | Dígito decimal               | `[0-9]`               |
| `space`             | Espacio (whitespace)         | `\s`                  |
| `any character`     | Cualquier carácter           | `.`                   |
| `uppercase letter`  | Letra mayúscula              | `[A-Z]`               |
| `lowercase letter`  | Letra minúscula              | `[a-z]`               |

### 4.2 Clases avanzadas

| Token DSL           | Significado                                  | Regex generada                      |
|---------------------|-----------------------------------------------|-------------------------------------|
| `vowel`             | Vocal inglesa (mayúsculas y minúsculas)      | `[AEIOUaeiou]`                      |
| `consonant`         | Consonante inglesa                           | `[BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz]` |
| `word character`    | Carácter de palabra (letra, dígito, `_`)     | `\w`                                |
| `alphanumeric`      | Letra o dígito                               | `[A-Za-z0-9]`                       |
| `hex digit`         | Dígito hexadecimal                           | `[0-9A-Fa-f]`                       |
| `whitespace`        | Cualquier whitespace                         | `\s`                                |
| `non whitespace`    | Cualquier no-whitespace                      | `\S`                                |

### 4.3 Literales

- **Carácter literal:**  
  - `'a'`, `'b'`, `'1'`, `'@'`, etc.  
    → el carácter tal cual en la regex.

- **Cadena literal:**  
  - `'hello'`, `'abc123'`  
    → la cadena tal cual, sin las comillas, en la regex.

Ejemplos:

```text
'hello' followed by digit 3 times   →  hello[0-9]{3}
'a' or 'b'                          →  (a|b)
```

### 4.4 Rangos de caracteres

Sintaxis:

```text
range 'a' to 'z'
range '0' to '9'
range 'A' to 'F'
```

Semántica:

- `range 'a' to 'z'` → `[a-z]`
- `range '0' to '9'` → `[0-9]`

Se puede combinar con repeticiones:

```text
range 'a' to 'z' one or more    →  [a-z]+
```

> Nota: rangos invertidos como `range 'z' to 'a'` producen una regex inválida  
> (y, por tanto, se consideran error).

### 4.5 Cuantificadores

Tokens base (siempre aplican a lo inmediatamente anterior: clase, literal o grupo):

| Token DSL                   | Regex         | Descripción                                  |
|----------------------------|---------------|----------------------------------------------|
| `optional`                 | `?`           | Cero o una vez                               |
| `one or more`              | `+`           | Una o más veces                              |
| `zero or more`             | `*`           | Cero o más veces                             |
| `X times`                  | `{X}`         | Exactamente `X` veces                        |
| `between X and Y times`    | `{X,Y}`       | Entre `X` y `Y` veces                        |
| `at least X times`         | `{X,}`        | Como mínimo `X` veces                        |
| `at most X times`          | `{0,X}`       | Como máximo `X` veces                        |

Ejemplos:

```text
digit 3 times                      →  [0-9]{3}
digit between 2 and 5 times        →  [0-9]{2,5}
digit at least 2 times             →  [0-9]{2,}
digit at most 4 times              →  [0-9]{0,4}
uppercase letter optional          →  [A-Z]?
hex digit one or more              →  [0-9A-Fa-f]+
```

#### Números en inglés ilimitados

En todos los patrones con `X` o `Y` se aceptan:

- Números en cifras: `3`, `10`, `2008`…
- Números en inglés:
  - `one`, `two`, `three`, …, `nineteen`
  - `twenty`, `thirty`, …, `ninety`
  - `hundred`, `thousand`, `million`, `billion`
  - Combinaciones arbitrarias:

Ejemplos:

```text
digit twenty times                     → [0-9]{20}
letter seventy two times               → [a-zA-Z]{72}
digit one hundred and five times       → [0-9]{105}
digit two thousand and eight times     → [0-9]{2008}
hex digit three hundred forty one times→ [0-9A-Fa-f]{341}
```

Además se reconocen:

- `once`   → `1 times`
- `twice`  → `2 times`
- `thrice` → `3 times`

### 4.6 Agrupación y negación

#### Grupos

Sintaxis:

```text
group … end group
```

Opcionalmente seguido de una repetición:

```text
group digit followed by letter end group 3 times
→ ([0-9][a-zA-Z]){3}
```

#### Negación con `except`

Sintaxis:

```text
X except Y
```

Semántica: se toma `X` como clase principal y se **niega** `Y`.

Ejemplos:

```text
letter except 'a'     →  [^a]   (negación de 'a' sobre base de letras)
digit except '0'      →  [^0]
vowel except 'a'      →  [^aAEIOUeiou]  (se explica en la fase de “except”)
```

La implementación genera una clase negada `[^…]` construida a partir de `X` y `Y`.

### 4.7 Conectores de secuencia y alternativas

- **Secuencia:**

  ```text
  X followed by Y
  ```

  Se traduce a concatenación:

  ```text
  letter followed by digit one or more
  → [a-zA-Z][0-9]+
  ```

- **Alternativa (OR):**

  ```text
  X or Y
  ```

  Se traduce a:

  ```text
  (X|Y)
  ```

  Ejemplo:

  ```text
  letter one or more or digit one or more
  → ([a-zA-Z]+|[0-9]+)
  ```

---

## 5. Lista de Tokens soportados

### 5.1 Lista “canónica” de tokens

**Términos básicos**

- `letter`
- `digit`
- `space`
- `any character`
- `uppercase letter`
- `lowercase letter`
- Literales: `'a'`, `'b'`, `'1'`, `'@'`, `'hello'`, …

**Clases avanzadas**

- `vowel`
- `consonant`
- `word character`
- `alphanumeric`
- `hex digit`
- `whitespace`
- `non whitespace`

**Rangos**

- `range 'x' to 'y'`

**Agrupación y negación**

- `group`
- `end group`
- `except`

**Repeticiones**

- `optional`
- `one or more`
- `zero or more`
- `X times`
- `between X and Y times`
- `at least X times`
- `at most X times`

**Conectores**

- `followed by`
- `or`

### 5.2 Simplificación de Sinónimos y azúcar sintáctica (normalizador)

Además del conjunto de tokens anterior, el **normalizador** acepta muchas variantes, que internamente reescribe al DSL canónico.

Algunos ejemplos:

- Plurales y expresiones abreviadas:

  - `digits`, `numbers`                 → `digit one or more`
  - `letters`                           → `letter one or more`
  - `characters`                        → `any character one or more`
  - `lowercase letters`                 → `lowercase letter one or more`
  - `uppercase letters`                 → `uppercase letter one or more`
  - `spaces`, `space characters`        → `space one or more`
  - `whitespace`, `whitespaces`         → `whitespace one or more`
  - `vowels`, `consonants`              → `vowel / consonant one or more`
  - `alphanumerics`                     → `alphanumeric one or more`
  - `hex digits`                        → `hex digit one or more`
  - `non whitespaces`, `non whitespace characters` → `non whitespace one or more`
  - `word characters`                   → `word character one or more`

- Conectores alternativos:

  - `then`, `next`    → `followed by`
  - `optionally`      → `optional`

- Verbos de repetición:

  - `appear 3 times`, `repeat 3 times`  → `3 times`
  - `appear` / `appeared`               → `one or more`
  - `repeat` / `repeated`               → `one or more`

- Palabras de relleno (stopwords) que se ignoran:

  - `match`, `regex`, `regular`, `expression`, `pattern`, `string`, `strings`,
  - `this`, `that`, `which`, `who`, `whom`, `be`, `should`, `like`, `made`,  
    `consisting`, `find`, `of`, `into`, `up`, `a`, `an`, `the`, `please`…

Ejemplo:

```text
match a sequence of digits that appear three times
→ (tras normalización)  digit 3 times
→ Regex final: [0-9]{3}
```

---

## 6. Optimizaciones de la regex

La regex generada pasa por un **simplificador semántico** (`simplify_regex`) con varias reglas:

1. **Paréntesis innecesarios**

   - `(a)` → `a`  
   - `([0-9])` → `[0-9]`

2. **Repeticiones colapsadas**

   - `[0-9][0-9][0-9]` → `[0-9]{3}`

3. **Alternativas simples a clases de caracteres**

   - `(a|b|c)` → `[abc]`  
   - `([0-9]|[1-9])` → `[0-9]`

4. **Orden y limpieza de clases**

   - `[zaq]` → `[aqz]`  
   - Se eliminan duplicados dentro de `[]`.

5. **Reglas A/A\* y similares**

   - `A A*` → `A+`  
   - `A A+` → `A{2,}`  
   - `A{m} A{n}` → `A{m+n}`  
   - `A{m} A*` → `A{m,}`  
   - `A{1}` → `A` (se elimina `{1}`)  
   - `(X)+` donde `X` es simple → `X+`

Estas reglas se aplican de forma iterativa hasta alcanzar un punto fijo.

---

## 7. Errores típicos

`translate_to_regex(...)` y el CLI pueden devolver:

- `ERROR: La frase no coincide con el DSL.`  
  - Cuando la frase no se ajusta a la gramática normalizada.

- `ERROR interno: …`  
  - Excepción inesperada durante el parseo o la traducción.

Además, si la regex final no es compilable por `re`:

- `ERROR: La regex generada no es válida.`  
  - Por ejemplo: `range 'z' to 'a'` → `[z-a]` produce un error de rango en la clase de caracteres.

---

## 8. Ejemplos completos

Algunos ejemplos de `commands.show_examples()`:

```text
--- Básicos ---
  letter followed by digit
  uppercase letter followed by digit zero or more
  'hello' followed by digit between 2 and 4 times
  letter one or more or digit one or more

--- Clases avanzadas ---
  vowel followed by consonant
  word character one or more
  alphanumeric at least 3 times
  whitespace at most 2 times
  non whitespace one or more

--- Rangos ---
  range 'a' to 'z' one or more

--- Grupos ---
  group digit followed by letter end group 3 times

--- Negaciones ---
  letter except 'a'
```

---

## 9. Uso como librería (API Python)

Desde Python podemos importar directamente el traductor:

```python
from lark_parser import translate_to_regex, normalize_text, parse_normalized, translate_tree

regex = translate_to_regex("a lowercase letter optionally followed by three digits")
# regex == "[a-z]?[0-9]{3}"
```

O podemos revisar las fases que tiene implementadas:

```python
phrase = "digits that appear three times"

normalized = normalize_text(phrase)
tree = parse_normalized(normalized)
raw_regex = translate_tree(tree)
from utils import simplify_regex
final_regex = simplify_regex(raw_regex)
```

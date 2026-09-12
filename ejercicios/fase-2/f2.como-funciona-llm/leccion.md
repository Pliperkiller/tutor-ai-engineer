# f2.como-funciona-llm — Cómo funciona un LLM · Lección

*Lee este documento completo y responde las preguntas del final en el chat, una por una, para irlas desarrollando con el tutor.*

Esta lección asume que no sabes nada de modelos de lenguaje. Es larga a propósito: aquí está todo el porqué; en el chat solo discutimos tus respuestas.

---

## Por qué existe

**Qué es un LLM.** Un *modelo de lenguaje* es un programa que, dado un texto, calcula qué trozo de texto es más probable que venga después. "Large" (grande) significa que ese programa tiene miles de millones de parámetros (números ajustados durante el entrenamiento) y se entrenó leyendo una fracción enorme de internet. Claude, GPT y Gemini son LLMs. Cuando "chateas" con uno, lo que ocurre por dentro es que el modelo predice el siguiente trozo, lo añade al texto, vuelve a predecir el siguiente, y así hasta que decide parar.

**Qué se hacía antes y por qué era peor.** Antes de los LLMs, para que un programa "entendiera" lenguaje había dos caminos:
- *Reglas escritas a mano*: "si el usuario escribe 'horario', responde el horario". Funciona para diez frases; se rompe con la número once, con una falta de ortografía o con un sinónimo.
- *Un modelo pequeño por tarea*: uno para clasificar correos como spam, otro para traducir, otro para resumir. Cada uno necesita miles de ejemplos etiquetados a mano y solo sirve para su tarea.

Un LLM resuelve las dos cosas con un solo modelo: le describes la tarea en lenguaje corriente y la hace, sin reglas ni ejemplos etiquetados. Ese salto es lo que crea el trabajo de AI Engineer: ya no entrenas modelos, construyes sistemas alrededor de uno que ya existe.

**Por qué necesitas saber cómo funciona por dentro.** Porque en cuanto lo usas desde código te cobran, te limitan y te sorprende, y las tres cosas dependen de mecanismos concretos:
- Te cobran por *token*, no por palabra ni por letra. Si no sabes qué es un token, no puedes estimar un costo.
- Cada llamada tiene un tamaño máximo (la *ventana de contexto*). Si no sabes cómo se llena, tu programa fallará en producción con la conversación número 200.
- El modelo puede responder distinto a la misma pregunta. Si no sabes qué es la *temperatura*, no puedes decidir cuándo eso es deseable y cuándo es un bug.

Esos tres mecanismos, más un cuarto (los *embeddings*) que usarás en la Fase 3, son la lección de hoy.

---

## Términos que vas a ver

- **Modelo**: un programa que recibe una entrada, la pasa por millones de operaciones matemáticas con parámetros fijos y produce una salida. No "piensa" en el sentido humano: calcula.
- **Parámetros**: los números internos del modelo, ajustados durante el entrenamiento y congelados después. No los tocas nunca desde la API.
- **Entrenamiento**: la fase en la que se ajustan esos números leyendo texto. Ya pasó; tú usas el resultado.
- **Inferencia**: usar el modelo ya entrenado para producir una respuesta. Cada llamada a la API es una inferencia.
- **Prompt**: todo el texto que le mandas al modelo en una llamada (instrucciones, historial, pregunta).
- **Completion** (o respuesta): el texto que el modelo genera a partir del prompt.
- **Token**: la unidad mínima de texto que el modelo maneja. No es una letra ni una palabra: es un trozo de una tabla fija.
- **Tokenización**: el proceso de partir un texto en tokens.
- **Tokenizador**: el programa (y la tabla) que hace esa partición. Cada familia de modelos tiene el suyo.
- **Vocabulario**: la tabla completa de tokens que un tokenizador conoce. Tiene un tamaño fijo (del orden de 100.000 a 200.000 entradas).
- **BPE** (Byte Pair Encoding): el algoritmo con el que se construyó esa tabla. Lo verás explicado abajo.
- **Ventana de contexto**: la cantidad máxima de tokens que el modelo puede tener delante en una sola llamada, sumando lo que le mandas y lo que genera.
- **Autoregresivo**: forma de generar texto en la que cada token nuevo se calcula mirando todos los anteriores, incluidos los que el propio modelo acaba de generar.
- **Distribución de probabilidad**: una lista de "cuánto de probable es cada opción", donde todas las opciones suman 100%.
- **Sampling** (muestreo): elegir un token al azar según esa distribución, en vez de tomar siempre el más probable.
- **Temperatura**: un número que aplana o afila la distribución antes de muestrear. Controla cuánta variedad hay en la respuesta.
- **top_p / top_k**: otras dos formas de limitar entre qué tokens se muestrea. Las verás con la temperatura.
- **Determinista**: que da siempre la misma salida para la misma entrada.
- **Vector**: una lista ordenada de números, por ejemplo `[0.2, -1.3, 0.7]`.
- **Embedding**: un vector que representa el significado de un texto, de modo que textos parecidos tienen vectores parecidos.
- **Entorno virtual**: una carpeta con su propia copia de Python y sus librerías, para que este proyecto no mezcle versiones con otros. Ya lo usaste con `uv` en toda la Fase 1.

---

## Concepto

### 1. Lo único que hace un LLM: predecir el siguiente token

Toma esta frase incompleta: "El cielo es". Tú, sin pensar, completas "azul". Un LLM hace exactamente eso, pero con una diferencia: no elige una sola palabra, calcula una probabilidad para **cada token de su vocabulario** (los 200.000). Algo como:

| siguiente token | probabilidad |
|---|---|
| ` azul` | 66,7 % |
| ` gris` | 24,5 % |
| ` verde` | 5,5 % |
| ` negro` | 3,3 % |
| ...199.996 más | casi 0 % |

Luego elige uno (cómo lo elige es la sección 4), lo pega al final del texto, y **repite todo el cálculo** con el texto nuevo: "El cielo es azul" → ¿siguiente? Quizá ` porque`. Y otra vez. Y otra. Así, token a token, hasta que el token elegido es uno especial que significa "fin de la respuesta". A esto se le llama generación *autoregresiva*: cada paso depende de todos los anteriores, incluidos los que el modelo mismo acaba de producir.

**Analogía cotidiana**: el autocompletar del teclado del teléfono. Escribes "buenos" y te sugiere "días". Un LLM es ese autocompletar, pero entrenado con casi todo lo escrito por la humanidad y capaz de mirar miles de palabras hacia atrás en vez de una. **Dónde falla la analogía**: el autocompletar del teléfono solo sugiere la palabra siguiente y para; el LLM encadena miles de sugerencias seguidas y, gracias a eso, "escribe" párrafos coherentes, código o respuestas a preguntas. Y el del teléfono mira dos o tres palabras atrás; el LLM mira todo el prompt.

Dos consecuencias que vas a ver todo el tiempo:
1. El modelo no "sabe" la respuesta y luego la escribe; la va construyendo token a token. Por eso a veces empieza bien y se descarrila: cada token malo condiciona los siguientes.
2. Generar es caro: cada token de salida es una pasada completa por el modelo. Por eso la salida cuesta más que la entrada (en Claude Opus 5, 5 veces más por token).

> **Predicción intercalada 1**: si el modelo genera una respuesta de 300 tokens, ¿cuántas veces calculó la tabla de probabilidades completa? Anota tu respuesta antes de seguir. (Respuesta: 300 veces, una por token generado. Si respondiste 1, vuelve a leer "repite todo el cálculo".)

### 2. Tokens: en qué unidades "lee" el modelo

Un programa no puede operar sobre letras directamente: opera sobre números. Hay que convertir el texto en números. Las opciones obvias son malas:
- *Un número por letra*: la palabra "internacionalización" serían 20 números y el modelo tendría que "aprender" a juntar letras en palabras. Secuencias larguísimas, aprendizaje lento.
- *Un número por palabra*: bien para palabras comunes, pero ¿qué número le das a "desoxirribonucleico", a "Bogotá", a "xkcd" o a una palabra con error de tipeo? Necesitarías un vocabulario infinito.

La solución intermedia se llama **BPE** (Byte Pair Encoding) y funciona así. Antes de entrenar el modelo, se construye una tabla:
1. Se empieza con las 256 unidades mínimas (cada byte posible). Con eso cualquier texto del mundo se puede representar, aunque muy largo.
2. Se toma un corpus enorme de texto y se busca el par de unidades adyacentes que más veces aparece junto (por ejemplo `t` + `h`).
3. Ese par se fusiona en una unidad nueva (`th`) y se añade a la tabla.
4. Se repite el paso 2 con la tabla nueva, unas 200.000 veces. Van naciendo `the`, ` the`, `ing`, `ización`, ` gato`...

El resultado es un **vocabulario**: una tabla fija que asigna a cada trozo un número entero (su *id*). Las palabras muy comunes acaban siendo un solo token; las raras se parten en trozos que sí están en la tabla. Y como la tabla se construyó con un corpus donde había mucho más inglés que español, el inglés sale más "barato": mira en la demo cómo "internationalization" son 2 tokens y "internacionalización" son 3.

**Analogía cotidiana**: piezas de Lego. Tienes piezas de 1, 2, 4 y 8 puntos, y una figura cualquiera se arma combinándolas. Las formas comunes tienen su pieza grande dedicada; las raras se construyen con muchas piezas pequeñas. **Dónde falla la analogía**: las piezas de Lego son intercambiables; los tokens no. El token ` gato` (con espacio delante) y el token `gato` (sin espacio) son dos piezas **distintas**, con ids distintos, y el modelo aprendió cosas distintas sobre cada uno. El espacio no es un separador: es parte de la pieza.

Cosas concretas que salen de esto y que vas a comprobar en la demo:
- Mayúsculas y minúsculas son piezas distintas: `Hello` y `hello` tienen ids diferentes.
- Los números no se parten por dígitos ni por cifras completas: `1234567890` sale como `123`, `456`, `789`, `0`. Por eso los modelos hacen aritmética "rara": no ven los dígitos como tú.
- Un emoji o una letra acentuada puede ser 1 token o varios, según si estaba en la tabla.
- Una regla de dedo para estimar costos: en inglés ~4 caracteres por token (≈ 0,75 palabras por token); en español, ~3 caracteres por token. Un texto en español gasta entre 20 % y 40 % más tokens que el mismo texto en inglés.

**El modelo no ve letras.** Esto explica un fallo famoso: si preguntas cuántas "r" tiene "strawberry", el modelo a menudo se equivoca. No es que no sepa contar: es que "strawberry" le llega como uno o dos tokens (por ejemplo `str` + `awberry`), y dentro de un token las letras no existen como unidades separadas. Es como pedirte que cuentes las curvas de un carácter chino que solo conoces como dibujo completo.

**Cada familia de modelos tiene su tabla.** El tokenizador de Claude no es el de GPT ni el de Gemini. Los ids y los cortes cambian; el mecanismo no. En la demo usamos la tabla de OpenAI (`tiktoken`) porque es la única pública que corre en tu PC sin clave. Cuando en el tópico siguiente tengas la API key de Anthropic, la cuenta oficial para Claude se pide al endpoint `count_tokens`, nunca a `tiktoken`: los números serían de otro modelo.

> **Predicción intercalada 2**: ¿"perro" y "perros" comparten algún token? Piensa cómo BPE partiría cada uno y anota tu respuesta. La verás en el ejercicio.

### 3. Ventana de contexto: cuánto puede ver el modelo de una vez

El modelo calcula el siguiente token mirando todos los tokens anteriores. Ese "todos" tiene un tope físico: la **ventana de contexto**. Es el número máximo de tokens que caben en una llamada, **sumando** lo que mandas (prompt) y lo que el modelo genera (completion). Tamaños actuales:

| Modelo | Ventana de contexto |
|---|---|
| Claude Opus 5 / Sonnet 5 / Fable 5.1 | 1.000.000 tokens |
| Claude Haiku 4.5 | 200.000 tokens |

Un millón de tokens son unas 750.000 palabras en inglés: varios libros. Parece infinito; no lo es, por lo siguiente.

**El modelo no tiene memoria entre llamadas.** Esto es lo más importante de la sección y lo que más gente entiende mal. Cuando chateas, sientes que el modelo "recuerda" lo que dijiste hace cinco mensajes. No recuerda nada: la aplicación de chat **vuelve a mandarle toda la conversación** en cada llamada, desde el primer mensaje. En el turno 40, el prompt contiene los 39 turnos anteriores más tu mensaje nuevo. El modelo es una función pura: entrada completa → salida. Sin estado.

**Analogía cotidiana**: una pizarra de tamaño fijo con un profesor sin memoria. Cada vez que le haces una pregunta, tienes que escribir en la pizarra TODO lo que necesita saber, incluidas las preguntas y respuestas anteriores; él lee la pizarra entera, responde, y se olvida. Si la pizarra se llena, no cabe la pregunta nueva. **Dónde falla la analogía**: en una pizarra real borrarías lo viejo y ya; con el modelo, si borras un turno anterior, la respuesta cambia, porque para él ese turno nunca existió. Por eso resumir o recortar historial es una decisión de diseño delicada (se llama *compactación* y la verás en la Fase 4).

Tres consecuencias que vas a manejar en código:
1. **El costo crece con la conversación.** Si cada turno se reenvía entero, el turno 40 cuesta lo que pesan 40 turnos. Una conversación larga es cuadrática en costo. (Existe un mecanismo llamado *prompt caching* que abarata reenviar lo mismo; lo verás en `f2.llamadas-api`.)
2. **Si te pasas de la ventana, la API devuelve un error** (HTTP 400), no una respuesta recortada. Tu programa tiene que contar tokens antes de mandar, o manejar ese error.
3. **Más contexto no es gratis en calidad.** Un modelo con un millón de tokens delante puede "perder" un dato enterrado en el medio (lo que se conoce como *lost in the middle*). Meterle todo "por si acaso" empeora respuestas y sube costos. La Fase 3 (RAG) existe precisamente para mandar solo lo relevante.

> **Predicción intercalada 3**: una app de chat manda en cada turno un system prompt de 2.000 tokens más el historial. Si cada turno (pregunta + respuesta) pesa 500 tokens, ¿cuántos tokens de entrada se mandan en el turno 10? Anota el cálculo. (Respuesta: 2.000 + 9 × 500 + la pregunta nueva ≈ 6.500 + pregunta. Si te dio 2.500, releé "vuelve a mandarle toda la conversación".)

### 4. Temperatura y sampling: cómo se elige el siguiente token

Volvamos a la tabla de la sección 1. El modelo calculó, para "El cielo es", que ` azul` tiene 66,7 %, ` gris` 24,5 %, etc. Falta decidir **cuál** sale. Hay dos estrategias:

- **Greedy** ("codicioso"): tomar siempre el más probable. Salida repetitiva y a veces atascada en bucles ("el cielo es azul y el cielo es azul y...").
- **Sampling** (muestreo): tirar un dado cargado con esas probabilidades. El 66,7 % de las veces sale ` azul`, pero a veces sale ` gris`. Las respuestas varían y suenan más naturales.

La **temperatura** (`temperature`, un número que normalmente va de 0 a 2) modifica la tabla **antes** de tirar el dado. Por dentro, el modelo no produce probabilidades directamente sino unas puntuaciones crudas llamadas *logits*; la temperatura divide esos logits antes de convertirlos en probabilidades. El efecto sobre nuestro ejemplo, calculado de verdad:

| token | T = 0,2 | T = 0,7 | T = 1,0 | T = 2,0 |
|---|---|---|---|---|
| ` azul` | 99,3 % | 78,0 % | 66,7 % | 47,3 % |
| ` gris` | 0,7 % | 18,7 % | 24,5 % | 28,7 % |
| ` verde` | 0,0 % | 2,2 % | 5,5 % | 13,5 % |
| ` negro` | 0,0 % | 1,1 % | 3,3 % | 10,5 % |

Lee la tabla por columnas:
- **T baja (→ 0)**: la distribución se *afila*: el favorito se lleva casi todo. En T = 0 el muestreo se convierte en greedy: siempre el más probable. Salida estable, predecible, "aburrida".
- **T = 1**: la distribución tal como el modelo la calculó.
- **T alta (> 1)**: la distribución se *aplana*: los tokens raros ganan terreno. Salida más variada, más creativa y, pasado cierto punto, incoherente (con T = 2 uno de cada diez "El cielo es" termina en ` negro`).

**Analogía cotidiana**: un dado cargado y la temperatura es cuánto lo cargas. A T = 0 el dado está tan cargado que siempre cae en la misma cara. A T = 2 casi lo descargaste y cae en cualquiera. **Dónde falla la analogía**: el dado se tira una vez por token, no una vez por respuesta. Una respuesta de 300 tokens son 300 tiradas, y un solo resultado raro en la tirada 12 cambia todas las tiradas siguientes (recuerda: autoregresivo). Por eso una temperatura alta no da "una respuesta un poco distinta": puede dar una respuesta que se va por otro camino completo.

Dos matices que separan a quien lo entiende de quien lo repite:
1. **T = 0 no garantiza determinismo absoluto.** Casi siempre da lo mismo, pero el cálculo en GPU tiene pequeñas variaciones numéricas y a veces dos tokens quedan empatados. Si necesitas exactamente la misma salida siempre (por ejemplo para tests), no confíes en T = 0: guarda la salida (un *snapshot*) o valida la estructura en vez del texto literal.
2. **La temperatura no hace al modelo "más inteligente" ni "más tonto"**: la tabla de probabilidades es la misma. Solo cambia cómo se elige de ella.

**top_p y top_k**: otras dos perillas que limitan *entre cuántos* tokens se tira el dado, en vez de cambiar sus pesos. `top_k = 3` dice "solo considera los 3 más probables, ignora el resto". `top_p = 0,9` dice "ordena de mayor a menor y quédate con los primeros hasta acumular el 90 % de probabilidad" (en la columna T = 1 serían ` azul` + ` gris`, que suman 91 %). Sirven para cortar la cola de tokens absurdos sin afilar toda la distribución. Regla práctica: se mueve **una** perilla, no las tres a la vez, o no sabes qué causó qué.

**Nota de versión (importante para el tópico siguiente)**: en los modelos Claude actuales (Opus 5, Sonnet 5, Fable 5.1 y la familia 4.7/4.8) los parámetros `temperature`, `top_p` y `top_k` **fueron eliminados de la API**: mandarlos devuelve un error 400. Esos modelos razonan antes de responder (*thinking*) y el control de variedad se hace por otro camino (`effort`). Haiku 4.5, los modelos Claude anteriores y la API de OpenAI sí los aceptan. Por eso, cuando verifiquemos tus predicciones de temperatura contra la API real en `f2.llamadas-api`, lo haremos contra un modelo que aún las acepte.

> **Predicción intercalada 4**: tienes que extraer el número de factura de 500 PDFs a un JSON. ¿Temperatura baja o alta? ¿Y para generar 20 nombres candidatos para un producto? Anota el porqué de cada una en una frase.

### 5. Embeddings: el significado como coordenadas

Todo lo anterior trata al modelo como una caja que genera texto. Pero por dentro, en el primer paso, cada token se convierte en un **vector**: una lista de varios cientos o miles de números. Ese vector es el *embedding* del token. Durante el entrenamiento, los vectores se ajustaron de forma que tokens con significados parecidos quedan **cerca** (sus números se parecen) y tokens sin relación quedan lejos.

Hay modelos dedicados (los *modelos de embeddings*) que hacen lo mismo con un texto entero: le das una frase o un párrafo y te devuelven un solo vector que resume su significado. Ejemplo con vectores de dos números para que se pueda dibujar (los reales tienen 1.024 o más):

| texto | vector (inventado, 2D) |
|---|---|
| "¿Cómo reseteo mi contraseña?" | `[0,9, 0,1]` |
| "Olvidé mi clave de acceso" | `[0,8, 0,2]` |
| "¿Cuánto cuesta el plan anual?" | `[0,1, 0,9]` |

Las dos primeras frases no comparten casi ninguna palabra, pero sus vectores están casi encima: significan lo mismo. La tercera está lejos. Con una operación matemática (la *similitud coseno*, que mide el ángulo entre dos vectores) obtienes un número entre -1 y 1: cerca de 1 significa "mismo significado".

**Analogía cotidiana**: coordenadas en un mapa. Dos restaurantes con direcciones distintas pueden estar a 50 metros; dos con nombres parecidos pueden estar en ciudades distintas. Lo que importa es la posición, no el nombre. **Dónde falla la analogía**: un mapa tiene 2 dimensiones y puedes verlo; un embedding tiene más de mil y nadie puede visualizarlo. Además, en el mapa la distancia es fija; en los embeddings depende del modelo que los calculó: dos vectores de modelos distintos no se pueden comparar entre sí.

Para qué lo vas a usar: es la base de la **búsqueda semántica** y de RAG (Fase 3). En vez de buscar documentos que contengan la palabra exacta "contraseña", conviertes la pregunta a vector, conviertes cada documento a vector, y traes los más cercanos. Hoy solo necesitas la idea: *significado → lista de números → cercanía*.

---

## Demo mínima

Archivo: `ejercicios/fase-2/f2.como-funciona-llm/01-predecir-tokens/demo_tokens.py`. Léelo antes de correrlo; después de la salida está explicado línea por línea.

### Preparación

Abre una terminal **en la carpeta del ejercicio**:

```powershell
cd C:\Users\pipek\OneDrive\Documentos\dev\tutor-ai-engineer\ejercicios\fase-2\f2.como-funciona-llm\01-predecir-tokens
uv sync
```

Qué hace `uv sync`: lee `pyproject.toml` (la lista de dependencias del proyecto) y `uv.lock` (las versiones exactas ya fijadas por el tutor), crea la carpeta `.venv` (el entorno virtual de este ejercicio) e instala ahí `tiktoken` y `ruff`. Salida esperada: unas líneas que terminan con `+ tiktoken==0.14.0` (o similar) y `+ ruff==...`. Si `.venv` ya existía, dirá `Audited N packages` y no instalará nada.

```powershell
uv run python demo_tokens.py
```

Qué hace `uv run`: ejecuta el comando que sigue **dentro** del entorno virtual, sin que tengas que activarlo a mano. `python demo_tokens.py` corre el script. La primera vez, `tiktoken` descarga la tabla del vocabulario (unos MB) y la guarda en caché; las siguientes veces no toca la red.

Salida esperada (esta es la real, corrida por el tutor):

```text
vocabulary size: 200019

'hello'                            1 tokens  pieces=['hello']
' hello'                           1 tokens  pieces=[' hello']
'Hello'                            1 tokens  pieces=['Hello']
'Hello, world!'                    4 tokens  pieces=['Hello', ',', ' world', '!']
'supercalifragilistic'             6 tokens  pieces=['super', 'cal', 'if', 'rag', 'il', 'istic']
'desoxirribonucleico'              6 tokens  pieces=['des', 'ox', 'irr', 'ibon', 'ucle', 'ico']
'2024'                             2 tokens  pieces=['202', '4']
'1234567890'                       4 tokens  pieces=['123', '456', '789', '0']
'The cat sat on the mat.'          7 tokens  pieces=['The', ' cat', ' sat', ' on', ' the', ' mat', '.']
'El gato se sentó en la alfombra.' 10 tokens  pieces=['El', ' gato', ' se', ' sent', 'ó', ' en', ' la', ' alf', 'ombra', '.']

ids     : [4422, 99767, 458, 3860, 531, 469, 557, 76652, 127972, 13]
decoded : El gato se sentó en la alfombra.
```

Fíjate: la frase en inglés y su traducción dicen lo mismo, pero el español cuesta 10 tokens y el inglés 7. Y "sentó" se partió en ` sent` + `ó` porque el acento no estaba en la tabla junto con el resto de la palabra.

### El código, línea por línea

```python
import sys

import tiktoken
```
`sys` es el módulo estándar de Python para hablar con el sistema (aquí lo usamos para la salida de la consola). `tiktoken` es la librería del tokenizador; la instaló `uv sync`. Sin la segunda línea, `tiktoken.get_encoding` daría `NameError`.

```python
sys.stdout.reconfigure(encoding="utf-8")
```
`sys.stdout` es "la consola donde se imprime". En Windows, esa consola a veces usa una codificación antigua que no sabe mostrar "ó" ni emojis y los imprime como `?` o `�`. Esta línea le dice "usa UTF-8", la codificación que sí los representa. En Mac o Linux no hace falta, pero no estorba.

```python
encoding = tiktoken.get_encoding("o200k_base")
```
Carga la tabla del vocabulario y la guarda en la variable `encoding`. `"o200k_base"` es el nombre de la tabla que usa la familia GPT-4o: "o" por la familia, "200k" por su tamaño (unas 200.000 entradas), "base" porque es la versión sin añadidos de chat. A partir de aquí, `encoding` sabe convertir texto ↔ ids.

```python
def show(text: str) -> None:
    """Print how `text` is split: how many tokens, their ids and their pieces."""
```
Definimos una función auxiliar para no repetir cuatro líneas diez veces. Recibe un texto y no devuelve nada (`-> None`): solo imprime.

```python
    ids = encoding.encode(text)
```
**La línea central de la demo.** `encode` toma el texto y devuelve la lista de ids (enteros) de sus tokens, en orden. `"Hello, world!"` → `[13225, 11, 2375, 0]`. La longitud de esa lista es el número de tokens: eso es lo que te cobran.

```python
    pieces = [encoding.decode([token_id]) for token_id in ids]
```
`decode` hace lo contrario: lista de ids → texto. Aquí lo llamamos con **un id a la vez** (por eso `[token_id]`, una lista de un elemento) para recuperar el trozo de texto de cada token por separado. Es solo para que tú veas los cortes; en un programa real nunca harías esto. Sin esta línea, verías `[13225, 11, ...]` y no sabrías qué trozo es cada número.

```python
    print(f"{text!r:32} {len(ids):2} tokens  pieces={pieces}")
```
Imprime una fila alineada. `{text!r}` muestra el texto con comillas (`!r` = *repr*), lo que hace visible el espacio inicial de `' hello'`; `:32` reserva 32 caracteres para que las columnas queden alineadas. `len(ids)` es la cuenta de tokens.

```python
print(f"vocabulary size: {encoding.n_vocab}")
```
`n_vocab` es el tamaño de la tabla. Sale 200.019: 200.000 tokens "normales" más 19 especiales (como el de "fin de texto").

```python
show("hello")
show(" hello")
show("Hello")
```
Las tres llamadas que prueban lo que dijo la sección 2: misma palabra, con espacio delante, con mayúscula. Los tres son 1 token, pero **tres ids distintos** (compruébalo tú añadiendo `print(ids)` dentro de `show` si quieres).

```python
show("2024")
show("1234567890")
```
Los números se parten de tres en tres cifras, no por dígito. Por eso el modelo no "ve" que 1234567890 tiene diez dígitos.

```python
ids = encoding.encode("El gato se sentó en la alfombra.")
print("ids     :", ids)
print("decoded :", encoding.decode(ids))
```
El viaje de ida y vuelta: texto → ids → texto. `decode` con la lista completa reconstruye **exactamente** la frase original, acento incluido. Sin esa garantía, el modelo podría devolverte texto corrupto.

---

## Errores típicos

1. **"Una palabra es un token"** → presupuestos de costo un 30-40 % cortos, y en español más. Síntoma: la factura de la API llega más alta de lo estimado. Causa: las palabras raras, los acentos, los números y la puntuación se parten. Antídoto: contar con el tokenizador real, nunca con `len(text.split())`.
2. **"El modelo recuerda la conversación"** → se manda solo el mensaje nuevo y el modelo responde como si fuera el primero ("¿a qué te refieres con 'eso'?"). Causa: sin estado entre llamadas; el historial lo mantienes tú. Antídoto: la lista de mensajes vive en tu código y se reenvía entera.
3. **"Con `temperature=0` el test siempre pasa"** → un test que compara el texto literal falla una vez cada tantas corridas. Causa: T = 0 es casi determinista, no determinista. Antídoto: validar estructura (¿es JSON válido? ¿tiene el campo?) o comparar contra un snapshot guardado.
4. **Pedirle al modelo que cuente letras, invierta palabras o haga aritmética larga** → respuestas confiadas y erróneas. Causa: no ve letras ni dígitos, ve tokens. Antídoto: esas tareas se hacen con código (Python), y en la Fase 2 verás cómo hacer que el modelo llame a ese código (*tool use*).

---

## Preguntas — respóndelas en el chat

1. Sin correr nada todavía: `"gato"`, `" gato"` (con espacio delante) y `"Gato"`. ¿Cuántos tokens crees que es cada uno, y tienen el mismo id o ids distintos? Explica con la idea de "pieza de la tabla" por qué.
2. Una app de chat lleva 40 turnos. ¿Cuántas veces ha viajado el **primer** mensaje del usuario hasta el modelo? ¿Qué implica eso para el costo del turno 40 comparado con el turno 1?
3. Con la tabla de temperaturas de la sección 4: si le pides al modelo "El cielo es" 100 veces con T = 0,2 y 100 veces con T = 2,0, ¿cuántas veces esperas ` azul` en cada caso, aproximadamente? Y en una frase: ¿por qué T = 0 no garantiza exactamente la misma respuesta las 100 veces?
4. ¿Por qué un LLM se equivoca contando las "r" de "strawberry", y qué harías tú como AI Engineer si tu aplicación necesita esa cuenta bien hecha?

---

## Fuentes
- Anthropic, *Models overview* (ventanas de contexto y precios): https://docs.anthropic.com/en/docs/about-claude/models
- Anthropic, *Token counting* (`count_tokens`): https://docs.anthropic.com/en/docs/build-with-claude/token-counting
- OpenAI, `tiktoken` (repositorio): https://github.com/openai/tiktoken
- Sennrich et al., *Neural Machine Translation of Rare Words with Subword Units* (el paper original de BPE, 2016): https://arxiv.org/abs/1508.07909

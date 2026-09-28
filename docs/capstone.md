# Capstone — Asistente de expedientes legales

Decidido el 2026-09-27 (tras S36). Este documento fija el **dominio** del proyecto
que atraviesa las fases 2 a 8 y detalla el alcance de la **Fase 2**.

---

## 1. Por qué este documento existe

El roadmap no define un proyecto por fase: define **un solo proyecto que crece**.

| Fase | Qué le añade al asistente |
|---|---|
| f1 | La API base en FastAPI que lo sirve (endpoints, validación, tests). **Ya hecha** (como *Model Registry*). |
| f2 | Capa LLM: responde con tool calling y salidas estructuradas. ← **estás aquí** |
| f3 | RAG sobre el corpus del dominio, con métricas de retrieval. |
| f4 | Suite de evals + tracing. |
| f5 | Agente: tareas multi-paso del dominio vía un servidor MCP propio. |
| f6 | Desplegado en AWS con CI/CD y defensa contra prompt injection. |
| f7 | Un componente sensible a costo/latencia comparado contra un modelo abierto. |
| f8 | Demo pública + writeup de arquitectura y métricas. |

Elegir el dominio en f2 es comprometerse para seis fases. Por eso se escribe aquí
y no se decide de nuevo en cada capstone.

## 2. El dominio

**Asistente de gestión de expedientes para una firma legal.** Dominio elegido por
el estudiante: es su área de trabajo real (Rops.io, consultoría IT para firmas
legales sobre Filevine), así que aporta criterio de dominio que el tutor no tiene,
y es candidato a proyecto interno de la empresa.

**Generalización deliberada:** el sistema modela *gestión de expedientes*
(matters), no *Filevine*. No se acopla al API ni al vocabulario de un producto de
un tercero. Razones: (a) la demo pública de f8 no puede depender del acceso a un
producto comercial, (b) el valor del portafolio está en la arquitectura, no en la
integración, (c) si más adelante quieres conectarlo a Filevine de verdad, será una
implementación más detrás de la misma interfaz.

### 2.1 Regla de datos — no negociable

**Los datos son sintéticos desde su origen.** No se toman registros reales para
transformarlos después.

Por qué la anonimización de registros reales no sirve aquí:
- La pseudonimización (cambiar nombres por "Cliente A") deja **cuasi-identificadores**:
  la combinación de fecha de incidente + tipo de caso + jurisdicción + monto suele
  ser única y reidentifica al expediente.
- La estructura misma delata: un número de expediente con formato propio de la
  firma, una fecha poco común, un apellido raro que sobrevive al reemplazo.
- A partir de f6 los datos **salen de tu máquina** (deployment en AWS), y en f8
  son públicos. Un descuido en f2 se vuelve un incidente en f8.

**Lo que sí se hace:** un script generador (`scripts/generate_matters.py`) que
produce expedientes desde plantillas y listas de valores. Tú aportas la
*estructura* de los expedientes reales — qué campos existen, qué fases atraviesa
un caso, qué rangos son plausibles —, nunca los registros. El generador se versiona
con semilla fija para que los tests sean reproducibles.

### 2.2 Entidades

Mínimo viable para f2 (ampliable después):

- **Matter** (expediente): `matter_id`, `client_name`, `case_type`
  (p. ej. `personal_injury | contract_dispute | employment`), `status`
  (`intake | discovery | negotiation | closed`), `opened_on`, `statute_of_limitations`.
- **CaseNote** (nota de expediente): `matter_id`, `author`, `created_at`, `text`.
- **Intake** (contacto inicial sin estructurar): el texto libre de un correo o de
  la nota de una llamada. Es la materia prima de las salidas estructuradas.

## 3. Portar la API de f1

Tu API de f1 es un *Model Registry* (`/models`, `/models/{id}`, `/models/{id}/cost`,
API key, consumo de Frankfurter, suite de tests con mocks). El capstone necesita la
misma API con otras entidades.

**No es reescribir: es renombrar.** El esqueleto — routing, validación con Pydantic,
`Depends(verify_api_key)`, 404 y 201, conftest y fixtures — se conserva entero.
Cambian los modelos y las rutas:

| f1 (Model Registry) | Capstone (Matter Registry) |
|---|---|
| `GET /models` | `GET /matters` (con filtro opcional `?status=`) |
| `GET /models/{model_id}` | `GET /matters/{matter_id}` |
| `POST /models` | `POST /matters` |
| `GET /models/{model_id}/cost` | `GET /matters/{matter_id}/notes` |
| — | `POST /matters/{matter_id}/notes` |

Coste estimado: media sesión. Se hace al empezar el capstone, no antes.

## 4. Alcance de la Fase 2

**Criterio de dominio de la fase (del roadmap, literal):**

> Construir un asistente CLI que use tool calling con al menos 3 herramientas
> reales, devuelva salidas estructuradas validadas, maneje errores de API con
> reintentos y registre el costo en tokens de cada sesión.

Cuatro requisitos. Uno por uno:

### 4.1 Tool calling con ≥3 herramientas reales

Las herramientas son clientes HTTP de **tu propia API** — no funciones locales.
Esa es la diferencia con `01-agente-notas`: ahí las herramientas tocaban el disco;
aquí cruzan la red, y por eso pueden fallar de formas que el ejercicio no tenía
(timeout, 500, 401 por API key vencida) y que deben llegar al modelo como
`is_error` sin romper la conversación.

1. `list_matters(status: str | None)` — lista expedientes, filtro opcional.
2. `get_matter(matter_id: str)` — detalle. Camino de error obligatorio: id
   inexistente → 404 → `is_error: True`, y el modelo debe recuperarse (típicamente
   llamando a `list_matters`), como hizo con `shopping` en `01-agente-notas`.
3. `add_case_note(matter_id: str, text: str)` — **escritura**. Es la primera
   herramienta del proyecto con efecto de lado sobre datos reales del sistema:
   exige pensar qué pasa si el modelo la llama dos veces.
4. *(opcional)* `compute_deadline(from_date: str, days: int)` — cálculo de plazos.
   Aritmética pura, sin red: buen contraste con las otras tres.

### 4.2 Salidas estructuradas validadas

Aquí entra `f2.salidas-estructuradas` (el tópico que sigue). El caso del dominio:

**Extraer un `Intake` estructurado de un texto libre.** Entrada: el correo o la
nota de llamada de un cliente potencial, en prosa. Salida: un modelo Pydantic
validado (`client_name`, `case_type` como `Literal[...]`, `incident_date`,
`summary`, `urgency`). El criterio del tópico pide **20 textos con 100% de tasa de
parseo**, incluyendo estrategia de reintento ante salidas inválidas — los 20 textos
salen del generador sintético.

Este es el punto donde tu `f1.pydantic-validacion` (`dominado`) hace el trabajo
pesado: el modelo Pydantic **es** el contrato, y el `enum` del JSON Schema es el
`Literal[...]` que ya sabes escribir.

### 4.3 Reintentos ante errores de API

Reusa el cliente con backoff exponencial de `f2.llamadas-api`
(`01-cliente-anthropic`). Dos capas distintas que no hay que confundir:

- **Error de la API del LLM** (429, 500, timeout) → reintento con backoff. El
  usuario no se entera.
- **Error de una herramienta** (404 de tu API, argumento inválido) → `is_error: True`
  hacia el modelo. El modelo decide qué hacer. **No** se reintenta a ciegas.

Distinguirlas es exactamente el límite de `is_error` que te costó ver en S35.

### 4.4 Registro del costo en tokens por sesión

Cada llamada al LLM reporta `usage.input_tokens` y `usage.output_tokens`. El
asistente acumula por sesión y, al salir, imprime el total y el costo en dólares.
Ojo con lo que ya sabes de f2: en un loop de tool calling **el historial completo
se reenvía en cada vuelta**, así que los tokens de entrada crecen de forma
cuadrática con el número de vueltas. Verlo en el contador es media lección.

### 4.5 Fuera de alcance en f2

No metas aquí lo que tiene su propia fase: nada de RAG ni base vectorial (f3),
nada de evals automatizados ni Langfuse (f4), nada de MCP (f5), nada de deployment
(f6). `f2.multi-proveedor` sí entra si llega antes que el capstone: la capa de
abstracción con fallback envuelve al cliente del asistente.

## 5. Estructura propuesta

```
capstone/
  pyproject.toml
  scripts/
    generate_matters.py      # datos sintéticos, semilla fija
  api/                       # la API de f1, portada a matters
    main.py
    models.py
    conftest.py
  assistant/
    cli.py                   # el bucle de conversación
    tools.py                 # los clientes HTTP de la API
    declarations.py          # los TOOLS que ve el modelo
    extraction.py            # texto libre -> modelo Pydantic
    llm_client.py            # reintentos con backoff + contador de tokens
  tests/
```

## 6. Definición de terminado

- [ ] El generador produce ≥30 expedientes y ≥20 textos de intake sintéticos, reproducibles con semilla.
- [ ] La API de matters corre y su suite de tests pasa.
- [ ] El asistente CLI mantiene una conversación usando las 3 herramientas.
- [ ] Un id de expediente inexistente produce `is_error` y el asistente se recupera sin caerse.
- [ ] Los 20 intakes parsean a Pydantic al 100%, con reintento ante salida inválida.
- [ ] Un 429 o un timeout del LLM se reintenta con backoff y no llega al usuario.
- [ ] Al salir, el CLI imprime tokens de entrada, de salida y costo de la sesión.
- [ ] Tests con mocks del LLM: la suite corre sin red y sin gastar tokens (patrón `FakeClient` de `01-agente-notas`).

## 7. Decisiones abiertas

- Nombre del proyecto (hoy: "asistente de expedientes").
- Si el store de la API sigue en memoria o pasa a SQLite. En memoria basta para f2;
  f3 va a querer persistencia.
- Qué proveedor secundario usar en `f2.multi-proveedor` (decidir **antes** de esa
  sesión: es el único pendiente de f2 con fricción de credenciales).

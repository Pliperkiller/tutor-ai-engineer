# Roadmap estándar de AI Engineer (2026 →)

Parte desde cero (sin asumir experiencia previa en programación) y llega a un perfil de AI Engineer de capa de aplicación: alguien que construye sistemas de producción sobre LLMs — RAG, agentes, integraciones — sin entrenar modelos desde cero. Cada fase tiene un criterio de dominio verificable que servirá para ubicar el punto de partida real de quien lo use.

## Principios de diseño

1. **Profundidad sobre amplitud**: una herramienta representativa por categoría (un framework de agentes, una vector DB, una plataforma de observabilidad), no el zoológico completo. Cambiar de herramienta después es trivial; dominar el patrón no.
2. **Primero lo que no caduca**: Python sólido, APIs, cómo funcionan los LLMs y cómo se evalúan. Los frameworks de moda rotan cada 18 meses; estos fundamentos no.
3. **Sesgo hacia donde va el campo (según la investigación 2026)**: agentes en producción, MCP como protocolo estándar de integración, evals como disciplina central ("un RAG sin evaluación es un demo, no un sistema de producción") y observabilidad como requisito base.
4. **La IA como copiloto**: se asume uso de asistentes de código durante todo el roadmap. Lo que se entrena es el criterio que la IA no da: diseñar la arquitectura, detectar cuándo el sistema falla y decidir qué patrón aplica.
5. **Certificaciones como señal, no como fin**: máximo 1-2 grandes como ancla ATS; el consenso 2026 es claro en que el portafolio desplegado pesa más que cualquier badge.

## Mapa general

| # | Fase | Horas est. | Certificación ancla |
|---|------|-----------|---------------------|
| 1 | Fundamentos de programación para IA | 80 | — |
| 2 | LLMs, prompting y tool use | 60 | — (cursos gratuitos DeepLearning.AI) |
| 3 | RAG y bases vectoriales | 70 | — |
| 4 | Evals y observabilidad | 50 | — |
| 5 | Agentes y MCP | 80 | — (LangChain Academy, gratuita) |
| 6 | Deployment y LLMOps | 70 | AWS Certified AI Practitioner o Azure AI-102 |
| 7 | Modelos abiertos y fine-tuning selectivo | 60 | — |
| 8 | Portafolio y perfil profesional | 40 | — |

Total ≈ 510 horas efectivas entre estudio y práctica.

---

## Fase 1 — Fundamentos de programación para IA (~80 h)

**Objetivo:** escribir Python de calidad profesional y entender cómo se construyen y consumen APIs, la base de todo lo demás.

**Conceptos**
- Python intermedio (tipado con type hints, dataclasses/Pydantic, manejo de errores, async básico)
- Control de versiones (Git: branches, PRs, historia limpia)
- Entornos y dependencias (uv o venv + pip)
- APIs REST (verbos HTTP, status codes, JSON, autenticación con API keys)
- Testing (pytest: unit tests, fixtures, mocking de llamadas externas)

**Tecnologías:** Python 3.12+, Git/GitHub, FastAPI, pytest, Pydantic.

**Criterio de dominio:** construir una API REST con FastAPI que consuma una API pública externa, valide entradas/salidas con Pydantic, tenga suite de tests con pytest (incluyendo mocks de la API externa) y esté en un repo con historia de commits legible.

**Certificación:** ninguna necesaria en esta fase.

---

## Fase 2 — LLMs, prompting y tool use (~60 h)

**Objetivo:** entender qué es un LLM por dentro (a nivel de usuario avanzado) y dominar la interacción programática: la habilidad núcleo del rol.

**Conceptos**
- Cómo funciona un LLM (tokens, ventana de contexto, temperatura, embeddings como representación)
- Prompt engineering estructurado (system prompts como contratos, few-shot, formatos con XML/secciones)
- Tool use / function calling (definir herramientas, ciclo de llamada-resultado)
- Salidas estructuradas (JSON mode, validación con Pydantic)
- Streaming, manejo de errores de API y control de costos (conteo de tokens, presupuestos)
- Comparación entre proveedores (por qué producción usa múltiples modelos)

**Tecnologías:** APIs de Anthropic y OpenAI (las dos: comparar es parte del aprendizaje), Pydantic para validación.

**Criterio de dominio:** construir un asistente CLI que use tool calling con al menos 3 herramientas reales (p. ej. clima, cálculo, búsqueda en archivos), devuelva salidas estructuradas validadas, maneje errores de API con reintentos y registre el costo en tokens de cada sesión.

**Certificación:** ninguna necesaria; los short courses gratuitos de DeepLearning.AI cubren esta fase.

---

## Fase 3 — RAG y bases vectoriales (~70 h)

**Objetivo:** dominar el patrón más desplegado en producción: conectar un LLM a conocimiento privado con retrieval de calidad medible.

**Conceptos**
- Embeddings en profundidad (modelos de embedding, similitud coseno, dimensionalidad)
- Chunking (estrategias por tamaño, semánticas, por estructura del documento; trade-offs)
- Búsqueda híbrida (vectorial + keyword/BM25) y reranking
- Pipeline RAG completo (ingesta → indexación → retrieval → generación con contexto)
- Evaluación de retrieval (precision/recall de contexto, faithfulness, relevancia de respuesta)
- Limitaciones del RAG vectorial puro (cuándo se necesita retrieval estructurado o sobre grafos)

**Tecnologías:** pgvector (PostgreSQL) como vector DB principal, RAGAS para evaluación.

**Criterio de dominio:** construir un RAG sobre un corpus real de 50+ documentos, con búsqueda híbrida y reranking, y reportar métricas RAGAS (faithfulness y answer relevancy) sobre un set de 20+ preguntas, documentando qué decisión de chunking mejoró más los números y por qué.

**Certificación:** ninguna necesaria en esta fase.

---

## Fase 4 — Evals y observabilidad (~50 h)

**Objetivo:** adquirir la disciplina que separa a un AI engineer de un entusiasta: medir sistemáticamente si el sistema funciona y detectar cuándo deja de hacerlo.

**Conceptos**
- Diseño de datasets de evaluación (casos dorados, casos límite, casos adversarios)
- LLM-as-judge (rúbricas programáticas, sus sesgos y cómo calibrarlo)
- Regression testing de prompts (versionar prompts como código, evals por cambio)
- Tracing y observabilidad (trazas de cada llamada, latencia, costo, tasa de error)
- Métricas de producto vs. métricas de modelo

**Tecnologías:** Langfuse (open source) para tracing y gestión de evals; pytest para integrarlos a CI.

**Criterio de dominio:** montar una suite de evals automatizada sobre el RAG de la Fase 3 que corra en CI (GitHub Actions), y demostrar que detecta una regresión inyectada a propósito (p. ej. degradar el prompt del sistema) haciendo fallar el pipeline.

**Certificación:** ninguna necesaria en esta fase.

---

## Fase 5 — Agentes y MCP (~80 h)

**Objetivo:** construir sistemas donde el LLM decide y ejecuta pasos — el segmento de mayor crecimiento del campo — con arquitectura seria, no loops improvisados.

**Conceptos**
- Anatomía de un agente (loop razonamiento-acción, condiciones de parada, presupuestos)
- Grafos de estado (nodos, aristas condicionales, checkpointing, human-in-the-loop)
- Memoria (de corto plazo en contexto, de largo plazo persistida)
- MCP — Model Context Protocol (el estándar 2026 de integración de herramientas: construir servidores y consumirlos)
- Multi-agente (cuándo sí y cuándo es sobre-ingeniería)
- Guardrails y sandboxing de acciones (permisos, confirmación humana para acciones irreversibles)

**Tecnologías:** LangGraph como framework de agentes, MCP (SDK oficial de Python).

**Criterio de dominio:** construir un agente en LangGraph que resuelva una tarea multi-paso real (p. ej. investigar un tema y producir un informe con fuentes), consumiendo al menos un servidor MCP construido por ti, con checkpointing, un punto de aprobación humana, trazas en Langfuse y evals de la Fase 4 aplicados a su salida.

**Certificación:** ninguna necesaria; LangChain Academy (gratuita) cubre LangGraph.

---

## Fase 6 — Deployment y LLMOps (~70 h)

**Objetivo:** llevar el sistema a producción real: contenedores, cloud, CI/CD y operación con costos y seguridad bajo control.

**Conceptos**
- Contenedores (Docker: imágenes, multi-stage builds)
- Despliegue en cloud (un proveedor: cómputo serverless o contenedores gestionados)
- CI/CD (pipeline que corre tests + evals y despliega)
- Seguridad de sistemas LLM (prompt injection, manejo de secretos, límites de tasa)
- Operación (monitoreo de latencia/costo/errores, presupuestos de tokens, caching, fallback entre modelos)

**Tecnologías:** Docker, AWS (ECS/Fargate o Lambda + Bedrock como opción de inferencia gestionada), GitHub Actions.

**Criterio de dominio:** desplegar el agente de la Fase 5 en AWS con CI/CD completo (tests + evals como gate), observabilidad en producción, un mecanismo de defensa contra prompt injection demostrable y un reporte del costo mensual estimado del sistema bajo una carga definida.

**Certificación:** AWS Certified AI Practitioner (ancla económica y filtro ATS) o Azure AI-102 si el stack objetivo es Microsoft. Una de las dos, no ambas.

---

## Fase 7 — Modelos abiertos y fine-tuning selectivo (~60 h)

**Objetivo:** ganar el criterio para decidir cuándo un modelo abierto o un fine-tuning superan al prompting sobre un modelo frontera — y ejecutarlo cuando aplique.

**Conceptos**
- Ecosistema de modelos abiertos (familias, tamaños, licencias, cuándo usarlos)
- Inferencia local y self-hosted (cuantización, trade-offs de latencia/costo/privacidad)
- Fine-tuning eficiente (LoRA/QLoRA: qué es, qué datos requiere, qué problemas resuelve)
- El árbol de decisión prompting → RAG → fine-tuning (y por qué ese orden)
- Evaluación comparativa honesta entre alternativas

**Tecnologías:** Hugging Face (hub + transformers), Ollama para inferencia local, Unsloth o PEFT para LoRA.

**Criterio de dominio:** hacer fine-tuning LoRA de un modelo abierto pequeño para una tarea específica (p. ej. clasificación o extracción con formato propio) y publicar una comparación con evals contra el mejor prompt sobre un modelo frontera: métricas, costo y latencia de ambas rutas, con recomendación justificada.

**Certificación:** ninguna necesaria en esta fase.

---

## Fase 8 — Portafolio y perfil profesional (~40 h)

**Objetivo:** convertir el trabajo de las fases anteriores en evidencia contratable: el activo que, según todo el consenso 2026, pesa más que títulos y badges.

**Conceptos**
- Curaduría de repos (READMEs con arquitectura, decisiones y demo; historia limpia)
- Writeups técnicos (1-2 posts explicando un problema real resuelto y sus métricas)
- Demo pública (el capstone accesible con un link)
- System design de sistemas LLM (practicar el formato de entrevista del rol: diseñar un RAG/agente en pizarra con trade-offs)

**Tecnologías:** GitHub, un blog (el medio es indiferente), el stack ya dominado.

**Criterio de dominio:** capstone desplegado públicamente con link funcional + writeup técnico publicado con métricas reales + repo curado, y un simulacro de entrevista de system design de un sistema LLM resuelto por escrito (problema → arquitectura → trade-offs → evals).

**Certificación:** ninguna necesaria en esta fase.

---

## Certificaciones: orden de prioridad

| Prioridad | Certificación | Fase | Por qué |
|---|---|---|---|
| 1 | AWS Certified AI Practitioner (~USD 100) | 6 | La ancla nueva de AWS para IA: barata, reconocida por filtros ATS y alineada con el stack cloud del roadmap. |
| 1 (alternativa) | Microsoft Azure AI-102 (~USD 165) | 6 | Rediseñada para GenAI (Azure OpenAI, RAG en Azure); elegir esta en lugar de AWS solo si el mercado objetivo es enterprise-Microsoft. |
| 2 | Cursos gratuitos: DeepLearning.AI (short courses de LLMs/RAG) y LangChain Academy | 2-5 | ROI infinito: gratuitos y enseñan exactamente las habilidades de las fases centrales. Valen como aprendizaje, no como credencial. |
| 3 (opcional) | AWS ML Specialty o Google Professional ML Engineer | Post-roadmap | Solo si se apunta a empresas grandes que filtran por ellas; son de ML clásico y exigen 60-150 h extra. |

Regla: máximo 1-2 certificaciones grandes; el resto del tiempo va a proyectos. El consenso investigado es unánime: una certificación + un proyecto desplegado supera a una colección de badges.

## Proyecto transversal (capstone evolutivo)

Un único proyecto que crece fase a fase: **un asistente de conocimiento sobre un dominio real** (elige uno con documentos de verdad: la documentación de una herramienta, normativa de un sector, manuales internos de un negocio).

- **F1:** la API base en FastAPI que servirá el asistente (endpoints, validación, tests).
- **F2:** capa LLM: el asistente responde con tool calling y salidas estructuradas.
- **F3:** RAG: responde con base en el corpus del dominio, con métricas de retrieval.
- **F4:** suite de evals + tracing: cada cambio al asistente pasa por evaluación automática.
- **F5:** se convierte en agente: ejecuta tareas multi-paso del dominio vía un servidor MCP propio.
- **F6:** desplegado en AWS con CI/CD, observabilidad y defensa contra prompt injection.
- **F7:** un componente sensible a costo/latencia se compara (o migra) contra un modelo abierto fine-tuneado.
- **F8:** demo pública + writeup con la arquitectura y las métricas del sistema completo.

El resultado final demuestra exactamente lo que el mercado 2026 contrata: el ciclo completo de un sistema LLM de producción — retrieval, agencia, evaluación, despliegue y criterio de costos — en un solo artefacto verificable.

## Estimación de tiempo según ritmo

| Ritmo semanal | Duración total aprox. |
|---|---|
| 3.5 h (solo sesiones de 30 min/día) | ~33 meses |
| 6 h (sesiones diarias + 1 bloque de práctica) | ~20 meses |
| 10 h | ~12 meses |

Nota: las sesiones de 30 min sirven para teoría; los criterios de dominio exigen bloques de práctica de 1-2 h. A ritmo de solo 30 min/día el roadmap no es viable en la práctica — los criterios no se completan sin bloques largos.

## Fuentes principales

- **roadmap.sh — AI Engineer**: definición del rol como capa de aplicación (usar modelos pre-entrenados, no crearlos). https://roadmap.sh/ai-engineer
- **Dataquest — AI Engineer Roadmap (2026)**: skills esenciales (Python, LLM APIs, RAG, agentes) y timeline realista de 8-12 meses desde cero. https://www.dataquest.io/blog/ai-engineer-roadmap/
- **Technovids — AI Engineer Skills 2026**: secuencia consensuada (Python/APIs → LLM → RAG → agentes → MCP → LLMOps) y proyectos de portafolio de mayor señal. https://technovids.com/ai-engineer-skills
- **LangChain — State of Agent Engineering 2026**: 57% con agentes en producción; calidad como barrera #1; observabilidad (89%) por encima de evals (52%); multi-modelo como norma. https://www.langchain.com/state-of-agent-engineering
- **AI Engineer — 2026 Q1 Report**: MCP como estándar de integración, evals rigurosos sobre "vibes", límites del RAG vectorial puro. https://www.ai.engineer/AIE_2026_Q1_report.pdf
- **FinalRound AI — Software Engineering Job Market 2026**: crecimiento de vacantes AI/ML (163% 2024→2025, +74% 2026), ~3.4 vacantes por candidato calificado, agentic AI +280% YoY. https://www.finalroundai.com/blog/software-engineering-job-market-2026
- **365 Data Science — AI Engineer Job Outlook**: solo ~2.5% de vacantes apuntan a 0-2 años de experiencia; Python en 71% de las vacantes; AWS/Azure dominan. https://365datascience.com/career-advice/career-guides/ai-engineer-job-outlook-2025/
- **CertSelect — Are AI Certifications Worth It (2026)**: los perfiles que se contratan combinan repos end-to-end + writeups + 1 certificación ancla; el portafolio manda. https://certselect.com/us/en/ai/are-ai-certifications-worth-it/
- **Careery — Best GenAI Certifications 2026**: certificaciones gratuitas (DeepLearning.AI, LangChain Academy) como mejor ROI; cloud certs como filtro enterprise. https://careery.pro/blog/ai-careers/best-ai-certifications
- **Firecrawl — Agentic AI Trends 2026**: verificabilidad como mapa de dónde funcionan los agentes; necesidad de datos frescos y guardrails. https://www.firecrawl.dev/blog/agentic-ai-trends

---
topic_id: f2.salidas-estructuradas
aliases: ["f2.salidas-estructuradas"]
fase: 2
tipo: codigo
estado: no_visto
nivel: sin_evaluar
tags: [fase/2, estado/no_visto]
---

# Salidas estructuradas

**Prerequisitos:** [[Tool use y function calling|Tool use / function calling]]

**Criterio de dominio:** Extrae datos estructurados de 20 textos libres hacia un modelo Pydantic con tasa de parseo del 100%, incluyendo estrategia de reintento ante salidas inválidas.

## Apuntes

**S37 (2026-09-28)** — Lección escrita y entregada: `ejercicios/fase-2/f2.salidas-estructuradas/leccion.md`, con el `Intake` del capstone (`intake.py`) y tres demos (`demo_parse_failures.py` offline, `demo_structured_parse.py` contra la API, `demo_manual_retry.py` offline con `FakeClient`). Ejes: dos capas de "válido" (sintaxis vs contrato), la escalera prompt → JSON mode → structured outputs (decodificación restringida) → Pydantic + reintento, qué garantiza y qué no el schema, `messages.parse` vs `create` + `output_config`, y reintento con retroalimentación frente al backoff de transporte. Cerré la sesión sin leerla: queda de tarea leerla y traer las 4 preguntas (la 1 es de predicción, antes de correr la demo 1). El estado sigue `no_visto`: aún no hubo lectura ni discusión.

Dato verificado por el tutor sobre el SDK (anthropic 1.9): `messages.parse` lanza `pydantic.ValidationError` igual si la respuesta rompe una regla, si se trunca por `max_tokens` o si es un `refusal`, así que no deja mirar el `stop_reason`. Para distinguir las causas hace falta el camino manual.

## Errores cometidos

## Relacionados

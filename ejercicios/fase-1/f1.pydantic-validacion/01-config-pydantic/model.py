"""Configuración de un asistente LLM, ahora con Pydantic.

Completa ModelConfig según la especificación del enunciado.
"""

from pydantic import BaseModel, Field, field_validator


class ModelConfig(BaseModel):
    modelo: str
    temperatura: float = Field(ge=0.0, le=1.0, default=0.7 )
    max_tokens: int = Field(gt=0, default=1024)

    @field_validator('modelo',mode='after')
    @classmethod
    def starts_with_claude(cls, value: str):
        if not value.startswith("claude-"):
            raise ValueError(f"el modelo {value} debe de empezar con la expresion 'claude-'")
        return value
    

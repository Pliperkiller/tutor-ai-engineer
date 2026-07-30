"""Config de asistente con modelos anidados.

Escribe aqui los 3 modelos segun la especificacion del enunciado:
Herramienta, ModelConfig (copiala del ejercicio 01) y AsistenteConfig.
"""

from pydantic import BaseModel, Field, field_validator, model_validator


class Herramienta(BaseModel):
    nombre: str
    descripcion: str = Field(min_length=10)
    timeout_s: float = Field(gt=0.0, le=120.0 ,default=30.0)

    @field_validator('nombre', mode='after')
    @classmethod
    def upercase_no_space_validator(cls,value: str):
        if value.lower() != value:
            raise ValueError(f"el nombre {value} debe ser todo en minúsculas")

        if value.replace(" ",'') != value:
            raise ValueError(f"el nombre {value} no debe contener espacios")

        return value



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
    

class AsistenteConfig(BaseModel):
    nombre: str = Field(min_length=3)
    modelo: ModelConfig
    herramientas: list[Herramienta] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_non_repeated_tools(self):

        tool_names = [tool.nombre for tool in self.herramientas]

        count_dict = {}

        for name in tool_names:
            count_dict[name] = tool_names.count(name)

        for name, counts in count_dict.items():
            if counts > 1:
                raise ValueError(f"el nombre {name} se encuentra {counts} veces en la lista, no puede haber herramientas con nombres duplicados")

        
        return self

    @model_validator(mode='after')
    def validate_name_agent(self):
        if self.nombre.startswith("agente-") and len(self.herramientas) == 0:
            raise ValueError("los asistentes tipo agente deben de tener herramientas asignadas")

        return self

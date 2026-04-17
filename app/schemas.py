from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProjetoBase(BaseModel):
    titulo: str
    descricao: str
    tech: str
    emoji: Optional[str] = "📁"

class ProjetoCreate(ProjetoBase):
    pass

class Projeto(ProjetoBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True
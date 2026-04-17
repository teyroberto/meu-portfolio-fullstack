from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descricao = Column(String)
    status = Column(String, default="pendente")  # "pendente", "fazendo", "concluido"
    prioridade = Column(String) # "baixa", "media", "alta"
    
class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True, nullable=False)
    descricao = Column(Text, nullable=False)
    tech = Column(String, nullable=False)
    emoji = Column(String, default="📁")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class LinkEncurtado(Base):
    __tablename__ = "links_encurtados"
    id = Column(Integer, primary_key=True, index=True)
    url_original = Column(String)
    codigo = Column(String, unique=True, index=True)

class Transacao(Base):
    __tablename__ = "transacoes"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String)
    valor = Column(Float) # Usamos Float para dinheiro
    tipo = Column(String) # "entrada" ou "saida"
    categoria = Column(String) # "Salário", "Lazer", "Comida", etc.
    data = Column(String) # Vamos salvar a data como string por enquanto
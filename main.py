import string
import random
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel

# Importações do seu sistema de pastas
from app import models, schemas
from app.database import engine, get_db, Base  # Importamos a Base correta daqui

# Cria as tabelas no banco (incluindo Projetos e agora Links)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Full-Stack - Roberto", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # Adicione o link da Vercel aqui!
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://meu-portfolio-fullstack.vercel.app" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Garante que a tabela de links seja criada
models.Base.metadata.create_all(bind=engine)

# --- SCHEMAS ---
class TarefaCreate(BaseModel):
    titulo: str
    descricao: str
    prioridade: str

class TarefaUpdate(BaseModel):
    status: str

class LinkSchema(BaseModel):
    url_original: str

class TransacaoCreate(BaseModel):
    descricao: str
    valor: float
    tipo: str
    categoria: str
    data: str

# --- FUNÇÕES AUXILIARES ---
def gerar_codigo_aleatorio(tamanho=5):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

# --- ROTAS DO ENCURTADOR ---

@app.post("/encurtar")
def encurtar_url(link: LinkSchema, db: Session = Depends(get_db)):
    codigo = gerar_codigo_aleatorio()
    
    # Mude para models.LinkEncurtado
    novo_link = models.LinkEncurtado(url_original=link.url_original, codigo=codigo) 
    db.add(novo_link)
    db.commit()
    db.refresh(novo_link)
    
    return {"link_curto": f"https://meu-portfolio-fullstack.onrender.com/r/{codigo}"}

@app.get("/r/{codigo}")
def redirecionar(codigo: str, db: Session = Depends(get_db)):
    # Mude para models.LinkEncurtado aqui também
    link_db = db.query(models.LinkEncurtado).filter(models.LinkEncurtado.codigo == codigo).first()
    
    if not link_db:
        raise HTTPException(status_code=404, detail="Link não encontrado")
    
    return RedirectResponse(url=link_db.url_original)
# --- ROTAS DE PROJETOS (CRUD) ---

@app.get("/")
def root():
    return {"mensagem": "API Online!", "status": "online"}

@app.get("/projetos", response_model=List[schemas.Projeto])
def listar_projetos(db: Session = Depends(get_db)):
    return db.query(models.Projeto).all()

@app.post("/projetos", response_model=schemas.Projeto)
def criar_projeto(projeto: schemas.ProjetoCreate, db: Session = Depends(get_db)):
    db_projeto = models.Projeto(**projeto.dict())
    db.add(db_projeto)
    db.commit()
    db.refresh(db_projeto)
    return db_projeto

@app.put("/projetos/{projeto_id}", response_model=schemas.Projeto)
def atualizar_projeto(projeto_id: int, projeto: schemas.ProjetoCreate, db: Session = Depends(get_db)):
    db_projeto = db.query(models.Projeto).filter(models.Projeto.id == projeto_id).first()
    if not db_projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    for key, value in projeto.dict().items():
        setattr(db_projeto, key, value)
    
    db.commit()
    db.refresh(db_projeto)
    return db_projeto

@app.delete("/projetos/{projeto_id}")
def deletar_projeto(projeto_id: int, db: Session = Depends(get_db)):
    db_projeto = db.query(models.Projeto).filter(models.Projeto.id == projeto_id).first()
    if not db_projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db.delete(db_projeto)
    db.commit()
    return {"mensagem": "Projeto deletado com sucesso"}

# ROTA 1: Salvar nova transação
@app.post("/transacoes")
def criar_transacao(t: TransacaoCreate, db: Session = Depends(get_db)):
    nova_t = models.Transacao(**t.dict())
    db.add(nova_t)
    db.commit()
    db.refresh(nova_t)
    return nova_t

# ROTA 2: Buscar saldo e resumo (O cérebro da planilha)
@app.get("/transacoes/resumo")
def resumo_financeiro(db: Session = Depends(get_db)):
    todas = db.query(models.Transacao).all()
    entradas = sum(t.valor for t in todas if t.tipo == "entrada")
    saidas = sum(t.valor for t in todas if t.tipo == "saida")
    saldo = entradas - saidas
    
    return {
        "saldo": saldo,
        "entradas": entradas,
        "saidas": saidas,
        "total_items": len(todas)
    }

@app.delete("/transacoes/reset")
def resetar_transacoes(db: Session = Depends(get_db)):
    db.query(models.Transacao).delete()
    db.commit()
    return {"mensagem": "Histórico limpo com sucesso"}

# Certifique-se de que você tem a rota para listar as transações individuais
@app.get("/transacoes")
def listar_transacoes(db: Session = Depends(get_db)):
    return db.query(models.Transacao).order_by(models.Transacao.id.desc()).all()

@app.post("/tarefas")
def criar_tarefa(t: TarefaCreate, db: Session = Depends(get_db)):
    nova_t = models.Tarefa(**t.dict(), status="pendente")
    db.add(nova_t)
    db.commit()
    db.refresh(nova_t)
    return nova_t

# ROTA 2: Listar todas
@app.get("/tarefas")
def listar_tarefas(db: Session = Depends(get_db)):
    return db.query(models.Tarefa).all()

# ROTA 3: Mudar Status (O pulo do gato para o Trello)
@app.patch("/tarefas/{tarefa_id}")
def mudar_status(tarefa_id: int, t: TarefaUpdate, db: Session = Depends(get_db)):
    db_tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    db_tarefa.status = t.status
    db.commit()
    return db_tarefa

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    # Note as aspas em "main:app"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
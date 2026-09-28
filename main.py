from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.rotas import router

# "app" é o nome que o FastAPI, o uvicorn e os tutoriais esperam por convenção.
app = FastAPI(
    title="Zerando Manaus",
    description="API do jogo Zerando Manaus: fases, jogadores e respostas.",
    version="0.1.0",
)

# CORS: sem isto o navegador bloqueia o front (outra porta/origem) de chamar a API.
# "*" libera qualquer site — ok em desenvolvimento; em produção troque pelo
# endereço real do front, ex.: ["https://zerandomanaus.com.br"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Status"])
def status_api():
    return {"status": "ok", "docs": "/docs"}

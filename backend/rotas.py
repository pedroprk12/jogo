"""Endpoints da API (parte da pessoa 1).

Esta camada só recebe a requisição, valida, chama o repositório (dados) e a
gamificação (regras) e monta a resposta. Não tem regra de negócio nem acesso
direto a arquivo — assim cada pessoa mexe no seu arquivo sem conflito.
"""

import threading
import uuid

from fastapi import APIRouter, HTTPException, status

from backend import gameficacao, repositorio
from backend.schemas import (
    FaseDetalhe,
    FaseResumo,
    Jogador,
    JogadorCriar,
    RespostaEnviar,
    RespostaResultado,
)

router = APIRouter()

# O FastAPI roda endpoints `def` (não async) em várias threads ao mesmo tempo.
# Sem esta trava, duas respostas simultâneas do mesmo jogador poderiam ler o
# JSON antigo e uma sobrescreveria o XP da outra. (Só vale para 1 processo;
# com banco de dados de verdade isso deixa de ser necessário.)
_trava_escrita = threading.Lock()


def _obter_fase(fase_id: int) -> dict:
    fase = repositorio.buscar_fase(fase_id)
    if fase is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fase não encontrada")
    return fase


def _obter_jogador(jogador_id: str) -> dict:
    jogador = repositorio.buscar_jogador(jogador_id)
    if jogador is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Jogador não encontrado")
    return jogador


def _montar_jogador(jogador_id: str, dados: dict) -> Jogador:
    """Converte o registro salvo no formato que a API devolve.

    Nível e status não são gravados: são calculados a partir do XP e das
    fases, para nunca ficarem inconsistentes com eles.
    """
    return Jogador(
        id=jogador_id,
        nome=dados["nome"],
        xp=dados["xp"],
        nivel=gameficacao.calcular_nivel(dados["xp"]),
        status=gameficacao.calcular_status(len(dados["fases_concluidas"])),
        fases_concluidas=sorted(dados["fases_concluidas"]),
    )


# ---------- Fases ----------

@router.get("/fases", response_model=list[FaseResumo], tags=["Fases"])
def listar_fases():
    fases = repositorio.listar_fases()
    return [
        FaseResumo(id=int(fase_id), nome=fase["nome"], categoria=fase["categoria"])
        for fase_id, fase in sorted(fases.items(), key=lambda item: int(item[0]))
    ]


@router.get("/fases/{fase_id}", response_model=FaseDetalhe, tags=["Fases"])
def detalhar_fase(fase_id: int):
    # O response_model FaseDetalhe usa PerguntaPublica, então o campo
    # "correta" de cada pergunta é descartado antes de sair da API.
    return {"id": fase_id, **_obter_fase(fase_id)}


# ---------- Jogadores ----------

@router.post(
    "/jogadores",
    response_model=Jogador,
    status_code=status.HTTP_201_CREATED,
    tags=["Jogadores"],
)
def criar_jogador(dados: JogadorCriar):
    # uuid4 gera um id aleatório impossível de adivinhar, ao contrário de 1, 2, 3...
    jogador_id = uuid.uuid4().hex
    novo = {"nome": dados.nome, "xp": 0, "acertos": [], "fases_concluidas": []}
    with _trava_escrita:
        repositorio.salvar_jogador(jogador_id, novo)
    return _montar_jogador(jogador_id, novo)


@router.get("/jogadores/{jogador_id}", response_model=Jogador, tags=["Jogadores"])
def obter_jogador(jogador_id: str):
    return _montar_jogador(jogador_id, _obter_jogador(jogador_id))


@router.post(
    "/jogadores/{jogador_id}/fases/{fase_id}/respostas",
    response_model=RespostaResultado,
    tags=["Jogadores"],
)
def responder(jogador_id: str, fase_id: int, resposta: RespostaEnviar):
    fase = _obter_fase(fase_id)
    perguntas = fase["perguntas"]

    if resposta.pergunta >= len(perguntas):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pergunta não encontrada")
    pergunta = perguntas[resposta.pergunta]
    if resposta.alternativa >= len(pergunta["alternativas"]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Alternativa inválida")

    # A correção acontece aqui no servidor: o navegador nunca decide se acertou.
    acertou = resposta.alternativa == pergunta["correta"]

    # Ler, alterar e gravar precisa ser atômico (ver comentário da trava).
    with _trava_escrita:
        jogador = _obter_jogador(jogador_id)
        xp_ganho = gameficacao.registrar_resposta(
            jogador, fase_id, resposta.pergunta, acertou, len(perguntas)
        )
        repositorio.salvar_jogador(jogador_id, jogador)

    return RespostaResultado(
        acertou=acertou,
        xp_ganho=xp_ganho,
        xp_total=jogador["xp"],
        nivel=gameficacao.calcular_nivel(jogador["xp"]),
        fase_concluida=fase_id in jogador["fases_concluidas"],
    )

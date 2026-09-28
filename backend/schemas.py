"""Modelos Pydantic que definem o contrato da API (entrada e saída de cada endpoint).

Tudo o que o front-end envia ou recebe passa por estes modelos, então eles
servem como documentação viva: o /docs do FastAPI é gerado a partir daqui.
"""

from pydantic import BaseModel, Field


# ---------- Fases ----------

class FaseResumo(BaseModel):
    """Dados mínimos de uma fase, usados para desenhar o mapa."""

    id: int
    nome: str
    categoria: str


class PerguntaPublica(BaseModel):
    """Pergunta como o jogador a vê.

    Não tem o campo `correta` de propósito: se o gabarito fosse enviado ao
    navegador, qualquer um veria a resposta pelo DevTools (F12).
    """

    enunciado: str
    alternativas: list[str]


class FaseDetalhe(FaseResumo):
    descricao: str
    desafio: str
    perguntas: list[PerguntaPublica]


# ---------- Jogadores ----------

class JogadorCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=40, examples=["Explorador Manauara"])


class Jogador(BaseModel):
    id: str
    nome: str
    xp: int
    nivel: int
    status: str
    fases_concluidas: list[int]


# ---------- Respostas ----------

class RespostaEnviar(BaseModel):
    """Resposta a uma pergunta. Os índices começam em 0."""

    pergunta: int = Field(ge=0, examples=[0])
    alternativa: int = Field(ge=0, examples=[1])


class RespostaResultado(BaseModel):
    acertou: bool
    xp_ganho: int
    xp_total: int
    nivel: int
    fase_concluida: bool

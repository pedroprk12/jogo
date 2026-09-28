import json

import pytest
from fastapi.testclient import TestClient

from backend import repositorio
from main import app

# Fases "de mentira", só para o teste: assim ele não depende do conteúdo
# real do fases.json, que a pessoa 2 ainda vai mudar.
FASES_TESTE = {
    "1": {
        "nome": "Teatro Amazonas",
        "categoria": "História",
        "descricao": "Descrição",
        "desafio": "Desafio",
        "perguntas": [
            {"enunciado": "P1", "alternativas": ["a", "b"], "correta": 1},
            {"enunciado": "P2", "alternativas": ["a", "b", "c"], "correta": 0},
        ],
    },
    "2": {
        "nome": "Mercado",
        "categoria": "Gastronomia",
        "descricao": "Descrição",
        "desafio": "Desafio",
        "perguntas": [{"enunciado": "P1", "alternativas": ["a", "b"], "correta": 0}],
    },
}


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    """Cliente HTTP apontando para JSONs temporários.

    O monkeypatch troca os caminhos do repositório só durante o teste: os
    arquivos reais em backend/ nunca são tocados, e cada teste começa limpo.
    """
    caminho_fases = tmp_path / "fases.json"
    caminho_fases.write_text(json.dumps(FASES_TESTE), encoding="utf-8")
    monkeypatch.setattr(repositorio, "CAMINHO_FASES", caminho_fases)
    monkeypatch.setattr(repositorio, "CAMINHO_JOGADORES", tmp_path / "jogadores.json")
    return TestClient(app)


@pytest.fixture
def jogador_id(cliente):
    return cliente.post("/jogadores", json={"nome": "Vini"}).json()["id"]


def responder(cliente, jogador_id, fase, pergunta, alternativa):
    return cliente.post(
        f"/jogadores/{jogador_id}/fases/{fase}/respostas",
        json={"pergunta": pergunta, "alternativa": alternativa},
    )


# ---------- Fases ----------

def test_lista_fases_em_ordem(cliente):
    resposta = cliente.get("/fases")

    assert resposta.status_code == 200
    assert [fase["id"] for fase in resposta.json()] == [1, 2]


def test_detalhe_da_fase_nao_expoe_gabarito(cliente):
    resposta = cliente.get("/fases/1")

    assert resposta.status_code == 200
    for pergunta in resposta.json()["perguntas"]:
        assert "correta" not in pergunta


def test_fase_inexistente_retorna_404(cliente):
    assert cliente.get("/fases/99").status_code == 404


# ---------- Jogadores ----------

def test_cria_jogador_zerado(cliente):
    resposta = cliente.post("/jogadores", json={"nome": "Vini"})

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["nome"] == "Vini"
    assert dados["xp"] == 0
    assert dados["nivel"] == 1
    assert dados["status"] == "Iniciante"


def test_nome_vazio_e_rejeitado(cliente):
    # 422 = o Pydantic barrou o dado antes de chegar no nosso código
    assert cliente.post("/jogadores", json={"nome": ""}).status_code == 422


def test_jogador_inexistente_retorna_404(cliente):
    assert cliente.get("/jogadores/nao-existe").status_code == 404


# ---------- Respostas ----------

def test_acerto_da_xp(cliente, jogador_id):
    resultado = responder(cliente, jogador_id, fase=1, pergunta=0, alternativa=1).json()

    assert resultado["acertou"] is True
    assert resultado["xp_ganho"] == 10
    assert resultado["xp_total"] == 10


def test_erro_nao_da_xp(cliente, jogador_id):
    resultado = responder(cliente, jogador_id, fase=1, pergunta=0, alternativa=0).json()

    assert resultado["acertou"] is False
    assert resultado["xp_ganho"] == 0


def test_repetir_acerto_nao_da_xp_de_novo(cliente, jogador_id):
    responder(cliente, jogador_id, fase=1, pergunta=0, alternativa=1)
    resultado = responder(cliente, jogador_id, fase=1, pergunta=0, alternativa=1).json()

    assert resultado["xp_ganho"] == 0
    assert resultado["xp_total"] == 10


def test_fase_so_conclui_com_todas_as_perguntas_certas(cliente, jogador_id):
    primeira = responder(cliente, jogador_id, fase=1, pergunta=0, alternativa=1).json()
    segunda = responder(cliente, jogador_id, fase=1, pergunta=1, alternativa=0).json()

    assert primeira["fase_concluida"] is False
    assert segunda["fase_concluida"] is True
    perfil = cliente.get(f"/jogadores/{jogador_id}").json()
    assert perfil["fases_concluidas"] == [1]
    assert perfil["status"] == "Turista Atento"


def test_progresso_fica_salvo(cliente, jogador_id):
    responder(cliente, jogador_id, fase=2, pergunta=0, alternativa=0)

    # Um GET novo lê do arquivo: prova que o XP foi persistido no JSON
    assert cliente.get(f"/jogadores/{jogador_id}").json()["xp"] == 10


@pytest.mark.parametrize(
    ("fase", "pergunta", "alternativa", "status_esperado"),
    [
        (99, 0, 0, 404),  # fase não existe
        (1, 5, 0, 404),   # pergunta não existe
        (1, 0, 9, 400),   # alternativa fora da lista
        (1, -1, 0, 422),  # índice negativo barrado pelo Pydantic (ge=0)
    ],
)
def test_respostas_invalidas(cliente, jogador_id, fase, pergunta, alternativa, status_esperado):
    resposta = responder(cliente, jogador_id, fase, pergunta, alternativa)

    assert resposta.status_code == status_esperado

"""Leitura e gravação dos dados em JSON.

PROVISÓRIO — esta parte é da pessoa 2. Aqui vai só o mínimo para a API
funcionar e ser testada. Ela pode reescrever o que quiser, desde que mantenha
os nomes e retornos das funções abaixo, que são o que a API usa.
"""

import json
from pathlib import Path

PASTA = Path(__file__).parent
CAMINHO_FASES = PASTA / "fases.json"
CAMINHO_JOGADORES = PASTA / "jogadores.json"


def _ler(caminho: Path) -> dict:
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _gravar(caminho: Path, dados: dict) -> None:
    with caminho.open("w", encoding="utf-8") as arquivo:
        # ensure_ascii=False grava acentos legíveis ("Águas"), sem virar códigos de escape Unicode
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def listar_fases() -> dict[str, dict]:
    """Todas as fases, indexadas pelo id em texto ("1", "2"...), como no JSON."""
    return _ler(CAMINHO_FASES)


def buscar_fase(fase_id: int) -> dict | None:
    return listar_fases().get(str(fase_id))


def buscar_jogador(jogador_id: str) -> dict | None:
    return _ler(CAMINHO_JOGADORES).get(jogador_id)


def salvar_jogador(jogador_id: str, dados: dict) -> None:
    jogadores = _ler(CAMINHO_JOGADORES)
    jogadores[jogador_id] = dados
    _gravar(CAMINHO_JOGADORES, jogadores)

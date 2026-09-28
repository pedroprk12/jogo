"""Regras de gamificação: XP, nível e status do jogador.

PROVISÓRIO — esta parte é da pessoa 3. Aqui vai só o mínimo para a API
funcionar. Ela pode mudar os valores e as regras à vontade, desde que mantenha
as assinaturas das funções abaixo, que são o que a API chama.

São funções puras (não leem arquivo nem rede): recebem dados e devolvem
dados. Isso as deixa fáceis de testar e de trocar sem mexer na API.
"""

XP_POR_ACERTO = 10
XP_POR_NIVEL = 100


def calcular_nivel(xp: int) -> int:
    return xp // XP_POR_NIVEL + 1


def calcular_status(fases_concluidas: int) -> str:
    if fases_concluidas == 0:
        return "Iniciante"
    if fases_concluidas < 3:
        return "Turista Atento"
    if fases_concluidas < 6:
        return "Guia Local"
    return "Mestre Manauara 🏆"


def registrar_resposta(
    jogador: dict, fase_id: int, pergunta: int, acertou: bool, total_perguntas: int
) -> int:
    """Atualiza o jogador (altera o dict recebido) e devolve o XP ganho.

    Só dá XP no primeiro acerto de cada pergunta — é isso que impede
    "farmar" XP repetindo a mesma fase, bug que existia no script.js.
    """
    if not acertou:
        return 0

    chave = f"{fase_id}:{pergunta}"
    if chave in jogador["acertos"]:
        return 0

    jogador["acertos"].append(chave)
    jogador["xp"] += XP_POR_ACERTO

    acertos_na_fase = sum(1 for c in jogador["acertos"] if c.startswith(f"{fase_id}:"))
    if acertos_na_fase == total_perguntas and fase_id not in jogador["fases_concluidas"]:
        jogador["fases_concluidas"].append(fase_id)

    return XP_POR_ACERTO

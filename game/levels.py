"""Definição declarativa das fases (labirintos, spawns, chegadas e canhões)."""
from dataclasses import dataclass
from game.entities import CannonSpec
from game.config import VELOCIDADE_JOGADOR_PADRAO


@dataclass(frozen=True)
class LevelConfig:
    """Configuração completa de uma fase do jogo."""

    numero: int
    nome: str
    arquivo_mapa: str
    escala_mapa: tuple[int, int]
    posicao_mapa: tuple[int, int]
    arquivo_splash: str
    duracao_splash: float
    arquivo_musica: str
    spawn_jogador: tuple[int, int]
    waypoints_chegada: list[tuple[int, int]]
    tamanho_entidade: int
    tamanho_colisao_parede: int
    velocidade_jogador: int
    canhoes: list[CannonSpec]
    tocar_tiro_inicial: bool = True


LEVELS: list[LevelConfig] = [
    # Nível 1 — Brabo Kids
    LevelConfig(
        numero=1,
        nome="Brabo Kids",
        arquivo_mapa="mapa.png",
        escala_mapa=(510, 510),
        posicao_mapa=(-5, -5),
        arquivo_splash="nivel1.png",
        duracao_splash=4.5,
        arquivo_musica="Map1Song.mp3",
        spawn_jogador=(25, 25),
        waypoints_chegada=[(438, 27)],
        tamanho_entidade=14,
        tamanho_colisao_parede=13,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        canhoes=[
            CannonSpec(x=475, y=100, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3)),
            CannonSpec(x=475, y=225, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3)),
            CannonSpec(x=475, y=350, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3)),
        ],
        tocar_tiro_inicial=True,
    ),
    # Nível 2 — Brabo Mestre
    LevelConfig(
        numero=2,
        nome="Brabo Mestre",
        arquivo_mapa="mapa2.png",
        escala_mapa=(520, 460),
        posicao_mapa=(-38, 16),
        arquivo_splash="nivel2.png",
        duracao_splash=6.0,
        arquivo_musica="Map2Song.mp3",
        spawn_jogador=(25, 60),
        waypoints_chegada=[(25, 29)],
        tamanho_entidade=14,
        tamanho_colisao_parede=13,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        canhoes=[
            CannonSpec(x=100, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(1, 3)),
            CannonSpec(x=225, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(1, 3)),
            CannonSpec(x=350, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(1, 3)),
            CannonSpec(
                x=475,
                y=25,
                direcao="left",
                offset_bala=(0, 8),
                intervalo_recarga=(3, 4),
                recarga_inicial=(3, 3),
            ),
        ],
        tocar_tiro_inicial=False,
    ),
    # Nível 3 — Brabo Tinhoso
    LevelConfig(
        numero=3,
        nome="Brabo Tinhoso",
        arquivo_mapa="mapa3.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel3.png",
        duracao_splash=6.0,
        arquivo_musica="Map3Song.mp3",
        spawn_jogador=(462, 25),
        # No Nível 3, tocar em (462, 462) muda a chegada para (25, 25) e atualiza o checkpoint!
        waypoints_chegada=[(462, 462), (25, 25)],
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        canhoes=[
            CannonSpec(
                x=475, y=100, direcao="left", offset_bala=(0, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=475, y=225, direcao="left", offset_bala=(0, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=475, y=350, direcao="left", offset_bala=(0, 0),
                intervalo_recarga=(1, 3), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=2, y=162, direcao="right", offset_bala=(8, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(3, 3),
            ),
            CannonSpec(
                x=2, y=280, direcao="right", offset_bala=(8, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=225, y=475, direcao="up", offset_bala=(8, 0),
                intervalo_recarga=(1, 3), recarga_inicial=(1, 2),
            ),
        ],
        tocar_tiro_inicial=True,
    ),
    # Nível 4 — Brabo Deus (Fogo cruzado nas 4 direções + Ida e Volta)
    LevelConfig(
        numero=4,
        nome="Brabo Deus",
        arquivo_mapa="mapa4.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel4.png",
        duracao_splash=6.0,
        arquivo_musica="Map4Song.mp3",
        spawn_jogador=(25, 462),
        # Ida até o canto superior direito (checkpoint) e volta ao canto inferior esquerdo!
        waypoints_chegada=[(462, 25), (25, 462)],
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        canhoes=[
            # Topo atirando para baixo (novidade do Nível 4!)
            CannonSpec(
                x=140, y=2, direcao="down", offset_bala=(8, 8),
                intervalo_recarga=(2, 4), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=320, y=2, direcao="down", offset_bala=(8, 8),
                intervalo_recarga=(2, 4), recarga_inicial=(2, 3),
            ),
            # Base atirando para cima
            CannonSpec(
                x=230, y=475, direcao="up", offset_bala=(8, 0),
                intervalo_recarga=(2, 3), recarga_inicial=(1, 2),
            ),
            # Direita atirando para a esquerda
            CannonSpec(
                x=475, y=115, direcao="left", offset_bala=(0, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=475, y=345, direcao="left", offset_bala=(0, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(2, 3),
            ),
            # Esquerda atirando para a direita
            CannonSpec(
                x=2, y=195, direcao="right", offset_bala=(8, 8),
                intervalo_recarga=(2, 3), recarga_inicial=(2, 3),
            ),
            CannonSpec(
                x=2, y=395, direcao="right", offset_bala=(8, 8),
                intervalo_recarga=(2, 4), recarga_inicial=(1, 3),
            ),
        ],
        tocar_tiro_inicial=True,
    ),
]

"""Definição declarativa das fases (cenários, ambientações, spawns 1-3P, puzzles e canhões)."""
from dataclasses import dataclass
from game.config import VELOCIDADE_JOGADOR_PADRAO
from game.entities import CannonSpec
from game.puzzles import PuzzleLayoutSpec


@dataclass(frozen=True)
class LevelConfig:
    """Configuração completa de uma fase do jogo."""

    numero: int
    nome: str
    bioma: str
    arquivo_ambiente: str
    arquivo_mapa: str
    escala_mapa: tuple[int, int]
    posicao_mapa: tuple[int, int]
    arquivo_splash: str
    duracao_splash: float
    arquivo_musica: str
    spawn_jogador: tuple[int, int]
    spawns_multi: list[tuple[int, int]]
    waypoints_chegada: list[tuple[int, int]]
    tamanho_entidade: int
    tamanho_colisao_parede: int
    velocidade_jogador: int
    puzzle: PuzzleLayoutSpec
    canhoes: list[CannonSpec]
    tocar_tiro_inicial: bool = True


LEVELS: list[LevelConfig] = [
    # Nível 1 — Brabo Kids | Cenário: Ruínas da Floresta Ancestral
    LevelConfig(
        numero=1,
        nome="Brabo Kids",
        bioma="floresta",
        arquivo_ambiente="amb_floresta.mp3",
        arquivo_mapa="mapa.png",
        escala_mapa=(510, 510),
        posicao_mapa=(-5, -5),
        arquivo_splash="nivel1.png",
        duracao_splash=4.5,
        arquivo_musica="Map1Song.mp3",
        spawn_jogador=(25, 25),
        spawns_multi=[(25, 25), (37, 25), (31, 31)],
        waypoints_chegada=[(438, 27)],
        tamanho_entidade=14,
        tamanho_colisao_parede=13,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="H",
            portao_rect=(157, 355, 20, 8),
            placa_principal=(211, 125),
            placa_extra_3p=(25, 159),
            alavanca_pos=(181, 353),
            totem_sabotagem_pos=(261, 25),
            cristais_pos=[(109, 241), (277, 57), (25, 461)],
        ),
        canhoes=[
            CannonSpec(x=475, y=100, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3)),
            CannonSpec(x=475, y=225, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3)),
            CannonSpec(x=475, y=350, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3)),
        ],
        tocar_tiro_inicial=True,
    ),
    # Nível 2 — Brabo Mestre | Cenário: Catacumbas Submersas
    LevelConfig(
        numero=2,
        nome="Brabo Mestre",
        bioma="abissal",
        arquivo_ambiente="amb_abissal.mp3",
        arquivo_mapa="mapa2.png",
        escala_mapa=(520, 460),
        posicao_mapa=(-38, 16),
        arquivo_splash="nivel2.png",
        duracao_splash=5.0,
        arquivo_musica="Map2Song.mp3",
        spawn_jogador=(25, 60),
        spawns_multi=[(25, 60), (37, 60), (31, 54)],
        waypoints_chegada=[(25, 29)],
        tamanho_entidade=14,
        tamanho_colisao_parede=13,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="V",
            portao_rect=(145, 422, 8, 20),
            placa_principal=(25, 216),
            placa_extra_3p=(105, 76),
            alavanca_pos=(135, 446),
            totem_sabotagem_pos=(161, 436),
            cristais_pos=[(209, 200), (391, 260), (73, 26)],
        ),
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
    # Nível 3 — Brabo Tinhoso | Cenário: Fortaleza Vulcânica
    LevelConfig(
        numero=3,
        nome="Brabo Tinhoso",
        bioma="vulcao",
        arquivo_ambiente="amb_vulcao.mp3",
        arquivo_mapa="mapa3.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel3.png",
        duracao_splash=5.0,
        arquivo_musica="Map3Song.mp3",
        spawn_jogador=(462, 25),
        spawns_multi=[(462, 25), (450, 25), (462, 37)],
        waypoints_chegada=[(462, 462), (25, 25)],
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="H",
            portao_rect=(238, 297, 20, 8),
            placa_principal=(448, 285),
            placa_extra_3p=(390, 25),
            alavanca_pos=(242, 309),
            totem_sabotagem_pos=(180, 25),
            cristais_pos=[(240, 103), (220, 243), (26, 461)],
        ),
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
    # Nível 4 — Brabo Deus | Cenário: Cidadela Celestial
    LevelConfig(
        numero=4,
        nome="Brabo Deus",
        bioma="divino",
        arquivo_ambiente="amb_divino.mp3",
        arquivo_mapa="mapa4.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel4.png",
        duracao_splash=5.0,
        arquivo_musica="Map4Song.mp3",
        spawn_jogador=(25, 461),
        spawns_multi=[(25, 461), (37, 461), (25, 449)],
        waypoints_chegada=[(461, 25), (25, 461)],
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="H",
            portao_rect=(261, 282, 26, 8),
            placa_principal=(25, 100),
            placa_extra_3p=(59, 424),
            alavanca_pos=(281, 266),
            totem_sabotagem_pos=(281, 290),
            cristais_pos=[(305, 442), (285, 26), (325, 284)],
        ),
        canhoes=[
            CannonSpec(
                x=140, y=2, direcao="down", offset_bala=(8, 8),
                intervalo_recarga=(2, 4), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=320, y=2, direcao="down", offset_bala=(8, 8),
                intervalo_recarga=(2, 4), recarga_inicial=(2, 3),
            ),
            CannonSpec(
                x=230, y=475, direcao="up", offset_bala=(8, 0),
                intervalo_recarga=(2, 3), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=475, y=115, direcao="left", offset_bala=(0, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(1, 2),
            ),
            CannonSpec(
                x=475, y=345, direcao="left", offset_bala=(0, 8),
                intervalo_recarga=(1, 3), recarga_inicial=(2, 3),
            ),
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

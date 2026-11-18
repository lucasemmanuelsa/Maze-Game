"""Definição declarativa das 8 fases (cenários, trilhas 8-bit, spawns 1-3P, puzzles, drones, canhões e Boss)."""
from __future__ import annotations
from dataclasses import dataclass, field
from game.config import VELOCIDADE_JOGADOR_PADRAO
from game.entities import CannonSpec, PatrolDroneSpec
from game.puzzles import PuzzleLayoutSpec


def _cpx(cx: int, cy: int) -> tuple[int, int]:
    """Converte coordenadas de célula (0..22) de mapas 465x465 em coordenadas de pixel livres de colisão."""
    x = 25 if cx == 0 else (461 if cx == 22 else 22 + cx * 20)
    y = 25 if cy == 0 else (461 if cy == 22 else 22 + cy * 20)
    return (x, y)


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
    drones: list[PatrolDroneSpec] = field(default_factory=list)
    tem_boss: bool = False
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
    # Nível 5 — Brabo Glacial | Cenário: Santuário Glacial (Cofres Selados + Portais Gêmeos + Drones)
    LevelConfig(
        numero=5,
        nome="Brabo Glacial",
        bioma="gelido",
        arquivo_ambiente="amb_gelido.mp3",
        arquivo_mapa="mapa5.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel5.png",
        duracao_splash=5.0,
        arquivo_musica="Map5Song.mp3",
        spawn_jogador=_cpx(0, 0),
        spawns_multi=[_cpx(0, 0), (25, 36), (25, 48)],
        waypoints_chegada=[_cpx(22, 22)],
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="H",
            portao_rect=(455, 333, 20, 6),  # Tranca o bolso leste (22,16)->(22,15) onde fica o Portal do Cofre SW!
            placa_principal=_cpx(10, 6),
            placa_extra_3p=_cpx(12, 15),
            alavanca_pos=_cpx(22, 14),
            totem_sabotagem_pos=_cpx(20, 2),  # Dentro do Cofre Selado NE!
            cristais_pos=[_cpx(19, 4), _cpx(2, 20), _cpx(11, 11)],
            portais_gemeos=[
                (_cpx(12, 2), _cpx(18, 1)),   # Labirinto Norte <-> Cofre Selado NE
                (_cpx(20, 12), _cpx(2, 18)),  # Bolso Trancado Leste <-> Cofre Selado SW
            ],
            esteiras_turbo=[_cpx(7, 6), _cpx(15, 15), _cpx(4, 12)],
        ),
        drones=[
            PatrolDroneSpec(ponto_a=_cpx(6, 6), ponto_b=_cpx(15, 6), velocidade=1.65),
            PatrolDroneSpec(ponto_a=_cpx(16, 15), ponto_b=_cpx(7, 15), velocidade=1.75),
        ],
        canhoes=[
            CannonSpec(x=475, y=135, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3), velocidade_bala=10),
            CannonSpec(x=475, y=315, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3), velocidade_bala=10),
            CannonSpec(x=2, y=215, direcao="right", offset_bala=(8, 8), intervalo_recarga=(2, 3), velocidade_bala=10),
            CannonSpec(x=175, y=2, direcao="down", offset_bala=(8, 8), intervalo_recarga=(2, 4), velocidade_bala=10),
            CannonSpec(x=315, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(2, 3), velocidade_bala=10),
        ],
        tocar_tiro_inicial=True,
    ),
    # Nível 6 — Brabo Kaioken | Cenário: Forja Cibernética (Revezamento do Núcleo Instável + Reator Central)
    LevelConfig(
        numero=6,
        nome="Brabo Kaioken",
        bioma="cyber",
        arquivo_ambiente="amb_cyber.mp3",
        arquivo_mapa="mapa6.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel6.png",
        duracao_splash=5.0,
        arquivo_musica="Map6Song.mp3",
        spawn_jogador=_cpx(0, 22),
        spawns_multi=[_cpx(0, 22), (25, 449), (25, 437)],
        waypoints_chegada=[_cpx(22, 0)],
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="V",
            portao_rect=(273, 56, 6, 20),  # Tranca o setor Norte (13,2)->(12,2) onde está o Núcleo Instável!
            placa_principal=_cpx(5, 10),
            placa_extra_3p=_cpx(17, 14),
            alavanca_pos=_cpx(11, 2),
            totem_sabotagem_pos=_cpx(11, 13),  # Entrada sul da Câmara do Reator
            cristais_pos=[_cpx(18, 18), _cpx(4, 4), _cpx(20, 10)],
            portais_gemeos=[
                (_cpx(2, 18), _cpx(20, 4)),
            ],
            esteiras_turbo=[_cpx(5, 6), _cpx(17, 6), _cpx(5, 16), _cpx(17, 16)],
            nucleo_energia=(_cpx(7, 1), _cpx(11, 11)),  # Do Cofre Norte até o Soquete no centro do Reator!
        ),
        drones=[
            PatrolDroneSpec(ponto_a=_cpx(4, 4), ponto_b=_cpx(18, 4), velocidade=1.85),
            PatrolDroneSpec(ponto_a=_cpx(18, 18), ponto_b=_cpx(4, 18), velocidade=1.85),
            PatrolDroneSpec(ponto_a=_cpx(9, 12), ponto_b=_cpx(13, 12), velocidade=1.45),
        ],
        canhoes=[
            CannonSpec(x=98, y=2, direcao="down", offset_bala=(8, 8), intervalo_recarga=(1, 3), velocidade_bala=10),
            CannonSpec(x=378, y=2, direcao="down", offset_bala=(8, 8), intervalo_recarga=(1, 3), velocidade_bala=10),
            CannonSpec(x=238, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(1, 3), velocidade_bala=10),
            CannonSpec(x=475, y=98, direcao="left", offset_bala=(0, 8), intervalo_recarga=(2, 3), velocidade_bala=10),
            CannonSpec(x=475, y=358, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3), velocidade_bala=10),
            CannonSpec(x=2, y=238, direcao="right", offset_bala=(8, 8), intervalo_recarga=(2, 3), velocidade_bala=10),
        ],
        tocar_tiro_inicial=True,
    ),
    # Nível 7 — Brabo Presságio | Cenário: Dimensão do Vazio (Cofre Dimensional + Ida e Volta Frenética)
    LevelConfig(
        numero=7,
        nome="Brabo Presságio",
        bioma="sombrio",
        arquivo_ambiente="amb_sombrio.mp3",
        arquivo_mapa="mapa7.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel7.png",
        duracao_splash=5.0,
        arquivo_musica="Map7Song.mp3",
        spawn_jogador=_cpx(0, 0),
        spawns_multi=[_cpx(0, 0), (25, 36), (25, 48)],
        waypoints_chegada=[_cpx(22, 22), _cpx(0, 0)],
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="V",
            portao_rect=(273, 454, 6, 22),  # Tranca o quadrante SE (12,22)->(13,22)
            placa_principal=_cpx(6, 16),
            placa_extra_3p=_cpx(18, 6),
            alavanca_pos=_cpx(14, 22),
            totem_sabotagem_pos=_cpx(10, 10),  # Dentro do Cofre do Vazio Central!
            cristais_pos=[_cpx(12, 12), _cpx(20, 4), _cpx(3, 21)],
            portais_gemeos=[
                (_cpx(18, 21), _cpx(11, 10)),  # Quadrante SE <-> Cofre Central Selado do Vazio!
                (_cpx(2, 20), _cpx(20, 2)),    # Atalho dimensional cruzado para a fuga!
            ],
            esteiras_turbo=[_cpx(5, 8), _cpx(16, 14), _cpx(11, 16)],
            nucleo_energia=(_cpx(11, 12), _cpx(20, 18)),  # Do Cofre do Vazio até o Reator SE!
        ),
        drones=[
            PatrolDroneSpec(ponto_a=_cpx(2, 8), ponto_b=_cpx(9, 8), velocidade=1.95),
            PatrolDroneSpec(ponto_a=_cpx(20, 14), ponto_b=_cpx(13, 14), velocidade=1.95),
            PatrolDroneSpec(ponto_a=_cpx(8, 16), ponto_b=_cpx(15, 16), velocidade=1.85),
        ],
        canhoes=[
            CannonSpec(x=138, y=2, direcao="down", offset_bala=(8, 8), intervalo_recarga=(1, 3), velocidade_bala=11),
            CannonSpec(x=338, y=2, direcao="down", offset_bala=(8, 8), intervalo_recarga=(1, 3), velocidade_bala=11),
            CannonSpec(x=238, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(1, 3), velocidade_bala=11),
            CannonSpec(x=475, y=158, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 2), velocidade_bala=11),
            CannonSpec(x=475, y=338, direcao="left", offset_bala=(0, 8), intervalo_recarga=(1, 3), velocidade_bala=11),
            CannonSpec(x=2, y=158, direcao="right", offset_bala=(8, 8), intervalo_recarga=(1, 3), velocidade_bala=11),
            CannonSpec(x=2, y=318, direcao="right", offset_bala=(8, 8), intervalo_recarga=(2, 3), velocidade_bala=11),
        ],
        tocar_tiro_inicial=True,
    ),
    # Nível 8 — Brabo Supremo | Cenário: Trono do Caos (BOSS FINAL: Olho Mecânico Primordial!)
    LevelConfig(
        numero=8,
        nome="Brabo Supremo",
        bioma="caos",
        arquivo_ambiente="amb_caos.mp3",
        arquivo_mapa="mapa8.png",
        escala_mapa=(465, 465),
        posicao_mapa=(16, 16),
        arquivo_splash="nivel8.png",
        duracao_splash=5.5,
        arquivo_musica="Map8Song.mp3",
        spawn_jogador=_cpx(0, 11),
        spawns_multi=[_cpx(0, 11), (25, 254), (25, 266)],
        waypoints_chegada=[_cpx(11, 11)],  # No centro da Arena do Boss após quebrar seus 3 Escudos!
        tamanho_entidade=12,
        tamanho_colisao_parede=11,
        velocidade_jogador=VELOCIDADE_JOGADOR_PADRAO,
        tem_boss=True,
        puzzle=PuzzleLayoutSpec(
            orientacao_portao="H",
            portao_rect=(416, 273, 20, 6),  # Tranca o hemisfério Norte (20,13)->(20,12) no início!
            placa_principal=_cpx(11, 16),
            placa_extra_3p=_cpx(4, 20),
            alavanca_pos=_cpx(20, 11),
            totem_sabotagem_pos=_cpx(8, 11),  # Borda Oeste da Arena: congela o Boss para a equipe!
            cristais_pos=[_cpx(1, 21), _cpx(11, 4), _cpx(21, 11)],
            portais_gemeos=[
                (_cpx(2, 20), _cpx(18, 20)),  # Rotação rápida no Sul
                (_cpx(2, 2), _cpx(18, 2)),    # Rotação rápida no Norte (pós-portão)
            ],
            esteiras_turbo=[_cpx(7, 2), _cpx(15, 2), _cpx(7, 20), _cpx(15, 20)],
            pilares_boss=[_cpx(1, 1), _cpx(21, 1), _cpx(21, 21)],  # 3 Pilares de Sobrecarga nos cantos!
        ),
        drones=[
            PatrolDroneSpec(ponto_a=_cpx(4, 2), ponto_b=_cpx(17, 2), velocidade=2.0),
            PatrolDroneSpec(ponto_a=_cpx(17, 20), ponto_b=_cpx(4, 20), velocidade=2.0),
        ],
        canhoes=[
            CannonSpec(x=118, y=2, direcao="down", offset_bala=(8, 8), intervalo_recarga=(2, 3), velocidade_bala=10),
            CannonSpec(x=378, y=2, direcao="down", offset_bala=(8, 8), intervalo_recarga=(2, 3), velocidade_bala=10),
            CannonSpec(x=118, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(2, 3), velocidade_bala=10),
            CannonSpec(x=378, y=475, direcao="up", offset_bala=(8, 0), intervalo_recarga=(2, 3), velocidade_bala=10),
            CannonSpec(x=475, y=138, direcao="left", offset_bala=(0, 8), intervalo_recarga=(2, 4), velocidade_bala=10),
            CannonSpec(x=475, y=358, direcao="left", offset_bala=(0, 8), intervalo_recarga=(2, 4), velocidade_bala=10),
        ],
        tocar_tiro_inicial=True,
    ),
]

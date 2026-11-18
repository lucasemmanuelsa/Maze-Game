"""Configurações globais, constantes visuais, controles multiplayer (movimento + Dash) e diretórios."""
import os
import pygame

# Diretórios e arquivos base (relativos à raiz do repositório)
DIRETORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRETORIO_IMAGENS = os.path.join(DIRETORIO_RAIZ, "imagens")
DIRETORIO_SONS = os.path.join(DIRETORIO_RAIZ, "sons")
CAMINHO_FONTE = os.path.join(DIRETORIO_RAIZ, "Gamer.ttf")
CAMINHO_BANCO = os.path.join(DIRETORIO_RAIZ, "nome_pontuacao.db")

# Janela e FPS
TITULO_JOGO = "Maze and Cannons: Frenesi Cooperativo (8 Fases)"
LARGURA_JANELA = 500
ALTURA_JANELA = 550
FPS = 60

# Paleta de cores (RGB)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERDE_LIMAO = (15, 255, 149)
VERMELHO = (255, 49, 46)
AZUL = (72, 172, 240)
ROSA = (252, 24, 152)
AMARELO = (252, 252, 4)
DOURADO = (255, 205, 56)
CIANO = (56, 236, 255)
LARANJA = (255, 145, 40)
VIOLETA = (188, 92, 255)

# Cores e identidades visuais dos Orbes Guardiões (Jogadores 1, 2 e 3)
CORES_JOGADORES: list[tuple[int, int, int]] = [
    (255, 62, 56),    # P1: Orbe Rubi
    (24, 242, 149),   # P2: Orbe Esmeralda
    (255, 206, 42),   # P3: Orbe Solar
]
CORES_NUCLEO_JOGADORES: list[tuple[int, int, int]] = [
    (255, 195, 180),
    (195, 255, 232),
    (255, 250, 200),
]
NOMES_CURTOS_JOGADORES = ["P1", "P2", "P3"]

# Esquemas de controles locais (1, 2 ou 3 jogadores no mesmo teclado + gamepads)
CONTROLES_SOLO = {
    "left": (pygame.K_LEFT, pygame.K_a),
    "right": (pygame.K_RIGHT, pygame.K_d),
    "up": (pygame.K_UP, pygame.K_w),
    "down": (pygame.K_DOWN, pygame.K_s),
    "dash": (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_e),
}

CONTROLES_MULTI: list[dict[str, tuple[int, ...]]] = [
    # Jogador 1: Setas + Espaço / Shift Direito para Dash
    {
        "left": (pygame.K_LEFT,),
        "right": (pygame.K_RIGHT,),
        "up": (pygame.K_UP,),
        "down": (pygame.K_DOWN,),
        "dash": (pygame.K_SPACE, pygame.K_RSHIFT, pygame.K_RCTRL, pygame.K_SLASH),
    },
    # Jogador 2: W A S D + E / Q / Shift Esquerdo para Dash
    {
        "left": (pygame.K_a,),
        "right": (pygame.K_d,),
        "up": (pygame.K_w,),
        "down": (pygame.K_s,),
        "dash": (pygame.K_e, pygame.K_q, pygame.K_LSHIFT),
    },
    # Jogador 3: I J K L (ou Numpad 8456) + U / O / Numpad 0 para Dash
    {
        "left": (pygame.K_j, pygame.K_KP4),
        "right": (pygame.K_l, pygame.K_KP6),
        "up": (pygame.K_i, pygame.K_KP8),
        "down": (pygame.K_k, pygame.K_KP5),
        "dash": (pygame.K_u, pygame.K_o, pygame.K_KP0),
    },
]

# Cores das posições no Ranking (1º ao 10º)
CORES_RANKING = [
    BRANCO,
    VERMELHO,
    AMARELO,
    AMARELO,
    VERDE_LIMAO,
    AZUL,
    AZUL,
    VERMELHO,
    BRANCO,
    ROSA,
]
LABELS_RANKING = ["1ST", "2ND", "3RD", "4TH", "5TH", "6TH", "7TH", "8TH", "9TH", "10TH"]

# Parâmetros gerais e mecânicas frenéticas
VIDAS_INICIAIS = 5
VELOCIDADE_JOGADOR_PADRAO = 2
VELOCIDADE_BALA_PADRAO = 9
TAMANHO_BALA = 10
ESPESSURA_BARREIRA = 9

TEMPO_CAPSULA_REVIVER = 5.5
TEMPO_CONGELAMENTO_SABOTAGEM = 6.5
DURACAO_DASH = 0.14
RECARGA_DASH = 1.45
PASSOS_POR_FRAME_DASH = 5
DURACAO_TURBO = 2.4
TEMPO_CALOR_NUCLEO_COOP = 10.5
JANELA_PILARES_BOSS_SOLO = 16.0
JANELA_PILARES_BOSS_COOP = 6.5

# Limites da área jogável dentro das barreiras
LIMITE_MIN_X = 25
LIMITE_MAX_X = 462
LIMITE_MIN_Y = 25
LIMITE_MAX_Y = 462

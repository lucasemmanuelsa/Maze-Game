"""Configurações globais, constantes visuais e caminhos de diretórios do jogo."""
import os

# Diretórios e arquivos base (relativos à raiz do repositório)
DIRETORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRETORIO_IMAGENS = os.path.join(DIRETORIO_RAIZ, "imagens")
DIRETORIO_SONS = os.path.join(DIRETORIO_RAIZ, "sons")
CAMINHO_FONTE = os.path.join(DIRETORIO_RAIZ, "Gamer.ttf")
CAMINHO_BANCO = os.path.join(DIRETORIO_RAIZ, "nome_pontuacao.db")

# Janela e FPS
TITULO_JOGO = "Maze and Cannons"
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

# Parâmetros gerais de jogabilidade
VIDAS_INICIAIS = 5
VELOCIDADE_JOGADOR_PADRAO = 2
VELOCIDADE_BALA_PADRAO = 9
TAMANHO_BALA = 10
ESPESSURA_BARREIRA = 9

# Limites da área jogável dentro das barreiras
LIMITE_MIN_X = 25
LIMITE_MAX_X = 462
LIMITE_MIN_Y = 25
LIMITE_MAX_Y = 462

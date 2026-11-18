"""Carregamento e gerenciamento centralizado de imagens, fontes e áudios."""
import os
import pygame

from game.config import CAMINHO_FONTE, DIRETORIO_IMAGENS, DIRETORIO_SONS


class AssetManager:
    """Gerencia o cache de imagens, fontes e efeitos sonoros do jogo."""

    def __init__(self) -> None:
        self._imagens: dict[tuple[str, tuple[int, int] | None], pygame.Surface] = {}
        self._fontes: dict[int, pygame.font.Font] = {}

        # Efeitos sonoros principais
        self.som_tiro = pygame.mixer.Sound(os.path.join(DIRETORIO_SONS, "tiro1.mp3"))
        self.som_tiro.set_volume(0.1)

        self.som_dano = pygame.mixer.Sound(os.path.join(DIRETORIO_SONS, "dano.mp3"))
        self.som_game_over = pygame.mixer.Sound(os.path.join(DIRETORIO_SONS, "somGameOver.mp3"))

        self.som_click = pygame.mixer.Sound(os.path.join(DIRETORIO_SONS, "click.mp3"))
        self.som_click.set_volume(0.1)

        self.som_chegada = pygame.mixer.Sound(os.path.join(DIRETORIO_SONS, "somchegada.mp3"))
        self.som_chegada.set_volume(0.1)

        # Sprites base reutilizados
        self.coracao = self.carregar_imagem("coracao.png", escala=(36, 36))
        self.canhao_base = self.carregar_imagem("canhao.png", escala=(24, 24))
        self.game_over = self.carregar_imagem("Game_Over.png")
        self.icone = self.carregar_imagem("lab.png")

    def carregar_imagem(
        self,
        nome_arquivo: str,
        escala: tuple[int, int] | None = None,
        converter: bool = False,
    ) -> pygame.Surface:
        chave = (nome_arquivo, escala)
        if chave not in self._imagens:
            caminho = os.path.join(DIRETORIO_IMAGENS, nome_arquivo)
            superficie = pygame.image.load(caminho)
            if converter:
                superficie = superficie.convert()
            if escala is not None:
                superficie = pygame.transform.scale(superficie, escala)
            self._imagens[chave] = superficie
        return self._imagens[chave]

    def fonte(self, tamanho: int) -> pygame.font.Font:
        if tamanho not in self._fontes:
            self._fontes[tamanho] = pygame.font.Font(CAMINHO_FONTE, tamanho)
        return self._fontes[tamanho]

    def tocar_musica(self, nome_arquivo: str, volume: float = 0.08, loop: int = -1) -> None:
        pygame.mixer.music.stop()
        caminho = os.path.join(DIRETORIO_SONS, nome_arquivo)
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)

    def parar_musica(self) -> None:
        pygame.mixer.music.stop()

    def sprite_canhao(self, direcao: str) -> pygame.Surface:
        """Retorna o sprite do canhão orientado para a direção do disparo."""
        # A imagem original canhao.png aponta para a direita ("right")
        if direcao == "right":
            return self.canhao_base
        canhao_esq = pygame.transform.flip(self.canhao_base, True, False)
        if direcao == "left":
            return canhao_esq
        if direcao == "up":
            return pygame.transform.rotate(canhao_esq, -90)
        if direcao == "down":
            return pygame.transform.rotate(canhao_esq, 90)
        raise ValueError(f"Direção de canhão inválida: {direcao}")

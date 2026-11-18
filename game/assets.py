"""Carregamento e gerenciamento centralizado de imagens, fontes, efeitos sonoros e ambientação."""
import os
import pygame

from game.config import CAMINHO_FONTE, DIRETORIO_IMAGENS, DIRETORIO_SONS


class AssetManager:
    """Gerencia o cache de imagens, fontes, trilhas retrô, efeitos de puzzles e ambientações."""

    def __init__(self) -> None:
        self._imagens: dict[tuple[str, tuple[int, int] | None], pygame.Surface] = {}
        self._fontes: dict[int, pygame.font.Font] = {}
        self._sons_ambiente: dict[str, pygame.mixer.Sound] = {}

        pygame.mixer.set_num_channels(12)
        self._canal_ambiente = pygame.mixer.Channel(0)

        # Efeitos sonoros clássicos
        self.som_tiro = self._carregar_som("tiro1.mp3", 0.10)
        self.som_dano = self._carregar_som("dano.mp3", 0.55)
        self.som_game_over = self._carregar_som("somGameOver.mp3", 0.70)
        self.som_click = self._carregar_som("click.mp3", 0.15)
        self.som_chegada = self._carregar_som("somchegada.mp3", 0.25)

        # Novos efeitos sonoros das mecânicas cooperativas e interações de cenário
        self.som_placa = self._carregar_som("placa.wav", 0.28)
        self.som_portao = self._carregar_som("portao.wav", 0.32)
        self.som_alavanca = self._carregar_som("alavanca.wav", 0.35)
        self.som_cristal = self._carregar_som("cristal.wav", 0.36)
        self.som_portal_aberto = self._carregar_som("portal_aberto.wav", 0.40)
        self.som_sabotagem = self._carregar_som("sabotagem.wav", 0.34)
        self.som_reviver = self._carregar_som("reviver.wav", 0.40)

        # Sprites base reutilizados
        self.coracao = self.carregar_imagem("coracao.png", escala=(22, 22))
        self.canhao_base = self.carregar_imagem("canhao.png", escala=(24, 24))
        self.game_over = self.carregar_imagem("Game_Over.png")
        self.icone = self.carregar_imagem("lab.png")

    def _carregar_som(self, nome_arquivo: str, volume: float) -> pygame.mixer.Sound:
        som = pygame.mixer.Sound(os.path.join(DIRETORIO_SONS, nome_arquivo))
        som.set_volume(volume)
        return som

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

    def tocar_musica(self, nome_arquivo: str, volume: float = 0.09, loop: int = -1) -> None:
        pygame.mixer.music.stop()
        caminho = os.path.join(DIRETORIO_SONS, nome_arquivo)
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)

    def parar_musica(self) -> None:
        pygame.mixer.music.stop()
        self.parar_ambiente()

    def iniciar_ambiente(self, arquivo_ambiente: str | None, volume: float = 0.14) -> None:
        """Toca em loop contínuo a ambientação sonora do cenário junto com a trilha 8-bit."""
        self._canal_ambiente.stop()
        if not arquivo_ambiente:
            return
        if arquivo_ambiente not in self._sons_ambiente:
            caminho = os.path.join(DIRETORIO_SONS, arquivo_ambiente)
            if os.path.exists(caminho):
                self._sons_ambiente[arquivo_ambiente] = pygame.mixer.Sound(caminho)
        som_amb = self._sons_ambiente.get(arquivo_ambiente)
        if som_amb is not None:
            som_amb.set_volume(volume)
            self._canal_ambiente.play(som_amb, loops=-1)

    def parar_ambiente(self) -> None:
        self._canal_ambiente.stop()

    def sprite_canhao(self, direcao: str) -> pygame.Surface:
        """Retorna o sprite do canhão orientado para a direção do disparo."""
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

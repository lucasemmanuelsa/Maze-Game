"""Entidades dinâmicas do jogo: Jogador (Player) e Canhões (Cannon)."""
from dataclasses import dataclass
from random import randint
import pygame

from game.collision import WallCollisionMap
from game.config import (
    LIMITE_MAX_X,
    LIMITE_MAX_Y,
    LIMITE_MIN_X,
    LIMITE_MIN_Y,
    ROSA,
    TAMANHO_BALA,
    VELOCIDADE_BALA_PADRAO,
    VELOCIDADE_JOGADOR_PADRAO,
    VERMELHO,
)


@dataclass(frozen=True)
class CannonSpec:
    """Especificação declarativa de um canhão em uma fase."""

    x: int
    y: int
    direcao: str  # "left", "right", "up", "down"
    offset_bala: tuple[int, int]
    intervalo_recarga: tuple[int, int] = (1, 3)
    recarga_inicial: tuple[int, int] | None = None
    velocidade_bala: int = VELOCIDADE_BALA_PADRAO


class Cannon:
    """Representa um canhão posicionado nas bordas do labirinto e seu projétil."""

    def __init__(self, spec: CannonSpec, sprite: pygame.Surface) -> None:
        self.spec = spec
        self.sprite = sprite
        self.x = spec.x
        self.y = spec.y
        self.bala_x = spec.x + spec.offset_bala[0]
        self.bala_y = spec.y + spec.offset_bala[1]

        intervalo_ini = spec.recarga_inicial or spec.intervalo_recarga
        self.tempo_recarga = randint(intervalo_ini[0], intervalo_ini[1])
        self.tempo_borda: int | None = None

    @property
    def rect_bala(self) -> pygame.Rect:
        return pygame.Rect(self.bala_x, self.bala_y, TAMANHO_BALA, TAMANHO_BALA)

    def desenhar_bala(self, janela: pygame.Surface) -> None:
        # Evita desenhar balas fora da arena (ex.: sobre o HUD inferior em y > 480)
        if 0 <= self.bala_x <= 490 and 0 <= self.bala_y <= 476:
            pygame.draw.rect(janela, ROSA, self.rect_bala)

    def desenhar_canhao(self, janela: pygame.Surface) -> None:
        janela.blit(self.sprite, (self.x, self.y))

    def atualizar(self, tempo_mapa: int, som_tiro: pygame.mixer.Sound) -> None:
        vel = self.spec.velocidade_bala
        direcao = self.spec.direcao

        if direcao == "left":
            self.bala_x -= vel
            tocou_borda = self.rect_bala.collidepoint(0, self.bala_y)
        elif direcao == "right":
            self.bala_x += vel
            tocou_borda = self.rect_bala.collidepoint(500, self.bala_y)
        elif direcao == "up":
            self.bala_y -= vel
            tocou_borda = self.rect_bala.collidepoint(self.bala_x, 0)
        elif direcao == "down":
            self.bala_y += vel
            tocou_borda = self.rect_bala.collidepoint(self.bala_x, 500)
        else:
            tocou_borda = False

        if tocou_borda and self.tempo_borda is None:
            self.tempo_borda = tempo_mapa

        if self.tempo_borda is not None and tempo_mapa >= self.tempo_borda + self.tempo_recarga:
            self.bala_x = self.x + self.spec.offset_bala[0]
            self.bala_y = self.y + self.spec.offset_bala[1]
            min_t, max_t = self.spec.intervalo_recarga
            self.tempo_recarga = randint(min_t, max_t)
            self.tempo_borda = None
            som_tiro.play()


class Player:
    """Representa o jogador explorando o labirinto."""

    def __init__(
        self,
        spawn_pos: tuple[int, int],
        tamanho_desenho: int = 14,
        tamanho_colisao: int = 13,
        velocidade: int = VELOCIDADE_JOGADOR_PADRAO,
    ) -> None:
        self.spawn_x, self.spawn_y = spawn_pos
        self.x, self.y = spawn_pos
        self.dx = 0
        self.dy = 0
        self.tamanho_desenho = tamanho_desenho
        self.tamanho_colisao = tamanho_colisao
        self.velocidade = velocidade

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.tamanho_desenho, self.tamanho_desenho)

    def definir_spawn(self, pos: tuple[int, int]) -> None:
        self.spawn_x, self.spawn_y = pos

    def reposicionar_no_spawn(self) -> None:
        self.x = self.spawn_x
        self.y = self.spawn_y

    def processar_evento(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.dx = -self.velocidade
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.dx = self.velocidade
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.dy = -self.velocidade
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.dy = self.velocidade
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.dx = 0
            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                self.dy = 0

    def mover(self, colisao_paredes: WallCollisionMap) -> None:
        # Eixo X
        if self.dx != 0:
            self.x += self.dx
            if colisao_paredes.colide_retangulo(
                self.x, self.y, self.tamanho_colisao, self.tamanho_colisao
            ):
                self.x -= self.dx

        # Eixo Y
        if self.dy != 0:
            self.y += self.dy
            if colisao_paredes.colide_retangulo(
                self.x, self.y, self.tamanho_colisao, self.tamanho_colisao
            ):
                self.y -= self.dy

        # Barreiras limitadoras externas
        self.x = max(LIMITE_MIN_X, min(LIMITE_MAX_X, self.x))
        self.y = max(LIMITE_MIN_Y, min(LIMITE_MAX_Y, self.y))

    def desenhar(self, janela: pygame.Surface) -> None:
        pygame.draw.rect(janela, VERMELHO, self.rect)

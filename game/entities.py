"""Entidades dinâmicas do jogo: Orbe Guardião (Player) para 1-3 jogadores e Bastiões de Canhão (Cannon)."""
from __future__ import annotations
from dataclasses import dataclass
from random import randint
import pygame

from game.collision import WallCollisionMap
from game.config import (
    CIANO,
    CONTROLES_MULTI,
    CONTROLES_SOLO,
    LIMITE_MAX_X,
    LIMITE_MAX_Y,
    LIMITE_MIN_X,
    LIMITE_MIN_Y,
    TAMANHO_BALA,
    TEMPO_CAPSULA_REVIVER,
    VELOCIDADE_BALA_PADRAO,
    VELOCIDADE_JOGADOR_PADRAO,
)
from game.visuals import desenhar_orbe_guardiao, desenhar_projetil_canhao


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
    """Representa um canhão posicionado na muralha do labirinto e sua esfera de plasma."""

    def __init__(self, spec: CannonSpec, sprite: pygame.Surface) -> None:
        self.spec = spec
        self.sprite = sprite
        self.x = spec.x
        self.y = spec.y
        self.bala_x = spec.x + spec.offset_bala[0]
        self.bala_y = spec.y + spec.offset_bala[1]

        intervalo_ini = spec.recarga_inicial or spec.intervalo_recarga
        self.tempo_recarga = randint(intervalo_ini[0], intervalo_ini[1])
        self.tempo_borda: float | None = None
        self.congelado = False

    @property
    def rect_bala(self) -> pygame.Rect:
        return pygame.Rect(self.bala_x, self.bala_y, TAMANHO_BALA, TAMANHO_BALA)

    def desenhar_bala(self, janela: pygame.Surface, t: float) -> None:
        desenhar_projetil_canhao(
            janela,
            self.bala_x,
            self.bala_y,
            self.spec.direcao,
            t,
            congelado=self.congelado,
        )

    def desenhar_canhao(self, janela: pygame.Surface) -> None:
        # Pedestal de pedra sob o canhão
        pygame.draw.rect(janela, (42, 44, 52), (self.x - 1, self.y - 1, 26, 26), border_radius=4)
        janela.blit(self.sprite, (self.x, self.y))
        if self.congelado:
            pygame.draw.rect(janela, CIANO, (self.x - 1, self.y - 1, 26, 26), width=2, border_radius=4)

    def atualizar(self, tempo_decorrido_seg: float, som_tiro: pygame.mixer.Sound, congelado: bool = False) -> None:
        self.congelado = congelado
        if congelado:
            return

        vel = self.spec.velocidade_bala
        direcao = self.spec.direcao

        if direcao == "left":
            self.bala_x -= vel
            tocou_borda = self.bala_x <= 0
        elif direcao == "right":
            self.bala_x += vel
            tocou_borda = self.bala_x + TAMANHO_BALA >= 500
        elif direcao == "up":
            self.bala_y -= vel
            tocou_borda = self.bala_y <= 0
        elif direcao == "down":
            self.bala_y += vel
            tocou_borda = self.bala_y + TAMANHO_BALA >= 500
        else:
            tocou_borda = False

        if tocou_borda and self.tempo_borda is None:
            self.tempo_borda = tempo_decorrido_seg

        if self.tempo_borda is not None and tempo_decorrido_seg >= self.tempo_borda + self.tempo_recarga:
            self.bala_x = self.x + self.spec.offset_bala[0]
            self.bala_y = self.y + self.spec.offset_bala[1]
            min_t, max_t = self.spec.intervalo_recarga
            self.tempo_recarga = randint(min_t, max_t)
            self.tempo_borda = None
            som_tiro.play()


class Player:
    """Representa um Orbe Guardião controlado localmente por teclado ou gamepad."""

    def __init__(
        self,
        indice: int,
        num_jogadores_total: int,
        spawn_pos: tuple[int, int],
        tamanho_desenho: int = 14,
        tamanho_colisao: int = 13,
        velocidade: int = VELOCIDADE_JOGADOR_PADRAO,
        joystick: pygame.joystick.Joystick | None = None,
    ) -> None:
        self.indice = indice
        self.num_jogadores_total = num_jogadores_total
        self.controles = CONTROLES_SOLO if num_jogadores_total == 1 else CONTROLES_MULTI[indice % 3]
        self.joystick = joystick

        self.spawn_x, self.spawn_y = spawn_pos
        self.x, self.y = spawn_pos
        self.dx = 0
        self.dy = 0
        self.olhar_dx = 1
        self.olhar_dy = 0

        self.tamanho_desenho = tamanho_desenho
        self.tamanho_colisao = tamanho_colisao
        self.velocidade = velocidade

        # Estados cooperativos
        self.em_capsula_reviver = False
        self.timer_reviver = 0.0
        self.timer_invulneravel = 0.0
        self.extraido_no_portal = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.tamanho_desenho, self.tamanho_desenho)

    @property
    def pode_levar_dano(self) -> bool:
        return not self.em_capsula_reviver and not self.extraido_no_portal and self.timer_invulneravel <= 0.0

    def definir_spawn(self, pos: tuple[int, int]) -> None:
        self.spawn_x, self.spawn_y = pos

    def reposicionar_no_spawn(self, invulnerabilidade: float = 1.6) -> None:
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.em_capsula_reviver = False
        self.timer_reviver = 0.0
        self.timer_invulneravel = invulnerabilidade

    def entrar_em_capsula(self) -> None:
        self.em_capsula_reviver = True
        self.timer_reviver = TEMPO_CAPSULA_REVIVER
        self.dx = 0
        self.dy = 0

    def reviver_no_local(self) -> None:
        self.em_capsula_reviver = False
        self.timer_reviver = 0.0
        self.timer_invulneravel = 2.0

    def ler_comandos(self, teclas_pressionadas: pygame.key.ScancodeWrapper) -> None:
        if self.em_capsula_reviver or self.extraido_no_portal:
            self.dx = 0
            self.dy = 0
            return

        esq = any(teclas_pressionadas[k] for k in self.controles["left"])
        dir_ = any(teclas_pressionadas[k] for k in self.controles["right"])
        cima = any(teclas_pressionadas[k] for k in self.controles["up"])
        baixo = any(teclas_pressionadas[k] for k in self.controles["down"])

        # Suporte adicional a controle/gamepad USB/Bluetooth
        if self.joystick is not None and self.joystick.get_init():
            if self.joystick.get_numaxes() >= 2:
                ax = self.joystick.get_axis(0)
                ay = self.joystick.get_axis(1)
                if ax < -0.4:
                    esq = True
                elif ax > 0.4:
                    dir_ = True
                if ay < -0.4:
                    cima = True
                elif ay > 0.4:
                    baixo = True
            if self.joystick.get_numhats() >= 1:
                hx, hy = self.joystick.get_hat(0)
                if hx < 0:
                    esq = True
                elif hx > 0:
                    dir_ = True
                if hy > 0:
                    cima = True
                elif hy < 0:
                    baixo = True

        self.dx = (-self.velocidade if esq else 0) + (self.velocidade if dir_ else 0)
        self.dy = (-self.velocidade if cima else 0) + (self.velocidade if baixo else 0)
        if self.dx != 0 or self.dy != 0:
            self.olhar_dx = (1 if self.dx > 0 else (-1 if self.dx < 0 else 0))
            self.olhar_dy = (1 if self.dy > 0 else (-1 if self.dy < 0 else 0))

    def _bloqueado(
        self,
        colisao_paredes: WallCollisionMap,
        portao_bloqueado: pygame.Rect | None,
    ) -> bool:
        if colisao_paredes.colide_retangulo(self.x, self.y, self.tamanho_colisao, self.tamanho_colisao):
            return True
        if portao_bloqueado is not None:
            rc = pygame.Rect(self.x, self.y, self.tamanho_colisao, self.tamanho_colisao)
            if rc.colliderect(portao_bloqueado):
                return True
        return False

    def atualizar(
        self,
        dt: float,
        colisao_paredes: WallCollisionMap,
        portao_bloqueado: pygame.Rect | None = None,
    ) -> bool:
        """
        Atualiza movimento e temporizadores.
        Retorna True caso o tempo da cápsula de resgate tenha esgotado neste frame.
        """
        if self.timer_invulneravel > 0.0:
            self.timer_invulneravel = max(0.0, self.timer_invulneravel - dt)

        if self.em_capsula_reviver:
            self.timer_reviver -= dt
            if self.timer_reviver <= 0.0:
                return True
            return False

        if self.extraido_no_portal:
            return False

        if self.dx != 0:
            self.x += self.dx
            if self._bloqueado(colisao_paredes, portao_bloqueado):
                self.x -= self.dx
                passo_x = 1 if self.dx > 0 else -1
                self.x += passo_x
                if self._bloqueado(colisao_paredes, portao_bloqueado):
                    self.x -= passo_x

        if self.dy != 0:
            self.y += self.dy
            if self._bloqueado(colisao_paredes, portao_bloqueado):
                self.y -= self.dy
                passo_y = 1 if self.dy > 0 else -1
                self.y += passo_y
                if self._bloqueado(colisao_paredes, portao_bloqueado):
                    self.y -= passo_y

        self.x = max(LIMITE_MIN_X, min(LIMITE_MAX_X, self.x))
        self.y = max(LIMITE_MIN_Y, min(LIMITE_MAX_Y, self.y))
        return False

    def desenhar(
        self,
        janela: pygame.Surface,
        t: float,
        fonte_tag: pygame.font.Font | None = None,
    ) -> None:
        if self.extraido_no_portal:
            return
        progresso = self.timer_reviver / TEMPO_CAPSULA_REVIVER if self.em_capsula_reviver else 1.0
        desenhar_orbe_guardiao(
            janela=janela,
            x=self.x,
            y=self.y,
            tamanho=self.tamanho_desenho,
            indice_jogador=self.indice,
            olhar_dx=self.olhar_dx,
            olhar_dy=self.olhar_dy,
            t=t,
            em_capsula_reviver=self.em_capsula_reviver,
            progresso_reviver=progresso,
            invulneravel=self.timer_invulneravel > 0.0,
            mostrar_tag=self.num_jogadores_total > 1,
            fonte_tag=fonte_tag,
        )

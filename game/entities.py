"""Entidades dinâmicas: Orbe Guardião (com Dash de Fase e Turbo), Canhões, Drones Caçadores e Boss."""
from __future__ import annotations
from dataclasses import dataclass
import math
from random import randint
import pygame

from game.collision import WallCollisionMap
from game.config import (
    AMARELO,
    BRANCO,
    CIANO,
    CONTROLES_MULTI,
    CONTROLES_SOLO,
    DOURADO,
    DURACAO_DASH,
    LARANJA,
    LIMITE_MAX_X,
    LIMITE_MAX_Y,
    LIMITE_MIN_X,
    LIMITE_MIN_Y,
    PASSOS_POR_FRAME_DASH,
    PRETO,
    RECARGA_DASH,
    TAMANHO_BALA,
    TEMPO_CAPSULA_REVIVER,
    VELOCIDADE_BALA_PADRAO,
    VELOCIDADE_JOGADOR_PADRAO,
    VERMELHO,
    VIOLETA,
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


@dataclass(frozen=True)
class PatrolDroneSpec:
    """Especificação de uma Sentinela / Drone Caçador patrulhando um corredor."""

    ponto_a: tuple[int, int]
    ponto_b: tuple[int, int]
    velocidade: float = 1.65
    tamanho: int = 12


class PatrolDrone:
    """Sentinela arcana que patrulha entre dois pontos; pode ser congelada por EMP ou atordoada com Dash!"""

    def __init__(self, spec: PatrolDroneSpec) -> None:
        self.spec = spec
        self.fx = float(spec.ponto_a[0])
        self.fy = float(spec.ponto_a[1])
        self.indo_para_b = True
        self.congelado = False
        self.timer_atordoado = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(round(self.fx)), int(round(self.fy)), self.spec.tamanho, self.spec.tamanho)

    @property
    def ativo_dano(self) -> bool:
        return not self.congelado and self.timer_atordoado <= 0.0

    def atordoar(self, duracao: float = 3.2) -> bool:
        """Atordoa o drone quando um jogador atravessa ele usando Dash de Fase."""
        if self.timer_atordoado <= 0.25:
            self.timer_atordoado = duracao
            return True
        return False

    def atualizar(self, dt: float, congelado: bool = False) -> None:
        self.congelado = congelado
        if self.timer_atordoado > 0.0:
            self.timer_atordoado = max(0.0, self.timer_atordoado - dt)
        if congelado or self.timer_atordoado > 0.0:
            return

        alvo = self.spec.ponto_b if self.indo_para_b else self.spec.ponto_a
        dx = alvo[0] - self.fx
        dy = alvo[1] - self.fy
        dist = math.hypot(dx, dy)
        passo = self.spec.velocidade * (dt * 60.0)
        if dist <= max(0.5, passo):
            self.fx, self.fy = float(alvo[0]), float(alvo[1])
            self.indo_para_b = not self.indo_para_b
        else:
            self.fx += (dx / dist) * passo
            self.fy += (dy / dist) * passo

    def desenhar(self, janela: pygame.Surface, t: float) -> None:
        tam = self.spec.tamanho
        cx = int(round(self.fx)) + tam // 2
        cy = int(round(self.fy)) + tam // 2
        raio = max(6, tam // 2 + 1)

        if self.congelado or self.timer_atordoado > 0.0:
            pygame.draw.circle(janela, (24, 54, 72), (cx, cy), raio + 1)
            pygame.draw.circle(janela, CIANO, (cx, cy), raio, 2)
            pygame.draw.circle(janela, BRANCO, (cx, cy), 2)
            return

        # Lâminas orbitais giratórias + núcleo caçador
        for k in range(4):
            ang = t * 9.0 + k * (math.pi / 2.0)
            bx = cx + int(math.cos(ang) * (raio + 2))
            by = cy + int(math.sin(ang) * (raio + 2))
            pygame.draw.circle(janela, LARANJA if k % 2 == 0 else VIOLETA, (bx, by), 2)

        pygame.draw.circle(janela, (34, 18, 44), (cx, cy), raio)
        pygame.draw.circle(janela, VIOLETA, (cx, cy), raio, 1)
        pygame.draw.circle(janela, VERMELHO, (cx, cy), 3)
        pygame.draw.circle(janela, AMARELO, (cx, cy), 1)


class BossCore:
    """
    Olho Mecânico Primordial (Boss da Fase 8 — Brabo Supremo):
    - Possui 3 Escudos Arcanos que só quebram quando a equipe sobrecarrega os Pilares de Canto.
    - Dispara ondas radiais giratórias de esferas de plasma pela arena central.
    """

    def __init__(self, centro: tuple[int, int] = (248, 248), escudos: int = 3) -> None:
        self.cx, self.cy = centro
        self.max_escudos = escudos
        self.escudos_restantes = escudos
        self.derrotado = False
        self.congelado = False
        self.timer_ataque = 1.35
        self.angulo_base = 0.0
        self.timer_dano_visual = 0.0
        self.projeteis: list[list[float]] = []  # [x, y, vx, vy]

    @property
    def rect_corpo(self) -> pygame.Rect:
        return pygame.Rect(self.cx - 14, self.cy - 14, 28, 28)

    def quebrar_escudo(self) -> bool:
        """Remove 1 escudo do Boss, limpa projéteis atuais e retorna True se foi derrotado."""
        if self.derrotado:
            return True
        self.escudos_restantes = max(0, self.escudos_restantes - 1)
        self.timer_dano_visual = 1.1
        self.projeteis.clear()
        if self.escudos_restantes <= 0:
            self.derrotado = True
            return True
        return False

    def atualizar(self, dt: float, som_tiro: pygame.mixer.Sound, congelado: bool = False) -> None:
        self.congelado = congelado
        if self.timer_dano_visual > 0.0:
            self.timer_dano_visual = max(0.0, self.timer_dano_visual - dt)
        if self.derrotado or congelado:
            return

        # Atualiza projéteis radiais ativos
        fator = dt * 60.0
        vivos: list[list[float]] = []
        for p in self.projeteis:
            p[0] += p[2] * fator
            p[1] += p[3] * fator
            if 18.0 <= p[0] <= 482.0 and 18.0 <= p[1] <= 482.0:
                vivos.append(p)
        self.projeteis = vivos

        # Dispara nova onda radial conforme a fase de fúria (3 -> 2 -> 1 escudos)
        self.timer_ataque -= dt
        if self.timer_ataque <= 0.0:
            furia = self.max_escudos - self.escudos_restantes  # 0, 1 ou 2
            qtd = 6 + furia * 2  # 6, 8 ou 10 esferas na onda radial
            vel = 2.15 + furia * 0.30
            self.angulo_base += 0.42
            for i in range(qtd):
                ang = self.angulo_base + (2.0 * math.pi * i) / qtd
                vx = math.cos(ang) * vel
                vy = math.sin(ang) * vel
                self.projeteis.append([float(self.cx), float(self.cy), vx, vy])
            self.timer_ataque = max(1.25, 2.05 - furia * 0.32)
            som_tiro.play()

    def colide_com_jogador(self, rect_jogador: pygame.Rect) -> bool:
        if self.derrotado or self.congelado:
            return False
        if rect_jogador.colliderect(self.rect_corpo):
            return True
        for p in self.projeteis:
            rp = pygame.Rect(int(p[0]) - 4, int(p[1]) - 4, 8, 8)
            if rect_jogador.colliderect(rp):
                return True
        return False

    def desenhar(self, janela: pygame.Surface, t: float) -> None:
        if self.derrotado:
            # Cratera rúnica fumegante após derrota (abre espaço visual para o Portal Final!)
            pygame.draw.circle(janela, (36, 26, 44), (self.cx, self.cy), 18)
            pygame.draw.circle(janela, DOURADO, (self.cx, self.cy), 18, 1)
            return

        # Projéteis radiais
        for p in self.projeteis:
            px, py = int(p[0]), int(p[1])
            if self.congelado:
                pygame.draw.circle(janela, CIANO, (px, py), 4)
            else:
                pygame.draw.circle(janela, VIOLETA, (px, py), 5)
                pygame.draw.circle(janela, AMARELO, (px, py), 2)

        # Anéis de Escudo Arcano ao redor do Boss
        for s in range(self.escudos_restantes):
            raio_s = 19 + s * 4 + int(math.sin(t * 6.0 + s) * 1.5)
            cor_s = CIANO if self.congelado else (DOURADO if s == 0 else VIOLETA)
            pygame.draw.circle(janela, cor_s, (self.cx, self.cy), raio_s, 1)

        # Corpo do Olho Mecânico Primordial
        cor_corpo = BRANCO if (self.timer_dano_visual > 0.0 and int(t * 20) % 2 == 0) else (56, 18, 42)
        pygame.draw.circle(janela, PRETO, (self.cx, self.cy), 16)
        pygame.draw.circle(janela, cor_corpo, (self.cx, self.cy), 14)
        pygame.draw.circle(janela, VERMELHO if not self.congelado else CIANO, (self.cx, self.cy), 8)
        pupila_x = self.cx + int(math.cos(t * 3.0) * 3)
        pupila_y = self.cy + int(math.sin(t * 3.0) * 3)
        pygame.draw.circle(janela, AMARELO, (pupila_x, pupila_y), 4)
        pygame.draw.circle(janela, PRETO, (pupila_x, pupila_y), 2)


class Player:
    """Representa um Orbe Guardião controlado localmente por teclado ou gamepad, com Dash de Fase e Turbo."""

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

        # Estados cooperativos e habilidades frenéticas
        self.em_capsula_reviver = False
        self.timer_reviver = 0.0
        self.timer_invulneravel = 0.0
        self.extraido_no_portal = False

        self.timer_dash = 0.0
        self.recarga_dash = 0.0
        self.dash_dx = 1
        self.dash_dy = 0
        self._dash_pressionado_ant = False
        self.rastro: list[tuple[int, int]] = []

        self.timer_turbo = 0.0
        self.carregando_nucleo = False
        self.cooldown_teleporte = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.tamanho_desenho, self.tamanho_desenho)

    @property
    def em_dash(self) -> bool:
        return self.timer_dash > 0.0

    @property
    def em_turbo(self) -> bool:
        return self.timer_turbo > 0.0

    @property
    def pode_levar_dano(self) -> bool:
        return (
            not self.em_capsula_reviver
            and not self.extraido_no_portal
            and self.timer_invulneravel <= 0.0
            and self.timer_dash <= 0.0
        )

    def definir_spawn(self, pos: tuple[int, int]) -> None:
        self.spawn_x, self.spawn_y = pos

    def reposicionar_no_spawn(self, invulnerabilidade: float = 1.6) -> None:
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.em_capsula_reviver = False
        self.timer_reviver = 0.0
        self.timer_invulneravel = invulnerabilidade
        self.timer_dash = 0.0
        self.rastro.clear()

    def entrar_em_capsula(self) -> None:
        self.em_capsula_reviver = True
        self.timer_reviver = TEMPO_CAPSULA_REVIVER
        self.dx = 0
        self.dy = 0
        self.timer_dash = 0.0

    def reviver_no_local(self) -> None:
        self.em_capsula_reviver = False
        self.timer_reviver = 0.0
        self.timer_invulneravel = 2.0

    def ler_comandos(self, teclas_pressionadas: pygame.key.ScancodeWrapper) -> bool:
        """Lê movimento e botão de Dash. Retorna True se o jogador acabou de acionar o Dash de Fase."""
        if self.em_capsula_reviver or self.extraido_no_portal:
            self.dx = 0
            self.dy = 0
            self._dash_pressionado_ant = False
            return False

        esq = any(teclas_pressionadas[k] for k in self.controles["left"])
        dir_ = any(teclas_pressionadas[k] for k in self.controles["right"])
        cima = any(teclas_pressionadas[k] for k in self.controles["up"])
        baixo = any(teclas_pressionadas[k] for k in self.controles["down"])
        quer_dash = any(teclas_pressionadas[k] for k in self.controles["dash"])

        # Suporte a controle/gamepad USB/Bluetooth
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
            num_btns = self.joystick.get_numbuttons()
            for btn_i in (0, 1, 2, 5):
                if btn_i < num_btns and self.joystick.get_button(btn_i):
                    quer_dash = True

        dir_x = (-1 if esq else 0) + (1 if dir_ else 0)
        dir_y = (-1 if cima else 0) + (1 if baixo else 0)
        self.dx = dir_x * self.velocidade
        self.dy = dir_y * self.velocidade

        if dir_x != 0 or dir_y != 0:
            self.olhar_dx = dir_x
            self.olhar_dy = dir_y

        iniciou_dash = False
        if quer_dash and not self._dash_pressionado_ant and self.recarga_dash <= 0.0:
            self.timer_dash = DURACAO_DASH
            self.recarga_dash = RECARGA_DASH
            self.dash_dx = dir_x if (dir_x != 0 or dir_y != 0) else self.olhar_dx
            self.dash_dy = dir_y if (dir_x != 0 or dir_y != 0) else self.olhar_dy
            if self.dash_dx == 0 and self.dash_dy == 0:
                self.dash_dx = 1
            iniciou_dash = True

        self._dash_pressionado_ant = quer_dash
        return iniciou_dash

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

    def _mover_com_deslize(
        self,
        passos_x: int,
        passos_y: int,
        colisao_paredes: WallCollisionMap,
        portao_bloqueado: pygame.Rect | None,
    ) -> None:
        """Move 1px por sub-passo garantindo zero atravessamento de paredes mesmo em alta velocidade."""
        sinal_x = 1 if passos_x > 0 else -1
        for _ in range(abs(passos_x)):
            self.x += sinal_x
            if self._bloqueado(colisao_paredes, portao_bloqueado):
                self.x -= sinal_x
                break

        sinal_y = 1 if passos_y > 0 else -1
        for _ in range(abs(passos_y)):
            self.y += sinal_y
            if self._bloqueado(colisao_paredes, portao_bloqueado):
                self.y -= sinal_y
                break

        self.x = max(LIMITE_MIN_X, min(LIMITE_MAX_X, self.x))
        self.y = max(LIMITE_MIN_Y, min(LIMITE_MAX_Y, self.y))

    def atualizar(
        self,
        dt: float,
        colisao_paredes: WallCollisionMap,
        portao_bloqueado: pygame.Rect | None = None,
    ) -> bool:
        """
        Atualiza movimento, Dash de Fase, Turbo e temporizadores.
        Retorna True caso o tempo da cápsula de resgate tenha esgotado neste frame.
        """
        if self.timer_invulneravel > 0.0:
            self.timer_invulneravel = max(0.0, self.timer_invulneravel - dt)
        if self.recarga_dash > 0.0:
            self.recarga_dash = max(0.0, self.recarga_dash - dt)
        if self.timer_turbo > 0.0:
            self.timer_turbo = max(0.0, self.timer_turbo - dt)
        if self.cooldown_teleporte > 0.0:
            self.cooldown_teleporte = max(0.0, self.cooldown_teleporte - dt)

        if self.em_capsula_reviver:
            self.timer_reviver -= dt
            if self.timer_reviver <= 0.0:
                return True
            return False

        if self.extraido_no_portal:
            return False

        if self.timer_dash > 0.0:
            self.rastro.append((self.x, self.y))
            self.rastro = self.rastro[-4:]
            self.timer_dash = max(0.0, self.timer_dash - dt)
            vel_dash = PASSOS_POR_FRAME_DASH + 2
            self._mover_com_deslize(
                self.dash_dx * vel_dash,
                self.dash_dy * vel_dash,
                colisao_paredes,
                portao_bloqueado,
            )
            return False

        if self.timer_turbo > 0.0 and (self.dx != 0 or self.dy != 0):
            self.rastro.append((self.x, self.y))
            self.rastro = self.rastro[-3:]
        elif self.rastro:
            self.rastro.pop(0)

        vel_extra = 1 if self.timer_turbo > 0.0 else 0
        px = (self.dx + (vel_extra if self.dx > 0 else (-vel_extra if self.dx < 0 else 0)))
        py = (self.dy + (vel_extra if self.dy > 0 else (-vel_extra if self.dy < 0 else 0)))
        self._mover_com_deslize(px, py, colisao_paredes, portao_bloqueado)
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
            em_dash=self.em_dash,
            em_turbo=self.em_turbo,
            carregando_nucleo=self.carregando_nucleo,
            rastro=self.rastro,
            mostrar_tag=self.num_jogadores_total > 1,
            fonte_tag=fonte_tag,
        )

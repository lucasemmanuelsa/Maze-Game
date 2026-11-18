"""Puzzles cooperativos dinâmicos que escalam automaticamente para 1, 2 ou 3 jogadores."""
from dataclasses import dataclass
import math
import pygame

from game.assets import AssetManager
from game.config import (
    AMARELO,
    BRANCO,
    CIANO,
    CORES_JOGADORES,
    DOURADO,
    PRETO,
    TEMPO_CONGELAMENTO_SABOTAGEM,
    VERDE_LIMAO,
    VERMELHO,
)


@dataclass(frozen=True)
class PuzzleLayoutSpec:
    """Coordenadas declarativas dos elementos de puzzle de uma fase."""

    orientacao_portao: str  # "H" ou "V"
    portao_rect: tuple[int, int, int, int]
    placa_principal: tuple[int, int]
    placa_extra_3p: tuple[int, int]
    alavanca_pos: tuple[int, int]
    totem_sabotagem_pos: tuple[int, int]
    cristais_pos: list[tuple[int, int]]


class LevelPuzzleManager:
    """
    Gerencia o estado interativo dos puzzles na fase atual:
    - Placas de Pressão Rúnicas (1 placa com trava solo em 1P; 1 placa de revezamento em 2P;
      2 placas simultâneas em 3P!).
    - Portão de Energia Ancestral + Alavanca de Destrave Permanente do outro lado.
    - Cristais Rúnicos Sintonizados (em 2P/3P cada amigo precisa buscar o cristal da sua cor!).
    - Totem Sabotador EMP (congela os canhões enquanto pisado + bônus temporal).
    - Portal Dimensional Ancestral (abre somente após reunir todos os Cristais).
    """

    def __init__(self, spec: PuzzleLayoutSpec, num_jogadores: int, tamanho_entidade: int) -> None:
        self.spec = spec
        self.num_jogadores = max(1, min(3, num_jogadores))
        self.tam = max(14, tamanho_entidade + 2)

        gx, gy, gw, gh = spec.portao_rect
        self.rect_portao = pygame.Rect(gx, gy, gw, gh)

        # Em 3 jogadores ativamos as 2 placas de sincronia; em 1P/2P usamos a placa principal
        pos_placas = [spec.placa_principal]
        if self.num_jogadores >= 3:
            pos_placas.append(spec.placa_extra_3p)
        self.placas_rects = [pygame.Rect(px, py, self.tam, self.tam) for px, py in pos_placas]
        self.placas_ativas = [False] * len(self.placas_rects)
        self.trava_solo_placa = False

        self.rect_alavanca = pygame.Rect(spec.alavanca_pos[0], spec.alavanca_pos[1], self.tam, self.tam)
        self.alavanca_acionada = False
        self.portao_aberto = False

        self.rect_sabotagem = pygame.Rect(
            spec.totem_sabotagem_pos[0], spec.totem_sabotagem_pos[1], self.tam, self.tam
        )
        self.sabotagem_pisada = False
        self.timer_sabotagem = 0.0
        self._recarga_som_sabotagem = 0.0

        # Cristais: 2 cristais universais no modo 1P; 2 sintonizados em 2P; 3 sintonizados em 3P
        qtd_cristais = 2 if self.num_jogadores <= 2 else 3
        self.cristais: list[dict] = []
        for idx in range(min(qtd_cristais, len(spec.cristais_pos))):
            cx, cy = spec.cristais_pos[idx]
            dono = None if self.num_jogadores == 1 else idx  # Em 2P/3P: 0->P1, 1->P2, 2->P3
            self.cristais.append(
                {
                    "rect": pygame.Rect(cx, cy, self.tam, self.tam),
                    "dono": dono,
                    "coletado": False,
                }
            )

        self.mensagem_evento: str = ""
        self.timer_mensagem: float = 0.0

    @property
    def cristais_coletados(self) -> int:
        return sum(1 for c in self.cristais if c["coletado"])

    @property
    def total_cristais(self) -> int:
        return len(self.cristais)

    @property
    def portal_destrancado(self) -> bool:
        return all(c["coletado"] for c in self.cristais)

    @property
    def canhoes_congelados(self) -> bool:
        return self.sabotagem_pisada or self.timer_sabotagem > 0.0

    def retangulo_bloqueio_portao(self) -> pygame.Rect | None:
        return None if self.portao_aberto else self.rect_portao

    def _anunciar(self, texto: str, duracao: float = 2.6) -> None:
        self.mensagem_evento = texto
        self.timer_mensagem = duracao

    def atualizar(
        self,
        jogadores_ativos: list,
        dt: float,
        assets: AssetManager,
    ) -> None:
        if self.timer_mensagem > 0.0:
            self.timer_mensagem = max(0.0, self.timer_mensagem - dt)
        if self._recarga_som_sabotagem > 0.0:
            self._recarga_som_sabotagem = max(0.0, self._recarga_som_sabotagem - dt)

        vivos = [j for j in jogadores_ativos if not j.em_capsula_reviver and not j.extraido_no_portal]

        # 1. Placas de Pressão
        estava_aberto = self.portao_aberto
        for i, pr in enumerate(self.placas_rects):
            pisando = any(j.rect.colliderect(pr) for j in vivos)
            if pisando and not self.placas_ativas[i]:
                assets.som_placa.play()
                if self.num_jogadores == 1:
                    self.trava_solo_placa = True
                    self._anunciar("PLACA ATIVADA! PORTAO DESTRAVADO")
                elif self.num_jogadores == 2 and not self.alavanca_acionada:
                    self._anunciar("SEGURE A PLACA PARA O PARCEIRO PASSAR!")
                elif self.num_jogadores == 3 and not self.alavanca_acionada:
                    self._anunciar("SINCRONIZE AS 2 PLACAS PARA ABRIR!")
            self.placas_ativas[i] = pisando or self.trava_solo_placa

        # 2. Alavanca Permanente (do outro lado do portão)
        if not self.alavanca_acionada:
            if any(j.rect.colliderect(self.rect_alavanca) for j in vivos):
                self.alavanca_acionada = True
                assets.som_alavanca.play()
                self._anunciar("ALAVANCA ACIONADA! PORTAO ABERTO PARA TODOS!")

        todas_placas = all(self.placas_ativas)
        self.portao_aberto = self.alavanca_acionada or self.trava_solo_placa or todas_placas
        if self.portao_aberto and not estava_aberto:
            assets.som_portao.play()

        # 3. Totem Sabotador EMP (congela canhões)
        pisando_totem = any(j.rect.colliderect(self.rect_sabotagem) for j in vivos)
        if pisando_totem:
            if not self.sabotagem_pisada and self.timer_sabotagem <= 0.1 and self._recarga_som_sabotagem <= 0.0:
                assets.som_sabotagem.play()
                self._recarga_som_sabotagem = 1.5
                self._anunciar("CANHOES CONGELADOS POR PULSO EMP!")
            self.timer_sabotagem = TEMPO_CONGELAMENTO_SABOTAGEM
        elif self.timer_sabotagem > 0.0:
            self.timer_sabotagem = max(0.0, self.timer_sabotagem - dt)
        self.sabotagem_pisada = pisando_totem

        # 4. Cristais Rúnicos Sintonizados
        estava_portal_aberto = self.portal_destrancado
        for c in self.cristais:
            if c["coletado"]:
                continue
            for j in vivos:
                if j.rect.colliderect(c["rect"]):
                    if c["dono"] is None or c["dono"] == j.indice:
                        c["coletado"] = True
                        if self.portal_destrancado and not estava_portal_aberto:
                            assets.som_portal_aberto.play()
                            self._anunciar("PORTAL ANCESTRAL ABERTO! AVANCEM!")
                        else:
                            assets.som_cristal.play()
                            restantes = self.total_cristais - self.cristais_coletados
                            self._anunciar(f"CRISTAL COLETADO! FALTAM {restantes}")
                        break
                    elif self.timer_mensagem <= 0.2:
                        dono_txt = f"P{c['dono'] + 1}"
                        self._anunciar(f"CRISTAL SINTONIZADO COM {dono_txt}!", 1.4)

    def desenhar_elementos_piso(self, janela: pygame.Surface, t: float) -> None:
        """Desenha placas, fios rúnicos, alavanca, totem EMP e portão de energia."""
        # Fio rúnico sutil ligando placas ativas ao portão
        if not self.alavanca_acionada:
            for i, pr in enumerate(self.placas_rects):
                if self.placas_ativas[i]:
                    pygame.draw.line(janela, (40, 175, 195), pr.center, self.rect_portao.center, 1)

        # Placas de Pressão
        for i, pr in enumerate(self.placas_rects):
            ativa = self.placas_ativas[i] or self.alavanca_acionada
            cor_borda = VERDE_LIMAO if ativa else AMARELO
            cor_miolo = (26, 150, 110) if ativa else (92, 76, 28)
            pygame.draw.rect(janela, (30, 32, 38), pr.inflate(4, 4), border_radius=3)
            pygame.draw.rect(janela, cor_miolo, pr, border_radius=3)
            pygame.draw.rect(janela, cor_borda, pr, width=2, border_radius=3)
            pygame.draw.circle(janela, BRANCO if ativa else DOURADO, pr.center, 2)

        # Alavanca Permanente
        ar = self.rect_alavanca
        pygame.draw.rect(janela, (44, 42, 52), (ar.x, ar.centery, ar.w, ar.h // 2 + 2), border_radius=2)
        haste_x = ar.right - 2 if self.alavanca_acionada else ar.left + 2
        cor_alav = VERDE_LIMAO if self.alavanca_acionada else VERMELHO
        pygame.draw.line(janela, BRANCO, (ar.centerx, ar.centery + 2), (haste_x, ar.top + 2), 3)
        pygame.draw.circle(janela, cor_alav, (haste_x, ar.top + 2), 4)

        # Totem Sabotador EMP
        sr = self.rect_sabotagem
        ativo_emp = self.canhoes_congelados
        cor_emp = CIANO if ativo_emp else (88, 134, 180)
        pygame.draw.circle(janela, (28, 36, 52), sr.center, sr.w // 2 + 2)
        pygame.draw.circle(janela, cor_emp, sr.center, sr.w // 2, 2)
        raio_pulso = 4 if int(t * 10) % 2 == 0 and ativo_emp else 3
        pygame.draw.circle(janela, BRANCO if ativo_emp else CIANO, sr.center, raio_pulso)

        # Portão de Energia Ancestral
        gr = self.rect_portao
        if not self.portao_aberto:
            pulso = int(45 * math.sin(t * 12.0))
            cor_laser = (255, max(30, 75 + pulso), 65)
            pygame.draw.rect(janela, cor_laser, gr, border_radius=2)
            if self.spec.orientacao_portao == "H":
                pygame.draw.line(janela, BRANCO, (gr.left + 2, gr.centery), (gr.right - 2, gr.centery), 2)
                pygame.draw.rect(janela, (90, 90, 105), (gr.left - 3, gr.top - 1, 4, gr.h + 2))
                pygame.draw.rect(janela, (90, 90, 105), (gr.right - 1, gr.top - 1, 4, gr.h + 2))
            else:
                pygame.draw.line(janela, BRANCO, (gr.centerx, gr.top + 2), (gr.centerx, gr.bottom - 2), 2)
                pygame.draw.rect(janela, (90, 90, 105), (gr.left - 1, gr.top - 3, gr.w + 2, 4))
                pygame.draw.rect(janela, (90, 90, 105), (gr.left - 1, gr.bottom - 1, gr.w + 2, 4))
        else:
            # Pilares recolhidos indicando passagem livre
            pygame.draw.rect(janela, (24, 96, 78), gr, width=1, border_radius=2)

        # Cristais Rúnicos flutuantes
        for idx, c in enumerate(self.cristais):
            if c["coletado"]:
                continue
            cr = c["rect"]
            flut = int(2 * math.sin(t * 5.0 + idx * 1.7))
            cx, cy = cr.centerx, cr.centery + flut
            cor_c = DOURADO if c["dono"] is None else CORES_JOGADORES[c["dono"] % 3]
            pts = [(cx, cy - 7), (cx + 6, cy), (cx, cy + 7), (cx - 6, cy)]
            pygame.draw.polygon(janela, cor_c, pts)
            pygame.draw.polygon(janela, BRANCO, pts, 1)
            pygame.draw.circle(janela, BRANCO, (cx - 1, cy - 2), 1)

    def desenhar_portal(
        self,
        janela: pygame.Surface,
        pos_portal: tuple[int, int],
        tamanho: int,
        t: float,
        eh_checkpoint_intermediario: bool = False,
    ) -> None:
        """Desenha o Altar / Portal Ancestral (selado enquanto faltam cristais, vórtice ativo quando aberto)."""
        cx = pos_portal[0] + tamanho // 2
        cy = pos_portal[1] + tamanho // 2
        raio = max(8, tamanho // 2 + 3)

        # Base de pedra do altar
        pygame.draw.circle(janela, (52, 58, 74), (cx, cy), raio + 2)

        if not self.portal_destrancado:
            # Portal selado com cadeado rúnico vermelho/âmbar
            pygame.draw.circle(janela, (120, 32, 46), (cx, cy), raio)
            pygame.draw.circle(janela, DOURADO, (cx, cy), raio, 2)
            pygame.draw.line(janela, VERMELHO, (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
            pygame.draw.line(janela, VERMELHO, (cx - 4, cy + 4), (cx + 4, cy - 4), 2)
        else:
            cor_vortice = DOURADO if eh_checkpoint_intermediario else CIANO
            cor_interna = VERDE_LIMAO if eh_checkpoint_intermediario else (180, 248, 255)
            pulso = int(2 * math.sin(t * 7.0))
            pygame.draw.circle(janela, cor_vortice, (cx, cy), raio + pulso)
            pygame.draw.circle(janela, (24, 72, 128), (cx, cy), max(4, raio - 2))
            pygame.draw.circle(janela, cor_interna, (cx, cy), max(2, raio - 5))

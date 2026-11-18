"""Puzzles cooperativos dinâmicos e mecânicas frenéticas (Teleporte, Turbo, Núcleo Instável, Pilares Boss e Combo)."""
from __future__ import annotations
from dataclasses import dataclass, field
import math
import pygame

from game.assets import AssetManager
from game.config import (
    AMARELO,
    BRANCO,
    CIANO,
    CORES_JOGADORES,
    DOURADO,
    DURACAO_TURBO,
    JANELA_PILARES_BOSS_COOP,
    JANELA_PILARES_BOSS_SOLO,
    LARANJA,
    PRETO,
    TEMPO_CALOR_NUCLEO_COOP,
    TEMPO_CONGELAMENTO_SABOTAGEM,
    VERDE_LIMAO,
    VERMELHO,
    VIOLETA,
)
from game.visuals import SparkSystem


@dataclass(frozen=True)
class PuzzleLayoutSpec:
    """Coordenadas declarativas dos puzzles e mecânicas especiais de uma fase."""

    orientacao_portao: str  # "H" ou "V"
    portao_rect: tuple[int, int, int, int]
    placa_principal: tuple[int, int]
    placa_extra_3p: tuple[int, int]
    alavanca_pos: tuple[int, int]
    totem_sabotagem_pos: tuple[int, int]
    cristais_pos: list[tuple[int, int]]
    portais_gemeos: list[tuple[tuple[int, int], tuple[int, int]]] = field(default_factory=list)
    esteiras_turbo: list[tuple[int, int]] = field(default_factory=list)
    nucleo_energia: tuple[tuple[int, int], tuple[int, int]] | None = None  # (origem_nucleo, soquete_reator)
    pilares_boss: list[tuple[int, int]] = field(default_factory=list)


class LevelPuzzleManager:
    """
    Gerencia os puzzles cooperativos e dinâmicas frenéticas da fase:
    - Placas de Pressão Rúnicas + Portão de Energia + Alavanca Permanente.
    - Cristais Rúnicos Sintonizados (1P universal; 2P/3P sintonizados por cor!).
    - Totem Sabotador EMP (congela canhões, drones e Boss!).
    - Portais Gêmeos de Dobra (acessam salas secretas seladas e atalhos táticos!).
    - Esteiras Turbo (impulso de velocidade + rastro flamejante).
    - Núcleo de Energia Instável ("Batata Quente" Co-op: passe para amigos para resetar sobrecarga e ganhar Turbo!).
    - Pilares de Sobrecarga do Boss (sincronia nos cantos da Fase 8 para quebrar escudos do Boss!).
    - Sistema de Combo & Bônus Temporal (-segundos no tempo final da fase!).
    """

    def __init__(self, spec: PuzzleLayoutSpec, num_jogadores: int, tamanho_entidade: int) -> None:
        self.spec = spec
        self.num_jogadores = max(1, min(3, num_jogadores))
        self.tam = max(14, tamanho_entidade + 2)

        gx, gy, gw, gh = spec.portao_rect
        self.rect_portao = pygame.Rect(gx, gy, gw, gh)

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

        qtd_cristais = 2 if self.num_jogadores <= 2 else 3
        self.cristais: list[dict] = []
        for idx in range(min(qtd_cristais, len(spec.cristais_pos))):
            cx, cy = spec.cristais_pos[idx]
            dono = None if self.num_jogadores == 1 else idx
            self.cristais.append(
                {
                    "rect": pygame.Rect(cx, cy, self.tam, self.tam),
                    "dono": dono,
                    "coletado": False,
                }
            )

        # Portais Gêmeos (pares A <-> B)
        self.pares_portais: list[tuple[pygame.Rect, pygame.Rect]] = [
            (
                pygame.Rect(pa[0], pa[1], self.tam, self.tam),
                pygame.Rect(pb[0], pb[1], self.tam, self.tam),
            )
            for pa, pb in spec.portais_gemeos
        ]

        # Esteiras Turbo
        self.rects_turbo: list[pygame.Rect] = [
            pygame.Rect(tx, ty, self.tam, self.tam) for tx, ty in spec.esteiras_turbo
        ]
        self._recarga_som_turbo = 0.0

        # Núcleo de Energia Instável (Relay Co-op)
        self.tem_nucleo = spec.nucleo_energia is not None
        self.nucleo_entregue = not self.tem_nucleo
        self.portador_nucleo: int | None = None
        self.calor_nucleo = TEMPO_CALOR_NUCLEO_COOP
        self._cooldown_passe_nucleo = 0.0
        if spec.nucleo_energia is not None:
            orig, soq = spec.nucleo_energia
            self.nucleo_origem = orig
            self.nucleo_pos = [float(orig[0]), float(orig[1])]
            self.rect_soquete = pygame.Rect(soq[0], soq[1], self.tam + 2, self.tam + 2)
        else:
            self.nucleo_origem = (0, 0)
            self.nucleo_pos = [0.0, 0.0]
            self.rect_soquete = pygame.Rect(0, 0, 1, 1)

        # Pilares de Sobrecarga do Boss (Fase 8)
        self.pilares_rects = [pygame.Rect(px, py, self.tam, self.tam) for px, py in spec.pilares_boss]
        self.pilares_ativos = [False] * len(self.pilares_rects)
        self.timer_janela_pilares = 0.0
        self.boss_derrotado = len(self.pilares_rects) == 0

        # Sistema de Combo & Bônus de Tempo
        self.combo = 0
        self.timer_combo = 0.0
        self.bonus_segundos = 0

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
        return (
            all(c["coletado"] for c in self.cristais)
            and self.nucleo_entregue
            and self.boss_derrotado
        )

    @property
    def canhoes_congelados(self) -> bool:
        return self.sabotagem_pisada or self.timer_sabotagem > 0.0

    def retangulo_bloqueio_portao(self) -> pygame.Rect | None:
        return None if self.portao_aberto else self.rect_portao

    def _anunciar(self, texto: str, duracao: float = 2.6) -> None:
        self.mensagem_evento = texto
        self.timer_mensagem = duracao

    def registrar_combo(self, rotulo: str, bonus_seg: int = 1) -> None:
        """Incrementa o multiplicador de combo da equipe e concede redução no cronômetro."""
        self.combo += 1
        self.timer_combo = 5.5
        ganho = bonus_seg + (1 if self.combo >= 4 else 0)
        self.bonus_segundos += ganho
        self._anunciar(f"{rotulo} | COMBO x{self.combo} (-{ganho}s!)", 2.2)

    def resetar_nucleo_para_origem(self, jogadores_ativos: list) -> None:
        for j in jogadores_ativos:
            j.carregando_nucleo = False
        self.portador_nucleo = None
        self.nucleo_pos = [float(self.nucleo_origem[0]), float(self.nucleo_origem[1])]
        self.calor_nucleo = TEMPO_CALOR_NUCLEO_COOP

    def atualizar(
        self,
        jogadores_ativos: list,
        dt: float,
        assets: AssetManager,
        sparks: SparkSystem | None = None,
    ) -> bool:
        """
        Atualiza todos os puzzles da fase.
        Retorna True caso os Pilares de Sobrecarga tenham acabado de quebrar 1 Escudo do Boss!
        """
        quebrou_escudo_boss = False

        if self.timer_mensagem > 0.0:
            self.timer_mensagem = max(0.0, self.timer_mensagem - dt)
        if self._recarga_som_sabotagem > 0.0:
            self._recarga_som_sabotagem = max(0.0, self._recarga_som_sabotagem - dt)
        if self._recarga_som_turbo > 0.0:
            self._recarga_som_turbo = max(0.0, self._recarga_som_turbo - dt)
        if self._cooldown_passe_nucleo > 0.0:
            self._cooldown_passe_nucleo = max(0.0, self._cooldown_passe_nucleo - dt)
        if self.timer_combo > 0.0:
            self.timer_combo = max(0.0, self.timer_combo - dt)
            if self.timer_combo <= 0.0:
                self.combo = 0

        vivos = [j for j in jogadores_ativos if not j.em_capsula_reviver and not j.extraido_no_portal]

        # 1. Placas de Pressão + Alavanca + Portão
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

        if not self.alavanca_acionada:
            if any(j.rect.colliderect(self.rect_alavanca) for j in vivos):
                self.alavanca_acionada = True
                assets.som_alavanca.play()
                if sparks is not None:
                    sparks.emitir(self.rect_alavanca.centerx, self.rect_alavanca.centery, VERDE_LIMAO, 14)
                self.registrar_combo("ALAVANCA DESTRAVADA!", bonus_seg=1)

        todas_placas = all(self.placas_ativas)
        self.portao_aberto = self.alavanca_acionada or self.trava_solo_placa or todas_placas
        if self.portao_aberto and not estava_aberto:
            assets.som_portao.play()

        # 2. Totem Sabotador EMP
        pisando_totem = any(j.rect.colliderect(self.rect_sabotagem) for j in vivos)
        if pisando_totem:
            if not self.sabotagem_pisada and self.timer_sabotagem <= 0.1 and self._recarga_som_sabotagem <= 0.0:
                assets.som_sabotagem.play()
                self._recarga_som_sabotagem = 1.5
                if sparks is not None:
                    sparks.emitir(self.rect_sabotagem.centerx, self.rect_sabotagem.centery, CIANO, 16)
                self._anunciar("PULSO EMP ATIVO! DEFESAS CONGELADAS!")
            self.timer_sabotagem = TEMPO_CONGELAMENTO_SABOTAGEM
        elif self.timer_sabotagem > 0.0:
            self.timer_sabotagem = max(0.0, self.timer_sabotagem - dt)
        self.sabotagem_pisada = pisando_totem

        # 3. Portais Gêmeos de Dobra (Teleporte bidirecional)
        for rect_a, rect_b in self.pares_portais:
            for j in vivos:
                if j.cooldown_teleporte > 0.0:
                    continue
                if j.rect.colliderect(rect_a):
                    j.x = rect_b.x
                    j.y = rect_b.y
                    j.cooldown_teleporte = 0.85
                    assets.som_teleporte.play()
                    if sparks is not None:
                        sparks.emitir(rect_a.centerx, rect_a.centery, VIOLETA, 10)
                        sparks.emitir(rect_b.centerx, rect_b.centery, CIANO, 14)
                elif j.rect.colliderect(rect_b):
                    j.x = rect_a.x
                    j.y = rect_a.y
                    j.cooldown_teleporte = 0.85
                    assets.som_teleporte.play()
                    if sparks is not None:
                        sparks.emitir(rect_b.centerx, rect_b.centery, VIOLETA, 10)
                        sparks.emitir(rect_a.centerx, rect_a.centery, CIANO, 14)

        # 4. Esteiras Turbo
        for rt in self.rects_turbo:
            for j in vivos:
                if j.rect.colliderect(rt):
                    if j.timer_turbo <= 0.35 and self._recarga_som_turbo <= 0.0:
                        assets.som_turbo.play()
                        self._recarga_som_turbo = 0.35
                        if sparks is not None:
                            sparks.emitir(rt.centerx, rt.centery, LARANJA, 10)
                    j.timer_turbo = DURACAO_TURBO

        # 5. Núcleo de Energia Instável (Relay Cooperativo "Batata Quente")
        if self.tem_nucleo and not self.nucleo_entregue:
            if self.portador_nucleo is not None:
                portador = next((j for j in jogadores_ativos if j.indice == self.portador_nucleo), None)
                if portador is None or portador.em_capsula_reviver or portador.extraido_no_portal:
                    self.resetar_nucleo_para_origem(jogadores_ativos)
                    self._anunciar("NUCLEO CAIU E VOLTOU AO PEDESTAL!", 2.2)
                else:
                    self.nucleo_pos = [float(portador.x), float(portador.y)]
                    # Em Co-op 2P/3P, o núcleo esquenta e incentiva passes entre amigos!
                    if self.num_jogadores > 1:
                        self.calor_nucleo -= dt
                        if self.calor_nucleo <= 0.0:
                            assets.som_dano.play()
                            if sparks is not None:
                                sparks.emitir(portador.rect.centerx, portador.rect.centery, VERMELHO, 18)
                            self.resetar_nucleo_para_origem(jogadores_ativos)
                            self._anunciar("SOBRECARGA! PASSE O NUCLEO AO PARCEIRO!", 2.6)
                        elif self._cooldown_passe_nucleo <= 0.0:
                            for aliado in vivos:
                                if aliado.indice != portador.indice and portador.rect.inflate(6, 6).colliderect(aliado.rect):
                                    portador.carregando_nucleo = False
                                    aliado.carregando_nucleo = True
                                    self.portador_nucleo = aliado.indice
                                    self.calor_nucleo = TEMPO_CALOR_NUCLEO_COOP
                                    self._cooldown_passe_nucleo = 0.75
                                    portador.timer_turbo = 1.8
                                    aliado.timer_turbo = 2.2
                                    assets.som_nucleo_pegar.play()
                                    if sparks is not None:
                                        sparks.emitir(aliado.rect.centerx, aliado.rect.centery, ROSA_NUCLEO, 16)
                                    self.registrar_combo(f"PASSE DE NUCLEO P{aliado.indice + 1}!", bonus_seg=2)
                                    break

                    # Checa entrega no Soquete do Reator!
                    if self.portador_nucleo is not None and portador.rect.colliderect(self.rect_soquete):
                        portador.carregando_nucleo = False
                        self.portador_nucleo = None
                        self.nucleo_entregue = True
                        estava_portal = self.portal_destrancado
                        assets.som_nucleo_encaixar.play()
                        if sparks is not None:
                            sparks.emitir(self.rect_soquete.centerx, self.rect_soquete.centery, VERDE_LIMAO, 24, 130.0)
                        self.registrar_combo("REATOR ENERGIZADO!", bonus_seg=3)
                        if estava_portal:
                            assets.som_portal_aberto.play()
                            self._anunciar("REATOR ATIVO! PORTAL ANCESTRAL ABERTO!", 2.8)
            else:
                rect_n = pygame.Rect(int(self.nucleo_pos[0]), int(self.nucleo_pos[1]), self.tam, self.tam)
                for j in vivos:
                    if j.rect.colliderect(rect_n):
                        self.portador_nucleo = j.indice
                        j.carregando_nucleo = True
                        self.calor_nucleo = TEMPO_CALOR_NUCLEO_COOP
                        self._cooldown_passe_nucleo = 0.65
                        assets.som_nucleo_pegar.play()
                        if sparks is not None:
                            sparks.emitir(rect_n.centerx, rect_n.centery, ROSA_NUCLEO, 14)
                        dica_n = (
                            "LEVE O NUCLEO AO REATOR CENTRAL!"
                            if self.num_jogadores == 1
                            else "LEVE AO REATOR! ENCOSTE NO AMIGO P/ PASSAR!"
                        )
                        self._anunciar(dica_n, 2.8)
                        break

        # 6. Pilares de Sobrecarga do Boss (Fase 8)
        if self.pilares_rects and not self.boss_derrotado:
            if any(self.pilares_ativos):
                self.timer_janela_pilares -= dt
                if self.timer_janela_pilares <= 0.0:
                    self.pilares_ativos = [False] * len(self.pilares_rects)
                    self._anunciar("TEMPO ESGOTADO! ATIVEM OS PILARES RAPIDO!", 2.2)

            janela_max = JANELA_PILARES_BOSS_SOLO if self.num_jogadores == 1 else JANELA_PILARES_BOSS_COOP
            for idx_p, rp in enumerate(self.pilares_rects):
                if self.pilares_ativos[idx_p]:
                    continue
                if any(j.rect.colliderect(rp) for j in vivos):
                    if not any(self.pilares_ativos):
                        self.timer_janela_pilares = janela_max
                    self.pilares_ativos[idx_p] = True
                    assets.som_placa.play()
                    if sparks is not None:
                        sparks.emitir(rp.centerx, rp.centery, DOURADO, 14)
                    faltam_p = sum(1 for a in self.pilares_ativos if not a)
                    if faltam_p > 0:
                        self._anunciar(
                            f"PILAR ATIVO! FALTAM {faltam_p} ({self.timer_janela_pilares:.1f}s)!",
                            2.0,
                        )

            if all(self.pilares_ativos):
                self.pilares_ativos = [False] * len(self.pilares_rects)
                self.timer_janela_pilares = 0.0
                quebrou_escudo_boss = True

        # 7. Cristais Rúnicos Sintonizados
        estava_portal_aberto = self.portal_destrancado
        for c in self.cristais:
            if c["coletado"]:
                continue
            for j in vivos:
                if j.rect.colliderect(c["rect"]):
                    if c["dono"] is None or c["dono"] == j.indice:
                        c["coletado"] = True
                        if sparks is not None:
                            cor_sp = DOURADO if c["dono"] is None else CORES_JOGADORES[c["dono"] % 3]
                            sparks.emitir(c["rect"].centerx, c["rect"].centery, cor_sp, 16)
                        self.registrar_combo("CRISTAL RUNICO!", bonus_seg=1)
                        if self.portal_destrancado and not estava_portal_aberto:
                            assets.som_portal_aberto.play()
                            self._anunciar("PORTAL ANCESTRAL ABERTO! AVANCEM!", 2.8)
                        else:
                            assets.som_cristal.play()
                        break
                    elif self.timer_mensagem <= 0.2:
                        dono_txt = f"P{c['dono'] + 1}"
                        self._anunciar(f"CRISTAL SINTONIZADO COM {dono_txt}!", 1.4)

        return quebrou_escudo_boss

    def desenhar_elementos_piso(self, janela: pygame.Surface, t: float) -> None:
        """Desenha portais gêmeos, esteiras turbo, placas, alavanca, totem EMP, núcleo, pilares e cristais."""
        # 1. Portais Gêmeos de Dobra
        cores_par = [VIOLETA, CIANO]
        for idx_par, (ra, rb) in enumerate(self.pares_portais):
            cor_p = cores_par[idx_par % len(cores_par)]
            pulso = int(2 * math.sin(t * 7.5 + idx_par))
            for rp in (ra, rb):
                pygame.draw.circle(janela, (26, 20, 44), rp.center, rp.w // 2 + 2)
                pygame.draw.circle(janela, cor_p, rp.center, max(4, rp.w // 2 + pulso), 2)
                pygame.draw.circle(janela, BRANCO, rp.center, 3)

        # 2. Esteiras Turbo (chevrons luminosos)
        for rt in self.rects_turbo:
            pygame.draw.rect(janela, (48, 28, 16), rt, border_radius=3)
            pygame.draw.rect(janela, LARANJA, rt, width=1, border_radius=3)
            desl = int((t * 18.0) % 6) - 2
            cx, cy = rt.centerx, rt.centery
            pygame.draw.polygon(
                janela,
                AMARELO,
                [(cx - 4, cy + 2 - desl // 2), (cx, cy - 4 - desl // 2), (cx + 4, cy + 2 - desl // 2)],
            )

        # 3. Fio rúnico ligando placas ao portão
        if not self.alavanca_acionada:
            for i, pr in enumerate(self.placas_rects):
                if self.placas_ativas[i]:
                    pygame.draw.line(janela, (40, 175, 195), pr.center, self.rect_portao.center, 1)

        # 4. Placas de Pressão
        for i, pr in enumerate(self.placas_rects):
            ativa = self.placas_ativas[i] or self.alavanca_acionada
            cor_borda = VERDE_LIMAO if ativa else AMARELO
            cor_miolo = (26, 150, 110) if ativa else (92, 76, 28)
            pygame.draw.rect(janela, (30, 32, 38), pr.inflate(4, 4), border_radius=3)
            pygame.draw.rect(janela, cor_miolo, pr, border_radius=3)
            pygame.draw.rect(janela, cor_borda, pr, width=2, border_radius=3)
            pygame.draw.circle(janela, BRANCO if ativa else DOURADO, pr.center, 2)

        # 5. Alavanca Permanente
        ar = self.rect_alavanca
        pygame.draw.rect(janela, (44, 42, 52), (ar.x, ar.centery, ar.w, ar.h // 2 + 2), border_radius=2)
        haste_x = ar.right - 2 if self.alavanca_acionada else ar.left + 2
        cor_alav = VERDE_LIMAO if self.alavanca_acionada else VERMELHO
        pygame.draw.line(janela, BRANCO, (ar.centerx, ar.centery + 2), (haste_x, ar.top + 2), 3)
        pygame.draw.circle(janela, cor_alav, (haste_x, ar.top + 2), 4)

        # 6. Totem Sabotador EMP
        sr = self.rect_sabotagem
        ativo_emp = self.canhoes_congelados
        cor_emp = CIANO if ativo_emp else (88, 134, 180)
        pygame.draw.circle(janela, (28, 36, 52), sr.center, sr.w // 2 + 2)
        pygame.draw.circle(janela, cor_emp, sr.center, sr.w // 2, 2)
        raio_pulso = 4 if int(t * 10) % 2 == 0 and ativo_emp else 3
        pygame.draw.circle(janela, BRANCO if ativo_emp else CIANO, sr.center, raio_pulso)

        # 7. Soquete do Reator + Núcleo de Energia Instável
        if self.tem_nucleo:
            soq = self.rect_soquete
            cor_soq = VERDE_LIMAO if self.nucleo_entregue else ROSA_NUCLEO
            pygame.draw.rect(janela, (24, 28, 40), soq.inflate(4, 4), border_radius=4)
            pygame.draw.rect(janela, cor_soq, soq, width=2, border_radius=4)
            pygame.draw.circle(janela, VERDE_LIMAO if self.nucleo_entregue else (90, 40, 80), soq.center, 4)

            if not self.nucleo_entregue and self.portador_nucleo is None:
                nx = int(self.nucleo_pos[0]) + self.tam // 2
                ny = int(self.nucleo_pos[1]) + self.tam // 2 + int(2 * math.sin(t * 6.0))
                pygame.draw.circle(janela, ROSA_NUCLEO, (nx, ny), 7)
                pygame.draw.circle(janela, BRANCO, (nx, ny), 4)

        # 8. Pilares de Sobrecarga do Boss
        for idx_p, rp in enumerate(self.pilares_rects):
            ligado = self.pilares_ativos[idx_p] or self.boss_derrotado
            cor_pil = VERDE_LIMAO if ligado else DOURADO
            pygame.draw.rect(janela, (36, 28, 48), rp.inflate(4, 4), border_radius=4)
            pygame.draw.rect(janela, cor_pil, rp, width=2, border_radius=4)
            pygame.draw.circle(janela, BRANCO if ligado else VERMELHO, rp.center, 4 if ligado else 3)

        # 9. Portão de Energia Ancestral
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
            pygame.draw.rect(janela, (24, 96, 78), gr, width=1, border_radius=2)

        # 10. Cristais Rúnicos flutuantes
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
        """Desenha o Altar / Portal Ancestral (selado enquanto faltam objetivos, vórtice ativo quando aberto)."""
        cx = pos_portal[0] + tamanho // 2
        cy = pos_portal[1] + tamanho // 2
        raio = max(8, tamanho // 2 + 3)

        pygame.draw.circle(janela, (52, 58, 74), (cx, cy), raio + 2)

        if not self.portal_destrancado:
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


ROSA_NUCLEO = (255, 92, 214)

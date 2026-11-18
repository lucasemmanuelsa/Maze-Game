"""Motor principal (Game Engine) de 8 fases para 1-3 jogadores com Dash, Drones, Núcleo Co-op e Boss."""
from __future__ import annotations
import random
import pygame

from game.assets import AssetManager
from game.collision import WallCollisionMap
from game.config import (
    ALTURA_JANELA,
    CIANO,
    DOURADO,
    FPS,
    LARGURA_JANELA,
    PRETO,
    TITULO_JOGO,
    VERDE_LIMAO,
    VERMELHO,
    VIDAS_INICIAIS,
    VIOLETA,
)
from game.database import ScoreDatabase
from game.entities import BossCore, Cannon, PatrolDrone, Player
from game.levels import LEVELS, LevelConfig
from game.puzzles import LevelPuzzleManager
from game.ui import (
    aguardar_com_eventos,
    desenhar_hud,
    exibir_game_over,
    exibir_intro,
    exibir_menu,
    exibir_ranking,
    exibir_splash_nivel,
)
from game.visuals import (
    AmbientParticles,
    SparkSystem,
    desenhar_moldura_cenario,
    renderizar_cenario_labirinto,
)


class MazeGame:
    """Controlador principal do jogo Maze and Cannons (1 a 3 jogadores locais, 8 fases)."""

    def __init__(self, levels: list[LevelConfig] | None = None) -> None:
        pygame.init()
        pygame.joystick.init()
        self.janela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        self.buffer_cena = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(TITULO_JOGO)

        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        pygame.display.set_icon(self.assets.icone)

        self.db = ScoreDatabase()
        self.levels = levels if levels is not None else LEVELS

        self.joysticks: list[pygame.joystick.Joystick] = []
        for idx in range(pygame.joystick.get_count()):
            js = pygame.joystick.Joystick(idx)
            js.init()
            self.joysticks.append(js)

        self._mapas_cache: dict[int, tuple[pygame.Surface, WallCollisionMap]] = {}
        for lvl in self.levels:
            superficie_bruta = self.assets.carregar_imagem(lvl.arquivo_mapa, escala=lvl.escala_mapa)
            colisao = WallCollisionMap(superficie_bruta, lvl.posicao_mapa)
            superficie_cenario = renderizar_cenario_labirinto(colisao, lvl.bioma, seed=lvl.numero)
            self._mapas_cache[lvl.numero] = (superficie_cenario, colisao)

    def executar(
        self,
        nivel_inicial: int = 1,
        pular_menu: bool = False,
        num_jogadores: int = 1,
    ) -> None:
        """Executa o fluxo completo: Intro -> Menu (1-3P) -> Fases 1..8 -> Banco/Ranking."""
        num_jogadores = max(1, min(3, num_jogadores))

        if pular_menu:
            nome_jogador = f"{num_jogadores}P" if num_jogadores > 1 else "TST"
        else:
            self.assets.tocar_musica("enter.mp3", volume=0.09, loop=-1)

            if not exibir_intro(self.janela, self.assets):
                pygame.quit()
                return

            nome_escolhido, num_jogadores = exibir_menu(
                self.janela, self.assets, jogadores_iniciais=num_jogadores
            )
            if nome_escolhido is None:
                pygame.quit()
                return
            nome_jogador = nome_escolhido

        vidas = VIDAS_INICIAIS + (num_jogadores - 1)
        pontuacao_total = 0
        fases_para_jogar = [lvl for lvl in self.levels if lvl.numero >= nivel_inicial]

        for config_fase in fases_para_jogar:
            concluiu, tempo_fase, vidas = self._jogar_fase(config_fase, vidas, num_jogadores)
            if not concluiu:
                pygame.quit()
                return
            pontuacao_total += tempo_fase

        self.assets.parar_ambiente()
        if nivel_inicial == 1 and not pular_menu:
            self.db.salvar_pontuacao(pontuacao_total, nome_jogador)

        top_10 = self.db.obter_top_10()
        exibir_ranking(self.janela, self.assets, top_10, self.clock)
        pygame.quit()

    def _criar_jogadores(self, lvl: LevelConfig, num_jogadores: int) -> list[Player]:
        jogadores: list[Player] = []
        for idx in range(num_jogadores):
            pos = lvl.spawn_jogador if num_jogadores == 1 else lvl.spawns_multi[idx % len(lvl.spawns_multi)]
            js = self.joysticks[idx] if idx < len(self.joysticks) else None
            jogadores.append(
                Player(
                    indice=idx,
                    num_jogadores_total=num_jogadores,
                    spawn_pos=pos,
                    tamanho_desenho=lvl.tamanho_entidade,
                    tamanho_colisao=lvl.tamanho_colisao_parede,
                    velocidade=lvl.velocidade_jogador,
                    joystick=js,
                )
            )
        return jogadores

    def _jogar_fase(
        self,
        lvl: LevelConfig,
        vidas: int,
        num_jogadores: int,
    ) -> tuple[bool, int, int]:
        """Executa o loop frenético de uma fase para 1, 2 ou 3 jogadores locais."""
        if not exibir_splash_nivel(
            self.janela,
            self.assets,
            lvl.arquivo_splash,
            lvl.arquivo_musica,
            lvl.arquivo_ambiente,
            lvl.bioma,
            num_jogadores,
            lvl.duracao_splash,
        ):
            return False, 0, vidas

        superficie_cenario, colisao_paredes = self._mapas_cache[lvl.numero]
        particulas = AmbientParticles(lvl.bioma)
        sparks = SparkSystem()
        jogadores = self._criar_jogadores(lvl, num_jogadores)
        puzzles = LevelPuzzleManager(lvl.puzzle, num_jogadores, lvl.tamanho_entidade)

        canhoes = [
            Cannon(spec, self.assets.sprite_canhao(spec.direcao))
            for spec in lvl.canhoes
        ]
        drones = [PatrolDrone(dspec) for dspec in lvl.drones]
        boss = BossCore() if lvl.tem_boss else None

        indice_waypoint = 0
        chegada_pos = lvl.waypoints_chegada[indice_waypoint]
        fonte_tag = pygame.font.SysFont("monospace", 10, bold=True)
        cooldown_esquiva_dash = [0.0] * num_jogadores
        timer_shake = 0.0

        if lvl.tocar_tiro_inicial:
            self.assets.som_tiro.play()

        ticks_inicio = pygame.time.get_ticks()

        while True:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            tempo_decorrido = (pygame.time.get_ticks() - ticks_inicio) / 1000.0
            tempo_bruto = int(tempo_decorrido)
            tempo_efetivo = max(1, tempo_bruto - puzzles.bonus_segundos)
            if timer_shake > 0.0:
                timer_shake = max(0.0, timer_shake - dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False, tempo_efetivo, vidas

            teclas = pygame.key.get_pressed()
            portao_bloqueado = puzzles.retangulo_bloqueio_portao()

            # 1. Comandos, Dash de Fase e atualização dos Orbes Guardiões
            for idx_j, j in enumerate(jogadores):
                if cooldown_esquiva_dash[idx_j] > 0.0:
                    cooldown_esquiva_dash[idx_j] = max(0.0, cooldown_esquiva_dash[idx_j] - dt)

                iniciou_dash = j.ler_comandos(teclas)
                if iniciou_dash:
                    self.assets.som_dash.play()
                    sparks.emitir(j.rect.centerx, j.rect.centery, CIANO, 10, 85.0)

                expirou_capsula = j.atualizar(dt, colisao_paredes, portao_bloqueado)
                if expirou_capsula:
                    vidas -= 1
                    if vidas <= 0:
                        exibir_game_over(self.janela, self.assets)
                        return False, tempo_efetivo, 0
                    j.reposicionar_no_spawn()

                # Se estiver em Dash de Fase: atravessa tiros ganhando Combo e atordoa Drones!
                if j.em_dash:
                    for dr in drones:
                        if j.rect.colliderect(dr.rect) and dr.atordoar(3.2):
                            self.assets.som_sabotagem.play()
                            sparks.emitir(dr.rect.centerx, dr.rect.centery, CIANO, 16, 110.0)
                            puzzles.registrar_combo("DRONE ATORDOADO!", bonus_seg=2)
                    if cooldown_esquiva_dash[idx_j] <= 0.0:
                        atravessou_tiro = any(j.rect.colliderect(c.rect_bala) for c in canhoes) or (
                            boss is not None
                            and not boss.derrotado
                            and any(
                                j.rect.colliderect(pygame.Rect(int(p[0]) - 4, int(p[1]) - 4, 8, 8))
                                for p in boss.projeteis
                            )
                        )
                        if atravessou_tiro:
                            cooldown_esquiva_dash[idx_j] = 1.6
                            sparks.emitir(j.rect.centerx, j.rect.centery, DOURADO, 12, 95.0)
                            puzzles.registrar_combo("DASH FANTASMA!", bonus_seg=1)

            # 2. Resgate cooperativo sem perder vidas (+ Combo de Equipe!)
            if num_jogadores > 1:
                vivos = [j for j in jogadores if not j.em_capsula_reviver and not j.extraido_no_portal]
                em_capsula = [j for j in jogadores if j.em_capsula_reviver]
                for caido in em_capsula:
                    if any(salvador.rect.colliderect(caido.rect.inflate(6, 6)) for salvador in vivos):
                        caido.reviver_no_local()
                        self.assets.som_reviver.play()
                        sparks.emitir(caido.rect.centerx, caido.rect.centery, VERDE_LIMAO, 18, 100.0)
                        puzzles.registrar_combo(f"P{caido.indice + 1} SALVO!", bonus_seg=2)

            # 3. Atualização de Puzzles, Canhões, Drones e Boss
            quebrou_escudo = puzzles.atualizar(jogadores, dt, self.assets, sparks=sparks)
            congelado_emp = puzzles.canhoes_congelados

            for canhao in canhoes:
                canhao.atualizar(tempo_decorrido, self.assets.som_tiro, congelado=congelado_emp)
            for dr in drones:
                dr.atualizar(dt, congelado=congelado_emp)
            if boss is not None:
                if quebrou_escudo:
                    derrotou = boss.quebrar_escudo()
                    if derrotou:
                        puzzles.boss_derrotado = True
                        timer_shake = 0.85
                        self.assets.som_boss_explosao.play()
                        sparks.emitir(boss.cx, boss.cy, DOURADO, 32, 165.0)
                        sparks.emitir(boss.cx, boss.cy, VIOLETA, 24, 130.0)
                        puzzles.registrar_combo("OLHO PRIMORDIAL DESTRUIDO!!", bonus_seg=5)
                        if puzzles.portal_destrancado:
                            self.assets.som_portal_aberto.play()
                    else:
                        timer_shake = 0.42
                        self.assets.som_boss_escudo.play()
                        sparks.emitir(boss.cx, boss.cy, VIOLETA, 22, 135.0)
                        puzzles.registrar_combo(
                            f"ESCUDO QUEBRADO! FALTAM {boss.escudos_restantes}!",
                            bonus_seg=3,
                        )
                boss.atualizar(dt, self.assets.som_tiro, congelado=congelado_emp)

            # 4. Colisão com perigos (Canhões, Drones ativos e Boss)
            for j in jogadores:
                if not j.pode_levar_dano:
                    continue
                bateu_canhao = any(j.rect.colliderect(c.rect_bala) for c in canhoes)
                bateu_drone = any(dr.ativo_dano and j.rect.colliderect(dr.rect) for dr in drones)
                bateu_boss = boss is not None and boss.colide_com_jogador(j.rect)

                if bateu_canhao or bateu_drone or bateu_boss:
                    self.assets.som_dano.play()
                    timer_shake = max(timer_shake, 0.25)
                    sparks.emitir(j.rect.centerx, j.rect.centery, VERMELHO, 16, 110.0)
                    puzzles.combo = 0

                    outros_em_campo = [
                        o for o in jogadores
                        if o is not j and not o.em_capsula_reviver and not o.extraido_no_portal
                    ]
                    if num_jogadores > 1 and len(outros_em_campo) > 0:
                        j.entrar_em_capsula()
                        puzzles._anunciar(f"P{j.indice + 1} CAIU! TOQUE NELE EM 5s PARA SALVAR!")
                    else:
                        vidas -= 1
                        if puzzles.tem_nucleo and not puzzles.nucleo_entregue:
                            puzzles.resetar_nucleo_para_origem(jogadores)
                        if vidas <= 0:
                            exibir_game_over(self.janela, self.assets)
                            return False, tempo_efetivo, 0
                        if num_jogadores == 1:
                            if not aguardar_com_eventos(0.65):
                                return False, tempo_efetivo, vidas
                            j.reposicionar_no_spawn()
                        else:
                            for m in jogadores:
                                if not m.extraido_no_portal:
                                    m.reposicionar_no_spawn()

            # 5. Checagem do Altar / Portal Ancestral
            rect_portal = pygame.Rect(
                chegada_pos[0], chegada_pos[1], lvl.tamanho_entidade + 2, lvl.tamanho_entidade + 2
            ).inflate(4, 4)

            if puzzles.portal_destrancado:
                tem_proximo_waypoint = indice_waypoint + 1 < len(lvl.waypoints_chegada)
                for j in jogadores:
                    if j.em_capsula_reviver or j.extraido_no_portal:
                        continue
                    if j.rect.colliderect(rect_portal):
                        self.assets.som_chegada.play()
                        sparks.emitir(rect_portal.centerx, rect_portal.centery, CIANO, 20, 120.0)
                        if tem_proximo_waypoint:
                            for membro in jogadores:
                                membro.definir_spawn(chegada_pos)
                                if membro.em_capsula_reviver:
                                    membro.reviver_no_local()
                            indice_waypoint += 1
                            chegada_pos = lvl.waypoints_chegada[indice_waypoint]
                            puzzles.registrar_combo("CHECKPOINT DA EQUIPE!", bonus_seg=2)
                            break
                        else:
                            j.extraido_no_portal = True
                            restantes = sum(1 for m in jogadores if not m.extraido_no_portal)
                            if restantes > 0:
                                puzzles._anunciar(f"P{j.indice + 1} ENTROU NO PORTAL! FALTAM {restantes}!")
                            else:
                                tempo_final = max(1, int(tempo_decorrido) - puzzles.bonus_segundos)
                                return True, tempo_final, vidas

            # 6. Renderização completa (com suporte a Screen Shake cinematográfico!)
            alvo = self.buffer_cena if timer_shake > 0.0 else self.janela
            alvo.fill(PRETO)
            alvo.blit(superficie_cenario, (0, 0))

            puzzles.desenhar_elementos_piso(alvo, tempo_decorrido)
            if boss is None or boss.derrotado:
                puzzles.desenhar_portal(
                    alvo,
                    chegada_pos,
                    lvl.tamanho_entidade,
                    tempo_decorrido,
                    eh_checkpoint_intermediario=(indice_waypoint + 1 < len(lvl.waypoints_chegada)),
                )

            if boss is not None:
                boss.desenhar(alvo, tempo_decorrido)
                if boss.derrotado:
                    puzzles.desenhar_portal(alvo, chegada_pos, lvl.tamanho_entidade, tempo_decorrido)

            for dr in drones:
                dr.desenhar(alvo, tempo_decorrido)

            for j in jogadores:
                j.desenhar(alvo, tempo_decorrido, fonte_tag=fonte_tag)

            for canhao in canhoes:
                canhao.desenhar_bala(alvo, tempo_decorrido)

            sparks.atualizar_e_desenhar(alvo, dt)
            particulas.atualizar_e_desenhar(alvo, tempo_decorrido)
            desenhar_moldura_cenario(alvo, lvl.bioma)

            for canhao in canhoes:
                canhao.desenhar_canhao(alvo)

            desenhar_hud(
                alvo,
                self.assets,
                vidas,
                tempo_efetivo,
                puzzles,
                num_jogadores,
                boss=boss,
            )

            if timer_shake > 0.0:
                self.janela.fill(PRETO)
                ox = random.randint(-3, 3)
                oy = random.randint(-3, 3)
                self.janela.blit(self.buffer_cena, (ox, oy))

            pygame.display.flip()

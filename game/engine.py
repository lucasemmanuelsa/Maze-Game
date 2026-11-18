"""Motor principal (Game Engine) para 1 a 3 jogadores locais com puzzles cooperativos e cenários 2.5D."""
from __future__ import annotations
import pygame

from game.assets import AssetManager
from game.collision import WallCollisionMap
from game.config import (
    ALTURA_JANELA,
    FPS,
    LARGURA_JANELA,
    PRETO,
    TITULO_JOGO,
    VIDAS_INICIAIS,
)
from game.database import ScoreDatabase
from game.entities import Cannon, Player
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
    desenhar_moldura_cenario,
    renderizar_cenario_labirinto,
)


class MazeGame:
    """Controlador principal do jogo Maze and Cannons (1 a 3 jogadores locais)."""

    def __init__(self, levels: list[LevelConfig] | None = None) -> None:
        pygame.init()
        pygame.joystick.init()
        self.janela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(TITULO_JOGO)

        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        pygame.display.set_icon(self.assets.icone)

        self.db = ScoreDatabase()
        self.levels = levels if levels is not None else LEVELS

        # Detecta gamepads locais conectados (se houver)
        self.joysticks: list[pygame.joystick.Joystick] = []
        for idx in range(pygame.joystick.get_count()):
            js = pygame.joystick.Joystick(idx)
            js.init()
            self.joysticks.append(js)

        # Pré-carrega colisões e renderiza os cenários detalhados (muros de pedra + vinhas + piso)
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
        """Executa o fluxo completo: Intro -> Menu (1-3P) -> Fases -> Banco/Ranking."""
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

        vidas = VIDAS_INICIAIS + (num_jogadores - 1)  # +1 vida extra por aliado na equipe
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
        """Executa o loop de uma fase para 1, 2 ou 3 jogadores locais."""
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
        jogadores = self._criar_jogadores(lvl, num_jogadores)
        puzzles = LevelPuzzleManager(lvl.puzzle, num_jogadores, lvl.tamanho_entidade)

        canhoes = [
            Cannon(spec, self.assets.sprite_canhao(spec.direcao))
            for spec in lvl.canhoes
        ]

        indice_waypoint = 0
        chegada_pos = lvl.waypoints_chegada[indice_waypoint]
        fonte_tag = pygame.font.SysFont("monospace", 10, bold=True)

        if lvl.tocar_tiro_inicial:
            self.assets.som_tiro.play()

        ticks_inicio = pygame.time.get_ticks()

        while True:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            tempo_decorrido = (pygame.time.get_ticks() - ticks_inicio) / 1000.0
            tempo_mapa = int(tempo_decorrido)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False, tempo_mapa, vidas

            teclas = pygame.key.get_pressed()
            portao_bloqueado = puzzles.retangulo_bloqueio_portao()

            # 1. Movimentação dos Orbes Guardiões e expiração de cápsulas de resgate
            for j in jogadores:
                j.ler_comandos(teclas)
                expirou_capsula = j.atualizar(dt, colisao_paredes, portao_bloqueado)
                if expirou_capsula:
                    vidas -= 1
                    if vidas <= 0:
                        exibir_game_over(self.janela, self.assets)
                        return False, tempo_mapa, 0
                    j.reposicionar_no_spawn()

            # 2. Resgate cooperativo: um aliado vivo encostando na cápsula salva sem perder vida!
            if num_jogadores > 1:
                vivos = [j for j in jogadores if not j.em_capsula_reviver and not j.extraido_no_portal]
                em_capsula = [j for j in jogadores if j.em_capsula_reviver]
                for caido in em_capsula:
                    if any(salvador.rect.colliderect(caido.rect.inflate(6, 6)) for salvador in vivos):
                        caido.reviver_no_local()
                        self.assets.som_reviver.play()
                        puzzles._anunciar(f"P{caido.indice + 1} RESGATADO SEM PERDER VIDA!")

            # 3. Atualização dos puzzles cooperativos e dos canhões
            puzzles.atualizar(jogadores, dt, self.assets)
            for canhao in canhoes:
                canhao.atualizar(
                    tempo_decorrido,
                    self.assets.som_tiro,
                    congelado=puzzles.canhoes_congelados,
                )

            # 4. Colisão com esferas de plasma dos canhões
            for j in jogadores:
                if not j.pode_levar_dano:
                    continue
                if any(j.rect.colliderect(c.rect_bala) for c in canhoes):
                    self.assets.som_dano.play()
                    outros_em_campo = [
                        o for o in jogadores
                        if o is not j and not o.em_capsula_reviver and not o.extraido_no_portal
                    ]
                    if num_jogadores > 1 and len(outros_em_campo) > 0:
                        j.entrar_em_capsula()
                        puzzles._anunciar(f"P{j.indice + 1} CAIU! TOQUE NELE EM 5s PARA SALVAR!")
                    else:
                        # Modo solo ou último sobrevivente da equipe atingido
                        vidas -= 1
                        if vidas <= 0:
                            exibir_game_over(self.janela, self.assets)
                            return False, tempo_mapa, 0
                        if num_jogadores == 1:
                            if not aguardar_com_eventos(0.75):
                                return False, tempo_mapa, vidas
                            j.reposicionar_no_spawn()
                        else:
                            for m in jogadores:
                                if not m.extraido_no_portal:
                                    m.reposicionar_no_spawn()

            # 5. Checagem do Altar / Portal Ancestral (somente destrancado após coletar os cristais!)
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
                        if tem_proximo_waypoint:
                            # Altar intermediário (fases de ida e volta): atualiza checkpoint de todo o grupo!
                            for membro in jogadores:
                                membro.definir_spawn(chegada_pos)
                                if membro.em_capsula_reviver:
                                    membro.reviver_no_local()
                            indice_waypoint += 1
                            chegada_pos = lvl.waypoints_chegada[indice_waypoint]
                            puzzles._anunciar("CHECKPOINT DA EQUIPE ATIVADO! RETORNEM AO PORTAL!")
                            break
                        else:
                            j.extraido_no_portal = True
                            restantes = sum(1 for m in jogadores if not m.extraido_no_portal)
                            if restantes > 0:
                                puzzles._anunciar(f"P{j.indice + 1} ENTROU NO PORTAL! FALTAM {restantes}!")
                            else:
                                return True, tempo_mapa, vidas

            # 6. Renderização completa do cenário, puzzles, partículas, canhões e HUD
            self.janela.fill(PRETO)
            self.janela.blit(superficie_cenario, (0, 0))

            puzzles.desenhar_elementos_piso(self.janela, tempo_decorrido)
            puzzles.desenhar_portal(
                self.janela,
                chegada_pos,
                lvl.tamanho_entidade,
                tempo_decorrido,
                eh_checkpoint_intermediario=(indice_waypoint + 1 < len(lvl.waypoints_chegada)),
            )

            for j in jogadores:
                j.desenhar(self.janela, tempo_decorrido, fonte_tag=fonte_tag)

            for canhao in canhoes:
                canhao.desenhar_bala(self.janela, tempo_decorrido)

            particulas.atualizar_e_desenhar(self.janela, tempo_decorrido)
            desenhar_moldura_cenario(self.janela, lvl.bioma)

            for canhao in canhoes:
                canhao.desenhar_canhao(self.janela)

            desenhar_hud(self.janela, self.assets, vidas, tempo_mapa, puzzles, num_jogadores)

            pygame.display.flip()

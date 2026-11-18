"""Motor principal (Game Engine) que coordena o fluxo de telas e a execução das fases."""
import pygame

from game.assets import AssetManager
from game.collision import WallCollisionMap
from game.config import (
    ALTURA_JANELA,
    AZUL,
    FPS,
    LARGURA_JANELA,
    PRETO,
    TITULO_JOGO,
    VIDAS_INICIAIS,
)
from game.database import ScoreDatabase
from game.entities import Cannon, Player
from game.levels import LEVELS, LevelConfig
from game.ui import (
    aguardar_com_eventos,
    desenhar_barreiras,
    desenhar_hud,
    exibir_game_over,
    exibir_intro,
    exibir_menu,
    exibir_ranking,
    exibir_splash_nivel,
)


class MazeGame:
    """Controlador principal do jogo Maze and Cannons."""

    def __init__(self, levels: list[LevelConfig] | None = None) -> None:
        pygame.init()
        self.janela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(TITULO_JOGO)

        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        pygame.display.set_icon(self.assets.icone)

        self.db = ScoreDatabase()
        self.levels = levels if levels is not None else LEVELS

        # Pré-carrega os mapas e máscaras de colisão uma única vez de forma silenciosa
        self._mapas_cache: dict[int, tuple[pygame.Surface, WallCollisionMap]] = {}
        for lvl in self.levels:
            superficie_mapa = self.assets.carregar_imagem(lvl.arquivo_mapa, escala=lvl.escala_mapa)
            colisao = WallCollisionMap(superficie_mapa, lvl.posicao_mapa)
            self._mapas_cache[lvl.numero] = (superficie_mapa, colisao)

    def executar(self) -> None:
        """Executa o fluxo completo: Intro -> Menu -> Fases -> Banco/Ranking."""
        self.assets.tocar_musica("enter.mp3", volume=0.08, loop=-1)

        if not exibir_intro(self.janela, self.assets):
            pygame.quit()
            return

        nome_jogador = exibir_menu(self.janela, self.assets)
        if nome_jogador is None:
            pygame.quit()
            return

        vidas = VIDAS_INICIAIS
        pontuacao_total = 0

        for config_fase in self.levels:
            concluiu, tempo_fase, vidas = self._jogar_fase(config_fase, vidas)
            if not concluiu:
                pygame.quit()
                return
            pontuacao_total += tempo_fase

        # Todas as fases concluídas: salva no banco e exibe o High Scores
        self.db.salvar_pontuacao(pontuacao_total, nome_jogador)
        top_10 = self.db.obter_top_10()
        exibir_ranking(self.janela, self.assets, top_10, self.clock)
        pygame.quit()

    def _jogar_fase(
        self,
        lvl: LevelConfig,
        vidas: int,
    ) -> tuple[bool, int, int]:
        """
        Executa o loop de uma fase.
        Retorna (fase_vencida, tempo_gasto_segundos, vidas_restantes).
        """
        if not exibir_splash_nivel(
            self.janela,
            self.assets,
            lvl.arquivo_splash,
            lvl.arquivo_musica,
            lvl.duracao_splash,
        ):
            return False, 0, vidas

        superficie_mapa, colisao_paredes = self._mapas_cache[lvl.numero]

        jogador = Player(
            spawn_pos=lvl.spawn_jogador,
            tamanho_desenho=lvl.tamanho_entidade,
            tamanho_colisao=lvl.tamanho_colisao_parede,
            velocidade=lvl.velocidade_jogador,
        )

        canhoes = [
            Cannon(spec, self.assets.sprite_canhao(spec.direcao))
            for spec in lvl.canhoes
        ]

        indice_waypoint = 0
        chegada_pos = lvl.waypoints_chegada[indice_waypoint]

        if lvl.tocar_tiro_inicial:
            self.assets.som_tiro.play()

        tempo_inicio = int(pygame.time.get_ticks() / 1000)

        while True:
            tempo_mapa = int(pygame.time.get_ticks() / 1000) - tempo_inicio

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False, tempo_mapa, vidas
                jogador.processar_evento(event)

            # Atualização física do jogador e das balas
            jogador.mover(colisao_paredes)
            for canhao in canhoes:
                canhao.atualizar(tempo_mapa, self.assets.som_tiro)

            # Checagem de dano por projétil
            rect_jogador = jogador.rect
            atingido = any(rect_jogador.colliderect(c.rect_bala) for c in canhoes)
            if atingido:
                self.assets.som_dano.play()
                if not aguardar_com_eventos(1.0):
                    return False, tempo_mapa, vidas
                jogador.reposicionar_no_spawn()
                vidas -= 1
                if vidas <= 0:
                    exibir_game_over(self.janela, self.assets)
                    return False, tempo_mapa, 0

            # Checagem de chegada / waypoints
            rect_chegada = pygame.Rect(
                chegada_pos[0], chegada_pos[1], lvl.tamanho_entidade, lvl.tamanho_entidade
            )
            if jogador.rect.colliderect(rect_chegada):
                self.assets.som_chegada.play()
                if indice_waypoint + 1 < len(lvl.waypoints_chegada):
                    # Avança para o próximo objetivo e define checkpoint (ex.: Nível 3)
                    jogador.definir_spawn(chegada_pos)
                    indice_waypoint += 1
                    chegada_pos = lvl.waypoints_chegada[indice_waypoint]
                    rect_chegada = pygame.Rect(
                        chegada_pos[0], chegada_pos[1], lvl.tamanho_entidade, lvl.tamanho_entidade
                    )
                else:
                    return True, tempo_mapa, vidas

            # Renderização do frame
            self.janela.fill(PRETO)
            self.janela.blit(superficie_mapa, lvl.posicao_mapa)
            jogador.desenhar(self.janela)
            pygame.draw.rect(self.janela, AZUL, rect_chegada)

            for canhao in canhoes:
                canhao.desenhar_bala(self.janela)

            desenhar_barreiras(self.janela)

            for canhao in canhoes:
                canhao.desenhar_canhao(self.janela)

            desenhar_hud(self.janela, self.assets, vidas, tempo_mapa)

            pygame.display.flip()
            self.clock.tick(FPS)

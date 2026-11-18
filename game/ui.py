"""Componentes de interface, seletor local de 1-3 jogadores, HUD cooperativo, telas e ranking."""
import time
import pygame

from game.assets import AssetManager
from game.config import (
    ALTURA_JANELA,
    AMARELO,
    AZUL,
    BRANCO,
    CIANO,
    CORES_JOGADORES,
    CORES_RANKING,
    DOURADO,
    LABELS_RANKING,
    LARGURA_JANELA,
    PRETO,
    VERDE_LIMAO,
    VERMELHO,
)
from game.puzzles import LevelPuzzleManager
from game.visuals import BIOMES, desenhar_orbe_guardiao


class Botao:
    """Botão interativo utilizado na tela de Ranking."""

    def __init__(
        self,
        texto: str,
        largura: int,
        altura: int,
        posicao: tuple[int, int],
        fonte: pygame.font.Font,
    ) -> None:
        self.pressed = False
        self.top_rect = pygame.Rect(posicao, (largura, altura))
        self.top_color = AZUL
        self.bottom_rect = pygame.Rect(posicao, (largura, altura))
        self.bottom_color = "#354B5E"

        self.text_surf = fonte.render(texto, True, BRANCO)
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def desenhar(self, janela: pygame.Surface) -> bool:
        clicado = False
        self.text_rect.center = self.top_rect.center
        self.bottom_rect.midtop = self.top_rect.midtop

        posicao_mouse = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(posicao_mouse):
            self.top_color = VERMELHO
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            elif self.pressed:
                self.pressed = False
                clicado = True
        else:
            self.pressed = False
            self.top_color = AZUL

        pygame.draw.rect(janela, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(janela, self.top_color, self.top_rect, border_radius=15)
        janela.blit(self.text_surf, self.text_rect)
        return clicado


def desenhar_hud(
    janela: pygame.Surface,
    assets: AssetManager,
    vidas: int,
    tempo_mapa: int,
    puzzles: LevelPuzzleManager,
    num_jogadores: int,
) -> None:
    """Desenha o painel inferior com corações, progresso de cristais, status do portão/EMP e tempo."""
    pygame.draw.rect(janela, (14, 16, 22), (0, 488, LARGURA_JANELA, 62))
    pygame.draw.line(janela, (62, 70, 88), (0, 488), (LARGURA_JANELA, 488), 2)

    # 1. Corações da equipe (esquerda, até 4 por linha para não sobrepor o centro)
    for i in range(max(0, vidas)):
        col_i = i % 4
        row_i = i // 4
        janela.blit(assets.coracao, (10 + col_i * 25, 495 + row_i * 24))

    # 2. Indicadores de Cristais e Portão (centro)
    fonte_info = pygame.font.SysFont("monospace", 13, bold=True)
    cor_cristal = VERDE_LIMAO if puzzles.portal_destrancado else DOURADO
    txt_cristal = fonte_info.render(
        f"CRISTAIS {puzzles.cristais_coletados}/{puzzles.total_cristais}",
        True,
        cor_cristal,
    )
    janela.blit(txt_cristal, (164, 496))

    if puzzles.canhoes_congelados:
        status_sub = f"EMP ATIVO ({puzzles.timer_sabotagem:.1f}s)"
        cor_sub = CIANO
    elif puzzles.portao_aberto:
        status_sub = "PORTAO: ABERTO"
        cor_sub = VERDE_LIMAO
    else:
        status_sub = "PORTAO: TRANCADO"
        cor_sub = AMARELO
    txt_portao = fonte_info.render(status_sub, True, cor_sub)
    janela.blit(txt_portao, (164, 514))

    if num_jogadores > 1:
        modo_txt = fonte_info.render(f"CO-OP {num_jogadores}P", True, CIANO)
        janela.blit(modo_txt, (164, 531))

    # 3. Cronômetro (direita)
    cronometro = assets.fonte(46).render(f"Tempo:{tempo_mapa}", True, BRANCO)
    janela.blit(cronometro, (324, 496))

    # 4. Mensagem contextual no topo da tela quando há eventos de puzzle/resgate
    if puzzles.timer_mensagem > 0.0 and puzzles.mensagem_evento:
        fonte_msg = pygame.font.SysFont("monospace", 12, bold=True)
        surf_msg = fonte_msg.render(puzzles.mensagem_evento, True, AMARELO)
        larg = surf_msg.get_width() + 16
        rx = (LARGURA_JANELA - larg) // 2
        pygame.draw.rect(janela, (12, 14, 20), (rx, 1, larg, 16), border_radius=4)
        pygame.draw.rect(janela, DOURADO, (rx, 1, larg, 16), width=1, border_radius=4)
        janela.blit(surf_msg, (rx + 8, 2))


def _processar_eventos_espera() -> tuple[bool, bool]:
    """Retorna (fechou_janela, pediu_pular) durante animações de intro/transição."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True, False
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return False, True
        if event.type == pygame.MOUSEBUTTONDOWN:
            return False, True
    return False, False


def aguardar_com_eventos(segundos: float, permitir_pular: bool = False) -> bool:
    """Aguarda o tempo especificado mantendo a janela responsiva. Retorna False se fechar."""
    passo = 0.04
    decorrido = 0.0
    while decorrido < segundos:
        fechou, pulou = _processar_eventos_espera()
        if fechou:
            return False
        if permitir_pular and pulou:
            return True
        dt = min(passo, segundos - decorrido)
        time.sleep(dt)
        decorrido += dt
    return True


def exibir_intro(janela: pygame.Surface, assets: AssetManager) -> bool:
    """Executa a animação inicial de fade-in/fade-out da logo. Retorna False se fechar."""
    preto_img = assets.carregar_imagem("preto.png", escala=(LARGURA_JANELA, ALTURA_JANELA)).copy()
    logo_img = assets.carregar_imagem("logofinal1.png", converter=True).copy()
    info_img = assets.carregar_imagem("whiletrue.png").copy()

    janela.fill(PRETO)

    for alpha in range(0, 255, 3):
        fechou, pulou = _processar_eventos_espera()
        if fechou:
            return False
        if pulou:
            return True
        pygame.time.delay(16)
        logo_img.set_alpha(alpha)
        janela.blit(logo_img, (0, 0))
        pygame.display.flip()

    for alpha in range(0, 255, 5):
        fechou, pulou = _processar_eventos_espera()
        if fechou:
            return False
        if pulou:
            return True
        pygame.time.delay(5)
        preto_img.set_alpha(alpha)
        janela.blit(preto_img, (0, 0))
        pygame.display.flip()

    for alpha in range(0, 255, 4):
        fechou, pulou = _processar_eventos_espera()
        if fechou:
            return False
        if pulou:
            return True
        pygame.time.delay(18)
        info_img.set_alpha(alpha)
        janela.blit(info_img, (0, 0))
        pygame.display.flip()

    pygame.display.flip()
    pygame.time.delay(80)
    return True


def exibir_menu(
    janela: pygame.Surface,
    assets: AssetManager,
    jogadores_iniciais: int = 1,
) -> tuple[str | None, int]:
    """
    Exibe o menu interativo com seleção de 1, 2 ou 3 jogadores locais e sigla de 3 letras.
    Retorna (nome_equipe_ou_None, num_jogadores).
    """
    pygame.font.init()
    fonte_nome = pygame.font.SysFont("Arial", 92, bold=True)
    fonte_ui = pygame.font.SysFont("monospace", 14, bold=True)
    fonte_mini = pygame.font.SysFont("monospace", 12, bold=True)

    nome_jogador = ""
    wallpaper = 0
    num_jogadores = max(1, min(3, jogadores_iniciais))
    clock = pygame.time.Clock()
    t0 = time.time()

    botoes_jogadores = [
        (1, pygame.Rect(45, 345, 130, 44)),
        (2, pygame.Rect(185, 345, 130, 44)),
        (3, pygame.Rect(325, 345, 130, 44)),
    ]

    while True:
        t = time.time() - t0
        fundo = assets.carregar_imagem(f"wallpaper{wallpaper}.png")
        janela.fill(PRETO)
        janela.blit(fundo, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, num_jogadores

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and wallpaper == 3:
                for qtd, rect_b in botoes_jogadores:
                    if rect_b.collidepoint(event.pos):
                        num_jogadores = qtd
                        assets.som_click.play()

            if event.type == pygame.KEYDOWN:
                if wallpaper == 0 and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    wallpaper = 1
                    assets.som_click.play()
                elif wallpaper == 1:
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_RETURN, pygame.K_SPACE):
                        wallpaper = 3
                        assets.som_click.play()
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        wallpaper = 2
                        assets.som_click.play()
                elif wallpaper == 2 and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    wallpaper = 1
                    assets.som_click.play()
                elif wallpaper == 3:
                    if event.key == pygame.K_TAB:
                        num_jogadores = (num_jogadores % 3) + 1
                        assets.som_click.play()
                    elif event.key in (pygame.K_1, pygame.K_KP1) and len(nome_jogador) == 0:
                        num_jogadores = 1
                        assets.som_click.play()
                    elif event.key in (pygame.K_2, pygame.K_KP2) and len(nome_jogador) == 0:
                        num_jogadores = 2
                        assets.som_click.play()
                    elif event.key in (pygame.K_3, pygame.K_KP3) and len(nome_jogador) == 0:
                        num_jogadores = 3
                        assets.som_click.play()
                    elif event.key == pygame.K_LEFT:
                        num_jogadores = 3 if num_jogadores == 1 else num_jogadores - 1
                        assets.som_click.play()
                    elif event.key == pygame.K_RIGHT:
                        num_jogadores = 1 if num_jogadores == 3 else num_jogadores + 1
                        assets.som_click.play()
                    elif event.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                        assets.som_click.play()
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and len(nome_jogador) == 3:
                        assets.som_click.play()
                        return nome_jogador, num_jogadores
                    elif event.key == pygame.K_ESCAPE:
                        wallpaper = 1
                        assets.som_click.play()
                    elif (
                        len(nome_jogador) < 3
                        and event.unicode
                        and event.unicode.isalpha()
                    ):
                        nome_jogador = (nome_jogador + event.unicode).upper()
                        assets.som_click.play()

        if wallpaper == 3:
            text_surface = fonte_nome.render(nome_jogador, True, BRANCO)
            janela.blit(text_surface, (170, 188))

            # Painel inferior de seleção de modo multiplayer local (1P / 2P / 3P)
            pygame.draw.rect(janela, (16, 18, 26), (25, 315, 450, 215), border_radius=10)
            pygame.draw.rect(janela, DOURADO, (25, 315, 450, 215), width=2, border_radius=10)

            titulo_modo = fonte_ui.render("MODO LOCAL (←/→, TAB ou Clique):", True, DOURADO)
            janela.blit(titulo_modo, (250 - titulo_modo.get_width() // 2, 323))

            for qtd, rect_b in botoes_jogadores:
                selecionado = num_jogadores == qtd
                cor_fundo = (44, 92, 138) if selecionado else (28, 32, 44)
                cor_borda = VERDE_LIMAO if selecionado else (90, 98, 118)
                pygame.draw.rect(janela, cor_fundo, rect_b, border_radius=8)
                pygame.draw.rect(janela, cor_borda, rect_b, width=2, border_radius=8)
                lbl = f"{qtd} JOGADOR" if qtd == 1 else f"{qtd} JOGADORES"
                surf_l = fonte_mini.render(lbl, True, BRANCO if selecionado else (180, 186, 200))
                janela.blit(surf_l, (rect_b.centerx - surf_l.get_width() // 2, rect_b.centery - 7))

            # Mostra os Orbes Guardiões ativos e seus controles
            esquemas = (
                ["P1: Setas ou WASD (Modo Solo com Trava de Placa)"]
                if num_jogadores == 1
                else (
                    ["P1 (Rubi): Setas ↑↓←→", "P2 (Esmeralda): W A S D"]
                    if num_jogadores == 2
                    else ["P1 (Rubi): Setas", "P2 (Esmeralda): WASD", "P3 (Solar): I J K L"]
                )
            )
            for idx in range(num_jogadores):
                ox = 68 + idx * 145
                desenhar_orbe_guardiao(janela, ox, 405, 16, idx, 1, 0, t)
                surf_c = fonte_mini.render(esquemas[idx], True, CORES_JOGADORES[idx])
                if num_jogadores == 1:
                    janela.blit(surf_c, (95, 406))
                else:
                    janela.blit(surf_c, (ox - 24, 428))

            dica = (
                "Digite 3 letras da equipe e aperte ESPACO/ENTER!"
                if len(nome_jogador) < 3
                else "PRONTO! Pressione ESPACO ou ENTER para iniciar!"
            )
            cor_dica = VERDE_LIMAO if len(nome_jogador) == 3 else AMARELO
            surf_d = fonte_ui.render(dica, True, cor_dica)
            janela.blit(surf_d, (250 - surf_d.get_width() // 2, 498))

        pygame.display.flip()
        clock.tick(60)


def exibir_splash_nivel(
    janela: pygame.Surface,
    assets: AssetManager,
    arquivo_splash: str,
    arquivo_musica: str,
    arquivo_ambiente: str,
    bioma: str,
    num_jogadores: int,
    duracao: float,
) -> bool:
    """Mostra a tela de apresentação do nível, o nome do cenário e inicia trilha + ambientação."""
    janela.fill(PRETO)
    assets.tocar_musica(arquivo_musica, volume=0.09, loop=-1)
    assets.iniciar_ambiente(arquivo_ambiente, volume=0.14)

    imagem_nivel = assets.carregar_imagem(arquivo_splash)
    janela.blit(imagem_nivel, (0, 0))

    tema = BIOMES.get(bioma, BIOMES["floresta"])
    fonte_cenario = pygame.font.SysFont("monospace", 13, bold=True)
    surf_cen = fonte_cenario.render(f"CENARIO: {tema.titulo_cenario.upper()}", True, DOURADO)
    modo_str = (
        "1P SOLO: Ative a placa, pegue os cristais e abra o portal!"
        if num_jogadores == 1
        else f"CO-OP {num_jogadores}P: Segurem placas, puxem a alavanca e peguem seus cristais!"
    )
    surf_modo = pygame.font.SysFont("monospace", 11, bold=True).render(modo_str, True, CIANO)
    janela.blit(surf_cen, (250 - surf_cen.get_width() // 2, 504))
    janela.blit(surf_modo, (250 - surf_modo.get_width() // 2, 524))

    pygame.display.flip()
    return aguardar_com_eventos(duracao, permitir_pular=True)


def exibir_game_over(janela: pygame.Surface, assets: AssetManager) -> bool:
    """Exibe a tela de Game Over com efeito sonoro."""
    janela.fill(PRETO)
    assets.parar_musica()
    assets.som_game_over.play()
    janela.blit(assets.game_over, (0, 0))
    pygame.display.flip()
    return aguardar_com_eventos(5.0, permitir_pular=True)


def exibir_ranking(
    janela: pygame.Surface,
    assets: AssetManager,
    top_10: list[tuple[int, str]],
    clock: pygame.time.Clock,
) -> None:
    """Renderiza a tabela High Scores (Top 10) até o jogador clicar em Sair ou fechar."""
    fonte_titulo = assets.fonte(70)
    fonte_cabecalho = assets.fonte(40)
    fonte_item = assets.fonte(35)
    fonte_botao = assets.fonte(30)

    botao_sair = Botao("Sair", 200, 30, (150, 515), fonte_botao)

    titulo = fonte_titulo.render("HIGH SCORES", True, VERMELHO)
    col_rank = fonte_cabecalho.render("RANK", True, AMARELO)
    col_score = fonte_cabecalho.render("SCORE", True, AMARELO)
    col_name = fonte_cabecalho.render("NAME", True, AMARELO)

    posicoes_y = [135, 175, 210, 245, 280, 320, 355, 390, 425, 460]

    while True:
        janela.fill(PRETO)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return

        if botao_sair.desenhar(janela):
            return

        janela.blit(titulo, (100, 15))
        janela.blit(col_rank, (60, 85))
        janela.blit(col_score, (210, 85))
        janela.blit(col_name, (355, 85))

        for idx in range(10):
            cor = CORES_RANKING[idx]
            y = posicoes_y[idx]
            label_surf = fonte_item.render(LABELS_RANKING[idx], True, cor)
            janela.blit(label_surf, (65, y))

            if idx < len(top_10):
                pontuacao, nome = top_10[idx]
                score_surf = fonte_item.render(str(pontuacao), True, cor)
                name_surf = fonte_item.render(str(nome), True, cor)
                janela.blit(score_surf, (230, y))
                janela.blit(name_surf, (365, y))

        pygame.display.flip()
        clock.tick(60)

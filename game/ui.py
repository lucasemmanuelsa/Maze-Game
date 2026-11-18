"""Componentes de interface, HUD, telas de abertura, menu, transição, game over e ranking."""
import time
import pygame

from game.assets import AssetManager
from game.config import (
    ALTURA_JANELA,
    AMARELO,
    AZUL,
    BRANCO,
    CORES_RANKING,
    ESPESSURA_BARREIRA,
    FPS,
    LABELS_RANKING,
    LARGURA_JANELA,
    PRETO,
    VERMELHO,
)


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
        """Desenha o botão e retorna True caso tenha sido clicado e solto."""
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


def desenhar_barreiras(janela: pygame.Surface, cor: tuple[int, int, int] = BRANCO) -> None:
    """Desenha as quatro barras limitadoras ao redor do labirinto."""
    pygame.draw.line(janela, cor, [16, 20], [484, 20], ESPESSURA_BARREIRA)
    pygame.draw.line(janela, cor, [20, 20], [20, 480], ESPESSURA_BARREIRA)
    pygame.draw.line(janela, cor, [480, 20], [480, 480], ESPESSURA_BARREIRA)
    pygame.draw.line(janela, cor, [16, 480], [484, 480], ESPESSURA_BARREIRA)


def desenhar_hud(
    janela: pygame.Surface,
    assets: AssetManager,
    vidas: int,
    tempo_mapa: int,
) -> None:
    """Desenha os corações de vida restantes e o cronômetro da fase atual."""
    for i in range(max(0, vidas)):
        janela.blit(assets.coracao, (10 + i * 36, 500))

    cronometro = assets.fonte(55).render(f"Tempo: {tempo_mapa}", True, BRANCO)
    janela.blit(cronometro, (285, 490))


def _processar_eventos_espera() -> tuple[bool, bool]:
    """Retorna (fechou_janela, pediu_pular) durante animações de intro/transição."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True, False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return False, True
    return False, False


def aguardar_com_eventos(segundos: float, permitir_pular: bool = False) -> bool:
    """Aguarda o tempo especificado mantendo a janela responsiva. Retorna False se fechar."""
    passo = 0.05
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

    for alpha in range(255):
        fechou, pulou = _processar_eventos_espera()
        if fechou:
            return False
        if pulou:
            return True
        pygame.time.delay(20)
        logo_img.set_alpha(alpha)
        janela.blit(logo_img, (0, 0))
        pygame.display.flip()

    for alpha in range(255):
        fechou, pulou = _processar_eventos_espera()
        if fechou:
            return False
        if pulou:
            return True
        pygame.time.delay(3)
        preto_img.set_alpha(alpha)
        janela.blit(preto_img, (0, 0))
        pygame.display.flip()

    for alpha in range(255):
        fechou, pulou = _processar_eventos_espera()
        if fechou:
            return False
        if pulou:
            return True
        pygame.time.delay(30)
        info_img.set_alpha(alpha)
        janela.blit(info_img, (0, 0))
        pygame.display.flip()

    pygame.display.flip()
    pygame.time.delay(100)
    return True


def exibir_menu(janela: pygame.Surface, assets: AssetManager) -> str | None:
    """Exibe o menu interativo e retorna a sigla de 3 letras do jogador (ou None ao sair)."""
    pygame.font.init()
    fonte_nome = pygame.font.SysFont("Arial", 110)
    nome_jogador = ""
    wallpaper = 0

    while True:
        fundo = assets.carregar_imagem(f"wallpaper{wallpaper}.png")
        janela.blit(fundo, (0, 0))
        pygame.time.delay(200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN and wallpaper == 3:
                assets.som_click.play()

                if event.key == pygame.K_BACKSPACE:
                    nome_jogador = nome_jogador[:-1]
                elif event.key == pygame.K_SPACE and len(nome_jogador) == 3:
                    return nome_jogador
                elif (
                    len(nome_jogador) < 3
                    and event.unicode
                    and event.unicode.isprintable()
                    and event.unicode != " "
                ):
                    nome_jogador = (nome_jogador + event.unicode).upper()

        comando = pygame.key.get_pressed()

        if wallpaper == 0 and comando[pygame.K_SPACE]:
            wallpaper = 1
            assets.som_click.play()
        elif wallpaper == 1 and comando[pygame.K_UP]:
            wallpaper = 3
            assets.som_click.play()
        elif wallpaper == 1 and comando[pygame.K_SPACE]:
            wallpaper = 1
            assets.som_click.play()
        elif wallpaper == 1 and comando[pygame.K_DOWN]:
            wallpaper = 2
            assets.som_click.play()
        elif wallpaper == 2 and comando[pygame.K_SPACE]:
            wallpaper = 1
            assets.som_click.play()
        elif wallpaper == 3:
            text_surface = fonte_nome.render(nome_jogador, True, BRANCO)
            janela.blit(text_surface, (160, 185))

        pygame.display.update()


def exibir_splash_nivel(
    janela: pygame.Surface,
    assets: AssetManager,
    arquivo_splash: str,
    arquivo_musica: str,
    duracao: float,
) -> bool:
    """Mostra a tela de apresentação do nível e inicia sua trilha sonora."""
    janela.fill(PRETO)
    assets.tocar_musica(arquivo_musica, volume=0.08, loop=-1)
    imagem_nivel = assets.carregar_imagem(arquivo_splash)
    janela.blit(imagem_nivel, (0, 0))
    pygame.display.flip()
    return aguardar_com_eventos(duracao, permitir_pular=True)


def exibir_game_over(janela: pygame.Surface, assets: AssetManager) -> None:
    """Exibe a tela e o áudio de Game Over."""
    assets.som_game_over.play()
    janela.fill(PRETO)
    assets.parar_musica()
    janela.blit(assets.game_over, (0, 0))
    pygame.display.flip()
    aguardar_com_eventos(8.0)


def exibir_ranking(
    janela: pygame.Surface,
    assets: AssetManager,
    registros: list[tuple[int, int, str]],
    clock: pygame.time.Clock,
) -> None:
    """Exibe a tabela Top 10 High Scores com botão de saída."""
    fonte_titulo = assets.fonte(80)
    fonte_tabela = assets.fonte(40)
    botao_sair = Botao("Sair", 160, 30, (170, 510), fonte_tabela)

    texto_titulo = fonte_titulo.render("HIGH SCORES", True, VERMELHO)
    texto_rank = fonte_tabela.render("RANK", True, AMARELO)
    texto_score = fonte_tabela.render("SCORE", True, AMARELO)
    texto_name = fonte_tabela.render("NAME", True, AMARELO)

    sair = False
    while not sair:
        janela.fill(PRETO)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sair = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 170 < x < 330 and 510 < y < 540:
                    sair = True

        if botao_sair.desenhar(janela):
            sair = True

        janela.blit(texto_titulo, (90, 0))
        janela.blit(texto_rank, (70, 100))
        janela.blit(texto_score, (210, 100))
        janela.blit(texto_name, (350, 100))

        for idx in range(10):
            cor = CORES_RANKING[idx]
            y_linha = 140 + idx * 30
            pos_surf = fonte_tabela.render(LABELS_RANKING[idx], True, cor)
            janela.blit(pos_surf, (75, y_linha))

            if idx < len(registros):
                _, score_val, nome_val = registros[idx]
                score_str = str(score_val)
                nome_str = str(nome_val)
            else:
                score_str = "---"
                nome_str = "---"

            janela.blit(fonte_tabela.render(score_str, True, cor), (240, y_linha))
            janela.blit(fonte_tabela.render(nome_str, True, cor), (360, y_linha))

        pygame.display.flip()
        clock.tick(FPS)

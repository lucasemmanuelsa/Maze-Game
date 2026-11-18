"""Renderizador procedural de cenários (alvenaria, pisos, vinhas, partículas) e do Orbe Guardião."""
from dataclasses import dataclass
import math
import random
import pygame

from game.collision import WallCollisionMap
from game.config import (
    AMARELO,
    BRANCO,
    CIANO,
    CORES_JOGADORES,
    CORES_NUCLEO_JOGADORES,
    DOURADO,
    NOMES_CURTOS_JOGADORES,
    PRETO,
    VERDE_LIMAO,
    VERMELHO,
)


@dataclass(frozen=True)
class BiomeTheme:
    """Paleta artística e atmosfera visual de um cenário."""

    chave: str
    titulo_cenario: str
    piso_base: tuple[int, int, int]
    piso_variacao: tuple[int, int, int]
    piso_rejunte: tuple[int, int, int]
    muro_topo: tuple[int, int, int]
    muro_meio: tuple[int, int, int]
    muro_base: tuple[int, int, int]
    muro_rejunte: tuple[int, int, int]
    vinha_escura: tuple[int, int, int]
    vinha_clara: tuple[int, int, int]
    flor_detalhe: tuple[int, int, int]
    moldura_pedra: tuple[int, int, int]
    moldura_borda: tuple[int, int, int]
    cor_particula: tuple[int, int, int]
    tipo_particula: str  # "firefly", "bubble", "ember", "stardust"


BIOMES: dict[str, BiomeTheme] = {
    "floresta": BiomeTheme(
        chave="floresta",
        titulo_cenario="Ruínas da Floresta Ancestral",
        piso_base=(34, 44, 32),
        piso_variacao=(42, 54, 38),
        piso_rejunte=(23, 30, 21),
        muro_topo=(152, 160, 134),
        muro_meio=(108, 116, 94),
        muro_base=(64, 70, 55),
        muro_rejunte=(50, 56, 43),
        vinha_escura=(26, 118, 48),
        vinha_clara=(72, 198, 84),
        flor_detalhe=(255, 214, 74),
        moldura_pedra=(76, 86, 66),
        moldura_borda=(134, 148, 114),
        cor_particula=(198, 255, 110),
        tipo_particula="firefly",
    ),
    "abissal": BiomeTheme(
        chave="abissal",
        titulo_cenario="Catacumbas Submersas",
        piso_base=(18, 36, 52),
        piso_variacao=(24, 46, 66),
        piso_rejunte=(11, 24, 36),
        muro_topo=(102, 158, 184),
        muro_meio=(64, 112, 138),
        muro_base=(36, 68, 88),
        muro_rejunte=(26, 52, 68),
        vinha_escura=(18, 142, 136),
        vinha_clara=(68, 238, 214),
        flor_detalhe=(156, 250, 255),
        moldura_pedra=(40, 78, 100),
        moldura_borda=(92, 166, 196),
        cor_particula=(130, 238, 255),
        tipo_particula="bubble",
    ),
    "vulcao": BiomeTheme(
        chave="vulcao",
        titulo_cenario="Fortaleza Vulcânica",
        piso_base=(40, 24, 24),
        piso_variacao=(52, 30, 28),
        piso_rejunte=(24, 14, 14),
        muro_topo=(126, 92, 86),
        muro_meio=(84, 58, 56),
        muro_base=(48, 30, 30),
        muro_rejunte=(196, 68, 24),
        vinha_escura=(118, 34, 26),
        vinha_clara=(214, 84, 32),
        flor_detalhe=(255, 196, 52),
        moldura_pedra=(68, 40, 38),
        moldura_borda=(184, 82, 44),
        cor_particula=(255, 136, 42),
        tipo_particula="ember",
    ),
    "divino": BiomeTheme(
        chave="divino",
        titulo_cenario="Cidadela Celestial",
        piso_base=(28, 24, 48),
        piso_variacao=(38, 32, 64),
        piso_rejunte=(18, 15, 34),
        muro_topo=(232, 214, 168),
        muro_meio=(182, 156, 108),
        muro_base=(116, 92, 58),
        muro_rejunte=(138, 112, 68),
        vinha_escura=(168, 42, 74),
        vinha_clara=(255, 192, 72),
        flor_detalhe=(255, 248, 196),
        moldura_pedra=(112, 88, 62),
        moldura_borda=(240, 204, 112),
        cor_particula=(255, 232, 138),
        tipo_particula="stardust",
    ),
}


def _clamp_u8(val: int) -> int:
    return 0 if val < 0 else (255 if val > 255 else val)


def renderizar_cenario_labirinto(
    colisao: WallCollisionMap,
    chave_bioma: str,
    seed: int = 1,
) -> pygame.Surface:
    """
    Constrói uma superfície 500x500 rica em detalhes (piso de lajotas, sombras projetadas,
    muros de pedra chanfrados 2.5D e vinhas penduradas) preservando 100% a geometria de colisão.
    """
    tema = BIOMES.get(chave_bioma, BIOMES["floresta"])
    w = WallCollisionMap.LARGURA_MAPA
    h = WallCollisionMap.ALTURA_MAPA
    grade = colisao.grade_paredes
    buf = bytearray(w * h * 3)

    pb_r, pb_g, pb_b = tema.piso_base
    pv_r, pv_g, pv_b = tema.piso_variacao
    pr_r, pr_g, pr_b = tema.piso_rejunte

    mt_r, mt_g, mt_b = tema.muro_topo
    mm_r, mm_g, mm_b = tema.muro_meio
    mb_r, mb_g, mb_b = tema.muro_base
    mr_r, mr_g, mr_b = tema.muro_rejunte

    # 1. Passada rápida pixel-a-pixel para lajotas de piso, sombras 2.5D e alvenaria encorpada
    # Cria máscara visual levemente encorpada (+1px à direita e +2px de face frontal abaixo) sem afetar colisão!
    vis_wall = bytearray(w * h)
    for y in range(16, h - 16):
        row_off = y * w
        for x in range(16, w - 16):
            idx = row_off + x
            if grade[idx] == 1:
                vis_wall[idx] = 1
            elif grade[idx - 1] == 1:
                vis_wall[idx] = 1
            elif grade[idx - w] == 1:
                vis_wall[idx] = 2  # Face frontal inferior da parede 2.5D
            elif y >= 18 and grade[idx - 2 * w] == 1 and grade[idx - w] == 0:
                vis_wall[idx] = 2

    for y in range(h):
        row_off = y * w
        tile_y = y & 15
        brick_row = y // 6
        brick_y = y % 6
        brick_shift = 6 if (brick_row & 1) else 0

        for x in range(w):
            idx = row_off + x
            out_i = idx * 3

            if x < 16 or x >= 484 or y < 16 or y >= 484:
                buf[out_i] = 10
                buf[out_i + 1] = 10
                buf[out_i + 2] = 14
                continue

            vw = vis_wall[idx]
            if vw == 1:
                acima_vazio = y > 0 and vis_wall[idx - w] == 0
                esq_vazio = x > 0 and vis_wall[idx - 1] == 0

                if acima_vazio or esq_vazio:
                    r, g, b = mt_r, mt_g, mt_b
                elif brick_y == 0 or ((x + brick_shift) % 12 == 0):
                    r, g, b = mr_r, mr_g, mr_b
                else:
                    hval = ((x // 12) * 37 + brick_row * 59 + seed * 13) & 15
                    delta = (hval - 7) * 2
                    r = _clamp_u8(mm_r + delta)
                    g = _clamp_u8(mm_g + delta)
                    b = _clamp_u8(mm_b + delta)

                buf[out_i] = r
                buf[out_i + 1] = g
                buf[out_i + 2] = b
            elif vw == 2:
                # Face lateral/frontal escura do muro de pedra (efeito 2.5D com argamassa vertical)
                if ((x + brick_shift) % 12 == 0):
                    r, g, b = _clamp_u8(mr_r - 14), _clamp_u8(mr_g - 14), _clamp_u8(mr_b - 14)
                else:
                    r, g, b = mb_r, mb_g, mb_b
                buf[out_i] = r
                buf[out_i + 1] = g
                buf[out_i + 2] = b
            else:
                stagger = 8 if ((y >> 4) & 1) else 0
                tile_x = (x + stagger) & 15
                if tile_x == 0 or tile_y == 0:
                    r, g, b = pr_r, pr_g, pr_b
                else:
                    cell_hash = (((x + stagger) >> 4) * 73 + (y >> 4) * 131 + seed * 19) & 7
                    if cell_hash < 3:
                        r, g, b = pv_r, pv_g, pv_b
                    else:
                        r, g, b = pb_r, pb_g, pb_b
                    speck = ((x * 17 + y * 31) & 15) - 7
                    r = _clamp_u8(r + speck)
                    g = _clamp_u8(g + speck)
                    b = _clamp_u8(b + speck)

                # Sombra projetada suave no piso abaixo e à direita do muro
                sombra = 0
                if y >= 2 and vis_wall[idx - w] != 0:
                    sombra += 18
                elif y >= 3 and vis_wall[idx - 2 * w] != 0:
                    sombra += 10
                if x >= 2 and vis_wall[idx - 1] != 0:
                    sombra += 12

                if sombra:
                    r = _clamp_u8(r - sombra)
                    g = _clamp_u8(g - sombra)
                    b = _clamp_u8(b - sombra)

                buf[out_i] = r
                buf[out_i + 1] = g
                buf[out_i + 2] = b

    superficie = pygame.image.frombuffer(bytes(buf), (w, h), "RGB").convert()

    # 2. Crescimento procedural de vinhas, musgos e brotos sobre os muros e beiradas
    rng = random.Random(seed * 9173 + 42)
    for y in range(20, h - 22, 3):
        row_off = y * w
        for x in range(20, w - 22, 3):
            idx = row_off + x
            if grade[idx] != 1:
                continue
            abaixo_vazio = grade[idx + w] == 0
            acima_vazio = grade[idx - w] == 0
            esq_vazio = grade[idx - 1] == 0
            dir_vazio = grade[idx + 1] == 0

            # Tufos de musgo/vinhas rasteiras no topo dos muros
            if (acima_vazio or esq_vazio or dir_vazio) and rng.random() < 0.20:
                comp = rng.randint(3, 8)
                vx, vy = x, y
                for step in range(comp):
                    cor_v = tema.vinha_clara if (step & 1) == 0 else tema.vinha_escura
                    pygame.draw.circle(superficie, cor_v, (vx, vy), 1 if step > 1 else 2)
                    vx += rng.choice((-1, 0, 1))
                    vy += rng.choice((0, 1))
                    if not (18 <= vx < 482 and 18 <= vy < 482):
                        break
                if rng.random() < 0.28:
                    superficie.set_at((x, y), tema.flor_detalhe)

            # Cipós / vinhas penduradas na beirada inferior dos muros (caem levemente sobre a sombra, sem afetar colisão!)
            if abaixo_vazio and rng.random() < 0.14:
                pend = rng.randint(2, 5)
                px = x
                for dy in range(pend):
                    py = y + dy
                    cor_v = tema.vinha_escura if dy == 0 else tema.vinha_clara
                    superficie.set_at((px, py), cor_v)
                    if dy % 2 == 1 and px + 1 < 482:
                        superficie.set_at((px + 1, py), tema.vinha_escura)
                    if dy == pend - 1 and rng.random() < 0.35:
                        superficie.set_at((px, py), tema.flor_detalhe)

    return superficie


def desenhar_moldura_cenario(janela: pygame.Surface, chave_bioma: str) -> None:
    """Substitui as antigas linhas brancas por uma muralha/moldura esculpida para os canhões."""
    tema = BIOMES.get(chave_bioma, BIOMES["floresta"])
    esp = 9
    bordas = [
        pygame.Rect(15, 15, 470, esp),
        pygame.Rect(15, 476, 470, esp),
        pygame.Rect(15, 15, esp, 470),
        pygame.Rect(476, 15, esp, 470),
    ]
    for r in bordas:
        pygame.draw.rect(janela, tema.moldura_pedra, r, border_radius=2)
        pygame.draw.rect(janela, tema.moldura_borda, r, width=1, border_radius=2)

    # Cantoneiras rúnicas nos 4 vértices
    for cx, cy in ((14, 14), (475, 14), (14, 475), (475, 475)):
        cant = pygame.Rect(cx, cy, 12, 12)
        pygame.draw.rect(janela, tema.muro_base, cant, border_radius=3)
        pygame.draw.rect(janela, tema.moldura_borda, cant, width=2, border_radius=3)
        pygame.draw.circle(janela, tema.flor_detalhe, cant.center, 2)


class AmbientParticles:
    """Partículas atmosféricas leves em tempo real para cada cenário (vagalumes, bolhas, brasas, poeira astral)."""

    def __init__(self, chave_bioma: str, quantidade: int = 24) -> None:
        self.tema = BIOMES.get(chave_bioma, BIOMES["floresta"])
        rng = random.Random(hash(chave_bioma) & 0xFFFF)
        self.particulas = [
            [
                rng.uniform(24.0, 476.0),
                rng.uniform(24.0, 476.0),
                rng.uniform(-0.35, 0.35),
                rng.uniform(-0.55, -0.15) if self.tema.tipo_particula in ("bubble", "ember") else rng.uniform(-0.25, 0.25),
                rng.uniform(0.0, 6.28),
            ]
            for _ in range(quantidade)
        ]

    def atualizar_e_desenhar(self, janela: pygame.Surface, t: float) -> None:
        cor = self.tema.cor_particula
        tipo = self.tema.tipo_particula
        for p in self.particulas:
            p[0] += p[2] + math.sin(t * 1.8 + p[4]) * 0.15
            p[1] += p[3]
            if p[0] < 22:
                p[0] = 476
            elif p[0] > 478:
                p[0] = 24
            if p[1] < 22:
                p[1] = 476
            elif p[1] > 478:
                p[1] = 24

            ix, iy = int(p[0]), int(p[1])
            pulso = 0.5 + 0.5 * math.sin(t * 4.0 + p[4])
            if tipo == "bubble":
                pygame.draw.circle(janela, cor, (ix, iy), 2, 1)
            elif tipo == "ember":
                raio = 2 if pulso > 0.6 else 1
                pygame.draw.circle(janela, cor, (ix, iy), raio)
            else:
                if pulso > 0.35:
                    pygame.draw.circle(janela, cor, (ix, iy), 2 if pulso > 0.8 else 1)


def desenhar_orbe_guardiao(
    janela: pygame.Surface,
    x: int,
    y: int,
    tamanho: int,
    indice_jogador: int,
    olhar_dx: int,
    olhar_dy: int,
    t: float,
    em_capsula_reviver: bool = False,
    progresso_reviver: float = 1.0,
    invulneravel: bool = False,
    mostrar_tag: bool = False,
    fonte_tag: pygame.font.Font | None = None,
) -> None:
    """
    Desenha o objeto controlável unificado do jogo inteiro: o Orbe Guardião Rúnico.
    Possui anel metálico ancestral, núcleo energético e visor direcional expressivo.
    """
    cor_principal = CORES_JOGADORES[indice_jogador % len(CORES_JOGADORES)]
    cor_nucleo = CORES_NUCLEO_JOGADORES[indice_jogador % len(CORES_NUCLEO_JOGADORES)]
    cx = x + tamanho // 2
    cy = y + tamanho // 2
    raio = max(6, tamanho // 2 + 1)

    if em_capsula_reviver:
        # Cápsula de Alma aguardando resgate de um aliado!
        pulso = 2 + int(2 * math.sin(t * 8.0))
        pygame.draw.circle(janela, cor_principal, (cx, cy), raio + pulso, 2)
        pygame.draw.circle(janela, (40, 50, 70), (cx, cy), raio - 1)
        pygame.draw.circle(janela, cor_nucleo, (cx, cy), max(2, raio - 4))
        # Barra de tempo restante acima da cápsula
        larg_barra = 18
        preenchido = max(1, int(larg_barra * max(0.0, min(1.0, progresso_reviver))))
        pygame.draw.rect(janela, PRETO, (cx - larg_barra // 2 - 1, y - 8, larg_barra + 2, 5))
        pygame.draw.rect(janela, cor_principal, (cx - larg_barra // 2, y - 7, preenchido, 3))
        return

    if invulneravel and int(t * 16) % 2 == 0:
        cor_principal = BRANCO

    # Sombra de flutuação no chão
    pygame.draw.ellipse(janela, (12, 14, 18), (cx - raio + 1, cy + raio - 2, (raio - 1) * 2, 4))

    # Aro metálico rúnico externo + corpo esférico + brilho especular
    pygame.draw.circle(janela, (52, 46, 38), (cx, cy), raio + 1)
    pygame.draw.circle(janela, (214, 184, 112), (cx, cy), raio, 1)
    pygame.draw.circle(janela, cor_principal, (cx, cy), raio - 1)
    pygame.draw.circle(janela, cor_nucleo, (cx - 1, cy - 1), max(2, raio - 4))

    # Olhos/visor luminosos apontando para a direção do movimento
    ox = 2 if olhar_dx > 0 else (-2 if olhar_dx < 0 else 0)
    oy = 2 if olhar_dy > 0 else (-2 if olhar_dy < 0 else 0)
    pygame.draw.rect(janela, (22, 18, 28), (cx - 3 + ox, cy - 2 + oy, 6, 3), border_radius=1)
    janela.set_at((cx - 2 + ox, cy - 1 + oy), BRANCO)
    janela.set_at((cx + 1 + ox, cy - 1 + oy), BRANCO)

    # Etiqueta compacta P1 / P2 / P3 no modo multiplayer
    if mostrar_tag and fonte_tag is not None:
        tag = NOMES_CURTOS_JOGADORES[indice_jogador % 3]
        surf_t = fonte_tag.render(tag, True, cor_principal)
        janela.blit(surf_t, (cx - surf_t.get_width() // 2, y - 12))


def desenhar_projetil_canhao(
    janela: pygame.Surface,
    bx: int,
    by: int,
    direcao: str,
    t: float,
    congelado: bool = False,
) -> None:
    """Desenha uma Esfera de Plasma Flamejante com rastro direcional no lugar do quadrado rosa."""
    if not (0 <= bx <= 490 and 0 <= by <= 476):
        return
    cx, cy = bx + 5, by + 5
    if congelado:
        pygame.draw.circle(janela, CIANO, (cx, cy), 5)
        pygame.draw.circle(janela, BRANCO, (cx, cy), 2)
        return

    # Rastro curto atrás da esfera
    rx = 5 if direcao == "left" else (-5 if direcao == "right" else 0)
    ry = 5 if direcao == "up" else (-5 if direcao == "down" else 0)
    pygame.draw.circle(janela, (190, 28, 110), (cx + rx, cy + ry), 4)
    pygame.draw.circle(janela, (255, 64, 156), (cx, cy), 5)
    raio_nucleo = 3 if int(t * 20) % 2 == 0 else 2
    pygame.draw.circle(janela, (255, 232, 180), (cx, cy), raio_nucleo)

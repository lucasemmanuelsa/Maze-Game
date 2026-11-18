"""Sistema otimizado de colisão pixel-a-pixel com as paredes dos labirintos."""
import pygame
from game.config import AZUL, BRANCO


class WallCollisionMap:
    """
    Pré-calcula uma tabela de soma de prefixos 2D (integral image) dos pixels de parede
    do mapa em uma área 500x500, mantendo exatamente o mesmo comportamento de colisão
    do código original em tempo constante O(1) por frame e expondo a malha para renderização.
    """

    LARGURA_MAPA = 500
    ALTURA_MAPA = 500

    def __init__(self, superficie_mapa: pygame.Surface, pos_mapa: tuple[int, int]) -> None:
        tela_temp = pygame.Surface((self.LARGURA_MAPA, self.ALTURA_MAPA))
        tela_temp.fill(AZUL)
        tela_temp.blit(superficie_mapa, pos_mapa)

        dados_rgb = pygame.image.tostring(tela_temp, "RGB")
        largura = self.LARGURA_MAPA
        altura = self.ALTURA_MAPA

        soma = [[0] * (largura + 1) for _ in range(altura + 1)]
        grade = bytearray(largura * altura)
        branco_bytes = bytes(BRANCO)

        idx = 0
        pidx = 0
        for y in range(altura):
            linha_atual = soma[y + 1]
            linha_anterior = soma[y]
            acumulado_linha = 0
            for x in range(largura):
                eh_parede = 1 if dados_rgb[idx : idx + 3] == branco_bytes else 0
                idx += 3
                grade[pidx] = eh_parede
                pidx += 1
                acumulado_linha += eh_parede
                linha_atual[x + 1] = linha_anterior[x + 1] + acumulado_linha

        self._soma = soma
        self.grade_paredes = grade

    def eh_parede(self, x: int, y: int) -> bool:
        """Retorna True se o pixel exato (x, y) pertencer a um muro."""
        if 0 <= x < self.LARGURA_MAPA and 0 <= y < self.ALTURA_MAPA:
            return self.grade_paredes[y * self.LARGURA_MAPA + x] == 1
        return False

    def colide_retangulo(self, x: int, y: int, largura: int, altura: int) -> bool:
        """Retorna True se houver qualquer pixel de parede dentro de Rect(x, y, largura, altura)."""
        x1 = max(0, int(x))
        y1 = max(0, int(y))
        x2 = min(self.LARGURA_MAPA, int(x + largura))
        y2 = min(self.ALTURA_MAPA, int(y + altura))

        if x1 >= x2 or y1 >= y2:
            return False

        s = self._soma
        total_brancos = s[y2][x2] - s[y1][x2] - s[y2][x1] + s[y1][x1]
        return total_brancos > 0

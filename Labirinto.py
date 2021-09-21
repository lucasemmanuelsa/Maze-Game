import time, pygame, os, sys
from random import randint


# inicializa todos os módulos que necessitam de inicialização dentro do pygame.
pygame.init()

# Criar a janela
janela = pygame.display.set_mode((500, 550))

clock = pygame.time.Clock()

diretorio_principal = os.path.dirname(__file__)
diretorio_imagens = os.path.join(diretorio_principal, 'imagens')
diretorio_sons = os.path.join(diretorio_principal, 'sons')

# Mudar o título do jogo
pygame.display.set_caption('Labirinto')
icone = pygame.image.load(os.path.join(diretorio_imagens, 'lab.png')) # imagem deve estar no diretório onde se encontra o programa
pygame.display.set_icon(icone)

# Carregando sons
musicatema = pygame.mixer.music.load(os.path.join(diretorio_sons, 'Thememusic.wav'))
# nextlvlsound = pygame.mixer.Sound(os.path.join(diretorio_sons, 'sound1.mp3')) APAGAR DPS

pygame.mixer.music.set_volume(0.08)
pygame.mixer.music.play(-1)

# Definindo cores
preto = (0,0,0)
branco = (255,255,255)
verdelimao = (15, 255, 149)
vermelho = (255, 49, 46)
azul = (72, 172, 240)
rosa = (252, 24, 152)
roxo = (27, 20, 100)

def criarCanhão(imagem ,x, y):
    janela.blit(imagem, (x, y))

def criarCoracao(imagem, x, y):
    janela.blit(imagem, (x, y))

def desenharMapa(mapa, x, y):
    janela.blit(mapa, (x, y))

# Carregando fonte do jogo
fonte = pygame.font.Font('Gamer.ttf', 55)

# imagem de coração
coracaoImagem1 = pygame.image.load(os.path.join(diretorio_imagens, 'coracao.png'))
coracaoImagem1 = pygame.transform.scale(coracaoImagem1, (36, 36))

coracao1X = 10
coracao1Y = 500

coracaoImagem2 = pygame.image.load(os.path.join(diretorio_imagens, 'coracao.png'))
coracaoImagem2 = pygame.transform.scale(coracaoImagem2, (36, 36))

coracao2X = 46
coracao2Y = 500

coracaoImagem3 = pygame.image.load(os.path.join(diretorio_imagens, 'coracao.png'))
coracaoImagem3 = pygame.transform.scale(coracaoImagem3, (36, 36))

coracao3X = 82
coracao3Y = 500

coracaoImagem4 = pygame.image.load(os.path.join(diretorio_imagens, 'coracao.png'))
coracaoImagem4 = pygame.transform.scale(coracaoImagem4, (36, 36))

coracao4X = 118
coracao4Y = 500

coracaoImagem5 = pygame.image.load(os.path.join(diretorio_imagens, 'coracao.png'))
coracaoImagem5 = pygame.transform.scale(coracaoImagem5, (36, 36))

coracao5X = 154
coracao5Y = 500
#----------------------------------------------------------------------------------------------
# imagem do canhão
canhaoImagem = pygame.image.load(os.path.join(diretorio_imagens, 'canhao.png'))
canhaoImagem = pygame.transform.scale(canhaoImagem, (24, 24))
canhaoImagem = pygame.transform.flip(canhaoImagem, True, False)

canhaoImagem2 = pygame.image.load(os.path.join(diretorio_imagens, 'canhao.png'))
canhaoImagem2 = pygame.transform.scale(canhaoImagem2, (24, 24))
canhaoImagem2 = pygame.transform.flip(canhaoImagem2, True, False)


# posição do canhão 1
canhao1X = 475
canhao1Y = 100

# bala canhao 1
bala1X = canhao1X
bala1Y = canhao1Y + 8
bala1MudançaX = 0
bala1MudançaY = 0
tempoBala1 = randint(1,3)
auxTempoBala1 = -tempoBala1

# posição do canhão 2
canhao2X = 475
canhao2Y = 225

# bala canhao 2
bala2X = canhao2X
bala2Y = canhao2Y + 8
bala2MudançaX = 0
bala2MudançaY = 0
tempoBala2 = randint(1,3)
auxTempoBala2 = -tempoBala2

# posição do canhão 3
canhao3X = 475
canhao3Y = 350

# bala canhao 3
bala3X = canhao3X
bala3Y = canhao3Y + 8
bala3MudançaX = 0
bala3MudançaY = 0
tempoBala3 = randint(1,3)
auxTempoBala3 = -tempoBala3

#velocidade das balas dos canhões
velocidadeBala = 9
#-----------------------------------------------------------------------------------------------


# imagem do mapa 1
mapa1 = pygame.image.load(os.path.join(diretorio_imagens, 'mapa.png'))
mapa1 = pygame.transform.scale(mapa1, (510, 510))


# imagem do mapa 2
mapa2 = pygame.image.load(os.path.join(diretorio_imagens, 'mapa2.png'))
mapa2 = pygame.transform.scale(mapa2, (520, 460))

# imagem do mapa 3
mapa3 = pygame.image.load(os.path.join(diretorio_imagens, 'mapa3.png'))
mapa3 = pygame.transform.scale(mapa3, (465, 465))


# Posição da chegada
chegadaX = 438
chegadaY = 27

# imagem do jogador
jogadorImagem = pygame.image.load(os.path.join(diretorio_imagens, 'jogador.png'))
jogadorImagem = pygame.transform.scale(jogadorImagem, (14, 14))
rectJogador = jogadorImagem.get_rect()

# Posiçao do jogador
jogadorX = 25 #438 
jogadorY = 25 #27
jogadorMudançaX = 0
jogadorMudançaY = 0
# Velocidade do jogador
velocidade = 2
# Contador de vida
vida = 5

# Espessura das paredes limitadoras
espessura = 9

# criando a variavel para armazenar o tempo
tempoMapa1 = 0 
#Menu do jogo ---------------------------------------------------------------------------------------

def menu (janela,wallpaper):
    pygame.font.init()
    fonte_base      = pygame.font.SysFont("Arial",110)
    str_jogador     = ''
    ContadorLetras  = 4

    def wallpaper_changer (num_wallpaper):
        fundo = pygame.image.load(os.path.join(diretorio_imagens, 'wallpaper{}.png'.format(num_wallpaper)))
        return fundo

    while janela != 0:
        janela.blit (wallpaper_changer(wallpaper),(0,0))
        pygame.time.delay(150)

        for event in pygame.event.get ():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and wallpaper == 3 and ContadorLetras > 0:
                str_jogador = str_jogador.upper()

                if event.key == pygame.K_BACKSPACE:
                    str_jogador = str_jogador[:-1]
                    ContadorLetras += 1

                elif ContadorLetras > 1:
                    str_jogador += event.unicode
                    ContadorLetras -= 1
                    str_jogador = str_jogador.upper()

                elif event.key == pygame.K_SPACE and len(str_jogador) == 3:
                    return str_jogador

        text_surface = fonte_base.render(str_jogador,True,(255,255,255))
        comando = pygame.key.get_pressed()

        if   wallpaper == 0 and comando[pygame.K_SPACE] : wallpaper = 1
        elif wallpaper == 1 and comando[pygame.K_UP]    : wallpaper = 3
        elif wallpaper == 1 and comando[pygame.K_SPACE] : wallpaper = 1
        elif wallpaper == 1 and comando[pygame.K_DOWN]  : wallpaper = 2
        elif wallpaper == 2 and comando[pygame.K_SPACE] : wallpaper = 1
        elif wallpaper == 3                             : janela.blit(text_surface,(160,185))

        pygame.display.update()

menu(janela,0)
#-----------------------------------------------------------------------------------------
janela.fill(preto)  # pinta a cor do fundo

# texto 'Nível 1' antes de começar o jogo
texto = fonte.render('Nível 1', True, vermelho)

janela.blit(texto, (180, 215))

pygame.display.flip()
time.sleep(3)
#-----------------------------------------------------------------------------------------------------
listaX = []
listaY = []

janela.fill(azul) # pinta a janela novamente

desenharMapa(mapa1, -5, -5)

for x in range(500): # pega as coordenadas de cada pixel preto do mapa e adiciona em uma lista, para ser possível fazer as colisões.
        for y in range(500):
            if janela.get_at((x, y)) == preto:
                listaX.append(x)
                listaY.append(y)

lista2X = []
lista2Y = []


janela.fill(azul)

janela.blit(mapa2, (-38,16))
for x in range(500):
    for y in range(500):
        if janela.get_at((x,y)) == branco:
            lista2X.append(x)
            lista2Y.append(y)
            

lista3X = []
lista3Y = []

janela.fill(azul)

desenharMapa(mapa3, 16, 16)

for x in range(500):
    for y in range(500):
        if janela.get_at((x,y)) == preto:
            lista3X.append(x)
            lista3Y.append(y)

#------------------------------------------------------------------------------------------------------
# Game loop, para a janela nao sumir rapidamente e o jogo permanecer rodando. Sem o while o programa fecha, por isso, quando apertar o botao fechar (pygame.QUIT), ele quebra o while e a janela encerra
sair = False
while sair != True: #CÓDIGO REFERENTE AO MAPA 1
    
    tempoMapa1 = int(pygame.time.get_ticks()/1000) - 3 # contagem do tempo

    janela.fill(preto) # pinta a janela de preto novamente

    cronometro = fonte.render('Tempo: ' + str(tempoMapa1), True, branco)
    janela.blit(cronometro, (285, 490)) # adiciona o cronometro na tela

    jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

    chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)

    bala1 = pygame.Rect(bala1X, bala1Y, 10, 10)
    bala2 = pygame.Rect(bala2X, bala2Y, 10, 10)
    bala3 = pygame.Rect(bala3X, bala3Y, 10, 10)

    for i in range(len(listaX)):
        janela.set_at((listaX[i], listaY[i]), branco)
        

    pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador
    
    pygame.draw.rect(janela, azul, (chegada)) # desenha minha chegada
    
    pygame.draw.rect(janela, rosa, (bala1)) # desenha a bala do canhao 1
    pygame.draw.rect(janela, rosa, (bala2)) # desenha a bala do canhao 2
    pygame.draw.rect(janela, rosa, (bala3)) # desenha a bala do canhao 3
    

    pygame.draw.line(janela, branco, [16,20], [484,20], espessura) # barra horizontal superior
    pygame.draw.line(janela, branco, [20,20], [20, 480], espessura) # barra na vertical esquerda
    pygame.draw.line(janela, branco, [480,20], [480,480], espessura) # barra vertical direita
    pygame.draw.line(janela, branco, [16,480], [484,480], espessura) # barra horizontal inferior
    
    #movimentação das balas
    bala1MudançaX = - velocidadeBala
    bala2MudançaX = - velocidadeBala
    bala3MudançaX = - velocidadeBala

    for event in pygame.event.get():
        if event.type == pygame.QUIT: # evento de fechar o jogo
            sair = True
        if event.type == pygame.KEYDOWN: # evento de controle, movimentar o jogador
            if event.key == pygame.K_LEFT:
                jogadorMudançaX = - velocidade
            if event.key == pygame.K_RIGHT:
                jogadorMudançaX = velocidade   
            if event.key == pygame.K_UP:
                jogadorMudançaY = - velocidade
            if event.key == pygame.K_DOWN:
                jogadorMudançaY = velocidade
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                jogadorMudançaX = 0
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                jogadorMudançaY = 0
    
    jogadorX += jogadorMudançaX
    jogadorY += jogadorMudançaY

    bala1X += bala1MudançaX
    bala2X += bala2MudançaX
    bala3X += bala3MudançaX
    
    criarCanhão(canhaoImagem, canhao1X, canhao1Y)
    criarCanhão(canhaoImagem, canhao2X, canhao2Y)
    criarCanhão(canhaoImagem, canhao3X, canhao3Y)

    criarCoracao(coracaoImagem1, coracao1X, coracao1Y)
    criarCoracao(coracaoImagem2, coracao2X, coracao2Y)
    criarCoracao(coracaoImagem3, coracao3X, coracao3Y)
    criarCoracao(coracaoImagem4, coracao4X, coracao4Y)
    criarCoracao(coracaoImagem5, coracao5X, coracao5Y)

    
    if pygame.Rect(bala1X, bala1Y, 10, 10).collidepoint(0, bala1Y): #se a bala encostar na borda da janela do jogo a variavel auxiliar vai receber o tempo do jogo nesse exato momento
        auxTempoBala1 = tempoMapa1
    if auxTempoBala1 + tempoBala1 == tempoMapa1: # a bala vai ser disparada a cada tempo definido da bala (de 1 a 3) de forma aleatória
        bala1X = canhao1X # a bala volta para a posição inicial
        tempoBala1 = randint(1,3)
    if pygame.Rect(bala2X, bala2Y, 10, 10).collidepoint(0, bala2Y):
        auxTempoBala2 = tempoMapa1
    if auxTempoBala2 + tempoBala2 == tempoMapa1:
        bala2X = canhao2X
        tempoBala2 = randint(1,3)
    if pygame.Rect(bala3X, bala3Y, 10, 10).collidepoint(0, bala3Y):
        auxTempoBala3 = tempoMapa1
    if auxTempoBala3 + tempoBala3 == tempoMapa1:
        bala3X = canhao3X
        tempoBala3 = randint(1,3)
    if jogador.colliderect(bala1) or jogador.colliderect(bala2) or jogador.colliderect(bala3):
        time.sleep(1)
        jogadorX = 25
        jogadorY = 25
        vida -= 1
    if vida == 4:
        coracaoImagem5.set_alpha(0)
    elif vida == 3:
        coracaoImagem4.set_alpha(0)
    elif vida == 2:
        coracaoImagem3.set_alpha(0)
    elif vida == 1:
        coracaoImagem2.set_alpha(0)
    if vida == 0:
        sair = True
        
    # Colisão com as paredes
    for i in range(len(listaX)):
        if pygame.Rect(jogadorX, jogadorY, 13, 13).collidepoint(listaX[i], listaY[i]):
            jogadorX -= jogadorMudançaX
            jogadorY -= jogadorMudançaY
        

    # Barreiras limitadoras do jogo
    if jogadorY <= 25:
        jogadorY = 25
    if jogadorY >= 462:
        jogadorY = 462
    if jogadorX <= 25:
        jogadorX = 25
    if jogadorX >= 462:
        jogadorX = 462

    if jogador.colliderect(chegada):
        # Tela antes do proximo mapa
        janela.fill(preto)
        texto2 = fonte.render('Nível 2', True, vermelho)
        janela.blit(texto2, (180, 215))
        pygame.display.flip()
        time.sleep(5)

        jogadorX = 25
        jogadorY = 60

        chegadaX = 25
        chegadaY = 29

        velocidade = 2

        canhaoImagem = pygame.transform.rotate(canhaoImagem, -90)

        canhao1X = 100
        canhao1Y = 475

        canhao2X = 225
        canhao2Y = 475

        canhao3X = 350
        canhao3Y = 475

        canhao4X = 475
        canhao4Y = 25

        bala1X = canhao1X + 8
        bala1Y = canhao1Y
        bala1MudançaX = 0
        bala1MudançaY = 0
        tempoBala1 = randint(1,2)
        auxTempoBala1 = -tempoBala1

        bala2X = canhao2X + 8
        bala2Y = canhao2Y
        bala2MudançaX = 0
        bala2MudançaY = 0
        tempoBala2 = randint(1,2)
        auxTempoBala2 = -tempoBala2

        bala3X = canhao3X + 8
        bala3Y = canhao3Y
        bala3MudançaX = 0
        bala3MudançaY = 0
        tempoBala3 = randint(1,2)
        auxTempoBala3 = -tempoBala3

        bala4X = canhao4X
        bala4Y = canhao4Y + 8
        bala4MudançaX = 0
        bala4MudançaY = 0
        tempoBala4 = 3
        auxTempoBala4 = -tempoBala4




        while sair != True: #Código do mapa 2
            janela.fill(preto)
            print(jogadorX, jogadorY)
            tempoMapa2 = int(pygame.time.get_ticks()/1000) - (tempoMapa1+9)
            cronometro = fonte.render('Tempo: ' + str(tempoMapa2), True, branco)

            janela.blit(cronometro, (285, 490))

            janela.blit(mapa2, (-38, 16))

            jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

            chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)

            bala1 = pygame.Rect(bala1X, bala1Y, 10, 10)
            bala2 = pygame.Rect(bala2X, bala2Y, 10, 10)
            bala3 = pygame.Rect(bala3X, bala3Y, 10, 10)
            bala4 = pygame.Rect(bala4X, bala4Y, 10, 10)

            pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador

            pygame.draw.rect(janela, azul, (chegada)) # desenha minha chegada
            
            pygame.draw.rect(janela, rosa, (bala1)) # desenha a bala do canhao 1
            pygame.draw.rect(janela, rosa, (bala2)) # desenha a bala do canhao 2
            pygame.draw.rect(janela, rosa, (bala3)) # desenha a bala do canhao 3
            pygame.draw.rect(janela, rosa, (bala4)) # desenha a bala do canhao 4

            pygame.draw.line(janela, branco, [16,20], [484,20], espessura) # barra horizontal superior
            pygame.draw.line(janela, branco, [20,20], [20, 480], espessura) # barra na vertical esquerda
            pygame.draw.line(janela, branco, [480,20], [480,480], espessura) # barra vertical direita
            pygame.draw.line(janela, branco, [16,480], [484,480], espessura) # barra horizontal inferior

            bala1Y += bala1MudançaY
            bala2Y += bala2MudançaY
            bala3Y += bala3MudançaY
            bala4X += bala4MudançaX

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # evento de fechar o jogo
                    sair = True
                if event.type == pygame.KEYDOWN: # evento de controle, movimentar o jogador
                    if event.key == pygame.K_LEFT:
                        jogadorMudançaX = - velocidade
                    if event.key == pygame.K_RIGHT:
                        jogadorMudançaX = velocidade   
                    if event.key == pygame.K_UP:
                        jogadorMudançaY = - velocidade
                    if event.key == pygame.K_DOWN:
                        jogadorMudançaY = velocidade
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        jogadorMudançaX = 0
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        jogadorMudançaY = 0
            
            jogadorX += jogadorMudançaX
            jogadorY += jogadorMudançaY

            bala1MudançaY = - velocidadeBala
            bala2MudançaY = - velocidadeBala
            bala3MudançaY = - velocidadeBala
            bala4MudançaX = - velocidadeBala

            criarCanhão(canhaoImagem, canhao1X, canhao1Y)
            criarCanhão(canhaoImagem, canhao2X, canhao2Y)
            criarCanhão(canhaoImagem, canhao3X, canhao3Y)
            criarCanhão(canhaoImagem2, canhao4X, canhao4Y)

            criarCoracao(coracaoImagem1, coracao1X, coracao1Y)
            criarCoracao(coracaoImagem2, coracao2X, coracao2Y)
            criarCoracao(coracaoImagem3, coracao3X, coracao3Y)
            criarCoracao(coracaoImagem4, coracao4X, coracao4Y)
            criarCoracao(coracaoImagem5, coracao5X, coracao5Y)

            # colisao com as paredes
            for i in range(len(lista2X)):
                if pygame.Rect(jogadorX, jogadorY, 13, 13).collidepoint(lista2X[i], lista2Y[i]):
                    jogadorX -= jogadorMudançaX
                    jogadorY -= jogadorMudançaY
                            
            # Barreiras
            if jogadorY <= 25:
                jogadorY = 25
            if jogadorY >= 462:
                jogadorY = 462
            if jogadorX <= 25:
                jogadorX = 25
            if jogadorX >= 462:
                jogadorX = 462

            if pygame.Rect(bala1X, bala1Y, 10, 10).collidepoint(bala1X, 0): #se a bala encostar na borda da janela do jogo a variavel auxiliar vai receber o tempo do jogo nesse exato momento
                auxTempoBala1 = tempoMapa2
            if auxTempoBala1 + tempoBala1 == tempoMapa2: # a bala vai ser disparada a cada tempo definido da bala (de 1 a 3) de forma aleatória
                bala1Y = canhao1Y # a bala volta para a posição inicial
                tempoBala1 = randint(1,2)
            if pygame.Rect(bala2X, bala2Y, 10, 10).collidepoint(bala2X, 0):
                auxTempoBala2 = tempoMapa2
            if auxTempoBala2 + tempoBala2 == tempoMapa2:
                bala2Y = canhao2Y
                tempoBala2 = randint(1,2)
            if pygame.Rect(bala3X, bala3Y, 10, 10).collidepoint(bala3X, 0):
                auxTempoBala3 = tempoMapa2
            if auxTempoBala3 + tempoBala3 == tempoMapa2:
                bala3Y = canhao3Y
                tempoBala3 = randint(1,2)
            if pygame.Rect(bala4X, bala4Y, 10, 10).collidepoint(0, bala4Y):
                auxTempoBala4 = tempoMapa2
            if auxTempoBala4 + tempoBala4 == tempoMapa2:
                bala4X = canhao4X
            if jogador.colliderect(bala1) or jogador.colliderect(bala2) or jogador.colliderect(bala3) or jogador.colliderect(bala4):
                time.sleep(1)
                jogadorX = 25
                jogadorY = 60
                vida -= 1
            if vida == 4:
                coracaoImagem5.set_alpha(0)
            elif vida == 3:
                coracaoImagem4.set_alpha(0)
            elif vida == 2:
                coracaoImagem3.set_alpha(0)
            elif vida == 1:
                coracaoImagem2.set_alpha(0)
            if vida == 0:
                sair = True

            if jogador.colliderect(chegada): #passar de mapa
                jogadorX = 452
                jogadorY = 25

                chegadaX = 462
                chegadaY = 462

                velocidade = 2

                while sair != True: #Código do mapa 3
                    janela.fill(preto)
                    
                    desenharMapa(mapa3, 16, 16)
                    

                    jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

                    chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)


                    pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador

                    pygame.draw.rect(janela, branco, (chegada)) # desenha minha chegada
                    
                    pygame.draw.line(janela, azul, [16,20], [484,20], espessura) # barra horizontal superior
                    pygame.draw.line(janela, azul, [20,20], [20, 480], espessura) # barra na vertical esquerda
                    pygame.draw.line(janela, azul, [480,20], [480,480], espessura) # barra vertical direita
                    pygame.draw.line(janela, azul, [16,480], [484,480], espessura) # barra horizontal inferior

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: # evento de fechar o jogo
                            sair = True
                        if event.type == pygame.KEYDOWN: # evento de controle, movimentar o jogador
                            if event.key == pygame.K_LEFT:
                                jogadorMudançaX = - velocidade
                            if event.key == pygame.K_RIGHT:
                                jogadorMudançaX = velocidade   
                            if event.key == pygame.K_UP:
                                jogadorMudançaY = - velocidade
                            if event.key == pygame.K_DOWN:
                                jogadorMudançaY = velocidade
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                                jogadorMudançaX = 0
                            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                                jogadorMudançaY = 0
                    
                    jogadorX += jogadorMudançaX
                    jogadorY += jogadorMudançaY

                    # colisao com as paredes
                    for i in range(len(lista3X)):
                        if pygame.Rect(jogadorX, jogadorY, 13, 13).collidepoint(lista3X[i], lista3Y[i]):
                            jogadorX -= jogadorMudançaX
                            jogadorY -= jogadorMudançaY


                    # Barreiras  #usar funçao 
                    if jogadorY <= 25:
                        jogadorY = 25
                    if jogadorY >= 462:
                        jogadorY = 462
                    if jogadorX <= 25:
                        jogadorX = 25
                    if jogadorX >= 462:
                        jogadorX = 462

                    if jogador.colliderect(chegada):
                        jogadorX = 452
                        jogadorY = 25

                        chegadaX = 25
                        chegadaY = 25


                    pygame.display.flip() 
                    clock.tick(60)
                

            pygame.display.flip()  
            clock.tick(60)


    pygame.display.flip() # atualiza a tela 
    clock.tick(60)


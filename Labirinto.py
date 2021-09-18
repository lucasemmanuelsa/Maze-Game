import time
import pygame
import os
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

# Carregando fonte
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

# posição do canhão 1
canhao1X = 475
canhao1Y = 100

# bala canhao 1
bala1X = canhao1X
bala1Y = canhao1Y + 8
bala1MudançaX = 0
tempoBala1 = randint(1,3)
auxTempoBala1 = -tempoBala1

# posição do canhão 2
canhao2X = 475
canhao2Y = 225

# bala canhao 2
bala2X = canhao2X
bala2Y = canhao2Y + 8
bala2MudançaX = 0
tempoBala2 = randint(1,3)
auxTempoBala2 = -tempoBala2

# posição do canhão 3
canhao3X = 475
canhao3Y = 350

# bala canhao 3
bala3X = canhao3X
bala3Y = canhao3Y + 8
bala3MudançaX = 0
tempoBala3 = randint(1,3)
auxTempoBala3 = -tempoBala3

velocidadeBala = 9
#-----------------------------------------------------------------------------------------------
def criarCanhão(x, y):
    janela.blit(canhaoImagem, (x, y))

def criarCoracao(imagem, x, y):
    janela.blit(imagem, (x, y))

def desenharMapa(mapa, x, y):
    janela.blit(mapa, (x, y))


# imagem do mapa 1
drawGroup = pygame.sprite.Group()
mapa = pygame.sprite.Sprite(drawGroup)
mapa.image = pygame.image.load(os.path.join(diretorio_imagens, 'mapa.png'))
mapa.image = pygame.transform.scale(mapa.image, (510, 510))
mapa.rect = pygame.Rect(-5, -5, 500, 500)

# imagem do mapa 2
mapa2 = pygame.image.load(os.path.join(diretorio_imagens, 'mapa2.png'))
mapa2 = pygame.transform.scale(mapa2, (575, 575))

# imagem do mapa 3
mapa3 = pygame.image.load(os.path.join(diretorio_imagens, 'mapa3.png'))
mapa3 = pygame.transform.scale(mapa3, (465, 465))

# imagem do mapa 4
mapa4 = pygame.image.load(os.path.join(diretorio_imagens, 'mapa4.png'))
mapa4 = pygame.transform.scale(mapa4, (465, 465))

# imagem da chegada
chegada = pygame.image.load(os.path.join(diretorio_imagens, 'chegada.png'))
chegada = pygame.transform.scale(chegada, (16, 16))
rectChegada = chegada.get_rect()

# imagem do jogador
jogadorImagem = pygame.image.load(os.path.join(diretorio_imagens, 'jogador.png'))
rectJogador = jogadorImagem.get_rect()


# Posiçao do jogador
jogadorX = 25 
jogadorY = 25 
jogadorMudançaX = 0
jogadorMudançaY = 0

# Posição da chegada
chegadaX = 438
chegadaY = 27

# Velocidade do jogador
velocidade = 2

# Espessura das paredes limitadoras
espessura = 9

# Contador de vida
vida = 5

# criando a variavel para armazenar o tempo
current_time = 0 

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

drawGroup.draw(janela)

for x in range(500): # pega as coordenadas de cada pixel preto do mapa 
        for y in range(500):
            if janela.get_at((x, y)) == preto:
                listaX.append(x)
                listaY.append(y)

lista2X = []
lista2Y = []


janela.fill(azul)

janela.blit(mapa2, (-38,-38))
for x in range(500):
    for y in range(500):
        if janela.get_at((x,y)) == preto:
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

lista4X = []
lista4Y = []

janela.fill(azul)

desenharMapa(mapa4, 16, 16)

for x in range(500):
    for y in range(500):
        if janela.get_at((x,y)) == preto:
            lista4X.append(x)
            lista4Y.append(y)
#------------------------------------------------------------------------------------------------------
# Game loop, para a janela nao sumir rapidamente e o jogo permanecer rodando. Sem o while o programa fecha, por isso, quando apertar o botao fechar (pygame.QUIT), ele quebra o while e a janela encerra
sair = False
while sair != True: #CÓDIGO REFERENTE AO MAPA 1
    
    current_time = int(pygame.time.get_ticks()/1000) - 3 # contagem do tempo

    janela.fill(preto) # pinta a janela de preto novamente

    cronometro = fonte.render('Tempo: ' + str(current_time), True, branco)
    janela.blit(cronometro, (300, 480)) # adiciona o cronometro na tela

    jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

    #chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)

    bala1 = pygame.Rect(bala1X, bala1Y, 10, 10)
    bala2 = pygame.Rect(bala2X, bala2Y, 10, 10)
    bala3 = pygame.Rect(bala3X, bala3Y, 10, 10)

    for i in range(len(listaX)):
        janela.set_at((listaX[i], listaY[i]), branco)
        
    rectChegada.x = chegadaX
    rectChegada.y = chegadaY

    rectJogador.x = jogadorX
    rectJogador.y = jogadorY
    #pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador
    janela.blit(jogadorImagem, rectJogador)
    janela.blit(chegada, rectChegada)
    #pygame.draw.rect(janela, azul, (chegada)) # desenha minha chegada
    
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
                jogadorImagem = pygame.transform.flip(jogadorImagem, False, False)
                janela.blit(jogadorImagem, rectJogador)                
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
    
    criarCanhão(canhao1X, canhao1Y)
    criarCanhão(canhao2X, canhao2Y)
    criarCanhão(canhao3X, canhao3Y)

    criarCoracao(coracaoImagem1, coracao1X, coracao1Y)
    criarCoracao(coracaoImagem2, coracao2X, coracao2Y)
    criarCoracao(coracaoImagem3, coracao3X, coracao3Y)
    criarCoracao(coracaoImagem4, coracao4X, coracao4Y)
    criarCoracao(coracaoImagem5, coracao5X, coracao5Y)

    
    if pygame.Rect(bala1X, bala1Y, 10, 10).collidepoint(0, bala1Y): #se a bala encostar na borda da janela do jogo a variavel auxiliar vai receber o tempo do jogo nesse exato momento
        auxTempoBala1 = current_time
    if auxTempoBala1 + tempoBala1 == current_time: # a bala vai ser disparada a cada tempo definido da bala (de 1 a 3) de forma aleatória
        bala1X = canhao1X # a bala volta para a posição inicial
        tempoBala1 = randint(1,3)
    if pygame.Rect(bala2X, bala2Y, 10, 10).collidepoint(0, bala2Y):
        auxTempoBala2 = current_time
    if auxTempoBala2 + tempoBala2 == current_time:
        bala2X = canhao2X
        tempoBala2 = randint(1,3)
    if pygame.Rect(bala3X, bala3Y, 10, 10).collidepoint(0, bala3Y):
        auxTempoBala3 = current_time
    if auxTempoBala3 + tempoBala3 == current_time:
        bala3X = canhao3X
        #tempoBala3 = randint(1,3)
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

    if jogador.colliderect(rectChegada):
        # Tela antes do proximo mapa
        janela.fill(preto)
        texto2 = fonte.render('Nível 2', True, branco)
        janela.blit(texto2, (180, 215))
        pygame.display.flip()
        time.sleep(5)

        jogadorX = 452
        jogadorY = 25

        chegadaX = 462
        chegadaY = 462

        velocidade = 3

        while sair != True: #Código do mapa 2
            janela.fill(branco)
            
            janela.blit(mapa2, (-38,-38))

            jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

            chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)


            pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador

            pygame.draw.rect(janela, preto, (chegada)) # desenha minha chegada
            
            pygame.draw.line(janela, preto, [16,20], [484,20], espessura) # barra horizontal superior
            pygame.draw.line(janela, preto, [20,20], [20, 480], espessura) # barra na vertical esquerda
            pygame.draw.line(janela, preto, [480,20], [480,480], espessura) # barra vertical direita
            pygame.draw.line(janela, preto, [16,480], [484,480], espessura) # barra horizontal inferior

            for event in pygame.event.get(): # evento de fechar o jogo
                if event.type == pygame.QUIT:
                    sair = True
                if event.type == pygame.KEYDOWN: # evento das teclas
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
                    
                    


            # Barreiras  #usar funçao 
            if jogadorY <= 25:
                jogadorY = 25
            if jogadorY >= 462:
                jogadorY = 462
            if jogadorX <= 25:
                jogadorX = 25
            if jogadorX >= 462:
                jogadorX = 462

            if jogadorX == chegadaX and jogadorY == chegadaY:
                jogadorX = 452
                jogadorY = 25

                chegadaX = 462
                chegadaY = 462

                velocidade = 2

                while sair != True: #Código do mapa 3
                    janela.fill(roxo)
                    
                    desenharMapa(mapa3, 16, 16)
                    

                    jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

                    chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)


                    pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador

                    pygame.draw.rect(janela, branco, (chegada)) # desenha minha chegada
                    
                    pygame.draw.line(janela, azul, [16,20], [484,20], espessura) # barra horizontal superior
                    pygame.draw.line(janela, azul, [20,20], [20, 480], espessura) # barra na vertical esquerda
                    pygame.draw.line(janela, azul, [480,20], [480,480], espessura) # barra vertical direita
                    pygame.draw.line(janela, azul, [16,480], [484,480], espessura) # barra horizontal inferior

                    for event in pygame.event.get(): # evento de fechar o jogo
                        if event.type == pygame.QUIT:
                            sair = True
                        if event.type == pygame.KEYDOWN: # evento das teclas
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

                    if jogadorX == chegadaX and jogadorY == chegadaY:
                        jogadorX = 452
                        jogadorY = 25

                        chegadaX = 25
                        chegadaY = 25
                        
                        while sair != True: #Código do mapa 4
                            janela.fill(branco)
                            
                            desenharMapa(mapa4, 16, 16)
                            

                            
                            
                            


                            pygame.draw.circle(janela, vermelho, (jogadorX, jogadorY), 8) # desenha meu jogador

                            pygame.draw.circle(janela, azul, (chegadaX, chegadaY), 8) # desenha minha chegada
                            
                            pygame.draw.line(janela, preto, [16,20], [484,20], espessura) # barra horizontal superior
                            pygame.draw.line(janela, preto, [20,20], [20, 480], espessura) # barra na vertical esquerda
                            pygame.draw.line(janela, preto, [480,20], [480,480], espessura) # barra vertical direita
                            pygame.draw.line(janela, preto, [16,480], [484,480], espessura) # barra horizontal inferior

                            for event in pygame.event.get(): # evento de fechar o jogo
                                if event.type == pygame.QUIT:
                                    sair = True
                                if event.type == pygame.KEYDOWN: # evento das teclas
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
                            for i in range(len(lista4X)):
                                if pygame.Rect(jogadorX, jogadorY, 7, 7).collidepoint(lista4X[i], lista4Y[i]):
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

                            if jogadorX == chegadaX and jogadorY == chegadaY:
                                jogadorX = 452
                                jogadorY = 25
                                sair = True

                            pygame.display.flip() # atualiza a tela 
                            clock.tick(60)


                    pygame.display.flip() # atualiza a tela 
                    clock.tick(60)
                

            pygame.display.flip() # atualiza a tela 
            clock.tick(60)


    pygame.display.flip() # atualiza a tela 
    clock.tick(60)


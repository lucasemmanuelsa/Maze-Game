import time
import pygame
import os

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
transparente = (0, 0, 0, 0)

# Carregando fonte
fonte = pygame.font.Font('Gamer.ttf', 55)

# imagem do canhão
canhaoImagem = pygame.image.load(os.path.join(diretorio_imagens, 'canhao.png'))
canhaoImagem = pygame.transform.scale(canhaoImagem, (24, 24))
canhaoImagem = pygame.transform.flip(canhaoImagem, True, False)

# posição do canhão 1
canhao1X = 475
canhao1Y = 100

# posição do canhão 2
canhao2X = 475
canhao2Y = 200

# posição do canhão 3
canhao3X = 475
canhao3Y = 300

# posição do canhão 4
canhao4X = 200
canhao4Y = 475

# bala canhao 1
bala1X = canhao1X
bala1Y = canhao1Y + 8
bala1MudançaX = 0
tempoBala = 3
auxTempo = -3
velocidadeBala = 9

# bala canhao 2
bala2X = canhao2X
bala2Y = canhao2Y + 8
bala2MudançaX = 0

# bala canhao 3
bala3X = canhao3X
bala3Y = canhao3Y + 8
bala3MudançaX = 0

# bala canhao 4
bala4X = canhao4X
bala4Y = canhao4Y

# imagem do mapa
drawGroup = pygame.sprite.Group()
mapa = pygame.sprite.Sprite(drawGroup)
mapa.image = pygame.image.load(os.path.join(diretorio_imagens, 'mapa.png'))
mapa.image = pygame.transform.scale(mapa.image, (510, 510))
mapa.rect = pygame.Rect(-5, -5, 500, 500)



# Posiçao do jogador
jogadorX = 25
jogadorY = 25
jogadorMudançaX = 0
jogadorMudançaY = 0

# Posição da chegada
chegadaX = 438
chegadaY = 27

def criarCanhão(x, y):
    janela.blit(canhaoImagem, (x, y))

janela.fill(preto)  # pinta a cor do fundo

# texto 'Nível 1' antes de começar o jogo
texto = fonte.render('Nível 1', True, vermelho)

janela.blit(texto, (180, 215))

pygame.display.flip()
time.sleep(3)

# Velocidade do jogador
velocidade = 2

# Espessura das paredes
espessura = 9

listaX = []
listaY = []

janela.fill(azul) # pinta a janela de preto novamente

pygame.display.flip()

drawGroup.draw(janela)

for x in range(500): #pega as coordenadas de cada pixel preto do meu mapa 
        for y in range(500):
            if janela.get_at((x, y)) == preto:
                listaX.append(x)
                listaY.append(y)
vida = 5
current_time = 0 #criando a variavel para armazenar o tempo

# Game loop, para a janela nao sumir rapidamente e o jogo permanecer rodando. Sem o while o programa fecha, por isso, quando apertar o botao fechar (pygame.QUIT), ele quebra o while e a janela encerra
sair = False
while sair != True: #CÓDIGO REFERENTE AO MAPA 1
    
    current_time = int(pygame.time.get_ticks()/1000) - 3 # contagem do tempo

    janela.fill(preto) # pinta a janela de preto novamente

    cronometro = fonte.render('Tempo: ' + str(current_time), True, branco)
    janela.blit(cronometro, (155, 500)) # adiciona o cronometro na tela

    jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

    chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)

    bala1 = pygame.Rect(bala1X, bala1Y, 10, 10)

    # drawGroup.draw(janela)
    for i in range(len(listaX)):
        janela.set_at((listaX[i], listaY[i]), branco)
        
   
    pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador

    pygame.draw.rect(janela, azul, (chegada)) # desenha minha chegada

    pygame.draw.rect(janela, rosa, (bala1)) # desenha a bala do canhao 1
    

    pygame.draw.line(janela, branco, [16,20], [484,20], espessura) # barra horizontal superior
    pygame.draw.line(janela, branco, [20,20], [20, 480], espessura) # barra na vertical esquerda
    pygame.draw.line(janela, branco, [480,20], [480,480], espessura) # barra vertical direita
    pygame.draw.line(janela, branco, [16,480], [484,480], espessura) # barra horizontal inferior
    
    bala1MudançaX = - velocidadeBala
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
    
    criarCanhão(canhao1X, canhao1Y)
    
    if pygame.Rect(bala1X, bala1Y, 10, 10).collidepoint(0, bala1Y):
        auxTempo = current_time
    if auxTempo + tempoBala == current_time:
        bala1X = canhao1X
    if jogador.colliderect(bala1):
        time.sleep(1)
        jogadorX = 25
        jogadorY = 25
        vida -= 1
        print(vida)
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
        texto2 = fonte.render('Nível 2', True, branco)
        janela.blit(texto2, (180, 215))
        pygame.display.flip()
        time.sleep(5)

        jogadorX = 452
        jogadorY = 25

        chegadaX = 462
        chegadaY = 462

        while sair != True: #Código do mapa 2
            janela.fill(verdelimao)

            jogador = pygame.Rect(jogadorX, jogadorY, 14, 14)

            chegada = pygame.Rect(chegadaX, chegadaY, 14, 14)

            # drawGroup.draw(janela) / desenharia o segundo mapa

            pygame.draw.rect(janela, vermelho, (jogador)) # desenha meu jogador

            pygame.draw.rect(janela, preto, (chegada)) # desenha minha chegada
            
            pygame.draw.line(janela, branco, [16,20], [484,20], espessura) # barra horizontal superior
            pygame.draw.line(janela, branco, [20,20], [20, 480], espessura) # barra na vertical esquerda
            pygame.draw.line(janela, branco, [480,20], [480,480], espessura) # barra vertical direita
            pygame.draw.line(janela, branco, [16,480], [484,480], espessura) # barra horizontal inferior

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


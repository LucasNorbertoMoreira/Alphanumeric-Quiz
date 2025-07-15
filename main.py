import pygame
import random
import sys
import os
import math

# --- Função para encontrar os ficheiros (assets) ---
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para o PyInstaller """
    try:
        # O PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- CONFIGURAÇÕES INICIAIS ---

pygame.init()
pygame.mixer.init()

BASE_LARGURA, BASE_ALTURA = 1280, 720
LARGURA_TELA, ALTURA_TELA = BASE_LARGURA, BASE_ALTURA
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
pygame.display.set_caption("Adivinhe o Número da Letra")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA_CLARO = (200, 200, 200)
CINZA_ESCURO = (100, 100, 100)
VERDE = (46, 204, 113)
VERMELHO = (231, 76, 60)
AZUL = (52, 152, 219)
AMARELO = (241, 196, 15)
VERMELHO_VINHO = (140, 20, 20)
VERMELHO_BRILHANTE = (190, 40, 40)


# --- Funções para o sistema de recorde ---
ARQUIVO_RECORDE = "recorde.txt"

def carregar_recorde():
    """Carrega o recorde atual do ficheiro."""
    try:
        with open(ARQUIVO_RECORDE, 'r') as f: return int(f.read().strip())
    except (FileNotFoundError, ValueError): return 0

def salvar_recorde(pontuacao):
    """Salva a nova pontuação como recorde no ficheiro."""
    try:
        with open(ARQUIVO_RECORDE, 'w') as f: f.write(str(pontuacao))
    except IOError as e: print(f"Erro ao salvar o recorde: {e}")

# --- Classe para o sistema de partículas ---
class Particula:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.raio = random.randint(3, 8)
        self.cor = random.choice([AZUL, VERDE, AMARELO, BRANCO])
        self.velocidade = random.uniform(2, 6)
        self.angulo = random.uniform(0, 2 * math.pi)
        self.vx, self.vy = math.cos(self.angulo) * self.velocidade, math.sin(self.angulo) * self.velocidade
        self.vida = random.randint(30, 60)

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vida -= 1
        self.vx *= 0.95; self.vy *= 0.95

    def draw(self, superficie):
        alpha = max(0, 255 * (self.vida / 60))
        temp_surf = pygame.Surface((self.raio * 2, self.raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (*self.cor, alpha), (self.raio, self.raio), self.raio)
        superficie.blit(temp_surf, (self.x - self.raio, self.y - self.raio))

# --- Classe para as letras flutuantes do menu ---
class LetraFlutuante:
    def __init__(self, largura_tela, altura_tela):
        self.letra = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.fonte = pygame.font.Font(None, random.randint(40, 120))
        self.x = random.randint(0, largura_tela)
        self.y = random.randint(0, altura_tela)
        self.velocidade_y = random.uniform(0.1, 0.5)
        self.alpha = 0
        self.max_alpha = random.randint(20, 80)
        self.estado = "aparecendo"
        self.tempo_visivel = pygame.time.get_ticks()
        self.duracao_visivel = random.randint(2000, 5000)

    def update(self, largura_tela, altura_tela):
        self.y -= self.velocidade_y
        if self.y < -100:
            self.y = altura_tela + 100
            self.x = random.randint(0, largura_tela)

        if self.estado == "aparecendo":
            self.alpha += 0.5
            if self.alpha >= self.max_alpha:
                self.alpha = self.max_alpha
                self.estado = "visivel"
                self.tempo_visivel = pygame.time.get_ticks()
        elif self.estado == "visivel":
            if pygame.time.get_ticks() - self.tempo_visivel > self.duracao_visivel:
                self.estado = "desaparecendo"
        elif self.estado == "desaparecendo":
            self.alpha -= 0.5
            if self.alpha <= 0:
                self.__init__(largura_tela, altura_tela)

    def draw(self, superficie):
        text_surf = self.fonte.render(self.letra, True, CINZA_ESCURO)
        text_surf.set_alpha(self.alpha)
        superficie.blit(text_surf, (self.x, self.y))

# --- CARREGAMENTO DE ASSETS ---
try:
    fundo_original = pygame.image.load(resource_path("fundo.png")).convert()
except (FileNotFoundError, pygame.error):
    fundo_original = None
fundo = None

try:
    som_acerto = pygame.mixer.Sound(resource_path("acerto.mp3"))
except pygame.error:
    som_acerto = None
try:
    som_erro = pygame.mixer.Sound(resource_path("erro.mp3"))
except pygame.error:
    som_erro = None

try:
    pygame.mixer.music.load(resource_path("musica_fundo.mp3"))
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Aviso: 'musica_fundo.mp3' não encontrada.")


# --- LÓGICA DE ESCALA DINÂMICA ---
fonte_para_emojis, fonte_titulo, fonte_grande, fonte_media, fonte_pequena, fonte_botao, fonte_feedback, fonte_creditos = (None,) * 8
input_rect_dims = {}
reset_button_rect, settings_button_rect, settings_button_menu_rect = None, None, None
music_slider_rect, sfx_slider_rect, music_handle_rect, sfx_handle_rect, settings_close_button_rect = (None,) * 5

def atualizar_elementos_escala(largura, altura):
    global LARGURA_TELA, ALTURA_TELA, tela, fundo
    global fonte_para_emojis, fonte_titulo, fonte_grande, fonte_media, fonte_pequena, fonte_botao, fonte_feedback, fonte_creditos
    global input_rect_dims, reset_button_rect, settings_button_rect, settings_button_menu_rect
    global music_slider_rect, sfx_slider_rect, music_handle_rect, sfx_handle_rect, settings_close_button_rect

    LARGURA_TELA, ALTURA_TELA = largura, altura
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
    escala = ALTURA_TELA / BASE_ALTURA

    if fundo_original:
        fundo = pygame.transform.scale(fundo_original, (LARGURA_TELA, ALTURA_TELA))

    # --- MUDANÇA AQUI: Lógica de carregamento de fontes mais robusta para exportação ---
    tamanho_emoji = int(65 * escala)
    tamanho_feedback = int(48 * escala)
    try:
        # Tenta carregar a fonte incluída no pacote .exe
        caminho_fonte = resource_path("DejaVuSans.ttf")
        fonte_para_emojis = pygame.font.Font(caminho_fonte, tamanho_emoji)
        fonte_feedback = pygame.font.Font(caminho_fonte, tamanho_feedback)
    except (FileNotFoundError, pygame.error):
        # Se falhar, usa a fonte padrão do Pygame (sem emojis)
        print("Aviso: Fonte 'DejaVuSans.ttf' não encontrada. Usando fonte padrão.")
        fonte_para_emojis = pygame.font.Font(None, tamanho_emoji)
        fonte_feedback = pygame.font.Font(None, tamanho_feedback)

    fonte_titulo = pygame.font.Font(None, int(95 * escala))
    fonte_grande = pygame.font.Font(None, int(200 * escala))
    fonte_media = pygame.font.Font(None, int(65 * escala))
    fonte_pequena = pygame.font.Font(None, int(48 * escala))
    fonte_botao = pygame.font.Font(None, int(55 * escala))
    fonte_creditos = pygame.font.Font(None, int(28 * escala))


    rect_w, rect_h = int(450 * escala), int(75 * escala)
    rect_x, rect_y = LARGURA_TELA / 2 - rect_w / 2, ALTURA_TELA / 2
    input_rect_dims = {'rect': (rect_x, rect_y, rect_w, rect_h), 'border': max(1, int(3 * escala)), 'radius': max(1, int(10 * escala))}

    button_size = int(60 * escala)
    margem_x_botao = LARGURA_TELA * 0.03
    reset_button_rect = pygame.Rect(LARGURA_TELA - margem_x_botao - button_size, (ALTURA_TELA / 2) - (button_size / 2), button_size, button_size)
    settings_button_rect = pygame.Rect(margem_x_botao, (ALTURA_TELA / 2) - (button_size / 2), button_size, button_size)
    settings_button_menu_rect = pygame.Rect(margem_x_botao, ALTURA_TELA - margem_x_botao - button_size, button_size, button_size)

    slider_w, slider_h = int(400 * escala), int(20 * escala)
    handle_w, handle_h = int(30 * escala), int(40 * escala)
    music_slider_rect = pygame.Rect((LARGURA_TELA - slider_w) / 2, ALTURA_TELA * 0.4, slider_w, slider_h)
    sfx_slider_rect = pygame.Rect((LARGURA_TELA - slider_w) / 2, ALTURA_TELA * 0.6, slider_w, slider_h)
    music_handle_rect = pygame.Rect(0, 0, handle_w, handle_h)
    sfx_handle_rect = pygame.Rect(0, 0, handle_w, handle_h)
    close_button_size = int(50 * escala)
    settings_close_button_rect = pygame.Rect(LARGURA_TELA / 2 + slider_w / 2 + 20*escala, ALTURA_TELA * 0.2 - close_button_size/2, close_button_size, close_button_size)


atualizar_elementos_escala(LARGURA_TELA, ALTURA_TELA)
relogio = pygame.time.Clock()

# --- DADOS DO JOGO ---
letras_numeros = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20, 'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26}
todas_letras = list(letras_numeros.keys())

mensagens_acerto = ["Acertou! :D", "Parabéns! :P", "Excelente! :]", "Correto! ☆", "Perfeito! :)", "Acertou em cheio!", "Magnífico! O_O", "Sem erros por aqui!", "Cravou ;)", "Impressionante!", "Mandou bem!", "Que precisão! 10/10", "Arrasou!", "Resposta exata!", "Brilhante! ☆"]
mensagens_erro_perto = ["Errado! Foi por pouco... :(", "Quase lá! Tente de novo."]
mensagens_erro_medio = ["Errado! Esta no caminho certo.", "Não foi dessa vez, mais uma!"]
mensagens_erro_longe = ["Errado! Um pouco longe...:L", "Hmm, a resposta e outra."]
recorde_atual = carregar_recorde()

# --- FUNÇÕES AUXILIARES ---
def desenhar_texto(texto, fonte, cor, superficie, x, y, align="center", scale=1.0):
    textobj = fonte.render(texto, True, cor)
    if scale != 1.0:
        orig_w, orig_h = textobj.get_size()
        if orig_w > 0 and orig_h > 0:
            textobj = pygame.transform.smoothscale(textobj, (int(orig_w * scale), int(orig_h * scale)))
    textrect = textobj.get_rect()
    if align == "center": textrect.center = (x, y)
    elif align == "topleft": textrect.topleft = (x, y)
    elif align == "topright": textrect.topright = (x, y)
    superficie.blit(textobj, textrect)

def desenhar_texto_com_quebra(texto, fonte, cor, superficie, rect):
    palavras = texto.split(' '); linhas, linha_atual = [], ""
    for palavra in palavras:
        teste_linha = linha_atual + palavra + " "
        if fonte.size(teste_linha)[0] < rect.width: linha_atual = teste_linha
        else: linhas.append(linha_atual); linha_atual = palavra + " "
    linhas.append(linha_atual)
    y = rect.top
    for linha in linhas:
        text_surf = fonte.render(linha, True, cor)
        text_rect = text_surf.get_rect(centerx=rect.centerx, top=y)
        superficie.blit(text_surf, text_rect)
        y += fonte.get_linesize()

def fade_out_transicao():
    fade_surface = pygame.Surface((LARGURA_TELA, ALTURA_TELA)); fade_surface.fill(PRETO)
    for alpha in range(0, 255, 15):
        fade_surface.set_alpha(alpha); tela.blit(fade_surface, (0, 0))
        pygame.display.flip(); pygame.time.delay(10)

def resetar_jogo():
    global pontuacao, vidas, acertos_consecutivos, letras_erradas_info, dificuldade_mantida, nivel_atual_exibido
    global letra_sorteada, numero_correto, input_usuario, feedback, feedback_cor, estado_jogo, recorde_atual
    global ultimo_feedback, historico_letras, particulas, shake_timer, letra_escala, animacao_letra_ativa
    pontuacao, vidas, acertos_consecutivos = 0, 3, 0
    letras_erradas_info = []
    dificuldade_mantida, nivel_atual_exibido = 0, -1
    input_usuario, feedback, feedback_cor = "", "", BRANCO
    ultimo_feedback = ""; historico_letras = []; particulas = []
    shake_timer = 0; letra_escala = 0.1; animacao_letra_ativa = True
    estado_jogo = "jogando"
    recorde_atual = carregar_recorde()
    letra_sorteada, numero_correto = sortear_nova_letra()

def sortear_nova_letra():
    global historico_letras, letra_escala, animacao_letra_ativa
    if dificuldade_mantida == 0: letras_disponiveis = todas_letras[:10]
    elif dificuldade_mantida == 1: letras_disponiveis = todas_letras[:15]
    else: letras_disponiveis = todas_letras
    pool_de_letras = [letra for letra in letras_disponiveis if letra not in historico_letras]
    if not pool_de_letras: pool_de_letras = letras_disponiveis
    nova_letra = random.choice(pool_de_letras)
    historico_letras.append(nova_letra)
    if len(historico_letras) > 5:
        historico_letras.pop(0)
    letra_escala = 0.1
    animacao_letra_ativa = True
    return nova_letra, letras_numeros[nova_letra]

# --- INICIALIZAÇÃO DAS VARIÁVEIS ---
estado_jogo = "menu"
pontuacao, vidas, acertos_consecutivos = 0, 3, 0
letras_erradas_info, dificuldade_mantida, nivel_atual_exibido = [], 0, -1
letra_sorteada, numero_correto, input_usuario, feedback, feedback_cor = "", 0, "", "", BRANCO
proximo_nome_nivel, proximo_descricao_nivel = "", ""
ultimo_feedback, historico_letras = "", []
volume_musica, volume_sfx = 0.05, 1.0
dragging_music_handle, dragging_sfx_handle = False, False
particulas, shake_timer, letra_escala, animacao_letra_ativa = [], 0, 1.0, False
letras_flutuantes = [LetraFlutuante(LARGURA_TELA, ALTURA_TELA) for _ in range(15)]

# --- LOOP PRINCIPAL DO JOGO ---
rodando = True
while rodando:
    mouse_pos = pygame.mouse.get_pos()
    # --- PROCESSAMENTO DE EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: rodando = False
        if event.type == pygame.VIDEORESIZE:
            largura, altura = max(event.w, 640), max(event.h, 360)
            atualizar_elementos_escala(largura, altura)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if estado_jogo == "jogando":
                    if reset_button_rect.collidepoint(event.pos): estado_jogo = "confirmando_reset"
                    if settings_button_rect.collidepoint(event.pos): estado_jogo = "settings"
                elif estado_jogo == "menu":
                    if settings_button_menu_rect.collidepoint(event.pos): estado_jogo = "settings"
                elif estado_jogo == "settings":
                    if music_handle_rect.collidepoint(event.pos): dragging_music_handle = True
                    if sfx_handle_rect.collidepoint(event.pos): dragging_sfx_handle = True
                    if settings_close_button_rect.collidepoint(event.pos): estado_jogo = "jogando" if pontuacao > 0 or vidas < 3 else "menu"

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: dragging_music_handle, dragging_sfx_handle = False, False
        
        if event.type == pygame.MOUSEMOTION:
            if dragging_music_handle:
                music_handle_rect.centerx = max(music_slider_rect.left, min(event.pos[0], music_slider_rect.right))
                volume_musica = (music_handle_rect.centerx - music_slider_rect.left) / music_slider_rect.width
                pygame.mixer.music.set_volume(volume_musica)
            if dragging_sfx_handle:
                sfx_handle_rect.centerx = max(sfx_slider_rect.left, min(event.pos[0], sfx_slider_rect.right))
                volume_sfx = (sfx_handle_rect.centerx - sfx_slider_rect.left) / sfx_slider_rect.width
                if som_acerto: som_acerto.set_volume(volume_sfx)
                if som_erro: som_erro.set_volume(volume_sfx)

        if event.type == pygame.KEYDOWN:
            if estado_jogo == "jogando":
                if event.key == pygame.K_RETURN:
                    try:
                        resposta = int(input_usuario)
                        if resposta == numero_correto:
                            acertos_consecutivos += 1; pontuacao += 1
                            nova_mensagem = random.choice(mensagens_acerto)
                            while len(mensagens_acerto) > 1 and nova_mensagem == ultimo_feedback: nova_mensagem = random.choice(mensagens_acerto)
                            feedback, ultimo_feedback = nova_mensagem, nova_mensagem
                            feedback_cor = VERDE
                            if som_acerto: som_acerto.play()
                            for _ in range(30): particulas.append(Particula(LARGURA_TELA / 2, ALTURA_TELA / 3))
                            if acertos_consecutivos > 0:
                                if acertos_consecutivos % 100 == 0: pontuacao += 100; feedback = f" ☆ LEGENDÁRIO! +100 PONTOS!  ☆"
                                elif acertos_consecutivos % 50 == 0: pontuacao += 50; feedback = f" ☆ INCRÍVEL! +50 PONTOS!  ☆"
                                elif acertos_consecutivos % 25 == 0: pontuacao += 25; feedback = f" ☆ ESPETACULAR! +25 PONTOS!  ☆"
                                elif acertos_consecutivos % 10 == 0: pontuacao += 10; feedback += f" +10 BÔNUS!"
                                elif acertos_consecutivos % 5 == 0: pontuacao += 5; feedback += f" +5 BÔNUS!"
                        else:
                            vidas -= 1; shake_timer = 15
                            diferenca = abs(resposta - numero_correto)
                            if diferenca <= 2: lista_erros = mensagens_erro_perto
                            elif diferenca <= 5: lista_erros = mensagens_erro_medio
                            else: lista_erros = mensagens_erro_longe
                            nova_mensagem = random.choice(lista_erros)
                            while len(lista_erros) > 1 and nova_mensagem == ultimo_feedback: nova_mensagem = random.choice(lista_erros)
                            feedback, ultimo_feedback = nova_mensagem, nova_mensagem
                            acertos_consecutivos = 0
                            letras_erradas_info.append((letra_sorteada, numero_correto))
                            feedback_cor = VERMELHO
                            if som_erro: som_erro.play()
                            if vidas <= 0: estado_jogo = "fim_de_jogo"
                        if estado_jogo == "jogando": letra_sorteada, numero_correto = sortear_nova_letra()
                    except ValueError:
                        feedback = "Digite apenas números!"; feedback_cor = AMARELO
                    input_usuario = ""
                elif event.key == pygame.K_BACKSPACE: input_usuario = input_usuario[:-1]
                else:
                    if event.unicode.isdigit(): input_usuario += event.unicode
            
            elif estado_jogo == "menu":
                if event.key == pygame.K_SPACE: fade_out_transicao(); resetar_jogo()
            elif estado_jogo == "fim_de_jogo":
                if event.key == pygame.K_SPACE: fade_out_transicao(); resetar_jogo()
            elif estado_jogo == "confirmando_dificuldade":
                if event.key == pygame.K_s: estado_jogo = "jogando"; nivel_atual_exibido = dificuldade_mantida
                elif event.key == pygame.K_n: estado_jogo = "menu"
            elif estado_jogo == "confirmando_reset":
                if event.key == pygame.K_s: estado_jogo = "menu"
                elif event.key == pygame.K_n: estado_jogo = "jogando"
            elif estado_jogo == "settings":
                if event.key == pygame.K_ESCAPE: estado_jogo = "jogando" if pontuacao > 0 or vidas < 3 else "menu"

    # --- LÓGICA DE ATUALIZAÇÃO ---
    if estado_jogo == "jogando":
        if acertos_consecutivos < 5: proximo_nivel_id = 0
        elif acertos_consecutivos < 10: proximo_nivel_id = 1
        else: proximo_nivel_id = 2
        if proximo_nivel_id > dificuldade_mantida:
            dificuldade_mantida = proximo_nivel_id
            if dificuldade_mantida == 1: proximo_nome_nivel, proximo_descricao_nivel = "Médio", "Letras de A a O"
            else: proximo_nome_nivel, proximo_descricao_nivel = "Difícil", "Todo o alfabeto"
            estado_jogo = "confirmando_dificuldade"
    
    if animacao_letra_ativa:
        letra_escala += 0.08
        if letra_escala >= 1.0: letra_escala = 1.0; animacao_letra_ativa = False
    
    for particula in particulas[:]:
        particula.update()
        if particula.vida <= 0: particulas.remove(particula)
    
    if estado_jogo == "menu":
        for letra in letras_flutuantes:
            letra.update(LARGURA_TELA, ALTURA_TELA)

    # --- DESENHO NA TELA ---
    offset_x, offset_y = 0, 0
    if shake_timer > 0:
        shake_timer -= 1; offset_x, offset_y = random.randint(-8, 8), random.randint(-8, 8)

    tela_desenho = tela
    if shake_timer > 0: tela_desenho = tela.copy()

    if fundo: tela_desenho.blit(fundo, (0, 0))
    else: tela_desenho.fill(PRETO)

    if estado_jogo == "menu":
        for letra in letras_flutuantes: letra.draw(tela_desenho)
        desenhar_texto("Adivinhe o Número da Letra", fonte_titulo, BRANCO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA / 4)
        desenhar_texto(f"RECORDE: {recorde_atual}", fonte_media, AMARELO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.4)
        desenhar_texto("Pressione ESPAÇO para começar", fonte_media, AZUL, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.55)
        desenhar_texto("Digite o número da letra e pressione Enter.", fonte_pequena, CINZA_CLARO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.7)
        cor_settings_botao = CINZA_CLARO if settings_button_menu_rect.collidepoint(mouse_pos) else CINZA_ESCURO
        pygame.draw.rect(tela_desenho, cor_settings_botao, settings_button_menu_rect, border_radius=int(settings_button_menu_rect.width / 2))
        desenhar_texto("⚙️", fonte_para_emojis, BRANCO, tela_desenho, settings_button_menu_rect.centerx, settings_button_menu_rect.centery)

    elif estado_jogo == "jogando" or estado_jogo == "confirmando_reset":
        margem = ALTURA_TELA * 0.05
        desenhar_texto(f"Pontuação: {pontuacao}", fonte_media, AMARELO, tela_desenho, margem, margem, align="topleft")
        desenhar_texto(f"Vidas: {'❤️' * vidas}", fonte_para_emojis, VERMELHO, tela_desenho, LARGURA_TELA - margem, margem, align="topright")
        cor_reset_botao = VERMELHO_BRILHANTE if reset_button_rect.collidepoint(mouse_pos) else VERMELHO_VINHO
        pygame.draw.rect(tela_desenho, cor_reset_botao, reset_button_rect, border_radius=int(reset_button_rect.width / 2))
        desenhar_texto("X", fonte_botao, BRANCO, tela_desenho, reset_button_rect.centerx, reset_button_rect.centery + (3 * (ALTURA_TELA/BASE_ALTURA)))
        cor_settings_botao = CINZA_CLARO if settings_button_rect.collidepoint(mouse_pos) else CINZA_ESCURO
        pygame.draw.rect(tela_desenho, cor_settings_botao, settings_button_rect, border_radius=int(settings_button_rect.width / 2))
        desenhar_texto("⚙️", fonte_para_emojis, BRANCO, tela_desenho, settings_button_rect.centerx, settings_button_rect.centery)
        desenhar_texto(letra_sorteada, fonte_grande, AZUL, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA / 3, scale=letra_escala)
        pygame.draw.rect(tela_desenho, CINZA_CLARO, input_rect_dims['rect'], input_rect_dims['border'], border_radius=input_rect_dims['radius'])
        desenhar_texto(input_usuario, fonte_media, BRANCO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA / 2 + input_rect_dims['rect'][3] / 2)
        feedback_rect = pygame.Rect(LARGURA_TELA * 0.1, ALTURA_TELA * 0.65, LARGURA_TELA * 0.8, ALTURA_TELA * 0.2)
        desenhar_texto_com_quebra(feedback, fonte_feedback, feedback_cor, tela_desenho, feedback_rect)
        if estado_jogo == "confirmando_reset":
            overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); tela_desenho.blit(overlay, (0, 0))
            desenhar_texto("Voltar ao Menu Principal?", fonte_titulo, AMARELO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA / 3)
            desenhar_texto("Todo o progresso da partida será perdido.", fonte_pequena, CINZA_CLARO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.5)
            desenhar_texto("Pressione [S] para confirmar ou [N] para cancelar", fonte_media, BRANCO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.65)

    elif estado_jogo == "confirmando_dificuldade":
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); tela_desenho.blit(overlay, (0, 0))
        desenhar_texto("NOVO NÍVEL!", fonte_titulo, AMARELO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA / 3)
        desenhar_texto(f"Dificuldade aumentada para {proximo_nome_nivel} ({proximo_descricao_nivel})", fonte_media, BRANCO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.5)
        desenhar_texto("Pressione [S] para continuar ou [N] para voltar ao menu", fonte_pequena, AMARELO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.75)

    elif estado_jogo == "settings":
        if fundo: tela_desenho.blit(fundo, (0, 0))
        else: tela_desenho.fill(PRETO)
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); tela_desenho.blit(overlay, (0, 0))
        pygame.draw.rect(tela_desenho, PRETO, (LARGURA_TELA * 0.2, ALTURA_TELA * 0.2, LARGURA_TELA * 0.6, ALTURA_TELA * 0.6), border_radius=20)
        pygame.draw.rect(tela_desenho, AZUL, (LARGURA_TELA * 0.2, ALTURA_TELA * 0.2, LARGURA_TELA * 0.6, ALTURA_TELA * 0.6), 5, border_radius=20)
        desenhar_texto("Configurações de Áudio", fonte_media, BRANCO, tela_desenho, LARGURA_TELA / 2, ALTURA_TELA * 0.25)
        desenhar_texto("Música", fonte_pequena, BRANCO, tela_desenho, LARGURA_TELA/2, music_slider_rect.y - 30)
        pygame.draw.rect(tela_desenho, CINZA_ESCURO, music_slider_rect, border_radius=10)
        music_handle_rect.center = (music_slider_rect.left + music_slider_rect.width * volume_musica, music_slider_rect.centery)
        pygame.draw.rect(tela_desenho, AZUL, music_handle_rect, border_radius=8)
        desenhar_texto("Efeitos Sonoros", fonte_pequena, BRANCO, tela_desenho, LARGURA_TELA/2, sfx_slider_rect.y - 30)
        pygame.draw.rect(tela_desenho, CINZA_ESCURO, sfx_slider_rect, border_radius=10)
        sfx_handle_rect.center = (sfx_slider_rect.left + sfx_slider_rect.width * volume_sfx, sfx_slider_rect.centery)
        pygame.draw.rect(tela_desenho, AZUL, sfx_handle_rect, border_radius=8)
        cor_close_botao = VERMELHO_BRILHANTE if settings_close_button_rect.collidepoint(mouse_pos) else VERMELHO_VINHO
        pygame.draw.rect(tela_desenho, cor_close_botao, settings_close_button_rect, border_radius=int(settings_close_button_rect.width/2))
        desenhar_texto("X", fonte_botao, BRANCO, tela_desenho, settings_close_button_rect.centerx, settings_close_button_rect.centery + (3 * (ALTURA_TELA/BASE_ALTURA)))

    elif estado_jogo == "fim_de_jogo":
        if pontuacao > recorde_atual:
            salvar_recorde(pontuacao); recorde_atual = pontuacao
            desenhar_texto("NOVO RECORDE!", fonte_titulo, AMARELO, tela, LARGURA_TELA / 2, ALTURA_TELA / 4)
        else:
            desenhar_texto("FIM DE JOGO", fonte_titulo, VERMELHO, tela, LARGURA_TELA / 2, ALTURA_TELA / 4)
        desenhar_texto(f"Pontuação Final: {pontuacao}", fonte_media, BRANCO, tela, LARGURA_TELA / 2, ALTURA_TELA / 2)
        if letras_erradas_info:
            desenhar_texto("Respostas corretas:", fonte_pequena, CINZA_CLARO, tela, LARGURA_TELA / 2, ALTURA_TELA * 0.60)
            pos_y = ALTURA_TELA * 0.65
            texto_erradas = ", ".join([f"{letra} = {num}" for letra, num in letras_erradas_info])
            desenhar_texto(texto_erradas, fonte_pequena, BRANCO, tela, LARGURA_TELA / 2, pos_y)
        desenhar_texto("Pressione ESPAÇO para jogar novamente", fonte_media, AMARELO, tela, LARGURA_TELA / 2, ALTURA_TELA * 0.77)

    # Desenhando os créditos em todas as telas
    margem_creditos = ALTURA_TELA * 0.04
    desenhar_texto("Por: Lucas N :)", fonte_creditos, CINZA_CLARO, tela_desenho, LARGURA_TELA - margem_creditos, ALTURA_TELA - margem_creditos, align="topright")

    for particula in particulas:
        particula.draw(tela_desenho)

    if shake_timer > 0:
        tela.blit(tela_desenho, (offset_x, offset_y))
    
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()
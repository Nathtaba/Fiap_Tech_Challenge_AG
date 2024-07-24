## Configuração Inicial: Importação de bibliotecas
import pygame
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
matplotlib.use("Agg") #O backend "Agg"  não depende de uma interface gráfica de usuário (GUI) 
# e é utilizado para renderizar gráficos em arquivos (como PNGs) em vez de exibi-los em uma janela interativa
import itertools
import textwrap
import math

#Definição de funções iniciais para cálculos e criação de rotas.

# Função para calcular a distância euclidiana entre duas coordenadas que representa distâncias reais em quilômetros
def calcular_distancia(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

# Função para calcular a distância total de uma rota
def calcular_distancia_total(rota, coordenadas_cidades):
    distancia_total = 0
    for i in range(len(rota) - 1):
        cidade_atual = cidades[rota[i]]
        proxima_cidade = cidades[rota[i + 1]]
        distancia_total += calcular_distancia(coordenadas_cidades[cidade_atual], coordenadas_cidades[proxima_cidade])
    # Adicionar a volta para a cidade inicial
    cidade_final = cidades[rota[-1]]
    cidade_inicial = cidades[rota[0]]
    distancia_total += calcular_distancia(coordenadas_cidades[cidade_final], coordenadas_cidades[cidade_inicial])
    return distancia_total

# Função para criar um indivíduo (rota aleatória) começando e terminando em Porto Alegre.
def criar_individuo(n_cidades):
    individuo = list(range(1, n_cidades))  # Começa de 1 para não incluir Porto Alegre (índice 0)
    random.shuffle(individuo)
    individuo = [0] + individuo + [0]  # Adiciona Porto Alegre no início e no fim
    return individuo

# Função para criar uma população inicial de indivíduos.
def gerar_populacao_inicial(tamanho_populacao, n_cidades):
    return [criar_individuo(n_cidades) for _ in range(tamanho_populacao)]

# Função que aplica mutação em um indivíduo com uma certa probabilidade. Troca duas posições aleatórias na rota.
def mutacao(individuo, taxa_mutacao):
    if random.random() < taxa_mutacao:
        i, j = random.sample(range(1, len(individuo) - 1), 2)  # Não inclui o primeiro e o último índice
        individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo

# Função de crossover (cruzamento) realiza o cruzamento entre dois pais para gerar um filho. 
# Garante que o filho contenha genes de ambos os pais sem repetições.
def cruzamento(pai1, pai2):
    tamanho = len(pai1)
    inicio, fim = sorted(random.sample(range(1, tamanho - 1), 2))
    filho = [None] * tamanho
    filho[0] = filho[-1] = 0  # Garantir que Porto Alegre esteja no início e no fim
    filho[inicio:fim] = pai1[inicio:fim]

    pointer = 1
    for gene in pai2:
        if gene not in filho:
            while filho[pointer] is not None:
                pointer += 1
            filho[pointer] = gene

    return filho

# Função de seleção por torneio onde seleciona um indivíduo com base em um torneio entre vários indivíduos da população.
def selecao_por_torneio(populacao, k=3):
    torneio = random.sample(populacao, k)
    torneio.sort(key=lambda x: calcular_distancia_total(x, coordenadas_cidades))
    return torneio[0]

# Função para avaliar a aptidão (distância total) de todos os indivíduos da população.
def avaliar_populacao(populacao, coordenadas_cidades):
    return [calcular_distancia_total(individuo, coordenadas_cidades) for individuo in populacao]

# Função para ordenar a população com base na aptidão dos indivíduos.
def ordenar_populacao(populacao, aptidao):
    return [ind for ind, _ in sorted(zip(populacao, aptidao), key=lambda x: x[1])]

# Configurações do Pygame para definição de largura, altura, taxa de atualização, cores e inicialização do Pygame.
WIDTH, HEIGHT = 1200, 800  # Ajustar largura para incluir o gráfico
NODE_RADIUS = 8
FPS = 30
MAP_X_OFFSET = 500  # Deslocar as cidades para o lado direito da janela

# GA
POPULATION_SIZE = 50
MUTATION_PROBABILITY = 0.05

# Definir cores do gráfico
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 139)
GREEN = (0, 255, 0)

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Melhor Rota - RS by Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1

# Leitura do banco de dados onde carrega os dados de um arquivo Excel contendo informações geoespaciais das cidades
df = pd.read_excel('Pesquisa_Dados_e_Mapas.xlsx')

# Inicialização das coordenadas definindo as coordenadas de Porto Alegre e preenche as coordenadas para as demais cidades do dataset.
coordenadas_cidades = {}
cidades = ['Porto Alegre'] + df['Municípios'].tolist()

# Definir coordenadas de Porto Alegre
coordenadas_cidades['Porto Alegre'] = (-51206533,-30031771)  # Coordenadas reais de PA.

# Preencher coordenadas para outras cidades conforme arquivo xlsx
for cidade in cidades[1:]:
    x_coord = int(df.loc[df['Municípios'] == cidade, 'Coordenadas X'].iloc[0])
    y_coord = int(df.loc[df['Municípios'] == cidade, 'Coordenadas Y'].iloc[0])
    coordenadas_cidades[cidade] = (x_coord, y_coord)
    
# Definir os limites da tela para a visualização das cidades na tela do Pygame.
X_MIN, X_MAX = MAP_X_OFFSET, 1100
Y_MIN, Y_MAX = 30, 630

# Obter limites das coordenadas reais
latitudes = [coord[0] for coord in coordenadas_cidades.values()]
longitudes = [coord[1] for coord in coordenadas_cidades.values()]
lat_min, lat_max = min(latitudes), max(latitudes)
lon_min, lon_max = min(longitudes), max(longitudes)

# Função para normalizar coordenadas para a tela do Pygame
def normalizar_coord(coord, min_real, max_real, min_screen, max_screen):
    return int(min_screen + (coord - min_real) / (max_real - min_real) * (max_screen - min_screen))

def rotacionar_90_graus(x, y, x_max, y_max):
    # Rotaciona (x, y) 90 graus para a direita em torno do ponto médio (centro do mapa)
    x_centro = (MAP_X_OFFSET + X_MAX) // 2
    y_centro = (Y_MIN + Y_MAX) // 2
    
    # Translada o ponto para que o centro do mapa seja a origem
    x_trans = x - x_centro
    y_trans = y - y_centro
    
    # Aplica a rotação
    x_rot = y_trans
    y_rot = -x_trans
    
    # Translada de volta para a posição original
    x_novo = x_rot + x_centro
    y_novo = y_rot + y_centro
    
    return x_novo, y_novo

# Preencher coordenadas normalizadas
for cidade, (lat, lon) in coordenadas_cidades.items():
    # Normaliza as coordenadas
    x_coord = normalizar_coord(lon, lon_min, lon_max, MAP_X_OFFSET+20, X_MAX-20)
    y_coord = normalizar_coord(lat, lat_min, lat_max, Y_MIN, Y_MAX)
    
    # Rotaciona as coordenadas
    x_rot, y_rot = rotacionar_90_graus(x_coord, y_coord, X_MAX-20, Y_MAX)
    
    # Atualiza o dicionário com as novas coordenadas
    coordenadas_cidades[cidade] = (int(x_rot), int(y_rot))

# Preencher coordenadas normalizadas
""" for cidade, (lat, lon) in coordenadas_cidades.items():
    x_coord = normalizar_coord(lon, lon_min, lon_max, MAP_X_OFFSET, X_MAX)
    y_coord = normalizar_coord(lat, lat_min, lat_max, Y_MIN, Y_MAX)
    coordenadas_cidades[cidade] = (int(x_coord), int(y_coord))  # Convertendo para inteiros """

# Função para desenhar as cidades na tela do Pygame, utilizando diferentes cores para Porto Alegre e outras cidades.
def draw_cities(screen, coordenadas, color, radius):
    for cidade, (x, y) in coordenadas.items():
        cor = GREEN if cidade == 'Porto Alegre' else color
        # Verificar se a cidade está dentro dos limites da tela antes de desenhar
        if X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX:
            pygame.draw.circle(screen, cor, (x, y), radius)
            pygame.draw.circle(screen, BLACK, (x, y), radius, 1)  # Borda preta
            # Desenhar nome da cidade próximo ao círculo
            font = pygame.font.SysFont(None, 20)
            text = font.render(cidade, True, BLACK)
            text_rect = text.get_rect(center=(x + radius + 10, y+10))
            screen.blit(text, text_rect)
            
# Função para desenha os caminhos da melhor rota encontrada na tela.
def draw_paths(screen, path, color, width=1):
    for i in range(len(path) - 1):
        cidade_atual = cidades[path[i]]
        proxima_cidade = cidades[path[i + 1]]
        pygame.draw.line(screen, color, coordenadas_cidades[cidade_atual], coordenadas_cidades[proxima_cidade], width)
    # Adicionar a volta para a cidade inicial Porto Alegre
    cidade_final = cidades[path[-1]]
    cidade_inicial = cidades[path[0]]
    pygame.draw.line(screen, color, coordenadas_cidades[cidade_final], coordenadas_cidades[cidade_inicial], width)

# Função para desenhar um gráfico de fitness (distância ao longo das gerações) na tela do Pygame.
def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Geração', y_label: str = 'Aptidão') -> None:
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.plot(x, y)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    plt.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0, 0))

def draw_directions(screen, font_size=20):
    font = pygame.font.SysFont(None, font_size)
    
    # Norte
    north_text = font.render("N", True, DARK_BLUE)
    north_rect = north_text.get_rect(center=(MAP_X_OFFSET + (X_MAX - MAP_X_OFFSET) // 2, Y_MIN - 10))
    screen.blit(north_text, north_rect)
    
    # Sul
    south_text = font.render("S", True, DARK_BLUE)
    south_rect = south_text.get_rect(center=(MAP_X_OFFSET + (X_MAX - MAP_X_OFFSET) // 2, Y_MAX + 10))
    screen.blit(south_text, south_rect)
    
    # Leste
    east_text = font.render("E", True, DARK_BLUE)
    east_rect = east_text.get_rect(center=(X_MAX + 20, Y_MIN + (Y_MAX - Y_MIN) // 2))
    screen.blit(east_text, east_rect)
    
    # Oeste
    west_text = font.render("W", True, DARK_BLUE)
    west_rect = west_text.get_rect(center=(MAP_X_OFFSET - 50, Y_MIN + (Y_MAX - Y_MIN) // 2))
    screen.blit(west_text, west_rect)


# Define um retângulo na tela do Pygame para exibir informações como geração, melhor aptidão e caminho da melhor solução.
info_rect = pygame.Rect(10, HEIGHT - 150, 1100, 140)
    
# Função para renderizar as informações dentro do retângulo definido na tela do Pygame.
def render_info_frame(screen, rect, generation, melhor_aptidao, nomes_melhor_solucao):
    pygame.draw.rect(screen, WHITE, rect)  # Limpar área do quadro
    pygame.draw.rect(screen, BLACK, rect, 2)  # Desenhar borda do quadro
    
    # Definir margens e espaçamentos
    margin = 10
    line_height = 20
    
    font = pygame.font.SysFont(None, 25)
    
    # Renderizar geração
    generation_text = font.render(f"Geração: {generation}°", True, BLACK)
    screen.blit(generation_text, (rect.left + margin, rect.top + margin))
    
    # Renderizar melhor aptidão
    Day = math.ceil(((melhor_aptidao*2)/60)/24) #calcula em quantos dias aproximadamente realizará a rota
    aptidao_text = font.render(f"Melhor aptidão: {round(melhor_aptidao, 2)} km", True, BLACK)
    screen.blit(aptidao_text, (rect.left + margin, rect.top + margin + line_height))
    
    # Converter índices de cidade para nomes de cidades
    nomes_melhor_solucao = [cidades[indice] for indice in melhor_solucao]
    
    # Renderizar caminho da melhor solução
    path_text = f"Melhor rota: {', '.join(nomes_melhor_solucao)}"
    # Quebrar o texto em várias linhas
    lines = textwrap.wrap(path_text, width=110)  # Quebrar em linhas de até 110 caracteres
    for i, line in enumerate(lines):
        path_line = font.render(line, True, BLACK)
        screen.blit(path_line, (rect.left + margin, rect.top + margin + line_height * (i + 2)))

    # Atualizar a tela
    pygame.display.flip()
        
# Gerar população inicial de rotas
populacao = gerar_populacao_inicial(POPULATION_SIZE, len(cidades))
# Listas para armazenar a melhor aptidão e as melhores soluções encontradas ao longo das gerações.
melhor_aptidao_valores = []
melhores_solucoes = []

# Definir quantidade máxima de gerações
#MAX_GENERATIONS = 1000  # Ajuste conforme necessário

# LOOP PRINCIPAL no Pygame
running = True # Variável de controle para manter o loop do Pygame em execução.
while running:
    for event in pygame.event.get(): #Captura eventos como fechar a janela ou pressionar uma tecla para encerrar o programa.
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
                
    generation = next(generation_counter) #Contador de geração atual.

    # Caso queira definir uma quantidade máxima de gerações
    #if generation > MAX_GENERATIONS:
        #running = False

    aptidao_populacao = avaliar_populacao(populacao, coordenadas_cidades) #Avalia a aptidão de toda a população.

    populacao = ordenar_populacao(populacao, aptidao_populacao) #Ordena a população com base na aptidão.

    #Armazenam a melhor aptidão e a melhor solução da população atual.
    melhor_aptidao = calcular_distancia_total(populacao[0], coordenadas_cidades)
    melhor_solucao = populacao[0] 
    melhor_aptidao_valores.append(melhor_aptidao)
    melhores_solucoes.append(melhor_solucao)
    
    screen.fill(WHITE)

    # Desenha as cidades e a rota
    draw_cities(screen, coordenadas_cidades, RED, NODE_RADIUS)
    
    draw_paths(screen, melhor_solucao, BLUE, width=3)
    draw_paths(screen, populacao[1], (128, 128, 128), width=1)
    
    # Desenha o gráfico de fitness na tela do Pygame
    draw_plot(screen, list(range(len(melhor_aptidao_valores))), 
              melhor_aptidao_valores, y_label="Aptidão - Distancia (km)")
    
    nomes_melhor_solucao = [cidades[indice] for indice in melhor_solucao]
    
    # Exibi as informações de geração, melhor aptidão e melhor caminho na tela do Pygame.
    render_info_frame(screen, info_rect, generation, melhor_aptidao, nomes_melhor_solucao)

    # Desenha as direções (N, S, E, W) na tela do Pygame
    draw_directions(screen, 40)


     # Exibir informações no terminal
    print('--------------------------------------------------------')
    print(f"Geração {generation}: \nMelhor aptidão Km = {round(melhor_aptidao, 2)}\nRota: {nomes_melhor_solucao}")

    nova_populacao = populacao[:10] #Gera uma nova população com seleção por torneio, cruzamento e mutação.
    while len(nova_populacao) < POPULATION_SIZE:
        pai1 = selecao_por_torneio(populacao)
        pai2 = selecao_por_torneio(populacao)
        filho = cruzamento(pai1, pai2)
        filho = mutacao(filho, MUTATION_PROBABILITY)
        nova_populacao.append(filho)
    
    populacao = nova_populacao

    #Atualiza a tela do Pygame e controla a taxa de quadros por segundo.
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

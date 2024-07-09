import pygame
from pygame.locals import *
import random
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib
#O backend "Agg"  não depende de uma interface gráfica de usuário (GUI) 
# e é utilizado para renderizar gráficos em arquivos (como PNGs) em vez de exibi-los em uma janela interativa
matplotlib.use("Agg")
from typing import List, Tuple
import itertools
import textwrap
import math

# Defina a escala de conversão de pixels para metros
PIXEL_TO_METER_RATIO = 1  # 1 pixel = 1 metro, ajuste conforme necessário

# Função para calcular a distância euclidiana entre duas coordenadas
def calcular_distancia(coord1, coord2):
    return np.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

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

# Função para criar um indivíduo (rota aleatória)
def criar_individuo(n_cidades):
    individuo = list(range(1, n_cidades))  # Começa de 1 para não incluir Porto Alegre (índice 0)
    random.shuffle(individuo)
    individuo = [0] + individuo + [0]  # Adiciona Porto Alegre no início e no fim
    return individuo

# Função para gerar a população inicial
def gerar_populacao_inicial(tamanho_populacao, n_cidades):
    return [criar_individuo(n_cidades) for _ in range(tamanho_populacao)]

# Função de mutação
def mutacao(individuo, taxa_mutacao):
    if random.random() < taxa_mutacao:
        i, j = random.sample(range(1, len(individuo) - 1), 2)  # Não inclui o primeiro e o último índice
        individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo

# Função de crossover (cruzamento)
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

# Função de seleção por torneio
def selecao_por_torneio(populacao, k=3):
    torneio = random.sample(populacao, k)
    torneio.sort(key=lambda x: calcular_distancia_total(x, coordenadas_cidades))
    return torneio[0]

# Função para avaliar a população
def avaliar_populacao(populacao, coordenadas_cidades):
    return [calcular_distancia_total(individuo, coordenadas_cidades) for individuo in populacao]

# Função para ordenar a população por aptidão
def ordenar_populacao(populacao, aptidao):
    return [ind for ind, _ in sorted(zip(populacao, aptidao), key=lambda x: x[1])]

# Configurações do Pygame
WIDTH, HEIGHT = 1200, 800  # Ajustar largura para incluir o gráfico
NODE_RADIUS = 8
FPS = 30
MAP_X_OFFSET = 600  # Deslocar as cidades para o lado direito da janela

# GA
POPULATION_SIZE = 50
MUTATION_PROBABILITY = 0.05

# Definir cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Best Path - RS by Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1

# Leitura do banco de dados
df = pd.read_excel('Pesquisa_Dados_e_Mapas.xlsx')

# Inicialização das coordenadas das cidades
coordenadas_cidades = {}
cidades = ['Porto Alegre'] + df['Municípios'].tolist()

# Definir coordenadas de Porto Alegre (exemplo, ajustar conforme necessário)
coordenadas_cidades['Porto Alegre'] = (-51206533,-30031771)  # Exemplo de coordenadas

# Preencher coordenadas para outras cidades
for cidade in cidades[1:]:
    x_coord = int(df.loc[df['Municípios'] == cidade, 'Coordenadas X'].iloc[0])
    y_coord = int(df.loc[df['Municípios'] == cidade, 'Coordenadas Y'].iloc[0])
    coordenadas_cidades[cidade] = (x_coord, y_coord)
    
# Definir os limites da tela
X_MIN, X_MAX = MAP_X_OFFSET, 1000
Y_MIN, Y_MAX = 50, 600

# Obter limites das coordenadas reais
latitudes = [coord[0] for coord in coordenadas_cidades.values()]
longitudes = [coord[1] for coord in coordenadas_cidades.values()]
lat_min, lat_max = min(latitudes), max(latitudes)
lon_min, lon_max = min(longitudes), max(longitudes)

# Função para normalizar coordenadas para a tela do Pygame
def normalizar_coord(coord, min_real, max_real, min_screen, max_screen):
    return int(min_screen + (coord - min_real) / (max_real - min_real) * (max_screen - min_screen))

# Preencher coordenadas normalizadas
for cidade, (lat, lon) in coordenadas_cidades.items():
    x_coord = normalizar_coord(lat, lat_min, lat_max, X_MIN, X_MAX)
    y_coord = HEIGHT - normalizar_coord(lon, lon_min, lon_max, Y_MIN, Y_MAX)  # Inverter a coordenada Y
    coordenadas_cidades[cidade] = (int(x_coord), int(y_coord))  # Convertendo para inteiros

# Funções de desenho
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
            text_rect = text.get_rect(center=(x + radius + 10, y))
            screen.blit(text, text_rect)

def draw_paths(screen, path, color, width=1):
    for i in range(len(path) - 1):
        cidade_atual = cidades[path[i]]
        proxima_cidade = cidades[path[i + 1]]
        pygame.draw.line(screen, color, coordenadas_cidades[cidade_atual], coordenadas_cidades[proxima_cidade], width)
    # Adicionar a volta para a cidade inicial
    cidade_final = cidades[path[-1]]
    cidade_inicial = cidades[path[0]]
    pygame.draw.line(screen, color, coordenadas_cidades[cidade_final], coordenadas_cidades[cidade_inicial], width)


def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Generation', y_label: str = 'Fitness') -> None:
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

# Definir retângulo para informações
info_rect = pygame.Rect(10, HEIGHT - 150, 1100, 140)
    
# Função para renderizar texto na tela do Pygame
def render_info_frame(screen, rect, generation, melhor_aptidao, nomes_melhor_solucao):
    pygame.draw.rect(screen, WHITE, rect)  # Limpar área do quadro
    pygame.draw.rect(screen, BLACK, rect, 2)  # Desenhar borda do quadro
    
    # Definir margens e espaçamentos
    margin = 10
    line_height = 20
    
    font = pygame.font.SysFont(None, 25)
    
    # Renderizar geração
    generation_text = font.render(f"Generation: {generation}°", True, BLACK)
    screen.blit(generation_text, (rect.left + margin, rect.top + margin))
    
    # Renderizar melhor aptidão
    Day = math.ceil(((melhor_aptidao*2)/60)/24) #calcula em quantos dias aproximadamente realizará a rota
    aptidao_text = font.render(f"Best Fitness: {round(melhor_aptidao, 2)} km - ~ {Day} days", True, BLACK)
    screen.blit(aptidao_text, (rect.left + margin, rect.top + margin + line_height))
    
    # Converter índices de cidade para nomes de cidades
    nomes_melhor_solucao = [cidades[indice] for indice in melhor_solucao]
    
    # Renderizar caminho da melhor solução (quebrando em várias linhas se necessário)
    path_text = f"Best Path: {', '.join(nomes_melhor_solucao)}"
    # Quebrar o texto em várias linhas
    lines = textwrap.wrap(path_text, width=110)  # Quebrar em linhas de até 30 caracteres
    for i, line in enumerate(lines):
        path_line = font.render(line, True, BLACK)
        screen.blit(path_line, (rect.left + margin, rect.top + margin + line_height * (i + 2)))

    # Atualizar a tela
    pygame.display.flip()
        
# Gerar população inicial
populacao = gerar_populacao_inicial(POPULATION_SIZE, len(cidades))
melhor_aptidao_valores = []
melhores_solucoes = []

# Definir quantidade máxima de gerações
#MAX_GENERATIONS = 1000  # Ajuste conforme necessário

# Loop principal do Pygame
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
                
    generation = next(generation_counter)
    
    # Verificar se atingiu a quantidade máxima de gerações
    #if generation > MAX_GENERATIONS:
        #running = False

    aptidao_populacao = avaliar_populacao(populacao, coordenadas_cidades)

    populacao = ordenar_populacao(populacao, aptidao_populacao)

    melhor_aptidao = calcular_distancia_total(populacao[0], coordenadas_cidades)
    melhor_solucao = populacao[0]
    
    melhor_aptidao_valores.append(melhor_aptidao)
    melhores_solucoes.append(melhor_solucao)
    
    screen.fill(WHITE)

    # Desenhar cidades e caminho
    draw_cities(screen, coordenadas_cidades, RED, NODE_RADIUS)
    
    draw_paths(screen, melhor_solucao, BLUE, width=3)
    draw_paths(screen, populacao[1], (128, 128, 128), width=1)
    
    # Desenhar gráfico
    draw_plot(screen, list(range(len(melhor_aptidao_valores))), 
              melhor_aptidao_valores, y_label="Fitness - Distance (pxls)")
    
    nomes_melhor_solucao = [cidades[indice] for indice in melhor_solucao]
    
    # Exibir informações na tela
    render_info_frame(screen, info_rect, generation, melhor_aptidao, nomes_melhor_solucao)


     # Exibir informações no terminal
    print('--------------------------------------------------------')
    print(f"Generation {generation}: \nBest fitness KM = {round(melhor_aptidao, 2)}\nPath: {nomes_melhor_solucao}")

    nova_populacao = populacao[:10]
    while len(nova_populacao) < POPULATION_SIZE:
        pai1 = selecao_por_torneio(populacao)
        pai2 = selecao_por_torneio(populacao)
        filho = cruzamento(pai1, pai2)
        filho = mutacao(filho, MUTATION_PROBABILITY)
        nova_populacao.append(filho)
    
    populacao = nova_populacao

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

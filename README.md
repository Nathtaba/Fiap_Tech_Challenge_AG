# Otimização de Rotas com Algoritmos Genéticos em Pygame

Este projeto implementa um algoritmo genético para resolver o Tech Challenge Fase 2 da Fiap utilizando Pygame para visualização. A rota é otimizada para minimizar a distância total percorrida por um caminhão que sai de Porto Alegre, visita algumas cidades do Rio Grande do Sul e retorna a Porto Alegre.

## Requisitos

- Python 3.7 ou superior
- Pygame
- NumPy
- Pandas
- Matplotlib

## Instalação

1. Clone este repositório:
    ```
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. Instale as dependências:
    ```
    pip install pygame numpy pandas matplotlib
    ```

3. Certifique-se de ter o arquivo de dados `Pesquisa_Dados_e_Mapas.xlsx` no mesmo diretório que o script.

Guias do arquivo:
- Fixo: base dos dados que serão utilizados no ato da execução
- Dados: banco de dados completo
  
Obs: Escolha as cidades que gostaria de simular e adicione na guia "Fixo" do arquivo.

## Uso

Execute o script com o seguinte comando:
```
python Tech_Challenge_RS.py
```

## Estrutura do Código

- calcular_distancia: Calcula a distância euclidiana entre duas coordenadas.
- calcular_distancia_total: Calcula a distância total de uma rota.
- criar_individuo: Cria uma rota aleatória (indivíduo).
- gerar_populacao_inicial: Gera a população inicial de rotas.
- mutacao: Aplica mutação em uma rota.
- cruzamento: Realiza o cruzamento (crossover) entre duas rotas.
- selecao_por_torneio: Seleciona uma rota utilizando o método de torneio.
- avaliar_populacao: Avalia a aptidão (distância total) de cada rota na população.
- ordenar_populacao: Ordena a população com base na aptidão.
- draw_cities: Desenha as cidades no Pygame.
- draw_paths: Desenha as rotas no Pygame.
- draw_plot: Desenha o gráfico de aptidão no Pygame.
- render_info_frame: Renderiza um quadro com informações na tela do Pygame.

## Funcionalidades

- Visualização das cidades e das rotas no Pygame.
- Algoritmo genético para otimização da rota.
- Gráfico de aptidão mostrando a melhoria ao longo das gerações.
- Quadro de informações no canto inferior esquerdo da tela mostrando a geração atual, a melhor aptidão e o melhor caminho.

## Personalização

- MAP_X_OFFSET: Ajusta o deslocamento das cidades na tela do Pygame.
- POPULATION_SIZE: Ajusta o tamanho da população.
- MUTATION_PROBABILITY: Ajusta a probabilidade de mutação.
- INFO_RECT: Ajusta a posição e dimensões do quadro de informações.

## Fonte dos Dados
Site: http://feedados.fee.tche.br/feedados/#!home/listarvariaveis (Caracterização do Território\Distância de Porto Alegre\2023 (km))

O arquivo Pesquisa_Dados_e_Mapas.xlsx foi obtido no site do Departamento Autônomo de Estradas de Rodagem do Rio Grande do Sul e contém dados de coordenadas das cidades do Rio Grande do Sul.


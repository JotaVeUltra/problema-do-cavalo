from functools import reduce
from itertools import product
from random import randint, shuffle, choices


def cruzar(individuo_a, individuo_b, corte, mutação, tipo_mutação):
    cromossomo_a = individuo_a['cromossomo']
    cromossomo_b = individuo_b['cromossomo']
    cromossomo_filho_a = cromossomo_a[:corte] + crossover(cromossomo_a[:corte], cromossomo_b[:])
    cromossomo_filho_b = cromossomo_b[:corte] + crossover(cromossomo_b[:corte], cromossomo_a[:])
    if mutação:  # inserção
        tipo_mutação(cromossomo_filho_a)
        tipo_mutação(cromossomo_filho_b)

    return [calcular_fenotipo(cromossomo_filho_a), calcular_fenotipo(cromossomo_filho_b)]


def crossover(corte_individuo_a, copia_individuo_b):
    for gene in corte_individuo_a:
        if gene in copia_individuo_b:
            copia_individuo_b.remove(gene)
    return copia_individuo_b


def inserção(filho):
    posição_1 = randint(0, len(filho) - 1)
    posição_2 = randint(0, len(filho) - 1)
    gene = filho.pop(posição_1)
    filho.insert(posição_2, gene)


def swap(filho):
    posição_1 = randint(0, len(filho) - 1)
    gene1 = filho.pop(posição_1)
    posição_2 = randint(0, len(filho) - 1)
    gene2 = filho.pop(posição_2)
    filho.insert(posição_2, gene1)
    filho.insert(posição_1, gene2)


def troca_de_posições_aleatória(filho):
    posição_1 = randint(0, len(filho) - 1)
    posição_2 = randint(0, len(filho) - 1)
    menor = posição_1 if posição_1 < posição_2 else posição_2
    tamanho = abs(posição_2 - posição_1)
    gene = []
    for i in range(tamanho):
        gene.append(filho.pop(menor))
    shuffle(gene)
    for i in range(tamanho):
        filho.insert(menor, gene.pop())


def inversão(filho):
    posição_1 = randint(0, len(filho) - 1)
    posição_2 = randint(0, len(filho) - 1)
    menor = posição_1 if posição_1 < posição_2 else posição_2
    tamanho = abs(posição_2 - posição_1)
    gene = []
    for i in range(tamanho):
        gene.append(filho.pop(menor))
    gene.reverse()
    for i in range(tamanho):
        filho.insert(menor, gene.pop())


def gerar_grafo_movimentos():
    grafo = [[[] for coluna in range(8)] for linha in range(8)]
    vertices = gerar_vertices()
    for x, y in vertices:
        grafo[x][y] = [v for v in vertices if
                       ((abs(v[0] - x) + abs(v[1] - y)) == 3) and abs(v[0] - x) < 3 and abs(v[1] - y) < 3]
    return grafo


def gerar_vertices():
    return [tuple(vertice) for vertice in product(range(8), repeat=2)]


def gerar_individuo():
    cromossomo = gerar_vertices()
    shuffle(cromossomo)
    return calcular_fenotipo(cromossomo)


def calcular_fenotipo(cromossomo):
    score = avaliar_adaptação(cromossomo)
    return {'cromossomo': cromossomo, 'score': score}


def gerar_população(tamanho_população):
    return [gerar_individuo() for _ in range(tamanho_população)]


def avaliar_adaptação(individuo):
    global grafo
    segmentos_de_caminho = 0
    for i, v in enumerate(individuo[:len(individuo) - 1]):
        if individuo[i + 1] not in grafo[v[0]][v[1]]:
            segmentos_de_caminho += 1
    return segmentos_de_caminho


def calcular_media(população):
    if len(população) == 0: return 0
    return sum(individuo['score'] for individuo in população) / len(população)


def buscar_melhor_adaptado(população):
    return reduce(lambda x, y: x if x['score'] < y['score'] else y, população)


def executar(gerações, tamanho_população, taxa_mutação, cruzamento_por_geração, tipo_mutação):
    população = gerar_população(tamanho_população)
    melhor_adaptado_da_geração = buscar_melhor_adaptado(população)
    melhor_adaptado = melhor_adaptado_da_geração
    for geração in range(gerações):
        if geração % 100 == 0:
            print(f'geração: {geração}')
            print(f'média da população: {calcular_media(população)}')
            print(f'melhor adaptado: {melhor_adaptado["score"]}')
            print(f'melhor adaptado da geração: {melhor_adaptado_da_geração["score"]}')
            print('-----------------------------------------')
        shuffle(população)
        reprodutores = população[:cruzamento_por_geração]
        nova_população = [individuo for individuo in população if individuo not in reprodutores]
        while reprodutores:
            mutação = randint(0, 100) <= taxa_mutação
            individuo_a = reprodutores.pop()
            individuo_b = reprodutores.pop()
            nova_população.append(individuo_a)
            nova_população.append(individuo_b)
            corte = randint(2, 62)
            nova_população += cruzar(individuo_a, individuo_b, corte, mutação, tipo_mutação)

        melhor_adaptado_da_geração = buscar_melhor_adaptado(nova_população)
        if melhor_adaptado_da_geração['score'] < melhor_adaptado['score']:
            melhor_adaptado = melhor_adaptado_da_geração
        if melhor_adaptado['score'] == 0:
            break
        população = roleta(nova_população, tamanho_população)

    média = calcular_media(população)
    return média, melhor_adaptado


def roleta(população, tamanho_população):
    weights = [(abs(individuo['score'] - 63) ** 7) for individuo in população]
    return choices(população, weights=weights, k=tamanho_população)


def elitismo(população):
    return sorted(população, key=lambda x: avaliar_adaptação(x['cromossomo']))[:int(len(população) / 2)]


def expectativa(população, geração):
    return [individuo for individuo in população if individuo['expectativa'] > geração]


def representar_tabuleiro(cromossomo):
    tabuleiro = []
    for l in range(8):
        linha = []
        for c in range(8):
            linha.append(f'{cromossomo.index((l,c)):02}')
        f_linha = '-'.join(linha)
        tabuleiro.append(f_linha)
    print('\n'.join(tabuleiro))


########################################################################################################################


GERAÇÕES = 100_000
TAMANHO_POPULAÇÃO = 100
TAXA_MUTAÇÃO = 5  # %
CRUZAMENTO_POR_GERAÇÃO = 80
TIPO_MUTAÇÃO = inversão

grafo = gerar_grafo_movimentos()

resultados_experimento = executar(GERAÇÕES,
                                  TAMANHO_POPULAÇÃO,
                                  TAXA_MUTAÇÃO,
                                  CRUZAMENTO_POR_GERAÇÃO,
                                  TIPO_MUTAÇÃO)

print(f'tipo de mutação: {TIPO_MUTAÇÃO.__name__}')
print(f'gerações: {GERAÇÕES}')
print(f'tamanho da população: {TAMANHO_POPULAÇÃO}')
print(f'cruzamento por geração: {CRUZAMENTO_POR_GERAÇÃO}')
print(f'taxa de mutação: {TAXA_MUTAÇÃO}')
print(f'média da população: {resultados_experimento[0]}')
print(f'indivíduo mais adaptado: {resultados_experimento[1]["cromossomo"]}')
print(f'segmentos: {resultados_experimento[1]["score"]}')
print('-------------------------------------------------------------')


representar_tabuleiro(resultados_experimento[1]["cromossomo"])

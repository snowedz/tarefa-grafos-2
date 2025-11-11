import numpy as np
import matplotlib.pyplot as plt
import heapq
import math


# Funções iniciais
def distancia(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def orientacao(a,b,c): # Comparar se 3 pontos são colineares ou qual direção é feita a curva
    val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
    if val == 0: 
        return 0 # colineares
    elif val > 0: 
        return 1 # curva horária
    else:
        return 2 # anti-horária

def intersecao(p1, q1, p2, q2): # Verifica se p1-q1 cruza p2-q2
    if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
        return False
    
    o1 = orientacao(p1, q1, p2)
    o2 = orientacao(p1, q1, q2)
    o3 = orientacao(p2, q2, p1)
    o4 = orientacao(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True
    return False

# Leitura do mapa
with open("mapa.txt", "r") as f:
    linhas = f.readlines()
    linhas = [linha.strip() for linha in linhas if linha.strip()]

q_start = tuple(map(float, linhas[0].split(',')))
q_goal = tuple(map(float, linhas[1].split(',')))
n_obs = int(linhas[2])
idx = 3
obstaculos = []

for _ in range(n_obs):
    n_vertices = int(linhas[idx])
    idx += 1
    vertices = []
    for _ in range(n_vertices):
        x, y = map(float, linhas[idx].split(','))
        vertices.append((x,y))
        idx += 1
    obstaculos.append(vertices)

arvore_vertices = [q_start, q_goal]
for obs in obstaculos:
    arvore_vertices.extend(obs)

# Construção do grafo de visibilidade
def grafo_visibilidade(vertices,obstaculos):
    arestas = []
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            p1 = vertices[i]
            p2 = vertices[j]
            visivel = True
            for obs in obstaculos:
                for k in range(len(obs)):
                    q1 = obs[k]
                    q2 = obs[(k+1) % len(obs)]
                    if intersecao(p1, p2, q1, q2):
                        visivel = False
                        break
                if not visivel:
                    break
            if visivel:
                arestas.append((i, j, distancia(p1, p2)))
    return arestas

# Algoritmo de Kruskal
class Uniao:
    def __init__(self, n):
        self.parent = list(range(n))
    def find(self,x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self,x,y):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[ry] = rx

def kruskal(n, arestas):
    uniao = Uniao(n)
    mst = []
    for u, v, peso in sorted(arestas, key=lambda x: x[2]):
        if uniao.find(u) != uniao.find(v):
            uniao.union(u, v)
            mst.append((u, v, peso))
    return mst

def verticeMaisProximo(pos, vertices):
    return min(range(len(vertices)), key=lambda i: distancia(pos, vertices[i]))

# Algoritmo de busca
def busca_caminho(arvore, inicio, fim):
    adj = {i: [] for i in range(len(arvore_vertices))}
    for u, v, _ in arvore:
        adj[u].append(v)
        adj[v].append(u)
    visitado = set()
    caminho = []
    def dfs(atual):
        if atual == fim:
            caminho.append(atual)
            return True
        visitado.add(atual)
        for vizinho in adj[atual]:
            if vizinho not in visitado:
                if dfs(vizinho):
                    caminho.append(atual)
                    return True
        return False
    dfs(inicio)
    return list(reversed(caminho))

def plot_mapa(q_start, q_goal, obstaculos):
    plt.figure(figsize=(8, 8))
    for obs in obstaculos:
        xs, ys = zip(*obs)
        plt.fill(xs, ys, color='lightgray', edgecolor='black')
    plt.scatter(*q_start, c='green', s=100, label='Início')
    plt.scatter(*q_goal, c='red', s=100, label='Fim')
    plt.legend()
    plt.axis('equal')
    plt.savefig("mapa.png")

def plotar(q_start, q_goal, obstaculos, vertices, arestas, arvore, caminho):
    plt.figure(figsize=(8, 8))
    for obs in obstaculos:
        xs, ys = zip(*obs)
        plt.fill(xs, ys, color='lightgray', edgecolor='black')


    for u, v, _ in arestas:
        plt.plot([vertices[u][0], vertices[v][0]], [vertices[u][1], vertices[v][1]], 'b--', alpha=0.3)


    for u, v, _ in arvore:
        plt.plot([vertices[u][0], vertices[v][0]], [vertices[u][1], vertices[v][1]], 'g-', lw=2)


    cam_pts = [vertices[i] for i in caminho]
    plt.plot([p[0] for p in cam_pts], [p[1] for p in cam_pts], 'r-', lw=3, label='Caminho')


    plt.scatter(*zip(*vertices), c='black')
    plt.scatter(*q_start, c='green', s=100, label='Início')
    plt.scatter(*q_goal, c='red', s=100, label='Fim')


    plt.legend()
    plt.axis('equal')
    plt.savefig("saida.png")
    plt.show()


arestas = grafo_visibilidade(arvore_vertices, obstaculos)
arvore = kruskal(len(arvore_vertices), arestas)
inicio = verticeMaisProximo(q_start, arvore_vertices)
fim = verticeMaisProximo(q_goal, arvore_vertices)
caminho = busca_caminho(arvore, inicio, fim)

print('Caminho encontrado (índices):', caminho)
plot_mapa(q_start, q_goal, obstaculos)
plotar(q_start, q_goal, obstaculos, arvore_vertices, arestas, arvore, caminho)

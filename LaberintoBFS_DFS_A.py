import tkinter as tk
from tkinter import ttk
from collections import deque
from heapq import heappush, heappop

CELDA, FILAS, COLUMNAS = 26, 20, 28

def manhattan(a, b): 
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

class LaberintoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Laberinto: BFS, DFS y A*")
        self.resizable(False, False)
        self.mapa = [[0]*COLUMNAS for _ in range(FILAS)]  # 0 libre, 1 pared
        self.inicio, self.meta = (0,0), (FILAS-1, COLUMNAS-1)
        self.camino, self.poner_inicio_siguiente = [], False

        izquierda = ttk.Frame(self); izquierda.grid(row=0, column=0, padx=6, pady=6)
        derecha = ttk.Frame(self); derecha.grid(row=0, column=1, padx=6, pady=6, sticky="ns")

        self.canvas = tk.Canvas(izquierda, width=COLUMNAS*CELDA, height=FILAS*CELDA, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.cambiar_pared)
        self.canvas.bind("<Button-3>", self.poner_punto)

        self.algoritmo = tk.StringVar(value="A*")
        ttk.Label(derecha, text="Algoritmo:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(derecha, textvariable=self.algoritmo, values=["BFS","DFS","A*"], state="readonly", width=18)\
            .grid(row=1, column=0, sticky="ew", pady=2)

        ttk.Button(derecha, text="Resolver", command=self.resolver).grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Button(derecha, text="Limpiar camino", command=self.limpiar_camino).grid(row=3, column=0, sticky="ew", pady=2)
        ttk.Button(derecha, text="Limpiar paredes", command=self.limpiar_paredes).grid(row=4, column=0, sticky="ew", pady=2)
        ttk.Label(derecha, text="Izq: pared/libre\nDer: alterna inicio→meta").grid(row=5, column=0, pady=(8,0))
        ttk.Label(derecha, wraplength=200,
                  text="Notas: BFS halla ruta más corta (costos unitarios). "
                       "DFS no garantiza óptimo. A* (f=g+h) es óptimo con heurística admisible.").grid(row=6, column=0, pady=(8,0))

        self.dibujar_todo()

    def dibujar_celda(self, fila, col, color):
        x0, y0 = col*CELDA, fila*CELDA
        self.canvas.create_rectangle(x0, y0, x0+CELDA, y0+CELDA, fill=color, outline="#ddd")

    def dibujar_todo(self):
        self.canvas.delete("all")
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                self.dibujar_celda(fila, col, "black" if self.mapa[fila][col] else "white")
        for (f,c) in self.camino:
            if (f,c) not in (self.inicio, self.meta):
                self.dibujar_celda(f, c, "#74c0fc")
        self.dibujar_celda(*self.inicio, "#52b788")
        self.dibujar_celda(*self.meta, "#e76f51")


    def dentro_limites(self, fila, col): 
        return 0 <= fila < FILAS and 0 <= col < COLUMNAS

    def vecinos(self, fila, col):
        for df,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nf, nc = fila+df, col+dc
            if self.dentro_limites(nf,nc) and self.mapa[nf][nc]==0:
                yield (nf,nc)

    def cambiar_pared(self, e):
        col, fila = e.x//CELDA, e.y//CELDA
        if not self.dentro_limites(fila,col) or (fila,col) in (self.inicio, self.meta): return
        self.mapa[fila][col] ^= 1
        self.limpiar_camino(dibujar=False); self.dibujar_todo()

    def poner_punto(self, e):
        col, fila = e.x//CELDA, e.y//CELDA
        if not self.dentro_limites(fila,col) or self.mapa[fila][col]==1: return
        if self.poner_inicio_siguiente: self.inicio = (fila,col)
        else: self.meta = (fila,col)
        self.poner_inicio_siguiente = not self.poner_inicio_siguiente
        self.limpiar_camino(dibujar=False); self.dibujar_todo()

    def limpiar_camino(self, dibujar=True):
        self.camino = []
        if dibujar: self.dibujar_todo()

    def limpiar_paredes(self):
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                self.mapa[fila][col] = 0
        self.limpiar_camino()

    def reconstruir(self, padres, fin):
        actual, resultado = fin, []
        while actual in padres:
            resultado.append(actual)
            actual = padres[actual]
        return list(reversed(resultado))

    def ejecutar_bfs(self):
        inicio, meta = self.inicio, self.meta
        cola, visitados, padres = deque([inicio]), {inicio}, {}
        while cola:
            actual = cola.popleft()
            if actual == meta: return self.reconstruir(padres, meta)
            for vecino in self.vecinos(*actual):
                if vecino not in visitados:
                    visitados.add(vecino); padres[vecino] = actual; cola.append(vecino)
        return []

    def ejecutar_dfs(self):
        inicio, meta = self.inicio, self.meta
        pila, visitados, padres = [inicio], {inicio}, {}
        while pila:
            actual = pila.pop()
            if actual == meta: return self.reconstruir(padres, meta)
            for vecino in self.vecinos(*actual):
                if vecino not in visitados:
                    visitados.add(vecino); padres[vecino] = actual; pila.append(vecino)
        return []

    def ejecutar_astar(self):
        inicio, meta = self.inicio, self.meta
        costo_g, padres, cerrados, cola = {inicio:0}, {}, set(), []
        heappush(cola, (manhattan(inicio,meta), inicio))
        while cola:
            _, actual = heappop(cola)
            if actual in cerrados: continue
            cerrados.add(actual)
            if actual == meta: return self.reconstruir(padres, meta)
            for vecino in self.vecinos(*actual):
                nuevo_g = costo_g[actual] + 1
                if vecino not in costo_g or nuevo_g < costo_g[vecino]:
                    costo_g[vecino] = nuevo_g; padres[vecino] = actual
                    heappush(cola, (nuevo_g + manhattan(vecino,meta), vecino))
        return []

    def resolver(self):
        self.limpiar_camino(dibujar=False)
        eleccion = self.algoritmo.get()
        if eleccion == "BFS": self.camino = self.ejecutar_bfs()
        elif eleccion == "DFS": self.camino = self.ejecutar_dfs()
        else: self.camino = self.ejecutar_astar()
        self.dibujar_todo()

if __name__ == "__main__":
    LaberintoApp().mainloop()

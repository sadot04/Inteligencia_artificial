import tkinter as tk
from tkinter import ttk, messagebox

N = 9  # tamaño del tablero 9x9

class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku CSP: BT + Poda hacia adelante + MRV")
        self.resizable(False, False)

   
        marco_grilla = ttk.Frame(self); marco_grilla.grid(row=0, column=0, padx=6, pady=6)
        self.celdas = [[tk.Entry(marco_grilla, width=2, justify="center", font=("Consolas", 16)) for _ in range(N)] for _ in range(N)]
        for fila in range(N):
            for col in range(N):
                padx = (0 if col%3 else 4, 2)
                pady = (0 if fila%3 else 4, 2)
                self.celdas[fila][col].grid(row=fila, column=col, padx=padx, pady=pady)

 
        lateral = ttk.Frame(self); lateral.grid(row=0, column=1, padx=6, pady=6, sticky="ns")
        ttk.Button(lateral, text="Resolver", command=self.resolver).grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(lateral, text="Limpiar", command=self.limpiar).grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Button(lateral, text="Ejemplo", command=self.cargar_ejemplo).grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Label(lateral, text="MRV: elige la celda con menor dominio.\nPoda hacia adelante: reduce dominios tras asignar.").grid(row=3, column=0, pady=(8,0))

    def leer_tablero(self):
        tablero = [[0]*N for _ in range(N)]
        for fila in range(N):
            for col in range(N):
                valor = self.celdas[fila][col].get().strip()
                tablero[fila][col] = int(valor) if valor.isdigit() and 1 <= int(valor) <= 9 else 0
        return tablero

    def mostrar_tablero(self, tablero):
        for fila in range(N):
            for col in range(N):
                self.celdas[fila][col].delete(0, tk.END)
                if tablero[fila][col] != 0:
                    self.celdas[fila][col].insert(0, str(tablero[fila][col]))

    def limpiar(self):
        for fila in range(N):
            for col in range(N):
                self.celdas[fila][col].delete(0, tk.END)

    def cargar_ejemplo(self):
        ejemplo = [
            [0,0,0,2,6,0,7,0,1],
            [6,8,0,0,7,0,0,9,0],
            [1,9,0,0,0,4,5,0,0],
            [8,2,0,1,0,0,0,4,0],
            [0,0,4,6,0,2,9,0,0],
            [0,5,0,0,0,3,0,2,8],
            [0,0,9,3,0,0,0,7,4],
            [0,4,0,0,5,0,0,3,6],
            [7,0,3,0,1,8,0,0,0],
        ]
        self.mostrar_tablero(ejemplo)

    # --- Restricciones CSP ---
    def vecinos(self, fila, col):
        
        mismos_fila = [(fila, j) for j in range(N) if j != col]
        mismos_col = [(i, col) for i in range(N) if i != fila]
      
        base_fila, base_col = (fila//3)*3, (col//3)*3
        subcuadro = [(i, j) for i in range(base_fila, base_fila+3) for j in range(base_col, base_col+3) if (i, j) != (fila, col)]
        return list(set(mismos_fila + mismos_col + subcuadro))

    def consistente(self, tablero, fila, col, valor):
        if any(tablero[fila][j]==valor for j in range(N) if j!=col): return False
        if any(tablero[i][col]==valor for i in range(N) if i!=fila): return False
        base_fila, base_col = (fila//3)*3, (col//3)*3
        for i in range(base_fila, base_fila+3):
            for j in range(base_col, base_col+3):
                if (i,j)!=(fila,col) and tablero[i][j]==valor: return False
        return True

    def dominios_iniciales(self, tablero):
        dominios = {(fila,col): set(range(1,10)) for fila in range(N) for col in range(N)}
        for fila in range(N):
            for col in range(N):
                if tablero[fila][col] != 0:
                    dominios[(fila,col)] = {tablero[fila][col]}
     
        for fila in range(N):
            for col in range(N):
                valor = tablero[fila][col]
                if valor != 0:
                    for f,c in self.vecinos(fila,col):
                        dominios[(f,c)].discard(valor)
        return dominios

    def seleccionar_mrv(self, tablero, dominios):
        mejor, tamaño = None, 10
        for fila in range(N):
            for col in range(N):
                if tablero[fila][col]==0:
                    tam = len(dominios[(fila,col)])
                    if tam < tamaño:
                        mejor, tamaño = (fila,col), tam
        return mejor

    def poda_hacia_adelante(self, tablero, var, valor, dominios):
        fila, col = var; podados = []
        for f, c in self.vecinos(fila, col):
            if tablero[f][c]==0 and valor in dominios[(f,c)]:
                dominios[(f,c)].remove(valor); podados.append(((f,c), valor))
                if not dominios[(f,c)]:
                    return False, podados
        return True, podados

    def resolver(self):
        tablero = self.leer_tablero()
        dominios = self.dominios_iniciales(tablero)

        def backtracking():
            var = self.seleccionar_mrv(tablero, dominios)
            if var is None:  
                return True
            fila, col = var
            for valor in sorted(dominios[(fila,col)]):
                if self.consistente(tablero, fila, col, valor):
                    tablero[fila][col] = valor
                    ok, podados = self.poda_hacia_adelante(tablero, var, valor, dominios)
                    if ok and backtracking(): return True
                    
                    tablero[fila][col] = 0
                    for (celda, val) in podados:
                        dominios[celda].add(val)
            return False

        if backtracking():
            self.mostrar_tablero(tablero)
        else:
            messagebox.showwarning("Sudoku", "No se encontró solución válida.")

if __name__ == "__main__":
    SudokuApp().mainloop()

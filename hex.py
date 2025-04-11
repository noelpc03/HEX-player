import math
import random
import time
from collections import deque

class HexBoard:
    def __init__(self, size: int):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
    
    def clone(self) -> 'HexBoard':
        """Devuelve una copia del tablero actual"""
        new_board = HexBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        return new_board
    
    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        """Coloca una ficha si la casilla está vacía."""
        if self.board[row][col] == 0:
            self.board[row][col] = player_id
            return True
        return False  # No se puede colocar la ficha si la casilla ya está ocupada
    
    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías como tuplas (fila, columna)."""
        return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
    
    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador ha conectado sus dos lados opuestos."""
        visited = set()  # Conjunto de casillas visitadas
        queue = []  # Cola para la búsqueda en anchura (BFS)
        
        # Determina los nodos iniciales y la condición de victoria según el jugador
        if player_id == 1:
            start_nodes = [(i, 0) for i in range(self.size) if self.board[i][0] == 1]
            target = lambda x: x[1] == self.size - 1  # El objetivo es alcanzar el lado derecho
        else:
            start_nodes = [(0, i) for i in range(self.size) if self.board[0][i] == 2]
            target = lambda x: x[0] == self.size - 1  # El objetivo es alcanzar la parte inferior

        # BFS para buscar una conexión entre los lados opuestos
        for node in start_nodes:
            if node not in visited:
                queue.append(node)
                visited.add(node)
                
                while queue:
                    current = queue.pop(0)
                    if target(current):  # Si se alcanza el objetivo, hay conexión
                        return True
                    
                    # Explora los vecinos de la casilla actual
                    for neighbor in self.get_neighbors(current):
                        r, c = neighbor
                        if self.board[r][c] == player_id and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        return False  # No se encontró conexión
    
    def get_neighbors(self, pos) -> list:
        """Devuelve una lista de vecinos válidos para una posición dada."""
        row, col = pos
        neighbors = []
        deltas = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]  # Movimientos válidos en un tablero hexagonal
        
        for dr, dc in deltas:
            r = row + dr
            c = col + dc
            if 0 <= r < self.size and 0 <= c < self.size:  # Verifica que el vecino esté dentro del tablero
                neighbors.append((r, c))
        return neighbors

class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id

    def play(self, board: HexBoard) -> tuple:
        raise NotImplementedError("¡Implementa este método!")

class MCTSNode:
    def __init__(self, board: HexBoard, player: int, parent=None, move=None):
        # Nodo del árbol MCTS
        self.board = board  # Estado del tablero en este nodo
        self.player = player  # Jugador que realizó el movimiento
        self.parent = parent  # Nodo padre
        self.move = move  # Movimiento que llevó a este nodo
        self.children = []  # Lista de nodos hijos
        self.wins = 0  # Número de victorias acumuladas
        self.visits = 0  # Número de veces que se visitó este nodo
        self.untried_moves = board.get_possible_moves()  # Movimientos no explorados desde este estado

    def uct_value(self, exploration=1.4):
        """Calcula el valor UCT (Upper Confidence Bound for Trees) para este nodo."""
        if self.visits == 0:
            return float('inf')  # Si el nodo no ha sido visitado, se prioriza su exploración
        # Fórmula UCT: explotación + exploración
        return (self.wins / self.visits) + exploration * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self):
        """Devuelve el hijo con el mejor valor UCT."""
        return max(self.children, key=lambda child: child.uct_value())

class AIPlayer(Player):
    def __init__(self, player_id: int, time_limit=10):
        super().__init__(player_id)
        self.time_limit = time_limit  # Tiempo límite para calcular el movimiento (en segundos)
    
    def play(self, board: HexBoard) -> tuple:
        """Implementa el algoritmo MCTS para decidir el mejor movimiento."""
        root = MCTSNode(board, self.player_id)  # Nodo raíz del árbol MCTS
        start_time = time.time()  # Marca de tiempo inicial
        move_stack = deque()  # Pila para registrar los movimientos realizados
        
        # Ejecutar MCTS hasta que se agote el tiempo
        while time.time() - start_time < self.time_limit:
            node = root
            current_player = self.player_id
            
            # Selección: navega por el árbol hasta un nodo hoja
            while node.untried_moves == [] and node.children != []:
                node = node.best_child()
                move_stack.append(node.move)  # Registrar el movimiento
                board.place_piece(*node.move, current_player)
                current_player = 3 - current_player  # Cambia al jugador contrario
            
            # Expansión: agrega un nuevo nodo hijo si hay movimientos no explorados
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                board.place_piece(*move, node.player)
                move_stack.append(move)  # Registrar el movimiento
                current_player = 3 - node.player
                child = MCTSNode(board, current_player, parent=node, move=move)
                node.children.append(child)
                node.untried_moves.remove(move)
                node = child
            
            # Simulación: realiza movimientos aleatorios hasta alcanzar un estado terminal
            sim_player = current_player
            while True:
                if board.check_connection(1) or board.check_connection(2) or len(board.get_possible_moves()) == 0:
                    break
                move = random.choice(board.get_possible_moves())
                board.place_piece(*move, sim_player)
                move_stack.append(move)  # Registrar el movimiento
                sim_player = 3 - sim_player
            
            # Retropropagación: actualiza las estadísticas de los nodos en el camino hacia la raíz
            result = 1 if board.check_connection(self.player_id) else 0
            while node is not None:
                node.visits += 1
                node.wins += result
                node = node.parent
            
            # Deshacer todos los movimientos realizados durante esta iteración
            while move_stack:
                last_move = move_stack.pop()
                board.board[last_move[0]][last_move[1]] = 0  # Deshacer el movimiento
        
        # Selección final: elige el movimiento más visitado
        if not root.children:
            return random.choice(board.get_possible_moves())
        
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move
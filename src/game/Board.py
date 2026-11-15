from src.constants import EMPTY , BLACK , WHITE
from typing import List , Tuple
from dataclasses import dataclass , field

@dataclass
class BoardLine:
    """
    Represents one horizontal, vertical, or diagonal line on the Gomoku board.
    """
    nodes: List[int]
    node_set: set[int] = field(init=False)
    evaluation: List[int] = field(default_factory=lambda: [0, 0])

    def __post_init__(self):
        self.node_set = set(self.nodes)

    def contains(self, node: int) -> bool:
        return node in self.node_set
    
    def update_evaluation(self, board_matrix: List[List[int]], size: int):
        black_score = 0
        white_score = 0

        if len(self.nodes) < 5:
            self.evaluation = [0, 0]
            return

        for start in range(len(self.nodes) - 4):
            window = self.nodes[start:start + 5]

            black_count = 0
            white_count = 0

            for node in window:
                row = node // size
                col = node % size

                value = board_matrix[row][col]

                if value == BLACK:
                    black_count += 1
                elif value == WHITE:
                    white_count += 1

            if black_count > 0 and white_count > 0:
                continue

            if black_count > 0:
                black_score += 1

            if white_count > 0:
                white_score += 1

        self.evaluation = [black_score, white_score]

    def get_evaluation(self) -> List[int]:
        return self.evaluation.copy()



class Board:
    def __init__(self, size: int):
        if not 5 <= size <= 18:
            raise ValueError("Board size must be between 5 and 18.")
             
        self.size = size

        self.matrix = [
            [EMPTY for _ in range(size)]
            for _ in range(size)
        ]
        self.rows: List[BoardLine] = []
        self.columns: List[BoardLine] = []
        self.diagonals: List[BoardLine] = []
        self.cell_to_lines: dict[int, List[BoardLine]] = {}

        self._build_lines()

    def _build_rows(self):
        for row in range(self.size):

            nodes = []

            for col in range(self.size):
                node = self._to_node(row, col)
                nodes.append(node)

            line = BoardLine(nodes)
            self.rows.append(line)

            self._register_line(line)

    def _build_columns(self):
        for col in range(self.size):
            nodes = []

            for row in range(self.size):
                node = self._to_node(row, col)
                nodes.append(node)

            line = BoardLine(nodes)
            self.columns.append(line)

            self._register_line(line)

    def _build_diagonals(self):
        for row in range(self.size):
            nodes = []
            r = row
            c = 0
            while r < self.size and c < self.size:
                nodes.append(self._to_node(r, c))
                r += 1
                c += 1

            if len(nodes) >= 5:
                line = BoardLine(nodes)
                self.diagonals.append(line)
                self._register_line(line)

        for col in range(1, self.size):
            nodes = []

            r = 0
            c = col

            while r < self.size and c < self.size:
                nodes.append(self._to_node(r, c))
                r += 1
                c += 1

            if len(nodes) >= 5:
                line = BoardLine(nodes)
                self.diagonals.append(line)
                self._register_line(line)

        for row in range(self.size):
            nodes = []

            r = row
            c = self.size - 1

            while r < self.size and c >= 0:
                nodes.append(self._to_node(r, c))
                r += 1
                c -= 1

            if len(nodes) >= 5:
                line = BoardLine(nodes)
                self.diagonals.append(line)
                self._register_line(line)

        for col in range(self.size - 2, -1, -1):
            nodes = []

            r = 0
            c = col

            while r < self.size and c >= 0:
                nodes.append(self._to_node(r, c))
                r += 1
                c -= 1

            if len(nodes) >= 5:
                line = BoardLine(nodes)
                self.diagonals.append(line)
                self._register_line(line)

    def _register_line(self, line: BoardLine):
        for node in line.nodes:
            if node not in self.cell_to_lines:
                self.cell_to_lines[node] = []

            self.cell_to_lines[node].append(line)

    def _build_lines(self):
        self._build_rows()
        self._build_columns()
        self._build_diagonals()

    def _to_node(self, row: int, col: int) -> int:
        return row * self.size + col

    def _from_node(self, node: int) -> Tuple[int, int]:
        return divmod(node, self.size)


    def get_row(self, node: int) -> BoardLine:
        row, _ = self._from_node(node)
        return self.rows[row]

    def get_column(self, node: int) -> BoardLine:
        _, col = self._from_node(node)
        return self.columns[col]


    def get_diagonals(self, node: int) -> List[BoardLine]:
        return [
            line
            for line in self.cell_to_lines[node]
            if line in self.diagonals
        ]

    def get_specific_row(self, index: int) -> BoardLine:
        if not 0 <= index < self.size:
            raise IndexError("Row index out of range.")

        return self.rows[index]

    def get_specific_diagonal(self, index: int) -> BoardLine:
        if not 0 <= index < len(self.diagonals):
            raise IndexError("Diagonal index out of range.")

        return self.diagonals[index]


    def set_piece(self, node: int, player: int):

        if player not in (BLACK, WHITE):
            raise ValueError("Player must be BLACK or WHITE.")

        row, col = self._from_node(node)
        if self.matrix[row][col] != EMPTY:
            raise ValueError("Cell is already occupied.")

        self.matrix[row][col] = player

        for line in self.cell_to_lines[node]:
            line.update_evaluation(
                self.matrix,
                self.size
            )

    def get_evaluation(self) -> List[int]:
        black_score = 0
        white_score = 0
        for line in self.rows:
            black_score += line.evaluation[0]
            white_score += line.evaluation[1]

        for line in self.columns:
            black_score += line.evaluation[0]
            white_score += line.evaluation[1]

        for line in self.diagonals:
            black_score += line.evaluation[0]
            white_score += line.evaluation[1]

        return [black_score, white_score]


    def display(self):
        print()
        print("   ", end="")

        for col in range(self.size):
            print(f"{col:2}", end=" ")
            
        print()
        for row in range(self.size):
            print(f"{row:2} ", end="")
            for col in range(self.size):
                value = self.matrix[row][col]
                if value == EMPTY:
                    symbol = "."
                elif value == BLACK:
                    symbol = "B"
                else:
                    symbol = "W"
                print(f"{symbol:2}", end=" ")

            print()
        print()
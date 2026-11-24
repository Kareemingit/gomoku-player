from src.constants import BLACK, WHITE, EMPTY
import src.game.Board as Board
from src.game.Board import BoardLine as BoardLine
import random

class SmartPlayer:
    def __init__(self, player: int, thinking_depth: int):
        if player not in (BLACK, WHITE):
            raise ValueError("Player must be BLACK or WHITE.")

        if thinking_depth < 1:
            raise ValueError("Thinking depth must be at least 1.")
        
        self.player = player
        self.depth = thinking_depth
        self.opponent = WHITE if player == BLACK else BLACK
        self.candidate_moves_types = {
            "center": 0,
            "winning": 1,
            "threat": 2,
            "nearby": 3,
        }

    def _get_center_moves(self, board: Board.Board):
        size = board.size
        if size % 2 == 1:
            center = size // 2
            return [board._to_node(center, center)]

        center = size // 2

        return [
            board._to_node(center - 1, center - 1),
            board._to_node(center - 1, center),
            board._to_node(center, center - 1),
            board._to_node(center, center)
        ]

    def _would_win(self, board: Board.Board, node: int, player: int) -> bool:
        row, col = board._from_node(node)
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]

        for dr, dc in directions:
            count = 1
            
            r = row + dr
            c = col + dc

            while (0 <= r < board.size and 0 <= c < board.size and board.matrix[r][c] == player):
                count += 1
                r += dr
                c += dc

            r = row - dr
            c = col - dc

            while (0 <= r < board.size and 0 <= c < board.size and board.matrix[r][c] == player):
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True

        return False

    def _get_winning_moves(self,board: Board.Board,player: int,candidate_nodes=None):
        if candidate_nodes is None:
            candidate_nodes = self._get_nearby_moves(board,distance=1)

        winning_moves = []

        for node in candidate_nodes:
            if self._would_win(board, node, player):
                winning_moves.append(node)

        return winning_moves

    def _get_promising_window_moves(self, board: Board.Board, player: int):
        candidate_moves = set()

        for line in board.rows + board.columns + board.diagonals:
            if len(line.nodes) < 5:
                continue

            for start in range(len(line.nodes) - 4):
                window = line.nodes[start:start + 5]

                black_count = 0
                white_count = 0
                empty_nodes = []

                for node in window:
                    row, col = board._from_node(node)
                    value = board.matrix[row][col]
                    if value == BLACK:
                        black_count += 1
                    elif value == WHITE:
                        white_count += 1
                    else:
                        empty_nodes.append(node)

                if black_count > 0 and white_count > 0:
                    continue

                if player == BLACK:
                    player_count = black_count
                else:
                    player_count = white_count

                if player_count == 0:
                    continue

                candidate_moves.update(empty_nodes)
        return candidate_moves

    def _get_nearby_moves(self, board: Board.Board, distance=2):
        candidates = set()
        for node in board.non_empty_nodes:
            row, col = board._from_node(node)
            for dr in range(-distance, distance + 1):
                for dc in range(-distance, distance + 1):
                    if dr == 0 and dc == 0:
                        continue

                    new_row = row + dr
                    new_col = col + dc

                    if not (0 <= new_row < board.size and 0 <= new_col < board.size):
                        continue

                    if board.matrix[new_row][new_col] != EMPTY:
                        continue

                    node = board._to_node(new_row,new_col)

                    candidates.add(node)
        return candidates

    def get_candidate_moves(self, board: Board.Board , player: int):
        if board.is_empty():
            return self._get_center_moves(board)

        player_winning_moves = self._get_winning_moves(board, player)

        if player_winning_moves:
            return player_winning_moves

        opponent_winning_moves = self._get_winning_moves(board, self.opponent if player == self.player else self.player)

        if opponent_winning_moves:
            return opponent_winning_moves

        candidate_moves = self._get_promising_window_moves(board, player)

        candidate_moves.update(
            self._get_nearby_moves(board , 2)
        )

        return list(candidate_moves)

    #minmax algorithm with alpha-beta pruning
    def _minimax(self, board: Board.Board, alpha: int, beta: int, depth: int, maximizing_player: bool) -> float:
        if depth == 0 or board.is_terminal():
            return board.evaluate()

        current_player = self.player if maximizing_player else self.opponent
        candidate_moves = self.get_candidate_moves(board, current_player)
        if maximizing_player:
            max_value = -float('inf')
            for move in candidate_moves:
                board.set_piece(move, current_player)
                value = self._minimax(board, alpha, beta, depth - 1, False)
                board.remove_piece(move)

                max_value = max(max_value, value)
                alpha = max(alpha, value)

                if beta <= alpha:
                    break
            return max_value

        else:
            min_value = float('inf')
            for move in candidate_moves:
                board.set_piece(move, current_player)
                value = self._minimax(board, alpha, beta, depth - 1, True)
                board.remove_piece(move)

                min_value = min(min_value, value)
                beta = min(beta, value)

                if beta <= alpha:
                    break
            return min_value
        
    def get_best_move(self, board: Board.Board) -> int:
        candidate_moves = self.get_candidate_moves(board , self.player)
        if not candidate_moves:
            return None

        best_move = candidate_moves[0]

        if self.player == BLACK:
            best_score = -float('inf')
            for move in candidate_moves:
                board.set_piece(move, self.player)
                value = self._minimax(board, float('-inf'), float('inf'), self.depth - 1, False)
                board.remove_piece(move)

                if value > best_score:
                    best_score = value
                    best_move = move
        else:
            best_score = float('inf')
            for move in candidate_moves:
                board.set_piece(move, self.player)
                value = self._minimax(board, float('-inf'), float('inf'), self.depth - 1, True)
                board.remove_piece(move)

                if value < best_score:
                    best_score = value
                    best_move = move

        return best_move

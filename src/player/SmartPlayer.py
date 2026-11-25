from src.constants import BLACK, WHITE, EMPTY
import src.game.Board as Board
from src.game.Board import BoardLine as BoardLine

class SmartPlayer:
    def __init__(self, player: int, thinking_depth: int):
        if player not in (BLACK, WHITE):
            raise ValueError("SmartPlayer:Player must be BLACK or WHITE.")

        if not (1 < thinking_depth < 4):
            raise ValueError("SmartPlayer:Thinking depth must be at least 1 and at most 3.")
        
        self.player = player
        self.depth = thinking_depth
        self.opponent = WHITE if player == BLACK else BLACK

    def _would_win(self, board: Board.Board, node: int, player: int) -> bool:
        board.set_piece(node , player)
        res = board.has_winner(player)
        board.remove_piece(node)
        return res

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

    def _get_winning_moves(self,board: Board.Board,player: int,candidate_nodes=None):
        if candidate_nodes is None:
            candidate_nodes = self._get_nearby_moves(board,distance=1)

        winning_moves = []

        for node in candidate_nodes:
            if self._would_win(board, node, player):
                winning_moves.append(node)

        return winning_moves

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

    def _order_moves(self,board: Board.Board,candidate_moves: list[int], player: int) -> list[int]:
        scored_moves = []
        for move in candidate_moves:
            board.set_piece(move, player)

            try:
                score = board.evaluate()
            finally:
                board.remove_piece(move)

            scored_moves.append((score, move))

        scored_moves.sort(key=lambda item: item[0],reverse=(player == BLACK))

        return [move for score, move in scored_moves]

    def get_candidate_moves(self, board: Board.Board , player: int):
        if board.is_empty():
            return self._get_center_moves(board)

        player_winning_moves = self._get_winning_moves(board, player)

        if player_winning_moves:
            return player_winning_moves

        opponent_winning_moves = self._get_winning_moves(board, self.opponent if player == self.player else self.player)

        if opponent_winning_moves:
            return opponent_winning_moves
        
        candidate_moves = self._get_nearby_moves(board , 1)

        return list(candidate_moves)


    def _minimax(self, board: Board.Board, alpha: int, beta: int, depth: int, maximizing_player: bool) -> float:
        if depth == 0 or board.is_terminal():
            return board.evaluate()

        current_player = self.player if maximizing_player else self.opponent

        candidate_moves = self._order_moves(board , self.get_candidate_moves(board, current_player) , current_player)

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
        print(f"Getting best move for player {self.player} with depth {self.depth}")
        candidate_moves = self._order_moves(board , self.get_candidate_moves(board , self.player) , self.player)
        if not candidate_moves:
            return None
        
        print(f"Minmax:Evaluating moves for player {self.player}...")
        print(f"Minmax:Candidate moves: {candidate_moves}")
        print(f"Minmax:Candidate moves Count:" , {len(candidate_moves)})
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

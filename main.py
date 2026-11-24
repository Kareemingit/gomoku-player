from src.game.Board import Board
from src.constants import EMPTY , WHITE , BLACK
from src.player.SmartPlayer import SmartPlayer
import time

def main():
    board = Board(15)
    player1 = SmartPlayer(BLACK, 4)
    player2 = SmartPlayer(WHITE, 4)

    current_player = player1
    total_time_ms = 0
    rounds = 0
    while True:
        rounds += 1
        start = time.perf_counter()
        move = current_player.get_best_move(board)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        total_time_ms += elapsed_ms

        print(f"Elapsed time: {elapsed_ms:.2f} ms")
        if move is None:
            print("Game over! It's a draw.")
            break

        board.set_piece(move, current_player.player)
        print(f"Player {current_player.player} moves to {move}.")
        board.display()

        if board.has_winner(current_player.player):
            print(f"Player {current_player.player} wins!")
            break

        current_player = player2 if current_player == player1 else player1
    av_time_ms = total_time_ms / rounds

    print(f"average time: " ,{av_time_ms})


main()
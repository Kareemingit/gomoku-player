from src.game.Board import Board
from src.constants import EMPTY , WHITE , BLACK
from src.player.SmartPlayer import SmartPlayer

def main():
    board = Board(15)
    player1 = SmartPlayer(BLACK, 2)
    player2 = SmartPlayer(WHITE, 2)

    current_player = player1
    while True:
        move = current_player.get_best_move(board)
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


main()
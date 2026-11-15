# import src.ui.uiTest as ui
# import src.api.apiTest as api
# import src.game.gameTest as game
# import src.player.playerTest as player
# print("test")
# ui.uiTestFunc(5)
# api.apiTestFunc(15)
# game.gameTestFunc(20)
# player.playerTestFunc(17)

from src.game import Board
from src.constants import EMPTY , WHITE , BLACK
board = Board.Board(15)

board.display()

board.set_piece(112, BLACK)
board.set_piece(113 , WHITE)
board.set_piece(114, BLACK)
board.set_piece(12 , WHITE)
board.set_piece(115, BLACK)

board.display()

print("Evaluation:", board.get_evaluation())
import pygame

from gamecontroller import GameController
from tetromino import Tetromino
from matrix import Matrix
from sevenbag import SevenBag
from garbagesystem import GarbageSystem
from hold import Hold

class Bot:
  def __init__(self, me: GameController):
    self.me = me
  
  def takeAction(self): # this needs to end in a piece placement
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit()  # Exit the game
    self.generateLegalPlacements(self.me.active_piece, self.me.matrix)
    return
    self.me.hardDrop()

  def generateLegalPlacements(self, tetromino: Tetromino, matrix: Matrix, can_hold: bool): # create search tree
    res = [] # list of list[resulting matrix, action list]
    if can_hold:
      res.append([matrix, ["H"]]) # hold case, same matrix, hold action
    ori_x = tetromino.x
    for rotation in range(4): # for each rotation
      tetromino.x = ori_x
      actions = []
      # move left, then harddrop
      while not matrix.checkCollision(tetromino.x, tetromino.y, tetromino.getRotatedShape(rotation)):
        tetromino.x -= 1
        tetromino.y = 0
        y = tetromino.y
        actions.append("L")
        # simulate harddrop
        while not matrix.checkCollision(tetromino.x, y + 1, tetromino.getRotatedShape(rotation)):
          y += 1
        tetromino.y = y
        new_matrix = Matrix()
        new_matrix.lockTetromino(tetromino)
        actions.append("HD")
        res.append([new_matrix, actions])
    return res

if __name__ == "__main__":
  gc = GameController("bot", SevenBag(0), GarbageSystem(0))
  bot = Bot(gc)
  res = bot.generateLegalPlacements(Tetromino("I", 5, 0), gc.matrix, True)
  for i in res:
    print(i[1])
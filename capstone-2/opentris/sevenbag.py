import random

from constants import TETROMINOS
from tetromino import Tetromino

class SevenBag:
  def __init__(self, seed: int = None) -> None:
    if seed:
      self.seed = seed
    else:
      self.seed = random.random()
    random.seed(self.seed)
    self.bag = []

  def generateBag(self) -> list:
    self.bag = [*TETROMINOS]
    random.shuffle(self.bag)
  
  def getNextTetromino(self) -> Tetromino:
    if not self.bag:
      self.generateBag()
    tetromino = self.bag.pop(0)
    return Tetromino(tetromino)


# tests

if __name__ == "__main__":
  test = SevenBag(44)
  for i in range(10):
    for j in range(7):
      print(test.getNextTetromino().name, end=" ")
    print()
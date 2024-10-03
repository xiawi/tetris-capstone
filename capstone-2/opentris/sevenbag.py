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
    self.sequence = []

  def generateNewBag(self) -> None:
    new_bag = [*TETROMINOS]
    random.shuffle(new_bag)
    self.sequence.extend(new_bag)
  
  def getTetrominoAt(self, index) -> Tetromino:
    if index >= len(self.sequence):
      self.generateNewBag()
    tetromino = self.sequence[index]
    return Tetromino(tetromino)


# tests

if __name__ == "__main__":
  test = SevenBag(44)
    
from sevenbag import SevenBag
from tetromino import Tetromino

class Lookahead:
  def __init__(self, bag: SevenBag) -> None:
    self.bag = bag
    self.queue = []
    self.index = 0
    pass

  def fillQueue(self) -> None:
    while len(self.queue) < 5:
      self.queue.append(self.bag.getTetrominoAt(self.index))
      self.index += 1
    
  def getNextTetromino(self) -> Tetromino:
    if not self.queue:
      self.fillQueue()
    tetromino = self.queue.pop(0)
    self.fillQueue()
    return tetromino
  
  def getQueue(self) -> list:
    return self.queue


# tests

if __name__ == "__main__":
  test = Lookahead()
  for i in range(4):
    print(test.getNextTetromino().name)
    for tetromino in test.getQueue():
      print(tetromino.name, end=" ")
    print()
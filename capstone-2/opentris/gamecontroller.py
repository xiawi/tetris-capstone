from constants import WALL_KICK_DATA
from tetromino import Tetromino
from matrix import Matrix
from lookahead import Lookahead
from hold import Hold
from sevenbag import SevenBag

class GameController:
  def __init__(self, bag: SevenBag) -> None:
    self.matrix = Matrix()
    self.lookahead = Lookahead(bag)
    self.hold = Hold()
    self.active_piece = None
    self.spawnTetromino()

  def spawnTetromino(self, tetromino: Tetromino = None) -> None:
    if tetromino:
      self.active_piece = tetromino
    else:
      self.active_piece = self.lookahead.getNextTetromino()
    self.active_piece.x = 3 if self.active_piece.name == "I" or self.active_piece.name == "O" else 2
    self.active_piece.y = -2

  def holdPiece(self):
    if self.hold.can_hold:
      return_tet = self.hold.holdPiece(self.active_piece)
      if return_tet:
        self.spawnTetromino(return_tet)
      else:
        self.spawnTetromino()

  def moveLeft(self):
    if not self.matrix.checkCollision(self.active_piece.x - 1, self.active_piece.y, self.active_piece.getShape()):
      self.active_piece.x -= 1

  def moveRight(self):
    if not self.matrix.checkCollision(self.active_piece.x + 1, self.active_piece.y, self.active_piece.getShape()):
      self.active_piece.x += 1
  
  def softDrop(self):
    if not self.matrix.checkCollision(self.active_piece.x, self.active_piece.y + 1, self.active_piece.getShape()):
      self.active_piece.y += 1

  def hardDrop(self):
    y = self.active_piece.y  # Start from current y position
    while not self.matrix.checkCollision(self.active_piece.x, y + 1, self.active_piece.getShape()):
        y += 1  # Move down until collision occurs
    self.active_piece.y = y  # Set final y position
    self.matrix.lockTetromino(self.active_piece)  # Lock the piece in the matrix
    self.hold.resetStatus()
    self.spawnTetromino()

  def rotateLeft(self):
    next_rotation = (self.active_piece.current_rotation - 1) % 4
    if not self.matrix.checkCollision(self.active_piece.x, self.active_piece.y, self.active_piece.getRotatedShape(next_rotation)):
      self.active_piece.current_rotation = next_rotation
      return  # No need to check for wall kicks
    
    if self.active_piece.name == "I":
      kicks = WALL_KICK_DATA["IL"][self.active_piece.current_rotation]
    else:
      kicks = WALL_KICK_DATA["L"][self.active_piece.current_rotation]
    for dx, dy in kicks:
      new_x = self.active_piece.x + dx
      new_y = self.active_piece.y - dy
      if not self.matrix.checkCollision(new_x, new_y, self.active_piece.getRotatedShape(next_rotation)):
        self.active_piece.x = new_x
        self.active_piece.y = new_y
        self.active_piece.current_rotation = next_rotation
        break  # Exit after a successful wall kick

  def rotateRight(self):
    next_rotation = (self.active_piece.current_rotation + 1) % 4
    if not self.matrix.checkCollision(self.active_piece.x, self.active_piece.y, self.active_piece.getRotatedShape(next_rotation)):
      self.active_piece.current_rotation = next_rotation
      return  # No need to check for wall kicks
    
    if self.active_piece.name == "I":
      kicks = WALL_KICK_DATA["IL"][self.active_piece.current_rotation]
    else:
      kicks = WALL_KICK_DATA["L"][self.active_piece.current_rotation]
    for dx, dy in kicks:
      new_x = self.active_piece.x + dx
      new_y = self.active_piece.y - dy
      if not self.matrix.checkCollision(new_x, new_y, self.active_piece.getRotatedShape(next_rotation)):
        self.active_piece.x = new_x
        self.active_piece.y = new_y
        self.active_piece.current_rotation = next_rotation
        break  # Exit after a successful wall kick

# tests

if __name__ == "__main__":
  bag = SevenBag(1)
  gc = GameController(bag)
  gc.spawnTetromino()
  print(gc.hold.held_piece)
  print(gc.active_piece.name)
  print([tetromino.name for tetromino in gc.lookahead.queue])
  gc.holdPiece()
  gc.softDrop()
  gc.softDrop()
  gc.softDrop()
  gc.softDrop()
  print(gc.active_piece.y)
  print(gc.hold.held_piece.name)
  print(gc.active_piece.name)
  print([tetromino.name for tetromino in gc.lookahead.queue])
  gc.holdPiece()
  print(gc.active_piece.y)
  print(gc.hold.held_piece.name)
  print(gc.active_piece.name)
  print([tetromino.name for tetromino in gc.lookahead.queue])
  gc.hardDrop()
  print(gc.active_piece.y)
  print(gc.hold.held_piece.name)
  print(gc.active_piece.name)
  print([tetromino.name for tetromino in gc.lookahead.queue])
  gc.holdPiece()
  print(gc.hold.held_piece.name)
  print(gc.active_piece.name)
  print([tetromino.name for tetromino in gc.lookahead.queue])
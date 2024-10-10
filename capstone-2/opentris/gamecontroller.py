from constants import WALL_KICK_DATA, MATRIX_WIDTH, TETROMINOS
from tetromino import Tetromino
from matrix import Matrix
from lookahead import Lookahead
from hold import Hold
from sevenbag import SevenBag

class GameController:
  def __init__(self, name, bag: SevenBag) -> None:
    self.name = name
    self.matrix = Matrix()
    self.lookahead = Lookahead(bag)
    self.hold = Hold()
    self.active_piece = None
    self.has_lost = False
    self.most_recent_move = None
    self.combo = -1
    self.b2b = -1
    self.spawnTetromino()

  def spawnTetromino(self, tetromino: Tetromino = None) -> None:
    if tetromino:
      self.active_piece = tetromino
    else:
      self.active_piece = self.lookahead.getNextTetromino()
    self.active_piece.x = 3 if self.active_piece.name in ["I", "O"] else 2
    self.active_piece.y = 0

    shape = self.active_piece.getShape()

    for row_idx, row in enumerate(shape):
      for col_idx, cell in enumerate(row):
        if int(cell):  # Means this part of tetromino is filled
          matrix_x = self.active_piece.x + col_idx
          matrix_y = self.active_piece.y + row_idx
          if self.matrix.grid[matrix_y][matrix_x]:
            self.has_lost = True

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
      self.most_recent_move = "move"

  def moveRight(self):
    if not self.matrix.checkCollision(self.active_piece.x + 1, self.active_piece.y, self.active_piece.getShape()):
      self.active_piece.x += 1
      self.most_recent_move = "move"
  
  def softDrop(self):
    if not self.matrix.checkCollision(self.active_piece.x, self.active_piece.y + 1, self.active_piece.getShape()):
      self.active_piece.y += 1
      self.most_recent_move = "move"

  def hardDrop(self):
    y = self.active_piece.y  # Start from current y position
    while not self.matrix.checkCollision(self.active_piece.x, y + 1, self.active_piece.getShape()):
        y += 1  # Move down until collision occurs
    self.active_piece.y = y  # Set final y position

    self.matrix.lockTetromino(self.active_piece)  # Lock the piece in the matrix
    garbage = self.calculateGarbage()
    if garbage > 0:
      print(garbage)
    self.matrix.clearLines()
    self.most_recent_move = None
    self.hold.resetStatus()
    self.spawnTetromino()

  def calculateGarbage(self): # All Garbage Logic + Line Clearing for PC check
    garbage = 0
    lines_cleared = self.matrix.calculateLineClears()
    print(lines_cleared)

    if lines_cleared > 0:
      self.combo += 1
    else:
      self.combo = -1

    if self.combo >= 11:
      garbage += 5
    elif self.combo >= 8:
      garbage += 4
    elif self.combo >= 6:
      garbage += 3
    elif self.combo >= 4:
      garbage += 2
    elif self.combo >= 2:
      garbage += 1

    if self.isTspin() and not self.isMini():
      garbage += 2 * lines_cleared
    else:
      if lines_cleared == 2:
        garbage += 1
      elif lines_cleared == 3:
        garbage += 2
      elif lines_cleared == 4:
        garbage += 4

    # b2b check
    if lines_cleared > 0:
      if self.isTspin() or lines_cleared == 4:
        self.b2b += 1
      else:
        self.b2b = -1
      if self.b2b > 0:
        garbage += self.b2b

    if self.isPerfectClear():
      garbage += 6

    return garbage

  def isTspin(self):
    if self.most_recent_move == "rotate" and self.active_piece.name == "T":
      corners_filled = 0
      corners_to_check = [[1,0], [3,0], [1,2], [3,2]]
      for corner in corners_to_check:
        specific_corner_x = self.active_piece.x + corner[0]
        specific_corner_y = self.active_piece.y + corner[1]
        if specific_corner_x < 0 or specific_corner_x >= MATRIX_WIDTH:
          corners_filled += 1
        elif self.matrix.grid[specific_corner_y][specific_corner_x]:
          corners_filled += 1
      if corners_filled >= 3:
        return True
      else:
        return False
      
  def isMini(self):
    current_rotation = self.active_piece.current_rotation
    if current_rotation == 0:
      corners_to_check = [[1,0], [3,0]]
    elif current_rotation == 1:
      corners_to_check = [[3,0], [3,2]]
    elif current_rotation == 2:
      corners_to_check = [[1,2], [3,2]]
    else:
      corners_to_check = [[1,0], [1,2]]
    for corner in corners_to_check:
        specific_corner_x = self.active_piece.x + corner[0]
        specific_corner_y = self.active_piece.y + corner[1]
        if self.matrix.grid[specific_corner_y][specific_corner_x] == 0:
          return True
    return False
  
  def isPerfectClear(self):
    line_clears = self.matrix.calculateLineClears()
    occupied_rows = 0
    for idx, row in enumerate(self.matrix.grid):
      if not all(cell == 0 for cell in row):
        occupied_rows += 1
    return True if occupied_rows == line_clears else False

  def getGhostPosition(self):
    y = self.active_piece.y  # Start from current y position
    while not self.matrix.checkCollision(self.active_piece.x, y + 1, self.active_piece.getShape()):
        y += 1  # Move down until collision occurs
    return (self.active_piece.x, y)

  def rotateLeft(self):
    next_rotation = (self.active_piece.current_rotation - 1) % 4
    if not self.matrix.checkCollision(self.active_piece.x, self.active_piece.y, self.active_piece.getRotatedShape(next_rotation)):
      self.active_piece.current_rotation = next_rotation
      self.most_recent_move = "rotate"
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
        self.most_recent_move = "rotate"
        break  # Exit after a successful wall kick

  def rotateRight(self):
    next_rotation = (self.active_piece.current_rotation + 1) % 4
    if not self.matrix.checkCollision(self.active_piece.x, self.active_piece.y, self.active_piece.getRotatedShape(next_rotation)):
      self.active_piece.current_rotation = next_rotation
      self.most_recent_move = "rotate"
      return  # No need to check for wall kicks
    
    if self.active_piece.name == "I":
      kicks = WALL_KICK_DATA["IR"][self.active_piece.current_rotation]
    else:
      kicks = WALL_KICK_DATA["R"][self.active_piece.current_rotation]
    for dx, dy in kicks:
      new_x = self.active_piece.x + dx
      new_y = self.active_piece.y - dy
      if not self.matrix.checkCollision(new_x, new_y, self.active_piece.getRotatedShape(next_rotation)):
        self.active_piece.x = new_x
        self.active_piece.y = new_y
        self.active_piece.current_rotation = next_rotation
        self.most_recent_move = "rotate"
        break  # Exit after a successful wall kick

# tests

if __name__ == "__main__":
  bag = SevenBag(1)
  gc = GameController("yeet", bag)
  gc.spawnTetromino()
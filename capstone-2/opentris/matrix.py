from constants import MATRIX_HEIGHT, MATRIX_WIDTH, GRAY
from tetromino import Tetromino

class Matrix:
  def __init__(self) -> None:
    self.grid = [[0 for _ in range(MATRIX_WIDTH)] for _ in range(MATRIX_HEIGHT)]

  def __eq__(self, value: object) -> bool:
    if isinstance(value, Matrix):
      return self.grid == value.grid
    return False

  def lockTetromino(self, tetromino: Tetromino) -> None:
    shape = tetromino.getShape()
    for row_idx, row in enumerate(shape):
      for col_idx, cell in enumerate(row):
        if int(cell):  # Check if the cell is part of the Tetromino
          if tetromino.y + row_idx >= 0:  # Only lock if it's in the visible area
            self.grid[tetromino.y + row_idx][tetromino.x + col_idx] = tetromino.color
    
  def clearLines(self) -> None:
    for y in range(MATRIX_HEIGHT):
      if all(self.grid[y]):
        del self.grid[y]
        self.grid.insert(0, [0 for _ in range(MATRIX_WIDTH)])
  
  def calculateLineClears(self) -> int:
    lines_cleared = 0
    for y in range(MATRIX_HEIGHT):
      if all(self.grid[y]):
        lines_cleared += 1
    return lines_cleared

  def checkCollision(self, piece_x: int, piece_y: int, shape: list) -> bool:
    # Check if the Tetromino collides with the walls, bottom, or other pieces
    for row_idx, row in enumerate(shape):
      for col_idx, cell in enumerate(row):
        if int(cell):  # Check if the cell is part of the Tetromino
          new_x = piece_x + col_idx
          new_y = piece_y + row_idx
          if new_y >= MATRIX_HEIGHT:  # Collision with bottom
              return True
          if new_x < 0 or new_x >= MATRIX_WIDTH:  # Collision with walls
              return True
          if new_y >= 0 and self.grid[new_y][new_x]:  # Collision with locked piece
              return True
    return False
  
  def receiveAttack(self, lines, hole):
    for _ in range(lines):
      self.grid.pop(0)  # Remove the top row
      # Add a new garbage row at the bottom with a hole
      garbage_row = [GRAY if x != hole else 0 for x in range(MATRIX_WIDTH)]
      self.grid.append(garbage_row)
    pass


if __name__ == "__main__":
  m = Matrix()
  t = Tetromino("I",0,18)
  t2 = Tetromino("I",4,18)
  t3 = Tetromino("O",7,18)
  # print(m.clearLines())
  m.lockTetromino(t)
  for row in m.grid:
    print(row)
  m.lockTetromino(t2)
  for row in m.grid:
    print(row)
  m.lockTetromino(t3)
  for row in m.grid:
    print(row)
  
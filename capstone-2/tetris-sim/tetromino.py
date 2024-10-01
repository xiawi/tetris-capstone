from constants import TETROMINOS, MINO_SIZE, WALL_KICK_DATA
import pygame

class Tetromino:
  def __init__(self, name: str, matrix):
    self.name = name
    self.rotations = TETROMINOS[name][0]
    self.color = TETROMINOS[name][1]
    self.current_rotation = 0
    self.x = 3 if name == "I" or name == "O" else 2 # adjust spawn locations
    self.y = -2
    self.matrix = matrix
  
  def getShape(self, rotation):
    shape = []
    for number in self.rotations[rotation]:
      shape.append((bin(number)[2:].zfill(4)))
    return shape

  def draw(self, screen, matrix_x, matrix_y):
    shape = self.getShape(self.current_rotation)
    for row_idx, row in enumerate(shape):
      for col_idx, cell in enumerate(row):
        if int(cell):
          color = self.color
          pygame.draw.rect(
            screen,
            color,
            pygame.Rect(matrix_x + self.x * MINO_SIZE + col_idx * MINO_SIZE, matrix_y + self.y * MINO_SIZE + row_idx * MINO_SIZE, MINO_SIZE, MINO_SIZE)
        )

  def rotateRight(self):
    next_rotation = (self.current_rotation + 1) % 4
    if not self.matrix.checkCollision(self.x, self.y, self.getShape(next_rotation)):
      self.current_rotation = next_rotation
      return  # No need to check for wall kicks
    
    if self.name == "I":
      kicks = WALL_KICK_DATA["IR"][self.current_rotation]
    else:
      kicks = WALL_KICK_DATA["R"][self.current_rotation]
    for dx, dy in kicks:
      new_x = self.x + dx
      new_y = self.y - dy
      if not self.matrix.checkCollision(new_x, new_y, self.getShape(next_rotation)):
        self.x = new_x
        self.y = new_y
        self.current_rotation = next_rotation
        break  # Exit after a successful wall kick


  def rotateLeft(self):
    next_rotation = (self.current_rotation - 1) % 4
    if not self.matrix.checkCollision(self.x, self.y, self.getShape(next_rotation)):
      self.current_rotation = next_rotation
      return  # No need to check for wall kicks
    
    if self.name == "I":
      kicks = WALL_KICK_DATA["IL"][self.current_rotation]
    else:
      kicks = WALL_KICK_DATA["L"][self.current_rotation]
    for dx, dy in kicks:
      new_x = self.x + dx
      new_y = self.y - dy
      if not self.matrix.checkCollision(new_x, new_y, self.getShape(next_rotation)):
        self.x = new_x
        self.y = new_y
        self.current_rotation = next_rotation
        break  # Exit after a successful wall kick

  def moveLeft(self):
    if not self.matrix.checkCollision(self.x - 1, self.y, self.getShape(self.current_rotation)):
      self.x -= 1

  def moveRight(self):
    if not self.matrix.checkCollision(self.x + 1, self.y, self.getShape(self.current_rotation)):
      self.x += 1
  
  def softDrop(self):
    if not self.matrix.checkCollision(self.x, self.y + 1, self.getShape(self.current_rotation)):
      self.y += 1

  def hardDrop(self):
    y = self.y  # Start from current y position
    while not self.matrix.checkCollision(self.x, y + 1, self.getShape(self.current_rotation)):
        y += 1  # Move down until collision occurs
    self.y = y  # Set final y position
    self.matrix.lockPiece()  # Lock the piece in the matrix
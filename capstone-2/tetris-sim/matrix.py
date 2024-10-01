import random
from constants import MATRIX_HEIGHT, MATRIX_WIDTH, MINO_SIZE, TETROMINOS
import pygame 
from tetromino import Tetromino
from lookahead import Lookahead

class Matrix:

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.grid = [[0 for _ in range (0, MATRIX_WIDTH)] for _ in range (0, MATRIX_HEIGHT)] # empty grid
    self.lookahead = Lookahead()
    self.current_piece = None

  def drawGrid(self, screen):
    for x in range (0, MATRIX_WIDTH):
      for y in range (0, MATRIX_HEIGHT):
        rect = pygame.Rect(self.x + x * MINO_SIZE, self.y + y * MINO_SIZE, MINO_SIZE, MINO_SIZE)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

  def spawnPiece(self): # TODO: REWORK
    if self.lookahead.isEmpty():
      self.lookahead.generateQueue()
    tetromino = self.piece_sequence.pop(0)
    self.current_piece = Tetromino(tetromino, self)

  def draw(self, screen):
    self.drawGrid(screen)
    # Draw the current piece on the grid
    if self.current_piece:
      self.current_piece.draw(screen, self.x, self.y)

    for y, row in enumerate(self.grid):
      for x, cell in enumerate(row):
        if cell:
          pygame.draw.rect(screen, cell, pygame.Rect(self.x + x * MINO_SIZE, self.y + y * MINO_SIZE, MINO_SIZE, MINO_SIZE))


  def checkCollision(self, piece_x, piece_y, shape):
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
  
  def clearLines(self):
    # Clear full lines from the grid
    for y in range(MATRIX_HEIGHT):
      if all(self.grid[y]):
        del self.grid[y]
        self.grid.insert(0, [0 for _ in range(MATRIX_WIDTH)])

  def lockPiece(self):
    # Lock the current piece into the grid
    shape = self.current_piece.getShape(self.current_piece.current_rotation)
    for row_idx, row in enumerate(shape):
      for col_idx, cell in enumerate(row):
        if int(cell):  # Check if the cell is part of the Tetromino
          if self.current_piece.y + row_idx >= 0:  # Only lock if it's in the visible area
            self.grid[self.current_piece.y + row_idx][self.current_piece.x + col_idx] = self.current_piece.color
    self.clearLines()
    self.spawnPiece()

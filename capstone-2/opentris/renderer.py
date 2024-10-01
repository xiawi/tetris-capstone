import pygame
from constants import MINO_SIZE, BACKGROUND_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, MATRIX_HEIGHT, MATRIX_WIDTH, GRID_COLOR
from gamecontroller import GameController

class Renderer:
  def __init__(self, game_controller: GameController):
    self.game_controller = game_controller
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    self.x = 0
    self.y = 0

  def drawHold(self):
    x = (self.x + 1) * MINO_SIZE
    y = (self.y + 3) * MINO_SIZE
    hold_piece = self.game_controller.hold.getHeldPiece()  # Assuming you have a hold in GameController
    if hold_piece:
      # Draw the hold piece to the left of the matrix
      for row_idx, row in enumerate(hold_piece.getRotatedShape(0)):
          for col_idx, cell in enumerate(row):
              if int(cell):  # Only draw filled cells
                  rect_x = x + col_idx * MINO_SIZE
                  rect_y = y + row_idx * MINO_SIZE
                  piece_rect = pygame.Rect(rect_x, rect_y, MINO_SIZE, MINO_SIZE)
                  pygame.draw.rect(self.screen, hold_piece.color, piece_rect)
      # Optionally, draw an outline for the hold piece
    
  def drawGrid(self):
    x = (self.x + 6) * MINO_SIZE
    y = (self.y + 3) * MINO_SIZE
    # Draw the grid with a white outline and locked pieces
    for row in range(MATRIX_HEIGHT):
      for col in range(MATRIX_WIDTH):
        rect_x = x + col * MINO_SIZE
        rect_y = y + row * MINO_SIZE
        
        # Draw the outline for the grid cell
        pygame.draw.rect(self.screen, (255, 255, 255), (rect_x, rect_y, MINO_SIZE, MINO_SIZE), 1)  # White outline
        
        # Draw locked pieces (if any)
        cell_value = self.game_controller.matrix.grid[row][col]  # Assuming matrix.grid contains colors for locked pieces
        if cell_value != 0:  # Only draw if there's a locked piece
          pygame.draw.rect(self.screen, cell_value, (rect_x, rect_y, MINO_SIZE, MINO_SIZE))  # Draw filled cell

    
  def drawActivePiece(self):
    x = (self.x + 6) * MINO_SIZE
    y = (self.y + 3) * MINO_SIZE
    active_piece = self.game_controller.active_piece  # Assuming you have an active_piece in GameController
    if active_piece:
      shape = active_piece.getShape()
      for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
          if int(cell):  # Only draw filled cells
            rect_x = x + (active_piece.x + col_idx) * MINO_SIZE
            rect_y = y + (active_piece.y + row_idx) * MINO_SIZE
            piece_rect = pygame.Rect(rect_x, rect_y, MINO_SIZE, MINO_SIZE)
            pygame.draw.rect(self.screen, active_piece.color, piece_rect)

  def drawLookahead(self):
    x = (self.x + 17) * MINO_SIZE
    y = (self.y + 3) * MINO_SIZE
    lookahead = self.game_controller.lookahead.getQueue()
    for tetromino in lookahead:
      for row_idx, row in enumerate(tetromino.getRotatedShape(0)):
        for col_idx, cell in enumerate(row):
          if int(cell):
            rect_x = x + col_idx * MINO_SIZE
            rect_y = y + row_idx * MINO_SIZE
            piece_rect = pygame.Rect(rect_x, rect_y, MINO_SIZE, MINO_SIZE)
            pygame.draw.rect(self.screen, tetromino.color, piece_rect)
      y += 3 * MINO_SIZE
    pass

  def render(self):
      self.screen.fill(BACKGROUND_COLOR)
      self.drawHold()
      self.drawGrid()
      self.drawActivePiece()
      self.drawLookahead()
      pygame.display.flip()
import pygame
from constants import MINO_SIZE, BACKGROUND_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, MATRIX_HEIGHT, MATRIX_WIDTH, GRAY
from gamecontroller import GameController

class Renderer:
  def __init__(self, board: GameController):
    self.board = board
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

  def drawHold(self, game_controller: GameController, x: int):
    x = (x + 1) * MINO_SIZE
    y = 3 * MINO_SIZE
    hold_piece = game_controller.hold.getHeldPiece()  # Assuming you have a hold in GameController
    if hold_piece:
      # Draw the hold piece to the left of the matrix
      for row_idx, row in enumerate(hold_piece.getRotatedShape(0)):
          for col_idx, cell in enumerate(row):
              if int(cell):  # Only draw filled cells
                  rect_x = x + col_idx * MINO_SIZE
                  rect_y = y + row_idx * MINO_SIZE
                  piece_rect = pygame.Rect(rect_x, rect_y, MINO_SIZE, MINO_SIZE)
                  if not game_controller.has_lost:
                    pygame.draw.rect(self.screen, hold_piece.color, piece_rect)
                  else:
                    pygame.draw.rect(self.screen, GRAY, piece_rect)
    
  def drawGrid(self, game_controller: GameController, x: int):
    x = (x + 6) * MINO_SIZE
    y = 1 * MINO_SIZE
    # Draw the grid with a white outline and locked pieces
    for row in range(0, MATRIX_HEIGHT):
      for col in range(MATRIX_WIDTH):
        rect_x = x + col * MINO_SIZE
        rect_y = y + row * MINO_SIZE
        
        if row >= 2:
          # Draw the outline for the grid cell
          pygame.draw.rect(self.screen, (255, 255, 255), (rect_x, rect_y, MINO_SIZE, MINO_SIZE), 1)  # White outline
        
        # Draw locked pieces (if any)
        cell_value = game_controller.matrix.grid[row][col]  # Assuming matrix.grid contains colors for locked pieces
        if cell_value != 0:  # Only draw if there's a locked piece
          if not game_controller.has_lost:
            pygame.draw.rect(self.screen, cell_value, (rect_x, rect_y, MINO_SIZE, MINO_SIZE))  # Draw filled cell
          else:
            pygame.draw.rect(self.screen, GRAY, (rect_x, rect_y, MINO_SIZE, MINO_SIZE))

    
  def drawActivePiece(self, game_controller: GameController, x: int):
    x = (x + 6) * MINO_SIZE
    y = 1 * MINO_SIZE
    active_piece = game_controller.active_piece  # Assuming you have an active_piece in GameController
    if active_piece:
      shape = active_piece.getShape()
      for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
          if int(cell):  # Only draw filled cells
            rect_x = x + (active_piece.x + col_idx) * MINO_SIZE
            rect_y = y + (active_piece.y + row_idx) * MINO_SIZE
            piece_rect = pygame.Rect(rect_x, rect_y, MINO_SIZE, MINO_SIZE)
            if not game_controller.has_lost:
              pygame.draw.rect(self.screen, active_piece.color, piece_rect)
            else:
              pygame.draw.rect(self.screen, GRAY, piece_rect)

  def drawLookahead(self, game_controller: GameController, x: int):
    x = (x + 17) * MINO_SIZE
    y = 3 * MINO_SIZE
    lookahead = game_controller.lookahead.getQueue()
    for tetromino in lookahead:
      for row_idx, row in enumerate(tetromino.getRotatedShape(0)):
        for col_idx, cell in enumerate(row):
          if int(cell):
            rect_x = x + col_idx * MINO_SIZE
            rect_y = y + row_idx * MINO_SIZE
            piece_rect = pygame.Rect(rect_x, rect_y, MINO_SIZE, MINO_SIZE)
            if not game_controller.has_lost:
              pygame.draw.rect(self.screen, tetromino.color, piece_rect)
            else:
              pygame.draw.rect(self.screen, GRAY, piece_rect)
      y += 3 * MINO_SIZE
    pass

  def drawGhost(self, game_controller: GameController, x: int):
    x = (x + 6) * MINO_SIZE
    y = 1 * MINO_SIZE
    active_piece = game_controller.active_piece
    if active_piece:
      piece_x, piece_y = game_controller.getGhostPosition()
      shape = active_piece.getShape()
      for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
          if int(cell):  # Only draw filled cells
            rect_x = x + (piece_x + col_idx) * MINO_SIZE
            rect_y = y + (piece_y + row_idx) * MINO_SIZE
            piece_rect = pygame.Rect(rect_x, rect_y, MINO_SIZE, MINO_SIZE)
            pygame.draw.rect(self.screen, active_piece.color, piece_rect, 1) 
    pass

  def drawBoard(self, game_controller: GameController, x: int):
    self.drawHold(game_controller, x)
    self.drawGrid(game_controller, x)
    self.drawActivePiece(game_controller, x)
    self.drawLookahead(game_controller, x)
    self.drawGhost(game_controller, x)
    pass

  def render(self):
    self.screen.fill(BACKGROUND_COLOR)
    self.drawBoard(self.board, 0)
    pygame.display.set_caption("OpenTris")
    pygame.display.flip()
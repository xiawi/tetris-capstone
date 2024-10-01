import pygame
from constants import MINO_SIZE, BACKGROUND_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, MATRIX_HEIGHT, MATRIX_WIDTH
from gamecontroller import GameController

class Renderer:
  def __init__(self, game_controller: GameController):
    self.game_controller = game_controller
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
  def draw_grid(self):
    pass
    
  def draw_active_piece(self):
    pass

  def draw_hold(self):
    pass

  def draw_lookahead(self):
    pass

  def render(self):
      self.screen.fill(BACKGROUND_COLOR)
      self.draw_grid()
      self.draw_active_piece()
      self.draw_hold()
      self.draw_lookahead()
      pygame.display.flip()
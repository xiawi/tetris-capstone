import pygame

from gamecontroller import GameController

class Bot:
  def __init__(self, game_controller: GameController):
    self.game_controller = game_controller
  
  def takeAction(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit()  # Exit the game
    self.game_controller.hardDrop()
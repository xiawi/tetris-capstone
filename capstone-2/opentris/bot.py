import pygame

from gamecontroller import GameController

class Bot:
  def __init__(self, me: GameController, opponent: GameController):
    self.me = me
    self.opponent = opponent
  
  def takeAction(self): # this needs to end in a piece placement
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit()  # Exit the game
    self.me.hardDrop()
  
  def eval(self):

    pass
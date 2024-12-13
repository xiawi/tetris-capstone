import pygame

from settings import SEED
from gamecontroller import GameController
from tetromino import Tetromino
from sevenbag import SevenBag
from botonly_renderer import Renderer
from bot import Bot
from garbagesystem import GarbageSystem

class GameManager():
  def __init__(self):
    if SEED:
      seed = SEED
    else:
      seed = 9

    self.bag = SevenBag(seed)
    self.garbage_system = GarbageSystem(seed)

    self.board = GameController(self.bag, self.garbage_system)
    self.bot = Bot(self.board, [-0.9241634548042859, -0.6344800815480418, -1, -0.7518857423370778, 0.026389760264537543, -0.7016450659573539, 0.07718788025481071, 0.48772306100581286, -0.3671494868227996, 1])
    self.renderer = Renderer(self.board)
    self.clock = pygame.time.Clock()

  def run(self) -> GameController:
    running = True
    while running:
      try:
        self.clock.tick(11111)  # Keep smooth rendering
        self.renderer.render()  # Render the board
        self.bot.takeAction()

        if self.board.has_lost or self.board.tetrominos_placed > 100:
          pygame.time.wait(1000)
          break

        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            pygame.quit()
            exit()  # Exit the game
          # if event.type == pygame.KEYDOWN:
          #   self.bot.takeAction()
      except:
        running = False
    return self.board.total_attack / self.board.tetrominos_placed
    

if __name__ == "__main__":
  pygame.init()
  gm = GameManager()
  print(gm.run())
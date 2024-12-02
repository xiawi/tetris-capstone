import pygame
import random

from settings import SEED
from gamecontroller import GameController
from sevenbag import SevenBag
from botonly_renderer import Renderer
from bot import Bot
from garbagesystem import GarbageSystem

class GameManager():
  def __init__(self):
    if SEED:
      seed = SEED
    else:
      seed = random.random()

    self.bag = SevenBag(seed)
    self.garbage_system = GarbageSystem(seed)

    self.board = GameController("Bot", self.bag, self.garbage_system)
    for x in range(10):
      self.board.matrix.grid[21][x] = 1 if x < 7 else 0
      self.board.matrix.grid[20][x] = 1 if x < 9 else 0
      self.board.matrix.grid[19][x] = 1 if x < 9 else 0
    self.bot = Bot(self.board)
    self.renderer = Renderer(self.board)
    self.clock = pygame.time.Clock()

  def run(self) -> GameController:
    running = True
    while running:
      try:
        self.clock.tick(1)  # Keep smooth renderingy
        self.renderer.render()  # Render the board
        self.bot.takeAction()

        if self.board.has_lost:
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

if __name__ == "__main__":
  pygame.init()
  gm = GameManager()
  gm.run()
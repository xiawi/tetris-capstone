import pygame

from settings import QUEUE_SEED, PLAYER
from gamecontroller import GameController
from sevenbag import SevenBag
from inputhandler import InputHandler
from renderer import Renderer

class GameManager():
  def __init__(self):
    self.left_board = GameController(SevenBag(QUEUE_SEED))
    if PLAYER:
      self.input_handler = InputHandler(self.left_board)
    self.renderer = Renderer(self.left_board)
    self.clock = pygame.time.Clock()

  def run(self):
    running = True
    while running:
      self.input_handler.handleInput()  # Handle user input
      self.renderer.render()  # Render game state
      self.clock.tick(60)  # Control frame rate

if __name__ == "__main__":
  pygame.init()
  gm = GameManager()
  gm.run()
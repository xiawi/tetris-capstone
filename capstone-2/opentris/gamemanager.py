import pygame
import random

from settings import QUEUE_SEED, PLAYER
from gamecontroller import GameController
from sevenbag import SevenBag
from inputhandler import InputHandler
from renderer import Renderer
from bot import Bot

class GameManager():
  def __init__(self):
    if QUEUE_SEED:
      seed = QUEUE_SEED
    else:
      seed = random.random()
    self.bag = SevenBag(seed)
    self.left_board = GameController(self.bag)
    self.right_board = GameController(self.bag)
    if PLAYER:
      self.input_handler = InputHandler(self.left_board)
    else:
      self.left_bot = Bot(self.left_board, self.right_board)
    self.right_bot = Bot(self.right_board, self.left_board)
    self.renderer = Renderer(self.left_board, self.right_board)
    self.clock = pygame.time.Clock()
    self.current_player = "left"

  def switch_turns(self):
    if self.current_player == 'left':
      self.current_player = 'right'
    else:
      self.current_player = 'left'

  def run(self):
    running = True
    while running:
      self.clock.tick(120)  # Keep smooth rendering, but handle turns separately
      self.renderer.render()  # Render the boards

      if PLAYER:
        if self.current_player == 'left':
          self.input_handler.handleInput()  # Handle user input for left board
          if self.left_board.matrix.tetrominos_placed > self.right_board.matrix.tetrominos_placed:
              self.switch_turns()
        else:
          self.right_bot.takeAction()  # Right bot takes its turn
          self.switch_turns()
      else:
        if self.current_player == 'left':
          self.left_bot.takeAction()
          self.switch_turns()
        else:
          self.right_bot.takeAction()
          self.switch_turns()

if __name__ == "__main__":
  pygame.init()
  gm = GameManager()
  gm.run()
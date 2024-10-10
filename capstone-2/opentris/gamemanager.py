import pygame
import random

from settings import SEED, PLAYER
from gamecontroller import GameController
from sevenbag import SevenBag
from inputhandler import InputHandler
from renderer import Renderer
from bot import Bot
from storedgarbage import StoredGarbage

class GameManager():
  def __init__(self, left_name: str = "L", right_name: str = "R"):
    if SEED:
      seed = SEED
    else:
      seed = random.random()

    self.bag = SevenBag(seed)

    self.left_board = GameController(left_name, self.bag)
    self.right_board = GameController(right_name, self.bag)
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

  def run(self) -> GameController:
    running = True
    while running:
      try:
        self.clock.tick(120)  # Keep smooth rendering, but handle turns separately
        self.renderer.render()  # Render the boards

        if not self.left_board.has_lost and not self.right_board.has_lost:
          if PLAYER:
            if self.current_player == 'left':
              self.input_handler.handleInput()  # Handle user input for left board
              # if self.left_d
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
        else:
          pygame.time.wait(1000)
          break

        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            pygame.quit()
            exit()  # Exit the game
      except:
        running = False
    
    return self.left_board if self.right_board.has_lost else self.right_board
      
      

if __name__ == "__main__":
  pygame.init()
  gm = GameManager()
  gm.run()
import pygame
import random

from settings import SEED, PLAYER
from gamecontroller import GameController
from sevenbag import SevenBag
from inputhandler import InputHandler
from renderer import Renderer
from bot import Bot
from garbagesystem import GarbageSystem

class GameManager():
  def __init__(self, left_name: str = "L", right_name: str = "R"):
    if SEED:
      seed = SEED
    else:
      seed = random.random()

    self.bag = SevenBag(seed)
    self.garbage_system = GarbageSystem(seed)

    self.left_board = GameController(left_name, self.bag, self.garbage_system)
    self.right_board = GameController(right_name, self.bag, self.garbage_system)
    if PLAYER:
      self.input_handler = InputHandler(self.left_board)
    else:
      self.left_bot = Bot(self.left_board)
    self.right_bot = Bot(self.right_board)
    self.renderer = Renderer(self.left_board, self.right_board)
    self.clock = pygame.time.Clock()
    self.current_player = "left"

  def switchTurns(self):
    if self.current_player == 'left':
      self.current_player = 'right'
    else:
      self.current_player = 'left'

  def sendAttack(self, sender: GameController, receiver: GameController): # TODO
    if sender.most_recent_attack:
      receiver.storeAttack(sender.most_recent_attack)
      sender.most_recent_attack = 0

  def run(self) -> GameController:
    running = True
    while running:
      try:
        if PLAYER:
          self.clock.tick(120)  # Keep smooth rendering, but handle turns separately
        else:
          self.clock.tick(10)  # Keep smooth rendering, but handle turns separately
        self.renderer.render()  # Render the boards

        if not self.left_board.has_lost and not self.right_board.has_lost:
          if PLAYER:
            if self.current_player == 'left':
              self.input_handler.handleInput()  # Handle user input for left board
              if self.left_board.tetrominos_placed > self.right_board.tetrominos_placed:
                self.sendAttack(self.left_board, self.right_board)
                self.switchTurns()
            else:
              self.right_bot.takeAction()  # Right bot takes its turn
              self.sendAttack(self.right_board, self.left_board)
              self.switchTurns()
          else:
            if self.current_player == 'left':
              self.left_bot.takeAction()
              self.sendAttack(self.left_board, self.right_board)
              self.switchTurns()
            else:
              self.right_bot.takeAction()
              self.sendAttack(self.right_board, self.left_board)
              self.switchTurns()
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
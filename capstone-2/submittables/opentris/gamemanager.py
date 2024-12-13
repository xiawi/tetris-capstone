import pygame
import random

from settings import SEED, PLAYER, MAX_PIECES
from gamecontroller import GameController
from sevenbag import SevenBag
from inputhandler import InputHandler
from renderer import Renderer
from bot import Bot
from garbagesystem import GarbageSystem

class GameManager():
  def __init__(self, renderer:bool = True, left_weights: list = None, right_weights:list = None):
    if SEED:
      seed = SEED
    else:
      seed = random.random()

    self.bag = SevenBag(seed)
    self.garbage_system = GarbageSystem(seed)

    self.left_board = GameController(self.bag, self.garbage_system)
    self.right_board = GameController(self.bag, self.garbage_system)
    if PLAYER:
      self.input_handler = InputHandler(self.left_board)
    else:
      self.left_bot = Bot(self.left_board, left_weights)
    self.right_bot = Bot(self.right_board, right_weights)
    self.use_renderer = renderer
    if renderer:
      self.renderer = Renderer(self.left_board, self.right_board)
      self.clock = pygame.time.Clock()
    self.current_player = "left"

  def switchTurns(self):
    if self.current_player == 'left':
      self.current_player = 'right'
    else:
      self.current_player = 'left'

  def sendAttack(self, sender: GameController, receiver: GameController):
    if sender.most_recent_attack:
      receiver.storeAttack(sender.most_recent_attack)
      sender.most_recent_attack = 0

  def run(self) -> GameController:
    running = True
    
    while running:
      try:
        
        if self.use_renderer:
          if PLAYER:
            self.clock.tick(120)  # Keep smooth rendering, but handle turns separately
          else:
            self.clock.tick(10)  # Keep smooth rendering, but handle turns separately
          self.renderer.render()  # Render the boards

        if not self.left_board.has_lost and not self.right_board.has_lost and self.right_board.tetrominos_placed < MAX_PIECES:
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

        if self.use_renderer:
          for event in pygame.event.get():
            if event.type == pygame.QUIT:
              pygame.quit()
              exit()  # Exit the game
      except Exception as e:
        print(e)
        running = False
    
    if self.right_board.has_lost:
      winner = 0
    elif self.left_board.has_lost:
      winner = 1
    else:
      winner = 0.5

    return [winner, self.left_board.total_attack/self.left_board.tetrominos_placed, self.right_board.total_attack/self.right_board.tetrominos_placed, self.left_board.tetrominos_placed, self.right_board.tetrominos_placed]
      
      

if __name__ == "__main__":
  pygame.init()
  for i in range(45):
    gm = GameManager(False)
    print(gm.run())
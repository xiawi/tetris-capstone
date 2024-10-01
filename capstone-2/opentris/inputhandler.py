import pygame

from gamecontroller import GameController

class InputHandler:
  def __init__(self, game_controller: GameController):
    self.game_controller = game_controller

  def handleInput(self):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
      self.game_controller.softDrop()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit()  # Exit the game
      if event.type == pygame.KEYDOWN:
        self.processKeyEvent(event.key)

  def processKeyEvent(self, key):
    if key == pygame.K_LEFT:
      self.game_controller.moveLeft()
    if key == pygame.K_RIGHT:
      self.game_controller.moveRight()
    if key == pygame.K_SPACE:
      self.game_controller.hardDrop()
    if key == pygame.K_a:
      self.game_controller.rotateLeft()
    if key == pygame.K_s:
      self.game_controller.rotateRight()
    if key == pygame.K_d:
      self.game_controller.holdPiece()
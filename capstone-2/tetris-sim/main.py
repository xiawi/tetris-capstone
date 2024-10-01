import pygame
import constants
from matrix import Matrix

pygame.init()
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
clock = pygame.time.Clock()

running = True

m = Matrix(20, 50)

while running:

  keys = pygame.key.get_pressed()
  if keys[pygame.K_DOWN]:
    m.current_piece.softDrop()
  
  for event in pygame.event.get():

    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.KEYDOWN:

      if event.key == pygame.K_a:
        m.current_piece.rotateLeft()
      elif event.key == pygame.K_s:
        m.current_piece.rotateRight()
      elif event.key == pygame.K_d:
        m.current_piece = None
      elif event.key == pygame.K_LEFT:
        m.current_piece.moveLeft()
      elif event.key == pygame.K_RIGHT:
        m.current_piece.moveRight()
      elif event.key == pygame.K_SPACE:
        m.current_piece.hardDrop()

  screen.fill(constants.BLACK)
  
  if m.current_piece == None:
    m.spawnPiece()

  m.draw(screen)

  pygame.display.update()

  clock.tick(120)

pygame.quit()

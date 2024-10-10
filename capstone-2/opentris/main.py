import pygame

from gamemanager import GameManager

def main():
  pygame.init()
  game = GameManager("Bob", "Bot")
  winner = game.run()
  print(winner.name)
  print(winner.matrix.tetrominos_placed)

if __name__ == "__main__":
  main()
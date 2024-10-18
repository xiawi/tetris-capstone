import pygame

from gamemanager import GameManager

def main():
  pygame.init()
  game = GameManager("Bob", "Bot")
  winner = game.run()
  print(winner.name)
  print(winner.total_attack)
  print(winner.tetrominos_placed)
  print(winner.total_attack/winner.tetrominos_placed)

if __name__ == "__main__":
  main()
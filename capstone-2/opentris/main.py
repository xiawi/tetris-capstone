import pygame

from gamemanager import GameManager

def main():
  pygame.init()
  game = GameManager("Left", "Right")
  winner = game.run()
  attack_efficiency = winner.total_attack/winner.tetrominos_placed
  print(winner.name)
  print(winner.total_attack)
  print(winner.tetrominos_placed)
  print(attack_efficiency)
  return attack_efficiency

if __name__ == "__main__":
  main()
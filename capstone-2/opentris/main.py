import pygame

from gamemanager import GameManager

def main():
  pygame.init()
  game = GameManager()
  game.run()

if __name__ == "__main__":
  main()
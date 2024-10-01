import pygame
from sevenbag import SevenBag
from tetromino import Tetromino
from constants import MATRIX_WIDTH, MINO_SIZE

class Lookahead:
  def __init__(self):
    self.seven_bag = SevenBag()
    self.queue = []
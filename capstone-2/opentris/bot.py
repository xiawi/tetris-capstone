import pygame
import random
import copy

from gamecontroller import GameController
from tetromino import Tetromino
from matrix import Matrix
from sevenbag import SevenBag
from garbagesystem import GarbageSystem
from constants import MATRIX_HEIGHT, MATRIX_WIDTH

class Bot:
  def __init__(self, me: GameController):
    random.seed()
    self.me = me
    self.hole_weight = random.random()
    self.height_weight = random.random()
    self.line_clear_weight = 10 * random.random()
    print(self.hole_weight, self.height_weight, self.line_clear_weight)
  
  def takeAction(self): # this needs to end in a piece placement

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit()  # Exit the game

    curr_tetrominos_placed = self.me.tetrominos_placed

    while(self.me.tetrominos_placed == curr_tetrominos_placed):
      legal_placements = self.generateLegalPlacements(self.me.active_piece, self.me.matrix, self.me.hold.can_hold)
      legal_placements = sorted(
        legal_placements, 
        key=lambda placement: self.evaluatePlacement(placement[0], placement[2]),
        reverse = True)
      chosen_piece_seq = legal_placements[0]
      # return chosen_piece_seq
      actions = [i for i in chosen_piece_seq[1]]
      while not actions == []:
          a = actions.pop(0)
          if a == "H":
            self.me.holdPiece()
          if a == "LR":
            self.me.rotateLeft()
          if a == "RR":
            self.me.rotateRight()
          if a == "HD":
            self.me.hardDrop()
          if a == "L":
            self.me.moveLeft()
          if a =="R":
            self.me.moveRight()
          if a == "SD":
            self.me.softDrop()

  def generateLegalPlacements(self, tetromino:Tetromino, matrix: Matrix, can_hold: bool):
    
    matrices = []
    action_sequence = []
    line_clears = []
    
    if can_hold:
      matrices.append(matrix)
      action_sequence.append(["H"])
      line_clears.append(0)
      
    # find simple placements for each rotation, ie hard drop in each column with each rotation
    for rotation in range(4):
      
      tetromino_copy = copy.deepcopy(tetromino)
      tetromino_copy.current_rotation = rotation
      matrix_copy = copy.deepcopy(matrix)
      ori_x = tetromino_copy.x
      
      for x in self.getXRange(tetromino_copy, matrix_copy):
        actions = []
        new_tetromino = copy.deepcopy(tetromino_copy)
        new_matrix = copy.deepcopy(matrix_copy)
        new_tetromino.x = x
        
        match rotation:
          case 1:
            actions.append("RR")
          case 2:
            actions.extend(["RR", "RR"])
          case 3:
            actions.append("LR")
          case _:
            pass
          
        x_ref = x
        while x_ref != ori_x:
          if x_ref < ori_x:
            actions.append("L")
            x_ref += 1
          elif x_ref > ori_x:
            actions.append("R")
            x_ref -= 1
        
        lines = self.simulateHardDrop(new_tetromino, new_matrix)
        actions.append("HD")
        
        if not new_matrix in matrices:
          matrices.append(new_matrix)
          action_sequence.append(actions)
          line_clears.append(lines)
      
    return list(zip(matrices, action_sequence, line_clears))
      
  def getXRange(self, tetromino: Tetromino, matrix: Matrix):
    ghost_tetromino = copy.deepcopy(tetromino)
    while not matrix.checkCollision(ghost_tetromino.x - 1, ghost_tetromino.y, ghost_tetromino.getShape()):
      ghost_tetromino.x -= 1
    min_x = ghost_tetromino.x
    while not matrix.checkCollision(ghost_tetromino.x + 1, ghost_tetromino.y, ghost_tetromino.getShape()):
      ghost_tetromino.x += 1
    max_x = ghost_tetromino.x + 1
    return range(min_x, max_x)

  def simulateHardDrop(self, tetromino: Tetromino, matrix: Matrix):
    while not matrix.checkCollision(tetromino.x, tetromino.y + 1, tetromino.getShape()):
      tetromino.y += 1
    matrix.lockTetromino(tetromino)
    line_clears =  matrix.calculateLineClears()
    matrix.clearLines()
    return line_clears
  
  def evaluatePlacement(self, matrix: Matrix, cleared_lines):
    # evaluation function
    holes = self.getHoles(matrix)
    height = self.getHeight(matrix)
    evaluation = - self.hole_weight * holes - self.height_weight * height + self.line_clear_weight * cleared_lines
    return evaluation

  def getHoles(self, matrix: Matrix):
    holes = 0
    for x in range(MATRIX_WIDTH):
      for y in range(1, MATRIX_HEIGHT):
        if not matrix.grid[y][x] == matrix.grid[y - 1][x]:
          holes += 1
    return holes
            
  def getHeight(self, matrix):
    for i in range(MATRIX_HEIGHT):
      if any(matrix.grid[i]):
        return 22 - i
    return 0
  
if __name__ == "__main__":
   gc = GameController("bot", SevenBag(3), GarbageSystem(3))
   bot = Bot(gc)
   for x in range(MATRIX_WIDTH):
     gc.matrix.grid[21][x] = 1 if x != 0 else 0
     gc.matrix.grid[20][x] = 1 if x != 0 else 0
     gc.matrix.grid[19][x] = 1 if x != 0 else 0
     gc.matrix.grid[18][x] = 1 if x != 0 else 0
   placements = bot.generateLegalPlacements(Tetromino("I", 4, 0), gc.matrix, True)
   for placement in placements:
     print(bot.getHeight(placement[0]))
   action = bot.takeAction()
   print(bot.evaluatePlacement(action[0], action[2]))
   
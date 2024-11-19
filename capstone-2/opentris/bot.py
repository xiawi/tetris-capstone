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
      
    self.hole_weight = 0.9505323074748682
    self.height_weight = 0.7995978091274729
    self.line_clear_weight = 0.06271360911767687
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
      # actions = ["SD","SD"]

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
      landing_states = []
      
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
        landing_states.append([new_tetromino.x, new_tetromino.y])
        actions.append("HD")
        
        if not new_matrix in matrices:
          matrices.append(new_matrix)
          action_sequence.append(actions)
          line_clears.append(lines)
      
      tuck_considerations = []
      
      for i in range(1, len(landing_states)):
        if landing_states[i][1] - landing_states[i - 1][1] >= 2:
          # consider tucks for current state
          if [landing_states[i][0], landing_states[i - 1][1] + 2] not in tuck_considerations:
            tuck_considerations.append([landing_states[i][0], landing_states[i - 1][1] + 1])
        elif landing_states[i][1] - landing_states[i - 1][1] <= -2:
          if [landing_states[i - 1][0], landing_states[i][1] + 2] not in tuck_considerations:
            tuck_considerations.append([landing_states[i - 1][0], landing_states[i][1] + 1])
            
      for c in tuck_considerations:
        
        actions = []
        new_tetromino = copy.deepcopy(tetromino_copy)
        new_matrix = copy.deepcopy(matrix_copy)
        new_tetromino.x = c[0]
        new_tetromino.y = c[1]

        match rotation:
          case 1:
            actions.append("RR")
          case 2:
            actions.extend(["RR", "RR"])
          case 3:
            actions.append("LR")
          case _:
            pass
          
        x_ref = c[0]
        while x_ref != ori_x:
          if x_ref < ori_x:
            actions.append("L")
            x_ref += 1
          elif x_ref > ori_x:
            actions.append("R")
            x_ref -= 1
        
        y_ref = c[1]
        while y_ref != 0:
          actions.append("SD")
          y_ref -= 1
          
        while not new_matrix.checkCollision(new_tetromino.x, new_tetromino.y, new_tetromino.getShape()):
          new_tetromino.y += 1
          actions.append("SD")
          for x in self.getXRange(new_tetromino, new_matrix):
            if x == new_tetromino.x:
              pass
            else:
              tucked_actions = actions[:]
              tucked_tetromino = copy.deepcopy(new_tetromino)
              tucked_matrix = copy.deepcopy(new_matrix)
              
              while tucked_tetromino.x != x:
                if tucked_tetromino.x > x:
                  tucked_tetromino.x -= 1
                  tucked_actions.append("L")
                elif tucked_tetromino.x < x:
                  tucked_tetromino.x += 1
                  tucked_actions.append("R")
              
              lines = self.simulateHardDrop(tucked_tetromino, tucked_matrix)
              landing_states.append([tucked_tetromino.x, tucked_tetromino.y])
              tucked_actions.append("HD")
              
              if not tucked_matrix in matrices:
                matrices.append(tucked_matrix)
                action_sequence.append(tucked_actions)
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
    # evaluation = - 20 * holes - height
    return evaluation

  def getHoles(self, matrix: Matrix):
    # TODO redo this part man please don't forget man
    holes = 0
    for x in range(MATRIX_WIDTH):
      for y in range(1, MATRIX_HEIGHT):
        if matrix.grid[y - 1][x]:
          if matrix.grid[y][x] == 0:
            holes += 1
    return holes
            
  def getHeight(self, matrix):
    for i in range(MATRIX_HEIGHT):
      if any(matrix.grid[i]):
        return 22 - i
    return 0
  
if __name__ == "__main__":
   gc = GameController("bot", SevenBag(1), GarbageSystem(1))
   bot = Bot(gc)
   for x in range(MATRIX_WIDTH):
     gc.matrix.grid[21][x] = 1 if x < 5 else 0
     gc.matrix.grid[20][x] = 1 if x < 7 else 0
     gc.matrix.grid[19][x] = 1 if x < 7 else 0
     gc.matrix.grid[18][x] = 1 if x < 7 else 0
   placements = bot.generateLegalPlacements(Tetromino("L", 4, 0), gc.matrix, True)
   # print(bot.evaluatePlacement(placements[9][0], placements[9][2]))
   # print(bot.getHoles(placements[9][0]))
   for placement in placements:
     print(bot.evaluatePlacement(placement[0], placement[2]))
   bot.takeAction()
   
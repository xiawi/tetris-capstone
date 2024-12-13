import pygame
import random
import copy

from gamecontroller import GameController
from tetromino import Tetromino
from matrix import Matrix
from sevenbag import SevenBag
from garbagesystem import GarbageSystem
from constants import MATRIX_HEIGHT, MATRIX_WIDTH, WALL_KICK_DATA

class Bot:
  def __init__(self, me: GameController, weight_vector: list = None):
    random.seed()
    self.me = me
      
    # self.hole_weight = -0.6483074206751366
    # self.height_weight = -0.9550269397680944
    # self.line_clear_weight = 0.7139929472467322
    if not weight_vector:
      self.height_weight = random.uniform(-1,1)
      self.hole_weight = random.uniform(-1,1)
      self.column_transition_weight = random.uniform(-1,1)
      self.row_transition_weight = random.uniform(-1,1)
      self.hole_depth_weight = random.uniform(-1,1)
      self.cumulative_well_depth_weight = random.uniform(-1,1)
      self.row_hole_weight = random.uniform(-1,1)
      self.line_clear_weight = random.uniform(-1,1)
      self.attack_weight = random.uniform(-1,1)
      self.b2b_weight = random.uniform(-1,1)
    else:
      self.height_weight = weight_vector[0]
      self.hole_weight = weight_vector[1]
      self.column_transition_weight = weight_vector[2]
      self.row_transition_weight = weight_vector[3]
      self.hole_depth_weight = weight_vector[4]
      self.cumulative_well_depth_weight = weight_vector[5]
      self.row_hole_weight = weight_vector[6]
      self.line_clear_weight = weight_vector[7]
      self.attack_weight = weight_vector[8]
      self.b2b_weight = weight_vector[9]
    print(self.height_weight, self.hole_weight, self.column_transition_weight, self.row_transition_weight, self.hole_depth_weight, self.cumulative_well_depth_weight, self.row_hole_weight, self.line_clear_weight, self.attack_weight)
  
  def takeAction(self): # this needs to end in a piece placement
    # for event in pygame.event.get():
    #   if event.type == pygame.QUIT:
    #     pygame.quit()
    #     exit()  # Exit the game

    curr_tetrominos_placed = self.me.tetrominos_placed

    while(self.me.tetrominos_placed == curr_tetrominos_placed):
      legal_placements = self.generateLegalPlacements(self.me.active_piece, self.me.matrix, self.me.hold.can_hold)
      legal_placements = sorted(
        legal_placements, 
        key=lambda placement: self.evaluatePlacement(placement[0], placement[1], placement[2]),
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
    held_piece = []
    tuck_spin_considerations = []
    
    # consider holding if possible
    if can_hold:
      matrices.append(matrix)
      action_sequence.append(["H"])
      line_clears.append(0)
      held_piece.append(tetromino)
      
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
        landing_states_actions = copy.deepcopy(actions)
        landing_states.append([new_tetromino.x, new_tetromino.y, landing_states_actions])
        actions.append("HD")
        
        if not new_matrix in matrices:
          matrices.append(new_matrix)
          action_sequence.append(actions)
          line_clears.append(lines)
          held_piece.append(self.me.hold.held_piece)
      
      for i in range(1, len(landing_states)):
        if landing_states[i][1] - landing_states[i - 1][1] >= 1:
          # consider tucks for current state
          if [new_tetromino.current_rotation, landing_states[i][0], landing_states[i - 1][1] + 2] not in tuck_spin_considerations:
            rotation = new_tetromino.current_rotation
            x = landing_states[i][0]
            y = landing_states[i - 1][1]
            landing_action = landing_states[i][2]
            for i in range(0, y):
              landing_action.append("SD")
            tuck_spin_considerations.append([rotation, x, y, landing_action])
        elif landing_states[i][1] - landing_states[i - 1][1] <= -1:
          if [new_tetromino.current_rotation, landing_states[i - 1][0], landing_states[i][1] + 2] not in tuck_spin_considerations:
            rotation = new_tetromino.current_rotation
            x = landing_states[i - 1][0]
            y = landing_states[i][1]
            landing_action = landing_states[i - 1][2]
            for i in range(0, y):
              landing_action.append("SD")
            tuck_spin_considerations.append([rotation, x, y, landing_action])
    
    # tucks
    
    for c in tuck_spin_considerations:
      tetromino_copy = copy.deepcopy(tetromino)
      matrix_copy = copy.deepcopy(matrix)
      actions = copy.deepcopy(c[3])
      # print(actions, tetromino_copy.y)
      
      for action in actions:
        match action:
          case "L":
            tetromino_copy.x -= 1
          case "R":
            tetromino_copy.x += 1
          case "SD":
            tetromino_copy.y += 1
          case "LR":
            tetromino_copy.current_rotation = (tetromino_copy.current_rotation - 1) % 4
          case "RR":
            tetromino_copy.current_rotation = (tetromino_copy.current_rotation + 1) % 4   
      
      while not matrix_copy.checkCollision(tetromino_copy.x, tetromino_copy.y - 1, tetromino_copy.getShape()):
        tetromino_copy.y += 1
        actions.append("SD")
        
        # get full range of movement
        for x in self.getXRange(tetromino_copy, matrix_copy):
          if x == tetromino_copy.x:
            pass
          else:
            tucked_actions = copy.deepcopy(actions)
            tucked_tetromino = copy.deepcopy(tetromino_copy)
            tucked_matrix = copy.deepcopy(matrix_copy)
            
            while tucked_tetromino.x != x:
              if tucked_tetromino.x > x:
                tucked_tetromino.x -= 1
                tucked_actions.append("L")
              else:
                tucked_tetromino.x += 1
                tucked_actions.append("R")
            
            lines = self.simulateHardDrop(tucked_tetromino, tucked_matrix)
            tucked_actions.append("HD")
            
            if not tucked_matrix in matrices:
              matrices.append(tucked_matrix)
              action_sequence.append(tucked_actions)
              line_clears.append(lines)
              held_piece.append(self.me.hold.held_piece)
    
    post_spin_matrices = []
    post_spin_action_sequence = []
    post_spin_line_clears = []
    
    
    for actions in action_sequence:
      tetromino_copy = copy.deepcopy(tetromino)
      matrix_copy = copy.deepcopy(matrix)
      actions_copy = copy.deepcopy(actions)
      actions_copy.pop()
      
      for action in actions_copy:
        match action:
          case "L":
            tetromino_copy.x -= 1
          case "R":
            tetromino_copy.x += 1
          case "SD":
            tetromino_copy.y += 1
          case "LR":
            tetromino_copy.current_rotation = (tetromino_copy.current_rotation - 1) % 4
          case "RR":
            tetromino_copy.current_rotation = (tetromino_copy.current_rotation + 1) % 4   
      
      while not matrix_copy.checkCollision(tetromino_copy.x, tetromino_copy.y + 1, tetromino_copy.getShape()):
        tetromino_copy.y += 1
        actions_copy.append("SD")
        
      # print(actions_copy)
    
      new_tetromino_copy = copy.deepcopy(tetromino_copy)
      new_matrix_copy = copy.deepcopy(matrix_copy)
      new_actions_copy = copy.deepcopy(actions_copy)
    
      # simulate right rotates
      for i in range(4):
        # print(tetromino_copy.current_rotation, tetromino_copy.x, tetromino_copy.y)

        self.simulateRightRotate(new_tetromino_copy, new_matrix_copy)
        new_actions_copy.append("RR")
        
        spun_tetromino = copy.deepcopy(new_tetromino_copy)
        spun_matrix = copy.deepcopy(new_matrix_copy)
        spun_actions = copy.deepcopy(new_actions_copy)
        
        lines_cleared = self.simulateHardDrop(spun_tetromino, spun_matrix)
        spun_actions.append("HD")
        
        if not spun_matrix in post_spin_matrices and not spun_matrix in matrices:
          post_spin_matrices.append(spun_matrix)
          post_spin_action_sequence.append(spun_actions)
          post_spin_line_clears.append(lines_cleared)
          held_piece.append(self.me.hold.held_piece)
          # print(1)
        else:
          # print(spun_actions, 0)
          break
        
      new_tetromino_copy = copy.deepcopy(tetromino_copy)
      new_matrix_copy = copy.deepcopy(matrix_copy)
      new_actions_copy = copy.deepcopy(actions_copy)
        
      # simulate left rotates
      for i in range(4):
        # print(tetromino_copy.current_rotation, tetromino_copy.x, tetromino_copy.y)
        self.simulateLeftRotate(new_tetromino_copy, new_matrix_copy)
        new_actions_copy.append("LR")
        
        spun_tetromino = copy.deepcopy(new_tetromino_copy)
        spun_matrix = copy.deepcopy(new_matrix_copy)
        spun_actions = copy.deepcopy(new_actions_copy)
        
        lines_cleared = self.simulateHardDrop(spun_tetromino, spun_matrix)
        spun_actions.append("HD")
        
        if not spun_matrix in post_spin_matrices and not spun_matrix in matrices:
          post_spin_matrices.append(spun_matrix)
          post_spin_action_sequence.append(spun_actions)
          post_spin_line_clears.append(lines_cleared)
          held_piece.append(self.me.hold.held_piece)
        else:
          break
    
    matrices.extend(post_spin_matrices)
    action_sequence.extend(post_spin_action_sequence)
    line_clears.extend(post_spin_line_clears)
        
    return list(zip(matrices, action_sequence, line_clears, held_piece))
  
  def getXRange(self, tetromino: Tetromino, matrix: Matrix):
    ghost_tetromino = copy.deepcopy(tetromino)
    while not matrix.checkCollision(ghost_tetromino.x - 1, ghost_tetromino.y, ghost_tetromino.getShape()):
      ghost_tetromino.x -= 1
    min_x = ghost_tetromino.x
    while not matrix.checkCollision(ghost_tetromino.x + 1, ghost_tetromino.y, ghost_tetromino.getShape()):
      ghost_tetromino.x += 1
    max_x = ghost_tetromino.x + 1
    return range(min_x, max_x)
  
  def simulateLeftRotate(self, tetromino: Tetromino, matrix: Matrix):
    next_rotation = (tetromino.current_rotation - 1) % 4
    if not matrix.checkCollision(tetromino.x, tetromino.y, tetromino.getRotatedShape(next_rotation)):
      tetromino.current_rotation = next_rotation
      return  # No need to check for wall kicks
    
    if tetromino.name == "I":
      kicks = WALL_KICK_DATA["IL"][tetromino.current_rotation]
    else:
      kicks = WALL_KICK_DATA["L"][tetromino.current_rotation]
    for dx, dy in kicks:
      new_x = tetromino.x + dx
      new_y = tetromino.y - dy
      if not matrix.checkCollision(new_x, new_y, tetromino.getRotatedShape(next_rotation)):
        tetromino.x = new_x
        tetromino.y = new_y
        tetromino.current_rotation = next_rotation
        break  # Exit after a successful wall kick
  
  def simulateRightRotate(self, tetromino: Tetromino, matrix: Matrix):
    next_rotation = (tetromino.current_rotation + 1) % 4
    if not matrix.checkCollision(tetromino.x, tetromino.y, tetromino.getRotatedShape(next_rotation)):
      tetromino.current_rotation = next_rotation
      return  # No need to check for wall kicks
    if tetromino.name == "I":
      kicks = WALL_KICK_DATA["IR"][tetromino.current_rotation]
    else:
      kicks = WALL_KICK_DATA["R"][tetromino.current_rotation]
    for dx, dy in kicks:
      new_x = tetromino.x + dx
      new_y = tetromino.y - dy
      if not matrix.checkCollision(new_x, new_y, tetromino.getRotatedShape(next_rotation)):
        tetromino.x = new_x
        tetromino.y = new_y
        tetromino.current_rotation = next_rotation
        break  # Exit after a successful wall kick

  def simulateHardDrop(self, tetromino: Tetromino, matrix: Matrix):
    # print(tetromino.current_rotation, tetromino.x, tetromino.y)
    while not matrix.checkCollision(tetromino.x, tetromino.y + 1, tetromino.getShape()):
      tetromino.y += 1
    matrix.lockTetromino(tetromino)
    line_clears =  matrix.calculateLineClears()
    matrix.clearLines()
    return line_clears
  
  def evaluatePlacement(self, matrix: Matrix, action_sequence, cleared_lines):
    # evaluation function
    height = self.getHeight(matrix)
    holes = self.getHoles(matrix)
    column_transition = self.getColumnTransition(matrix)
    row_transition = self.getRowTransition(matrix)
    hole_depth = self.getHoleDepth(matrix)
    cumulative_well_depth = self.getCumulativeWellDepth(matrix)
    row_hole = self.getRowHoles(matrix)
    attack = self.getAttack(action_sequence, cleared_lines)
    b2b = self.getB2b(action_sequence, cleared_lines)
    
    # evaluation = self.hole_weight * holes + self.height_weight * height + self.line_clear_weight * cleared_lines + self.column_transition_weight * self.getColumnTransition(matrix)
    evaluation = float(self.height_weight * height + 
                  self.hole_weight * holes +
                  self.column_transition_weight * column_transition +
                  self.row_transition_weight * row_transition +
                  self.hole_depth_weight * hole_depth +
                  self.cumulative_well_depth_weight * cumulative_well_depth +
                  self.row_hole_weight * row_hole +
                  self.line_clear_weight * cleared_lines +
                  self.attack_weight * attack +
                  self.b2b_weight * b2b
      )
    # evaluation = - 20 * holes - height
    return evaluation
            
  def getHeight(self, matrix):
    for i in range(MATRIX_HEIGHT):
      if any(matrix.grid[i]):
        return 22 - i
    return 0
  
  def getHoles(self, matrix: Matrix):
    holes = 0
    for x in range(MATRIX_WIDTH):
      filled_encountered = False
      for y in range(MATRIX_HEIGHT):
        if matrix.grid[y][x]:
          filled_encountered = True
        elif filled_encountered and matrix.grid[y][x] == 0:
          holes += 1
          
    return holes

  def getColumnTransition(self, matrix):
    column_transition = 0
    matrix_copy = copy.deepcopy(matrix)

    for x in range(MATRIX_WIDTH):
      for y in range(MATRIX_HEIGHT):
        if matrix_copy.grid[y][x]:
          matrix_copy.grid[y][x] = 1
    
    for column in range(MATRIX_WIDTH):
      for row in range(MATRIX_HEIGHT - 1):
        if matrix_copy.grid[row][column] != matrix_copy.grid[row + 1][column]:
          column_transition += 1
          
    return column_transition
  
  def getRowTransition(self, matrix):
    row_transition = 0
    matrix_copy = copy.deepcopy(matrix)
    
    for x in range(MATRIX_WIDTH):
      for y in range(MATRIX_HEIGHT):
        if matrix_copy.grid[y][x]:
          matrix_copy.grid[y][x] = 1
    
    for column in range(MATRIX_WIDTH - 1):
      for row in range(MATRIX_HEIGHT):
        if matrix_copy.grid[row][column] != matrix_copy.grid[row][column + 1]:
          row_transition += 1
          
    return row_transition
  
  def getHoleDepth(self, matrix):
    hole_depth = 0
    
    for x in range(MATRIX_WIDTH):
      depth = 0
      for y in range(MATRIX_HEIGHT):
        if matrix.grid[y][x]:
          depth += 1
        elif matrix.grid[y][x] == 0 and depth > 0:
          hole_depth += depth
      
    return hole_depth
  
  def getRowHoles(self, matrix):
    row_holes = 0
    
    for y in range(MATRIX_HEIGHT):
      has_filled_cell = any(matrix.grid[y][x] for x in range(MATRIX_WIDTH))
      if has_filled_cell:
        row_holes += sum(1 for x in range(MATRIX_WIDTH) if matrix.grid[y][x] == 0)
    
    return row_holes
  
  def getCumulativeWellDepth(self, matrix):
    well_depth = 0
    
    for x in range(MATRIX_WIDTH):
      for y in range(MATRIX_HEIGHT):
        if matrix.grid[y][x] == 0:
          # check if is well - if left and right sides are both filled, it is considered a well.
          left_filled = (x == 0 or matrix.grid[y][x - 1])
          right_filled = (x == MATRIX_WIDTH - 1 or matrix.grid[y][x + 1])
          if left_filled and right_filled:
            depth = 1
            for k in range(y + 1, MATRIX_HEIGHT):
              if matrix.grid[k][x]== 0:
                depth += 1
              else:
                break
            well_depth += 1
    
    return well_depth
  
  def getAttack(self, action_sequence, cleared_lines):
    action_copy = copy.deepcopy(action_sequence)
    action_copy.pop()
    if len(action_copy) != 0 and (action_copy[-1] == "LR" or action_copy[-1] == "RR"):
      most_recent_move = "rotate"
    else:
      most_recent_move = "move"
    attack = self.me.calculateAttack(cleared_lines, most_recent_move, True)
    return attack
  
  def getB2b(self, action_sequence, cleared_lines):
    b2b = self.me.b2b
    action_copy = copy.deepcopy(action_sequence)
    action_copy.pop()
    if len(action_copy) != 0 and (action_copy[-1] == "LR" or action_copy[-1] == "RR"):
      most_recent_move = "rotate"
    else:
      most_recent_move = "move"
    
    if cleared_lines > 0:
      if self.me.isTspin(most_recent_move) or cleared_lines == 4:
        b2b += 1
      else:
        b2b = -1
    
    return b2b
  
if __name__ == "__main__":
  gc = GameController(SevenBag(1), GarbageSystem(1))
  bot = Bot(gc)
  for x in range(10):
    gc.matrix.grid[21][x] = 1 if x < 4 or x >= 6 else 0
    gc.matrix.grid[20][x] = 1 if x < 5 or x >= 7 else 0

  # bot.takeAction()
  placements = bot.generateLegalPlacements(Tetromino("S", 5, 0), gc.matrix, True)
  # print(bot.evaluatePlacement(placements[9][0], placements[9][2]))
  # print(bot.getHoles(placements[9][0]))
  # for placement in placements:
    # print(bot.evaluatePlacement(placement[0], placement[2]))
  # for i in range(10):
  #   bot.takeAction()
  # col_trans_matrix = bot.getColumnTransition(gc.matrix)
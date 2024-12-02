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
  def __init__(self, me: GameController):
    random.seed()
    self.me = me
      
    # self.hole_weight = -0.6483074206751366
    # self.height_weight = -0.9550269397680944
    # self.line_clear_weight = 0.7139929472467322
    self.hole_weight = random.uniform(-1,0)
    self.height_weight = random.uniform(-1,0)
    self.line_clear_weight = random.uniform(0,1)
    self.column_transition_weight = random.uniform(-1,0)
    self.attack_weight = random.uniform(0,1)
    print(self.hole_weight, self.height_weight, self.line_clear_weight, self.attack_weight)
  
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
    tuck_spin_considerations = []
    
    # consider holding if possible
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
        landing_states_actions = copy.deepcopy(actions)
        landing_states.append([new_tetromino.x, new_tetromino.y, landing_states_actions])
        actions.append("HD")
        
        if not new_matrix in matrices:
          matrices.append(new_matrix)
          action_sequence.append(actions)
          line_clears.append(lines)
      
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
            
      
      while not matrix_copy.checkCollision(tetromino_copy.x, tetromino_copy.y + 1, tetromino_copy.getShape()):
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
        else:
          break
    
    matrices.extend(post_spin_matrices)
    action_sequence.extend(post_spin_action_sequence)
    line_clears.extend(post_spin_line_clears)
        
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
    holes = self.getHoles(matrix)
    height = self.getHeight(matrix)
    attack = self.getAttack(action_sequence, cleared_lines)
    # evaluation = self.hole_weight * holes + self.height_weight * height + self.line_clear_weight * cleared_lines + self.column_transition_weight * self.getColumnTransition(matrix)
    evaluation = self.hole_weight * holes + self.height_weight * height + self.attack_weight * attack
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

  def getColumnTransition(self, matrix):
    column_transition = 0
    prev_height = 0

    for i in range(MATRIX_HEIGHT):
      if matrix.grid[i][0] != 0:
        prev_height = 22 - i
        break

    for x in range(1, MATRIX_WIDTH):
      for y in range(MATRIX_HEIGHT):
        if y == 21 and not matrix.grid[y][x]:
          column_transition += prev_height
          prev_height = 0

        if matrix.grid[y][x]:
          column_transition += abs(prev_height - (22 - y))
          prev_height = 22 - y
          break
        
    
    return column_transition
  
  def getAttack(self, action_sequence, cleared_lines):
    action_copy = copy.deepcopy(action_sequence)
    action_copy.pop()
    if len(action_copy) != 0 and (action_copy[-1] == "LR" or action_copy[-1] == "RR"):
      most_recent_move = "rotate"
    else:
      most_recent_move = "move"
    attack = self.me.calculateAttack(cleared_lines, most_recent_move)
    return attack
  
if __name__ == "__main__":
  gc = GameController("bot", SevenBag(1), GarbageSystem(1))
  bot = Bot(gc)
  for x in range(10):
    gc.matrix.grid[21][x] = 1 if x != 2 else 0
    gc.matrix.grid[20][x] = 1 if x < 1 or x > 3 else 0
    gc.matrix.grid[19][x] = 1 if x < 2 else 0
  # bot.takeAction()
  placements = bot.generateLegalPlacements(Tetromino("T", 4, 0), gc.matrix, True)
  # print(bot.evaluatePlacement(placements[9][0], placements[9][2]))
  # print(bot.getHoles(placements[9][0]))
  # for placement in placements:
    # print(bot.evaluatePlacement(placement[0], placement[2]))
  for i in range(100):
    bot.takeAction()
from constants import TETROMINOS

class Tetromino:
  def __init__(self, name, x = None, y = None) -> None:
    self.name = name
    self.rotations = TETROMINOS[name][0]
    self.current_rotation = 0
    self.color = TETROMINOS[name][1]
    self.x = x
    self.y = y

  def getShape(self):
    shape = []
    for row in self.rotations[self.current_rotation]:
      shape.append((bin(row)[2:].zfill(4)))
    return shape
  
  def getRotatedShape(self, rotation):
    shape = []
    for row in self.rotations[rotation]:
      shape.append((bin(row)[2:].zfill(4)))
    return shape
  
if __name__ == "__main__":
  shape = Tetromino("T").getShape()
  for row in shape:
    print(row)
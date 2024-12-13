import random

class GarbageSystem:
  def __init__(self, seed):
    self.seed = seed
    random.seed(self.seed)
    self.hole_sequence = []

  def generateNewHole(self):
    hole = random.randint(0, 9)
    self.hole_sequence.append(hole)

  def getGarbageAt(self, index):
    while index >= len(self.hole_sequence):
      self.generateNewHole()
    return self.hole_sequence[index]

if __name__ == "__main__":
  gs = GarbageSystem(0)
  for i in range(0, 100):
    print(gs.getGarbageAt(i))
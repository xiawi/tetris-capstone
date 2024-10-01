import random
from constants import TETROMINOS

class SevenBag:
  def __init__(self, seed = None):
    if seed:
      self.seed = seed
    else:
      self.seed = random.random()
    
    random.seed(self.seed)

  def generateBag(self):
    print(self.seed)
    bag = [*TETROMINOS]
    random.shuffle(bag)
    self.seed = (self.seed * 48271 + 1) % (2**31 - 1) # Using a linear congruential generator approach
    random.seed(self.seed)
    return bag
    # return ['I','I','I','I','I','I']
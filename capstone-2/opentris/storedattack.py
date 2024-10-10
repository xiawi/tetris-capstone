import random

class StoredAttack:
  def __init__(self, seed) -> None:
    self.garbage_queue = []
    random.seed(seed)
  
  def addGarbageToQueue(self, lines):
    
    pass

  def popGarbage(self):
    self.garbage_queue.pop(0)
    pass

if __name__ == "__main__":
  pass
  
from garbagesystem import GarbageSystem

class StoredAttack:
  def __init__(self, garbage_system:GarbageSystem) -> None:
    self.index = 0
    self.garbage_system = garbage_system
    self.attack = []
    self.hole = []

  def storeAttack(self, lines):
    self.attack.append(lines)
    self.hole.append(self.garbage_system.getGarbageAt(self.index))
    self.index += 1

  def receiveAttack(self):
    if self.hasStoredAttack():
      attack = self.attack.pop(0)
      hole = self.hole.pop(0)
      return attack, hole
    else:
      return 0, 0
  
  def performAttack(self, lines):
    while self.hasStoredAttack():
      if lines >= self.attack[0]:
        lines = lines - self.attack[0]
        self.attack.pop(0)
        self.hole.pop(0)
      else:
        self.attack[0] = self.attack[0] - lines
        break
    return lines
  
  def hasStoredAttack(self):
    return len(self.attack) > 0

if __name__ == "__main__":
  sa = StoredAttack(GarbageSystem(1))
  sa.storeAttack(4)
  sa.storeAttack(5)
  print(sa.attack, sa.hole)
  print(sa.performAttack(3))
  print(sa.attack, sa.hole)
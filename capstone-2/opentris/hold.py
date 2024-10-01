from tetromino import Tetromino

class Hold:
  def __init__(self):
    self.held_piece = None
    self.can_hold = True

  def holdPiece(self, tetromino: Tetromino) -> Tetromino:
    if self.can_hold:
      return_tet = self.held_piece
      self.held_piece = tetromino
      self.can_hold = False
      return return_tet
    else:
      return None

  def resetStatus(self) -> None:
    self.can_hold = True

  def getHeldPiece(self) -> Tetromino:
    return self.held_piece
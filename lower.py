from typing import Tuple
from syntax import *

class IR_Transformer():
  stmts: list[Stmt]

  def lower(self, x: Exp) -> Exp:
      match x: 
          case Variable() | Num():
              return x
# cython: language_level=3
from .basic import *

_ORIGIN:tuple[int] = (0, 0)

class PositionSystem:
    # 原点
    @property
    def ORIGIN(self) -> tuple[int]: return _ORIGIN
    #转换坐标
    @staticmethod
    def convert(pos:any) -> tuple:
        #检测坐标
        if isinstance(pos, (list, tuple, numpy.ndarray)):
            return pos[0], pos[1]
        elif isinstance(pos, dict):
            return pos["x"], pos["y"]
        else:
            try:
                return pos.x, pos.y
            except Exception:
                EXCEPTION.fatal('Cannot convert position "{}".'.format(pos))
    #判断2个坐标是否相同
    def is_same(self, pos1:any, pos2:any) -> bool: return self.convert(pos1) == self.convert(pos2)
    #相加2个坐标
    def add(self, *positions:any) -> tuple[number]:
        x = 0
        y = 0
        for pos in positions:
            convetred_pos = self.convert(pos)
            x += convetred_pos[0]
            y += convetred_pos[1]
        return x,y
    #int化坐标
    @staticmethod
    def int(pos:tuple[number]) -> tuple[int]: return int(pos[0]), int(pos[1])
    #相减2个坐标
    def subtract(self, position:any, *positions:any) -> tuple[number]:
        x,y = self.convert(position)
        convetred_pos: tuple[number] 
        for pos in positions:
            convetred_pos = self.convert(pos)
            x -= convetred_pos[0]
            y -= convetred_pos[1]
        return x,y

Pos: PositionSystem = PositionSystem()

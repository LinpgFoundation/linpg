from .basic import *

_ORIGIN: tuple[int] = (0, 0)


class CoordinateSystem:
    # 原点
    @property
    def ORIGIN(self) -> tuple[int]:
        return _ORIGIN

    # 转换坐标
    @staticmethod
    def convert(pos: any) -> tuple:
        # 检测坐标
        if isinstance(pos, Iterable):
            if isinstance(pos, dict):
                return pos["x"], pos["y"]
            else:
                return pos[0], pos[1]
        else:
            try:
                return pos.x, pos.y
            except Exception:
                EXCEPTION.fatal('Unable to convert position "{}".'.format(pos))

    # 判断2个坐标是否相同
    def is_same(self, pos1: any, pos2: any) -> bool:
        return self.convert(pos1) == self.convert(pos2)

    # 相加2个坐标
    @staticmethod
    def add(*positions: tuple[number]) -> tuple:
        x = 0
        y = 0
        for pos in positions:
            x += pos[0]
            y += pos[1]
        return x, y

    # 相减2个坐标
    @staticmethod
    def subtract(position: tuple[number], *positions: tuple[number]) -> tuple:
        x = position[0]
        y = position[1]
        for pos in positions:
            x -= pos[0]
            y -= pos[1]
        return x, y

    # int化坐标
    def int(self, pos: any) -> tuple[int]:
        coverted_pos: tuple[number] = self.convert(pos)
        return int(coverted_pos[0]), int(coverted_pos[1])


Pos: CoordinateSystem = CoordinateSystem()

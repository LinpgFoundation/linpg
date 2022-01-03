from .header import *

ORIGIN: tuple[int, int] = (0, 0)

# 浮点坐标
class Positions:

    # 转换坐标
    @staticmethod
    def convert(pos: Any) -> tuple:
        # 检测坐标
        if isinstance(pos, dict):
            return pos["x"], pos["y"]
        elif isinstance(pos, (list, tuple, numpy.ndarray)):
            return pos[0], pos[1]
        else:
            try:
                return pos.x, pos.y
            except Exception:
                EXCEPTION.fatal('Unable to convert position "{}".'.format(pos))

    # 判断2个坐标是否相同
    @staticmethod
    def is_same(pos1: object, pos2: object) -> bool:
        return Positions.convert(pos1) == Positions.convert(pos2)

    # 相加2个坐标
    @staticmethod
    def add(*positions: tuple) -> tuple:
        x = 0
        y = 0
        for pos in positions:
            x += pos[0]
            y += pos[1]
        return x, y

    # 相减2个坐标
    @staticmethod
    def subtract(position: tuple, *positions: tuple) -> tuple:
        x = position[0]
        y = position[1]
        for pos in positions:
            x -= pos[0]
            y -= pos[1]
        return x, y


# 整数坐标
class Coordinates:

    # 转换坐标
    @staticmethod
    def convert(pos: Any) -> tuple[int, int]:
        # 检测坐标
        if isinstance(pos, dict):
            return int(pos["x"]), int(pos["y"])
        elif isinstance(pos, (tuple, list, numpy.ndarray)):
            return int(pos[0]), int(pos[1])
        else:
            try:
                return int(pos.x), int(pos.y)
            except Exception:
                EXCEPTION.fatal('Unable to convert position "{}".'.format(pos))

    # 判断2个坐标是否相同
    @staticmethod
    def is_same(pos1: object, pos2: object) -> bool:
        return Coordinates.convert(pos1) == Coordinates.convert(pos2)

    # 相加2个坐标
    @staticmethod
    def add(*positions: tuple) -> tuple[int, int]:
        x = 0
        y = 0
        for pos in positions:
            x += pos[0]
            y += pos[1]
        return int(x), int(y)

    # 相减2个坐标
    @staticmethod
    def subtract(position: tuple, *positions: tuple) -> tuple[int, int]:
        x = position[0]
        y = position[1]
        for pos in positions:
            x -= pos[0]
            y -= pos[1]
        return int(x), int(y)

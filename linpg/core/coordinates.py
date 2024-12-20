from ..media import *

# 原点
ORIGIN: Final[tuple[int, int]] = (0, 0)


# 浮点坐标
class Positions:
    # 转换坐标
    @staticmethod
    def convert(pos: Any) -> tuple[number, number]:
        # 检测坐标
        if isinstance(pos, dict):
            return pos["x"], pos["y"]
        elif isinstance(pos, (Sequence, numpy.ndarray)):
            return pos[0], pos[1]
        else:
            try:
                return pos.x, pos.y
            except Exception:
                Exceptions.fatal(f'Unable to convert position "{pos}".')

    # 判断2个坐标是否相同
    @staticmethod
    def is_same(pos1: object, pos2: object) -> bool:
        return Positions.convert(pos1) == Positions.convert(pos2)

    # 相加2个坐标
    @staticmethod
    def add(*positions: tuple[number, number]) -> tuple[number, number]:
        x: number = 0
        y: number = 0
        for pos in positions:
            x += pos[0]
            y += pos[1]
        return x, y

    # 相减2个坐标
    @staticmethod
    def subtract(position: tuple[number, number], *positions: tuple[number, number]) -> tuple[number, number]:
        x: number = position[0]
        y: number = position[1]
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
        elif isinstance(pos, (Sequence, numpy.ndarray)):
            return int(pos[0]), int(pos[1])
        else:
            try:
                return int(pos.x), int(pos.y)
            except Exception:
                Exceptions.fatal(f'Unable to convert position "{pos}".')

    # 判断2个坐标是否相同
    @staticmethod
    def is_same(pos1: object, pos2: object) -> bool:
        return Coordinates.convert(pos1) == Coordinates.convert(pos2)

    # 相加2个坐标
    @staticmethod
    def add(*positions: tuple[number, number]) -> tuple[int, int]:
        x: number = 0
        y: number = 0
        for pos in positions:
            x += pos[0]
            y += pos[1]
        return int(x), int(y)

    # 相减2个坐标
    @staticmethod
    def subtract(position: tuple[number, number], *positions: tuple[number, number]) -> tuple[int, int]:
        x: number = position[0]
        y: number = position[1]
        for pos in positions:
            x -= pos[0]
            y -= pos[1]
        return int(x), int(y)

    @staticmethod
    def get_in_diamond_shaped(_x: int, _y: int, _radius: int) -> list[tuple[int, int]]:
        if _radius == 1:
            return [(_x, _y)]
        elif _radius > 1:
            return [
                (x, y)
                for y in range(_y - _radius + 1, _y + _radius)
                for x in range(_x - _radius + abs(y - _y) + 1, _x + _radius - abs(y - _y))
            ]
        return []

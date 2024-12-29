import enum


# 表示方向的enum
@enum.verify(enum.UNIQUE)
class Directions(enum.IntEnum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


# 表示Axis轴
@enum.verify(enum.UNIQUE)
class Axis(enum.IntEnum):
    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()


# 表示位置
@enum.verify(enum.UNIQUE)
class Locations(enum.IntEnum):
    BEGINNING = enum.auto()
    END = enum.auto()
    MIDDLE = enum.auto()
    EVERYWHERE = enum.auto()

class AbstractMap:
    def __init__(self) -> None:
        # 行
        self.__row: int = 0
        # 列
        self.__column: int = 0

    def _update(self, row: int, column: int) -> None:
        self.__row = row
        self.__column = column

    @property
    def row(self) -> int:
        return self.__row

    @property
    def column(self) -> int:
        return self.__column

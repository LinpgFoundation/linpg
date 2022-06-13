from .decoration import *

# 点
class Point(Coordinate):
    def __eq__(self, other: "Point") -> bool:  # type: ignore[override]
        return self.x == other.x and self.y == other.y


# 描述AStar算法中的节点数据
class Node:
    def __init__(self, point: Point, endPoint: Point, g: number = 0):
        self.point: Point = point  # 自己的坐标
        self.father: Optional[Node] = None  # 父节点
        self.g = g  # g值，g值在用到的时候会重新算
        self.h = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值


# 基础地图框架
class AbstractMap:

    # 获取方块数据库
    __BLOCKS_DATABASE: dict = DataBase.get("Blocks")

    def __init__(self) -> None:
        # 地图数据
        self.__MAP: numpy.ndarray = numpy.asarray([])
        # 行
        self.__row: int = 0
        # 列
        self.__column: int = 0

    # 更新地图数据
    def _update(self, _data: list) -> None:
        self.__MAP = numpy.asarray(_data, dtype=numpy.dtype("<U32"))
        self.__row, self.__column = self.__MAP.shape

    @property
    def row(self) -> int:
        return self.__row

    @property
    def column(self) -> int:
        return self.__column

    # 计算精准位置
    def calculate_position(self, x: int_f, y: int_f) -> tuple[int, int]:
        widthTmp: float = MapImageParameters.get_block_width() * 0.43
        return (
            round((x - y) * widthTmp + self.row * widthTmp),
            round((y + x) * MapImageParameters.get_block_width() * 0.22 + MapImageParameters.get_block_width() * 0.4),
        )

    # 根据坐标获取地图块
    def _get_block(self, x: int, y: int) -> str:
        return str(self.__MAP[y][x])

    # 根据坐标更新地图块
    def _set_block(self, x: int, y: int, name: str) -> None:
        self.__MAP[y][x] = name

    # 以字典的形式获取地图的数据
    def to_dict(self) -> dict:
        # 转换地图数据
        MAP_t: tuple = tuple(self.__MAP.tolist())
        lookup_table: dict = {}
        for row in MAP_t:
            for item in row:
                if item not in lookup_table:
                    lookup_table[item] = 0
                else:
                    lookup_table[item] += 1
        sorted_lookup_table: list = sorted(lookup_table, key=lookup_table.get, reverse=True)  # type: ignore
        # 返回数据
        return {
            "map": {
                "array2d": [[sorted_lookup_table.index(item) for item in row] for row in MAP_t],
                "lookup_table": sorted_lookup_table,
            }
        }

    # 是否角色能通过该方块
    def if_block_can_pass_through(self, x: int, y: int) -> bool:
        return bool(self.__BLOCKS_DATABASE[self.__MAP[y][x]]["canPassThrough"])


# 寻路模块
class AStar(AbstractMap):

    # 可行走标记
    __pass_tag: int = 0

    def __init__(self) -> None:
        # 寻路用的ndarray地图
        self._map2d: numpy.ndarray = numpy.asarray([])
        # 终点
        self.__end_point: Point = Point(0, 0)
        # 开启表
        self.__open_list: list[Node] = []
        # 关闭表
        self.__close_list: list[Node] = []

    def _update(self, _data: list) -> None:
        super()._update(_data)
        self._map2d = numpy.zeros((self.row, self.column), dtype=numpy.byte)

    def __getMinNode(self) -> Node:
        """
        获得OpenList中F值最小的节点
        :return: Node
        """
        currentNode = self.__open_list[0]
        for node in self.__open_list:
            if node.g + node.h < currentNode.g + currentNode.h:
                currentNode = node
        return currentNode

    def __pointInCloseList(self, point: Point) -> bool:
        for node in self.__close_list:
            if node.point == point:
                return True
        return False

    def __pointInOpenList(self, point: Point) -> Optional[Node]:
        for node in self.__open_list:
            if node.point == point:
                return node
        return None

    def __end_pointInCloseList(self) -> Optional[Node]:
        for node in self.__open_list:
            if node.point == self.__end_point:
                return node
        return None

    def __searchNear(self, minF: Node, offSetX: int, offSetY: int) -> None:
        """
        搜索节点周围的点
        :param minF:F值最小的节点
        :param offSetX:坐标偏移量
        :param offSetY:
        :return:
        """
        # 越界检测
        if (
            minF.point.x + offSetX < 0
            or minF.point.x + offSetX > self.column - 1
            or minF.point.y + offSetY < 0
            or minF.point.y + offSetY > self.row - 1
        ):
            return
        # 如果是障碍，就忽略
        if self._map2d[minF.point.x + offSetX][minF.point.y + offSetY] != self.__pass_tag:
            return
        # 如果在关闭表中，就忽略
        currentPoint = Point(minF.point.x + offSetX, minF.point.y + offSetY)
        if self.__pointInCloseList(currentPoint):
            return
        # 设置单位花费
        if offSetX == 0 or offSetY == 0:
            step = 10
        else:
            step = 14
        # 如果不再openList中，就把它加入OpenList
        currentNode: Optional[Node] = self.__pointInOpenList(currentPoint)
        if currentNode is None:
            currentNode = Node(currentPoint, self.__end_point, g=minF.g + step)
            currentNode.father = minF
            self.__open_list.append(currentNode)
        # 如果在openList中，判断minF到当前点的G是否更小
        elif minF.g + step < currentNode.g:  # 如果更小，就重新计算g值，并且改变father
            currentNode.g = minF.g + step
            currentNode.father = minF

    def _startPathFinding(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list:
        """
        开始寻路
        :return: None或Point列表（路径）
        """
        # 初始化路径寻找使用的缓存列表
        self.__open_list.clear()
        self.__close_list.clear()
        # 判断寻路终点是否是障碍
        self.__end_point = Point(end_pos[0], end_pos[1])
        if (
            self.__end_point.y < 0
            or self.__end_point.y >= self.row
            or self.__end_point.x < 0
            or self.__end_point.x >= self.column
            or self._map2d[self.__end_point.x][self.__end_point.y] != self.__pass_tag  # 如果终点是障碍物
        ):
            return []
        # 1.将起点放入开启列表
        startNode = Node(Point(start_pos[0], start_pos[1]), self.__end_point)
        self.__open_list.append(startNode)
        # 2.主循环逻辑
        while True:
            # 找到F值最小的点
            minF = self.__getMinNode()
            # 把这个点加入closeList中，并且在openList中删除它
            self.__close_list.append(minF)
            self.__open_list.remove(minF)
            # 判断这个节点的上下左右节点
            self.__searchNear(minF, 0, -1)
            self.__searchNear(minF, 0, 1)
            self.__searchNear(minF, -1, 0)
            self.__searchNear(minF, 1, 0)
            # 判断是否终止
            point = self.__end_pointInCloseList()
            if point is not None:  # 如果终点在关闭表中，就返回结果
                cPoint = point
                pathList: list = []
                while True:
                    if cPoint.father:
                        pathList.append(cPoint.point)
                        cPoint = cPoint.father
                    else:
                        self.__open_list.clear()
                        self.__close_list.clear()
                        return list(reversed(pathList))
            if len(self.__open_list) == 0:
                self.__open_list.clear()
                self.__close_list.clear()
                return []

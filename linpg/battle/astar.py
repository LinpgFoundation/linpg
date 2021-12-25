from .weather import *

# 点
class Point(GameObject):
    def __eq__(self, other: "Point") -> bool:  # type: ignore[override]
        return self.x == other.x and self.y == other.y


# 描述AStar算法中的节点数据
class Node:
    def __init__(self, point: Point, endPoint: Point, g: number = 0):
        self.point = point  # 自己的坐标
        self.father = None  # 父节点
        self.g = g  # g值，g值在用到的时候会重新算
        self.h = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值


NULL_NODE: Node = Node(Point(-1, -1), Point(-1, -1))

# 寻路模块
class AStar:

    # 可行走标记
    __pass_tag: int = 0

    def __init__(self, row: int, column: int) -> None:
        # 寻路用的ndarray地图
        self._map2d: numpy.ndarray = numpy.zeros((column, row), dtype=int)
        # 行
        self.__row = row
        # 列
        self.__column = column
        # 终点
        self.__end_point: Point = Point(0, 0)
        # 开启表
        self.__open_list: list = []
        # 关闭表
        self.__close_list: list = []

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

    def __pointInOpenList(self, point: Point) -> Node:
        for node in self.__open_list:
            if node.point == point:
                return node
        return NULL_NODE

    def __end_pointInCloseList(self) -> Node:
        for node in self.__open_list:
            if node.point == self.__end_point:
                return node
        return NULL_NODE

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
            or minF.point.x + offSetX > self.__column - 1
            or minF.point.y + offSetY < 0
            or minF.point.y + offSetY > self.__row - 1
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
        currentNode: Node = self.__pointInOpenList(currentPoint)
        if currentNode is NULL_NODE:
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
            or self.__end_point.y >= self.__row
            or self.__end_point.x < 0
            or self.__end_point.x >= self.__column
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
            if point is not NULL_NODE:  # 如果终点在关闭表中，就返回结果
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

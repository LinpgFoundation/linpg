from .entity import *


# 点
class _AStarPoint(Coordinate):
    def __eq__(self, other: "_AStarPoint") -> bool:  # type: ignore[override]
        return self.x == other.x and self.y == other.y


# 描述AStar算法中的节点数据
class _AStarNode:
    def __init__(self, point: _AStarPoint, endPoint: _AStarPoint, g: number = 0):
        self.point: _AStarPoint = point  # 自己的坐标
        self.father: _AStarNode | None = None  # 父节点
        self.g: number = g  # g值，g值在用到的时候会重新算
        self.h: int = (abs(endPoint.x - point.x) + abs(endPoint.y - point.y)) * 10  # 计算h值


# 寻路模块
class AStar:
    # 寻路用的ndarray地图
    __map2d: numpy.ndarray = numpy.asarray([])
    # 行
    __row: int = 0
    # 列
    __column: int = 0
    # 终点
    __end_point: _AStarPoint = _AStarPoint(0, 0)
    # 开启表
    __open_list: list[_AStarNode] = []
    # 关闭表
    __close_list: list[_AStarNode] = []

    @classmethod
    def __update(cls, new_map2d: numpy.ndarray) -> None:
        cls.__open_list.clear()
        cls.__close_list.clear()
        cls.__map2d = new_map2d
        cls.__column, cls.__row = new_map2d.shape

    @classmethod
    def __is_out_of_bound(cls, _point: _AStarPoint) -> bool:
        return _point.y < 0 or _point.y >= cls.__row or _point.x < 0 or _point.x >= cls.__column

    # 获得OpenList中F值最小的节点
    @classmethod
    def __getMinNode(cls) -> _AStarNode:
        currentNode = cls.__open_list[0]
        for node in cls.__open_list:
            if node.g + node.h < currentNode.g + currentNode.h:
                currentNode = node
        return currentNode

    @classmethod
    def __pointInCloseList(cls, point: _AStarPoint) -> bool:
        for node in cls.__close_list:
            if node.point == point:
                return True
        return False

    @classmethod
    def __pointInOpenList(cls, point: _AStarPoint) -> _AStarNode | None:
        for node in cls.__open_list:
            if node.point == point:
                return node
        return None

    @classmethod
    def __end_pointInCloseList(cls) -> _AStarNode | None:
        for node in cls.__open_list:
            if node.point == cls.__end_point:
                return node
        return None

    # 搜索节点周围的点
    @classmethod
    def __searchNear(cls, minF: _AStarNode, offSetX: int, offSetY: int) -> None:
        minFNearByPoint: _AStarPoint = _AStarPoint(minF.point.x + offSetX, minF.point.y + offSetY)
        # 越界检测 / 如果是障碍，就忽略
        if cls.__is_out_of_bound(minFNearByPoint) or cls.__map2d[minFNearByPoint.x, minFNearByPoint.y] == 0:
            return
        # 如果在关闭表中，就忽略
        currentPoint = _AStarPoint(minFNearByPoint.x, minFNearByPoint.y)
        if cls.__pointInCloseList(currentPoint):
            return
        # 设置单位花费
        if offSetX == 0 or offSetY == 0:
            step = 10
        else:
            step = 14
        # 如果不再openList中，就把它加入OpenList
        currentNode: _AStarNode | None = cls.__pointInOpenList(currentPoint)
        if currentNode is None:
            currentNode = _AStarNode(currentPoint, cls.__end_point, minF.g + step)
            currentNode.father = minF
            cls.__open_list.append(currentNode)
        # 如果在openList中，判断minF到当前点的G是否更小
        elif minF.g + step < currentNode.g:  # 如果更小，就重新计算g值，并且改变father
            currentNode.g = minF.g + step
            currentNode.father = minF

    # 开始寻路
    @classmethod
    def search(cls, map2d: numpy.ndarray, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list[tuple[int, int]]:
        cls.__update(map2d)
        # 判断寻路终点是否是障碍
        cls.__end_point = _AStarPoint(end_pos[0], end_pos[1])
        if cls.__is_out_of_bound(cls.__end_point) or cls.__map2d[cls.__end_point.x, cls.__end_point.y] == 0:  # 如果终点是障碍物
            return []
        # 1.将起点放入开启列表
        startNode: _AStarNode = _AStarNode(_AStarPoint(start_pos[0], start_pos[1]), cls.__end_point)
        cls.__open_list.append(startNode)
        # 2.主循环逻辑
        while True:
            # 找到F值最小的点
            minF = cls.__getMinNode()
            # 把这个点加入closeList中，并且在openList中删除它
            cls.__close_list.append(minF)
            cls.__open_list.remove(minF)
            # 判断这个节点的上下左右节点
            cls.__searchNear(minF, 0, -1)
            cls.__searchNear(minF, 0, 1)
            cls.__searchNear(minF, -1, 0)
            cls.__searchNear(minF, 1, 0)
            # 如果终点在关闭表中，就返回结果
            if (_point := cls.__end_pointInCloseList()) is not None:
                cPoint = _point
                pathList: list[tuple[int, int]] = []
                while True:
                    if cPoint.father:
                        pathList.append(cPoint.point.get_pos())
                        cPoint = cPoint.father
                    else:
                        cls.__open_list.clear()
                        cls.__close_list.clear()
                        return list(reversed(pathList))
            if len(cls.__open_list) == 0:
                cls.__open_list.clear()
                cls.__close_list.clear()
                return []

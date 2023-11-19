from .astar import *


# 地图模块
class AbstractTileMap(Rectangle, SurfaceWithLocalPos):
    # 获取方块数据库
    __TILES_DATABASE: Final[dict] = DataBase.get("Tiles")
    # 获取场景装饰物数据库
    _DECORATION_DATABASE: Final[dict] = DataBase.get("Decorations")

    def __init__(self) -> None:
        # Rectangle模块
        Rectangle.__init__(self, 0, 0, 0, 0)
        # 本地坐标模块
        SurfaceWithLocalPos.__init__(self)
        # 地图数据
        self.__MAP: numpy.ndarray = numpy.array([])
        # 障碍数据
        self.__BARRIER_MASK: numpy.ndarray = numpy.array([])
        # 地图 tile lookup table
        self.__tile_lookup_table: list[str] = []
        # 行
        self.__row: int = 0
        # 列
        self.__column: int = 0
        # 地图渲染用的图层
        self.__map_surface: ImageSurface | None = None
        # 地图旧图层以渲染渐变效果
        self.__map_surface_old: ImageSurface | None = None
        # 不要保存地图旧图层
        self.__don_save_old_map_surface_for_next_update: bool = False
        # 背景图片
        self.__background_image: StaticImage | None = None
        # 使用一个hashmap以加速根据坐标寻找装饰物
        self.__decorations: dict[str, DecorationObject] = {}
        # 追踪是否需要更新的参数
        self.__need_update_surface: bool = True
        # 追踪目前已经画出的方块
        self.__tile_on_surface: numpy.ndarray = numpy.asarray([])
        # 是否需要更新地图图层
        self.__need_to_recheck_tile_on_surface: bool = True

    # 获取坐标类型的字典key
    @staticmethod
    def __get_coordinate_format_key(_coordinate: tuple[int, int]) -> str:
        return str(_coordinate[0]) + "_" + str(_coordinate[1])

    # 初始化地图数据
    def __init_map(self, map_data: numpy.ndarray, barrier_data: numpy.ndarray | None, tile_size: int_f) -> None:
        self.__MAP = map_data
        self.__row, self.__column = self.__MAP.shape
        self.__BARRIER_MASK = barrier_data if barrier_data is not None else numpy.zeros(self.shape, dtype=numpy.byte)
        # 初始化追踪目前已经画出的方块的2d列表
        self.__tile_on_surface = numpy.zeros(self.__MAP.shape, dtype=numpy.byte)
        # 初始化地图渲染用的图层
        self.__map_surface = None
        self.__map_surface_old = None
        # 更新地图渲染图层的尺寸
        self.set_tile_size(tile_size)

    # 标记地图需要完全更新
    def _refresh(self) -> None:
        self.__need_update_surface = True
        self.__need_to_recheck_tile_on_surface = True

    # 更新数据
    def update(self, _data: dict, _block_size: int_f) -> None:
        # 初始化地图数据
        self.__tile_lookup_table = list(_data["map"]["lookup_table"])
        barrier_data: list[list[int]] | None = _data["map"].get("barrier")
        self.__init_map(
            numpy.asarray(_data["map"].get("data", _data["map"].get("array2d")), dtype=numpy.byte),
            numpy.asarray(barrier_data, dtype=numpy.byte) if barrier_data is not None else None,
            _block_size,
        )
        # 暗度（仅黑夜场景有效）
        TileMapImagesModule.DARKNESS = 155 if bool(_data.get("at_night", False)) is True else 0
        # 设置本地坐标
        _local_x = _data.get("local_x")
        if _local_x is None:
            self.set_local_x(0)
        elif isinstance(_local_x, str):
            self.set_local_x(Numbers.convert_percentage(_local_x) * self.get_width())
        else:
            self.set_local_x(_local_x)
        _local_y = _data.get("local_y")
        if _local_y is None:
            self.set_local_y(0)
        elif isinstance(_local_y, str):
            self.set_local_y(Numbers.convert_percentage(_local_y) * self.get_height())
        else:
            self.set_local_y(_local_y)
        # 重置装饰物列表
        self.__decorations.clear()
        # 加载装饰物
        for _decoration in _data["decoration"]:
            self.add_decoration(_decoration)
        # 背景图片路径
        theBgiPath: str | None = _data.get("background_image")
        # 背景图片
        self.__background_image = (
            StaticImage(Images.quickly_load(Specification.get_directory("background_image", theBgiPath), False), 0, 0) if theBgiPath is not None else None
        )
        # 加载图片（确保图片模块初始化）
        for fileName in self.__tile_lookup_table:
            TileMapImagesModule.add_image(fileName)
        for decoration in self.__decorations.values():
            decoration.ensure_image_cached()

    # 装饰物
    @property
    def decorations(self) -> tuple[DecorationObject, ...]:
        return tuple(self.__decorations.values())

    # 行
    @property
    def row(self) -> int:
        return self.__row

    # 列
    @property
    def column(self) -> int:
        return self.__column

    # 列
    @property
    def shape(self) -> tuple[int, int]:
        return self.__column, self.__row

    # 设置障碍mask
    def set_barrier_mask(self, x: int, y: int, value: int) -> None:
        self.__BARRIER_MASK[x, y] = value

    # 新增轴
    def add_on_axis(self, index: int, axis: int = 0) -> None:
        axis = Numbers.keep_int_in_range(axis, 0, 1)
        if axis == 0:
            if index < 0 or index > self.row:
                EXCEPTION.fatal(f"Index {index} is out of bound at row!")
        elif index < 0 or index > self.column:
            EXCEPTION.fatal(f"Index {index} is out of bound at column!")
        self.__init_map(
            numpy.insert(self.__MAP, index, numpy.random.randint(len(self.__tile_lookup_table), size=self.__row if axis == 1 else self.__column), axis),
            numpy.insert(self.__BARRIER_MASK, index, numpy.zeros(self.__row if axis == 1 else self.__column), axis),
            TileMapImagesModule.TILE_SIZE,
        )

    # 移除轴
    def remove_on_axis(self, index: int, axis: int = 0) -> None:
        axis = Numbers.keep_int_in_range(axis, 0, 1)
        if axis == 0:
            if index < 0 or index >= self.row:
                EXCEPTION.fatal(f"Index {index} is out of bound at row!")
            for key in tuple(self.__decorations.keys()):
                if self.__decorations[key].y == index:
                    self.__decorations.pop(key)
        else:
            if index < 0 or index >= self.column:
                EXCEPTION.fatal(f"Index {index} is out of bound at column!")
            for key in tuple(self.__decorations.keys()):
                if self.__decorations[key].x == index:
                    self.__decorations.pop(key)
        self.__init_map(numpy.delete(self.__MAP, index, axis), numpy.delete(self.__BARRIER_MASK, index, axis), TileMapImagesModule.TILE_SIZE)

    # 获取方块宽度
    @property
    def tile_width(self) -> int:
        return TileMapImagesModule.TILE_TEMPLE_WIDTH

    # 获取方块高度
    @property
    def tile_height(self) -> int:
        return TileMapImagesModule.TILE_TEMPLE_HEIGHT

    # 获取方块图片尺寸
    @property
    def tile_size(self) -> int:
        return TileMapImagesModule.TILE_SIZE

    # 以字典的形式获取地图的数据
    def to_dict(self) -> dict[str, Any]:
        # 重新生成最优 lookup table
        unique_elem_table: tuple = numpy.unique(self.__MAP, return_counts=True)
        lookup_table: dict[str, int] = {self.__tile_lookup_table[unique_elem_table[0][i]]: unique_elem_table[1][i] for i in range(len(unique_elem_table[0]))}
        sorted_lookup_table: list[str] = sorted(lookup_table, key=lookup_table.get, reverse=True)  # type: ignore
        # 返回数据
        return {
            "decoration": [_item.to_dict() for _item in sorted(self.__decorations.values())],
            "map": {
                "data": numpy.vectorize(lambda _num: sorted_lookup_table.index(self.__tile_lookup_table[_num]))(self.__MAP).tolist(),
                "lookup_table": sorted_lookup_table,
                "barrier": self.__BARRIER_MASK.tolist(),
            },
        }

    # 是否角色能通过该方块
    def is_passable(self, _x: int, _y: int, supposed: bool = False) -> bool:
        if not supposed:
            return bool(self.__BARRIER_MASK[_x, _y] == 0)
        else:
            if bool(self.__TILES_DATABASE[self.get_tile(_x, _y).split(":")[0]]["passable"]) is True:
                _decoration: DecorationObject | None = self.__decorations.get(self.__get_coordinate_format_key((_x, _y)))
                return _decoration is None or bool(self._DECORATION_DATABASE[_decoration.type]["passable"])
            return False

    # 以百分比的形式获取本地坐标（一般用于存档数据）
    def get_local_pos_in_percentage(self) -> dict[str, str]:
        return {"local_x": str(round(self.local_x * 100 / self.get_width(), 5)) + "%", "local_y": str(round(self.local_y * 100 / self.get_height(), 5)) + "%"}

    # 根据坐标寻找装饰物
    def get_decoration(self, pos: object) -> DecorationObject | None:
        return self.__decorations.get(self.__get_coordinate_format_key(Coordinates.convert(pos)))

    # 新增装饰物
    def add_decoration(self, _item: dict | DecorationObject) -> None:
        if isinstance(_item, dict):
            _item = DecorationObject.from_dict(_item)
        self.__decorations[self.__get_coordinate_format_key(_item.get_pos())] = _item

    # 移除装饰物
    def remove_decoration(self, decoration: DecorationObject) -> None:
        self.__decorations.pop(self.__get_coordinate_format_key(decoration.get_pos()))

    # 获取装饰物数量
    def count_decorations(self) -> int:
        return len(self.__decorations)

    # 控制地图放大缩小
    def set_tile_size(self, newPerBlockWidth: int_f) -> None:
        # 记录老尺寸
        old_width: int = self.get_width()
        old_height: int = self.get_height()
        # 更新尺寸
        TileMapImagesModule.update_size(round(newPerBlockWidth))
        self.set_size(self.tile_width * max(self.__column, self.__row), self.tile_height * max(self.__column, self.__row))
        self.__don_save_old_map_surface_for_next_update = True
        if self.get_width() < Display.get_width():
            self.set_width(Display.get_width())
        if self.get_height() < Display.get_height():
            self.set_height(Display.get_height())
        # 自动校准坐标
        self.add_local_x((old_width - self.get_width()) / 2)
        self.add_local_y((old_height - self.get_height()) / 2)
        # 打上需要更新的标签
        self._refresh()

    # 设置local坐标
    def set_local_x(self, value: int_f) -> None:
        old_local_x: int = self.local_x
        super().set_local_x(value)
        if self.local_x != old_local_x:
            self.__need_update_surface = True

    def set_local_y(self, value: int_f) -> None:
        old_local_y: int = self.local_y
        super().set_local_y(value)
        if self.local_y != old_local_y:
            self.__need_update_surface = True

    # 获取title image, 子类可重写
    def _get_tile_image(self, x: int, y: int) -> StaticImage:
        return TileMapImagesModule.get_image(self.get_tile(x, y))

    # 把地图画到屏幕上
    def render(self, _surface: ImageSurface, screen_to_move_x: int = 0, screen_to_move_y: int = 0) -> tuple[int, int]:
        # 检测屏幕是不是移到了不移到的地方
        _min_local_x: int = _surface.get_width() - self.get_width()
        if self.local_x < _min_local_x:
            self.set_local_x(_min_local_x)
            screen_to_move_x = 0
        elif self.local_x > 0:
            self.set_local_x(0)
            screen_to_move_x = 0
        _min_local_y: int = _surface.get_height() - self.get_height()
        if self.local_y < _min_local_y:
            self.set_local_y(_min_local_y)
            screen_to_move_y = 0
        elif self.local_y > 0:
            self.set_local_y(0)
            screen_to_move_y = 0
        # 如果需要重新绘制地图
        if self.__need_update_surface is True:
            self.__need_update_surface = False
            if self.__need_to_recheck_tile_on_surface is True:
                if self.__background_image is not None:
                    self.__background_image.set_size(_surface.get_width(), _surface.get_height())
                if TileMapImagesModule.DARKNESS > 0:
                    if not self.__don_save_old_map_surface_for_next_update:
                        self.__map_surface_old = self.__map_surface
                    else:
                        self.__don_save_old_map_surface_for_next_update = False
                self.__map_surface = Surfaces.transparent(self.get_size())
                self.__tile_on_surface.fill(0)
                self.__need_to_recheck_tile_on_surface = False
            # 画出地图
            for y in range(self.__row):
                for x in range(self.__column):
                    posTupleTemp: tuple[int, int] = self.calculate_position(x, y)
                    if -self.tile_width <= posTupleTemp[0] < _surface.get_width() and -self.tile_width <= posTupleTemp[1] < _surface.get_height():
                        if self.__tile_on_surface[y, x] == 0:
                            evn_img: StaticImage = self._get_tile_image(x, y)
                            evn_img.set_pos(posTupleTemp[0] - self.local_x, posTupleTemp[1] - self.local_y)
                            evn_img.set_local_offset_availability(False)
                            if self.__map_surface is not None:
                                evn_img.draw(self.__map_surface)
                            self.__tile_on_surface[y, x] = 1
                            if y < self.__row - 1:
                                self.__tile_on_surface[y + 1, x] = 0
                            if x < self.__column - 1:
                                self.__tile_on_surface[y, x + 1] = 0
                        else:
                            pass
                    elif posTupleTemp[0] >= _surface.get_width() or posTupleTemp[1] >= _surface.get_height():
                        break
                if self.calculate_position(0, y + 1)[1] >= _surface.get_height():
                    break
        # 画出背景
        if self.__background_image is not None:
            self.__background_image.draw(_surface)
        else:
            _surface.fill(Colors.BLACK)
        if self.__map_surface is not None:
            _surface.blit(self.__map_surface.subsurface(-self.local_x, -self.local_y, _surface.get_width(), _surface.get_height()), ORIGIN)
        if self.__map_surface_old is not None:
            _surface.blit(self.__map_surface_old.subsurface(-self.local_x, -self.local_y, _surface.get_width(), _surface.get_height()), ORIGIN)
            _alpha: int | None = self.__map_surface_old.get_alpha()
            if _alpha is None:
                EXCEPTION.fatal("Invalid alpha detected while processing self.__map_surface_old.get_alpha()")
            _alpha -= 15
            if _alpha > 0:
                self.__map_surface_old.set_alpha(_alpha)
            else:
                self.__map_surface_old = None
        # 返回offset
        return screen_to_move_x, screen_to_move_y

    # 获取方块
    def get_tile(self, _x: int, _y: int) -> str:
        return self.__tile_lookup_table[int(self.__MAP[_y, _x])]

    # 更新方块
    def set_tile(self, _x: int, _y: int, name: str) -> None:
        # 根据坐标更新地图块
        try:
            self.__MAP[_y, _x] = self.__tile_lookup_table.index(name)
        except ValueError:
            self.__tile_lookup_table.append(name)
            self.__MAP[_y, _x] = len(self.__tile_lookup_table) - 1
        # 需更新
        self._refresh()

    # 更新方块
    def replace_tiles(self, from_tile: str, to_tile: str) -> None:
        # the tile id for 'from tile' in the lookup table
        from_tile_index: int = -1
        # the tile id for 'to tile' in the lookup table
        to_tile_index: int = -1
        # if 'from tile' exists in the lookup table
        try:
            from_tile_index = self.__tile_lookup_table.index(from_tile)
        # if 'from tile' does not exist in the lookup table
        except ValueError:
            # then nothing to replace
            return
        # if 'to tile' already exists in the lookup table
        try:
            # get 'to tile' id
            to_tile_index = self.__tile_lookup_table.index(to_tile)
            # replace
            self.__MAP[self.__MAP == from_tile_index] = to_tile_index
        # if 'to tile' does not exist in the lookup table
        except ValueError:
            # replace the tile name in lookup table
            self.__tile_lookup_table[from_tile_index] = to_tile
        # refresh and we are done
        self._refresh()

    # 计算在地图中的方块
    @abstractmethod
    def calculate_coordinate(self, on_screen_pos: tuple[int, int] | None = None) -> tuple[int, int] | None:
        EXCEPTION.fatal("calculate_coordinate()", 1)

    # 计算在地图中的位置
    @abstractmethod
    def calculate_position(self, x: int_f, y: int_f) -> tuple[int, int]:
        EXCEPTION.fatal("calculate_position()", 1)

    # 寻找2点之间的最短路径
    def find_path(self, start: tuple[int, int], goal: tuple[int, int], lenMax: int | None = None, map2d: numpy.ndarray | None = None) -> list[tuple[int, int]]:
        # 初始化寻路地图
        if map2d is None:
            map2d = numpy.ones(self.shape, dtype=numpy.byte)
        # subtract mask
        map2d = numpy.subtract(map2d, self.__BARRIER_MASK)
        # 如果目标坐标合法
        if 0 <= goal[1] < self.__row and 0 <= goal[0] < self.__column and map2d[goal[0], goal[1]] == 1:
            # 开始寻路
            _path: list[tuple[int, int]] = AStar.search(map2d, start, goal)
            # 预处理路径并返回
            return _path[:lenMax] if lenMax is not None and len(_path) > lenMax else _path
        # 返回空列表
        return []

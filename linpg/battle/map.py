# 尝试导入tcod库
_TCOD_INITIALIZED: bool = False
try:
    import tcod  # type: ignore

    _TCOD_INITIALIZED = True
except ImportError:
    pass

from .decoration import *


# 地图模块
class TileMap(Rectangle, SurfaceWithLocalPos):

    # 开发者使用的窗口
    __debug_win: Optional[RenderedWindow] = None
    __debug_win_unit: Final[int] = 10
    # 获取方块数据库
    __TILES_DATABASE: Final[dict] = DataBase.get("Tiles")
    # 获取场景装饰物数据库
    __DECORATION_DATABASE: Final[dict] = DataBase.get("Decorations")

    def __init__(self) -> None:
        # Rectangle模块
        Rectangle.__init__(self, 0, 0, 0, 0)
        # 本地坐标模块
        SurfaceWithLocalPos.__init__(self)
        # 地图数据
        self.__MAP: numpy.ndarray = numpy.asarray([])
        # 地图 tile lookup table
        self.__tile_lookup_table: list[str] = []
        # 行
        self.__row: int = 0
        # 列
        self.__column: int = 0
        # 地图渲染用的图层
        self.__map_surface: Optional[ImageSurface] = None
        self.__map_surface_old: Optional[ImageSurface] = None
        self.__don_save_old_map_surface_for_next_update: bool = False
        # 背景图片
        self.__background_image: Optional[StaticImage] = None
        # 使用一个hashmap以加速根据坐标寻找装饰物
        self.__decorations: dict[str, DecorationObject] = {}
        # 处于光处的区域
        self.__lit_area: tuple[tuple[int, int], ...] = tuple()
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

    # 更新数据
    def update(self, mapDataDic: dict, perBlockWidth: int_f, perBlockHeight: int_f) -> None:
        # 初始化地图数据
        self.__tile_lookup_table = list(mapDataDic["map"]["lookup_table"])
        self.__MAP = numpy.asarray(mapDataDic["map"]["array2d"], dtype=numpy.byte)
        self.__row, self.__column = self.__MAP.shape
        # 暗度（仅黑夜场景有效）
        MapImageParameters.set_darkness(155 if bool(mapDataDic.get("at_night", False)) is True else 0)
        # 更新地图渲染图层的尺寸
        self.set_tile_size(perBlockWidth, perBlockHeight)
        # 设置本地坐标
        _local_x = mapDataDic.get("local_x")
        if _local_x is None:
            self.set_local_x(0)
        elif isinstance(_local_x, str):
            self.set_local_x(Numbers.convert_percentage(_local_x) * self.get_width())
        else:
            self.set_local_x(_local_x)
        _local_y = mapDataDic.get("local_y")
        if _local_y is None:
            self.set_local_y(0)
        elif isinstance(_local_y, str):
            self.set_local_y(Numbers.convert_percentage(_local_y) * self.get_height())
        else:
            self.set_local_y(_local_y)
        # 重置装饰物列表
        self.__decorations.clear()
        # 加载装饰物
        for _data in mapDataDic["decoration"]:
            self.add_decoration(_data)
        # 初始化地图渲染用的图层
        self.__map_surface = None
        self.__map_surface_old = None
        # 背景图片路径
        theBgiPath: Optional[str] = mapDataDic.get("background_image")
        # 背景图片
        self.__background_image = (
            StaticImage(Images.quickly_load(Specification.get_directory("background_image", theBgiPath), False), 0, 0) if theBgiPath is not None else None
        )
        # 加载图片（确保图片模块初始化）
        for fileName in self.__tile_lookup_table:
            TileMapImagesModule.add_image(fileName)
        for decoration in self.__decorations.values():
            decoration.ensure_image_cached()
        # 处于光处的区域
        self.__lit_area = (
            tuple()
            if MapImageParameters.get_darkness() > 0
            else tuple(Coordinates.convert(area_coordinate) for area_coordinate in mapDataDic["map"].get("lit_area", []))
        )
        # 追踪目前已经画出的方块
        self.__tile_on_surface = numpy.zeros(self.__MAP.shape, dtype=numpy.byte)
        self.__need_to_recheck_tile_on_surface = True

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

    # 获取方块宽度
    @property
    def tile_width(self) -> int:
        return MapImageParameters.get_tile_width()

    # 获取方块高度
    @property
    def tile_height(self) -> int:
        return MapImageParameters.get_tile_height()

    # 以字典的形式获取地图的数据
    def to_dict(self) -> dict:
        # 重新生成最优 lookup table
        unique_elem_table: tuple = numpy.unique(self.__MAP, return_counts=True)
        lookup_table: dict[str, int] = {self.__tile_lookup_table[unique_elem_table[0][i]]: unique_elem_table[1][i] for i in range(len(unique_elem_table[0]))}
        sorted_lookup_table: list[str] = sorted(lookup_table, key=lookup_table.get, reverse=True)  # type: ignore
        # 返回数据
        return {
            "decoration": [_item.to_dict() for _item in sorted(self.__decorations.values())],
            "map": {
                "array2d": numpy.vectorize(lambda _num: sorted_lookup_table.index(self.__tile_lookup_table[_num]))(self.__MAP).tolist(),
                "lookup_table": sorted_lookup_table,
                "lit_area": [list(area_coordinate) for area_coordinate in self.__lit_area],
            },
        }

    # 是否角色能通过该方块
    def is_passable(self, _x: int, _y: int) -> bool:
        if bool(self.__TILES_DATABASE[self.get_tile(_x, _y).split(":")[0]]["passable"]) is True:
            _decoration: Optional[DecorationObject] = self.__decorations.get(self.__get_coordinate_format_key((_x, _y)))
            return _decoration is None or bool(self.__DECORATION_DATABASE[_decoration.type]["passable"])
        return False

    # 以百分比的形式获取本地坐标（一般用于存档数据）
    def get_local_pos_in_percentage(self) -> dict[str, str]:
        return {"local_x": str(round(self.local_x * 100 / self.get_width(), 5)) + "%", "local_y": str(round(self.local_y * 100 / self.get_height(), 5)) + "%"}

    # 开发者模式
    def dev_mode(self) -> None:
        if self.__debug_win is None:
            self.__debug_win = RenderedWindow(
                self.__row * self.__debug_win_unit + self.__debug_win_unit * (self.__row + 1) // 4,
                self.__column * self.__debug_win_unit + self.__debug_win_unit * (self.__row + 1) // 4,
                "debug window",
                True,
            )
        else:
            self.__debug_win = None

    # 根据坐标寻找装饰物
    def get_decoration(self, pos: object) -> Optional[DecorationObject]:
        return self.__decorations.get(self.__get_coordinate_format_key(Coordinates.convert(pos)))

    # 新增装饰物
    def _add_decoration(self, _item: DecorationObject) -> None:
        self.__decorations[self.__get_coordinate_format_key(_item.get_pos())] = _item

    def add_decoration(self, _data: dict) -> None:
        self._add_decoration(DecorationObject.from_dict(_data))

    # 移除装饰物
    def remove_decoration(self, decoration: DecorationObject) -> None:
        self.__decorations.pop(self.__get_coordinate_format_key(decoration.get_pos()))

    # 获取装饰物数量
    def count_decorations(self) -> int:
        return len(self.__decorations)

    # 控制地图放大缩小
    def set_tile_size(self, newPerBlockWidth: int_f, newPerBlockHeight: int_f) -> None:
        # 记录老尺寸
        old_width: int = self.get_width()
        old_height: int = self.get_height()
        # 更新尺寸
        TileMapImagesModule.update_size(round(newPerBlockWidth), round(newPerBlockHeight))
        self.set_size(TileMapImagesModule.TILE_TEMPLE_WIDTH * self.__column, TileMapImagesModule.TILE_TEMPLE_HEIGHT * self.__row)
        self.__don_save_old_map_surface_for_next_update = True
        if self.get_width() < Display.get_width():
            self.set_width(Display.get_width())
        if self.get_height() < Display.get_height():
            self.set_height(Display.get_height())
        # 自动校准坐标
        self.add_local_x((old_width - self.get_width()) / 2)
        self.add_local_y((old_height - self.get_height()) / 2)
        # 打上需要更新的标签
        self.__need_update_surface = True
        self.__need_to_recheck_tile_on_surface = True

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

    # 把地图画到屏幕上
    def display_map(self, _surface: ImageSurface, screen_to_move_x: int = 0, screen_to_move_y: int = 0) -> tuple:
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
                if MapImageParameters.get_darkness() > 0:
                    if not self.__don_save_old_map_surface_for_next_update:
                        self.__map_surface_old = self.__map_surface
                    else:
                        self.__don_save_old_map_surface_for_next_update = False
                self.__map_surface = Surfaces.transparent(self.get_size())
                self.__tile_on_surface.fill(0)
                self.__need_to_recheck_tile_on_surface = False
            # 画出地图
            posTupleTemp: tuple
            evn_img: StaticImage
            for y in range(self.__row):
                for x in range(self.__column):
                    posTupleTemp = self.calculate_position(x, y)
                    if (
                        -MapImageParameters.get_tile_width() <= posTupleTemp[0] < _surface.get_width()
                        and -MapImageParameters.get_tile_width() <= posTupleTemp[1] < _surface.get_height()
                    ):
                        if self.__tile_on_surface[y, x] == 0:
                            evn_img = TileMapImagesModule.get_image(self.get_tile(x, y), not self.is_coordinate_in_lit_area(x, y))
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
        # 显示调试窗口
        if self.__debug_win is not None and not self.__need_to_recheck_tile_on_surface:
            self.__debug_win.clear()
            self.__debug_win.fill(Colors.BLACK)
            start_x: int
            start_y: int
            for y in range(len(self.__tile_on_surface)):
                for x in range(len(self.__tile_on_surface[y])):
                    start_x = int(x * self.__debug_win_unit * 1.25 + self.__debug_win_unit / 4)
                    start_y = int(y * self.__debug_win_unit * 1.25 + self.__debug_win_unit / 4)
                    if self.__tile_on_surface[y, x] == 0:
                        self.__debug_win.draw_rect((start_x, start_y, self.__debug_win_unit, self.__debug_win_unit), Colors.WHITE)
                    else:
                        self.__debug_win.fill_rect((start_x, start_y, self.__debug_win_unit, self.__debug_win_unit), Colors.WHITE)
            # 显示开发面板
            self.__debug_win.present()
        # 画出背景
        if self.__background_image is not None:
            self.__background_image.draw(_surface)
        else:
            _surface.fill(Colors.BLACK)
        if self.__map_surface is not None:
            _surface.blit(self.__map_surface.subsurface(-self.local_x, -self.local_y, _surface.get_width(), _surface.get_height()), (0, 0))
        if self.__map_surface_old is not None:
            _surface.blit(self.__map_surface_old.subsurface(-self.local_x, -self.local_y, _surface.get_width(), _surface.get_height()), (0, 0))
            _alpha: Optional[int] = self.__map_surface_old.get_alpha()
            if _alpha is None:
                EXCEPTION.fatal("Invalid alpha detected while processing self.__map_surface_old.get_alpha()")
            _alpha -= 15
            if _alpha > 0:
                self.__map_surface_old.set_alpha(_alpha)
            else:
                self.__map_surface_old = None
        # 返回offset
        return screen_to_move_x, screen_to_move_y

    # 把装饰物画到屏幕上
    def display_decoration(self, _surface: ImageSurface, occupied_coordinates: tuple) -> None:
        # 计算需要画出的范围
        screen_min: int = -MapImageParameters.get_tile_width()
        # 历遍装饰物列表里的物品
        for _item in self.__decorations.values():
            # 在地图的坐标
            thePosInMap: tuple[int, int] = self.calculate_position(_item.x, _item.y)
            if screen_min <= thePosInMap[0] < _surface.get_width() and screen_min <= thePosInMap[1] < _surface.get_height():
                # 透明度
                decoration_alpha: int = 255
                if (
                    self.__DECORATION_DATABASE[_item.type].get("hidable", False) is True
                    and _item.get_pos() in occupied_coordinates
                    and self.is_coordinate_in_lit_area(_item.x, _item.y)
                ):
                    decoration_alpha = 100
                # 画出
                _item.blit(_surface, thePosInMap, not self.is_coordinate_in_lit_area(_item.x, _item.y), decoration_alpha)

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
        self.__need_update_surface = True
        self.__need_to_recheck_tile_on_surface = True

    # 计算在地图中的方块
    def calculate_coordinate(self, on_screen_pos: Optional[tuple[int, int]] = None) -> Optional[tuple[int, int]]:
        if on_screen_pos is None:
            on_screen_pos = Controller.mouse.get_pos()
        guess_x: int = int(
            (on_screen_pos[0] - self.local_x) / TileMapImagesModule.TILE_TEMPLE_WIDTH
            + (on_screen_pos[1] - self.local_y) / TileMapImagesModule.TILE_TEMPLE_HEIGHT
            - self.__row / 2
        )
        guess_y: int = int(
            (on_screen_pos[1] - self.local_y) / TileMapImagesModule.TILE_TEMPLE_HEIGHT
            - (on_screen_pos[0] - self.local_x) / TileMapImagesModule.TILE_TEMPLE_WIDTH
            + self.__row / 2
        )
        return (guess_x, guess_y) if self.__column > guess_x >= 0 and self.__row > guess_y >= 0 else None

    # 计算在地图中的位置
    def calculate_position(self, x: int_f, y: int_f) -> tuple[int, int]:
        return (
            round((x - y + self.__row - 1) * TileMapImagesModule.TILE_TEMPLE_WIDTH / 2) + self.local_x,
            round((y + x) * TileMapImagesModule.TILE_TEMPLE_HEIGHT / 2) + self.local_y,
        )

    # 获取可视光亮区域（子类可按需重写）
    def _get_lit_area(self, alliances_data: dict) -> set[tuple[int, int]]:
        lightArea: set[tuple[int, int]] = set()
        for _alliance in alliances_data.values():
            for _area in _alliance.get_effective_range_coordinates(self):
                for _pos in _area:
                    lightArea.add(_pos)
            lightArea.add((round(_alliance.x), round(_alliance.y)))
        return lightArea

    # 刷新可视光亮区域
    def refresh_lit_area(self, alliances_data: dict) -> None:
        self.__lit_area = tuple(self._get_lit_area(alliances_data))
        self.__need_update_surface = True
        self.__need_to_recheck_tile_on_surface = True

    # 查看坐标是否在光亮范围内
    def is_coordinate_in_lit_area(self, x: int_f, y: int_f) -> bool:
        return True if MapImageParameters.get_darkness() <= 0 else (round(x), round(y)) in self.__lit_area

    # 寻找2点之间的最短路径
    def find_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        alliances: dict,
        enemies: dict,
        can_move_through_darkness: bool = False,
        lenMax: Optional[int] = None,
        enemies_ignored: tuple = tuple(),
        ignore_alliances: bool = False,
    ) -> list[tuple[int, int]]:
        # 初始化寻路地图
        map2d: numpy.ndarray = numpy.ones((self.__column, self.__row), dtype=numpy.byte)
        # 如果角色无法移动至黑暗处
        if not can_move_through_darkness:
            map2d.fill(0)
            for _pos in self.__lit_area:
                map2d[_pos[0], _pos[1]] = 1
        # 如果不忽略友方角色，则将所有友方角色的坐标点设置为障碍区块
        if not ignore_alliances:
            for value in alliances.values():
                map2d[round(value.x), round(value.y)] = 0
        # 如果忽略友方角色，则确保终点没有友方角色
        else:
            for value in alliances.values():
                if round(value.x) == goal[0] and round(value.y) == goal[1]:
                    return []
        # 历遍地图，设置障碍区块
        for _x in range(self.__column):
            for _y in range(self.__row):
                if not self.is_passable(_x, _y):
                    map2d[_x, _y] = 0
        # 将所有敌方角色的坐标点设置为障碍区块
        for key, value in enemies.items():
            if key not in enemies_ignored:
                map2d[round(value.x), round(value.y)] = 0
        # 如果目标坐标合法
        if 0 <= goal[1] < self.__row and 0 <= goal[0] < self.__column and map2d[goal[0], goal[1]] == 1:
            # 开始寻路
            if _TCOD_INITIALIZED is True:
                _path: list[tuple[int, int]] = tcod.path.AStar(map2d, 1.0).get_path(start[0], start[1], goal[0], goal[1])
            else:
                EXCEPTION.fatal("You need to install tcod to enable path finding feature!", 4)
            # 预处理路径并返回
            return _path[:lenMax] if lenMax is not None and len(_path) > lenMax else _path
        # 返回空列表
        return []

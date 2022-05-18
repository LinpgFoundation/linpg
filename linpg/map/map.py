from .astar import *

# 地图模块
class MapObject(AStar, Rectangle, SurfaceWithLocalPos):

    # 获取方块数据库
    __BLOCKS_DATABASE: dict = DataBase.get("Blocks")
    # 开发者使用的窗口
    __debug_win: Optional[RenderedWindow] = None
    __debug_win_unit: int = 10

    def __init__(self) -> None:
        # 寻路模块
        AStar.__init__(self)
        # Rectangle模块
        Rectangle.__init__(self, 0, 0, 0, 0)
        # 本地坐标模块
        SurfaceWithLocalPos.__init__(self)
        # 地图数据
        self.__MAP: numpy.ndarray = numpy.asarray([])
        # 地图渲染用的图层
        self.__MAP_SURFACE: Optional[ImageSurface] = None
        # 背景图片路径
        self.__background_image: Optional[str] = None
        # 背景图片
        self.__BACKGROUND_SURFACE: Optional[StaticImage] = None
        # 装饰物
        self.__decorations: list[DecorationObject] = []
        # 处于光处的区域
        self.__light_area: tuple = tuple()
        # 追踪是否需要更新的参数
        self.__need_update_surface: bool = True
        # 追踪目前已经画出的方块
        self.__block_on_surface: numpy.ndarray = numpy.asarray([])
        # 是否需要更新地图图层
        self.__need_to_recheck_block_on_surface: bool = True

    def update(self, mapDataDic: dict, perBlockWidth: int_f, perBlockHeight: int_f) -> None:
        # 转换原始的地图数据
        lookup_table: tuple
        MAP_t: list
        if isinstance(mapDataDic["map"], Sequence):
            MAP_t = list(mapDataDic["map"])
            # 确认场景需要用到素材
            all_images_needed: list = []
            for theRow in MAP_t:
                for theItem in theRow:
                    if theItem not in all_images_needed:
                        all_images_needed.append(theItem)
            lookup_table = tuple(all_images_needed)
            del all_images_needed
        else:
            lookup_table = tuple(mapDataDic["map"]["lookup_table"])
            MAP_t = list(mapDataDic["map"]["array2d"])
            index: int = 0
            for i in range(len(MAP_t)):
                for j in range(len(MAP_t[i])):
                    index = int(MAP_t[i][j])
                    if 0 <= index < len(lookup_table):
                        MAP_t[i][j] = lookup_table[index]
                    else:
                        EXCEPTION.warn(
                            "A element with value {0} on x {1} and y {2} is not found in the lookup table, please fix it!".format(
                                index, j, i
                            )
                        )
                        MAP_t[i][j] = "TileTemplate01"
        # 初始化地图数据
        self.__MAP = numpy.asarray(MAP_t, dtype=numpy.dtype("<U32"))
        # 使用numpy的shape决定self.row和self.column
        row, column = self.__MAP.shape
        super()._update(row, column)
        # 背景图片路径
        self.__background_image = (
            str(mapDataDic["background_image"])
            if "background_image" in mapDataDic and mapDataDic["background_image"] is not None
            else None
        )
        # 暗度（仅黑夜场景有效）
        MapImageParameters.set_darkness(155 if "at_night" in mapDataDic and bool(mapDataDic["at_night"]) is True else 0)
        # 更新地图渲染图层的尺寸
        self.set_tile_block_size(perBlockWidth, perBlockHeight)
        # 设置本地坐标
        _local_x = mapDataDic.get("local_x")
        if _local_x is None:
            self.set_local_x(0)
        elif isinstance(_local_x, str):
            self.set_local_x(convert_percentage(_local_x) * self.get_width())
        else:
            self.set_local_x(_local_x)
        _local_y = mapDataDic.get("local_y")
        if _local_y is None:
            self.set_local_y(0)
        elif isinstance(_local_y, str):
            self.set_local_y(convert_percentage(_local_y) * self.get_height())
        else:
            self.set_local_y(_local_y)
        # 重置装饰物列表
        self.__decorations.clear()
        # 加载装饰物
        for decorationType, itemsThatType in mapDataDic["decoration"].items():
            for key in itemsThatType:
                self.add_decoration(itemsThatType[key], decorationType, key)
        # 对装饰物进行排序
        self.__decorations.sort()
        # 初始化环境图片管理模块
        self.__MAP_SURFACE = None
        # 背景图片
        if self.__background_image is not None:
            self.__BACKGROUND_SURFACE = StaticImage(
                RawImg.quickly_load(os.path.join("Assets", "image", "dialog_background", self.__background_image), False),
                0,
                0,
                0,
                0,
            )
        else:
            self.__BACKGROUND_SURFACE = None
        # 加载图片
        for fileName in lookup_table:
            TileMapImagesModule.add_image(fileName)
        for decoration in self.__decorations:
            DecorationImagesModule.add_image(
                decoration.get_type(), decoration.image if isinstance(decoration.image, str) else decoration.get_type()
            )
        # 处于光处的区域
        self.__light_area = tuple()
        # 追踪目前已经画出的方块
        self.__block_on_surface = numpy.zeros((self.row, self.column), dtype=numpy.byte)
        self.__need_to_recheck_block_on_surface = True

    @property
    def decorations(self) -> list:
        return self.__decorations

    # 获取方块宽度
    @property
    def block_width(self) -> int:
        return MapImageParameters.get_block_width()

    # 获取方块高度
    @property
    def block_height(self) -> int:
        return MapImageParameters.get_block_height()

    # 以字典的形式获取地图的数据
    def to_dict(self) -> dict:
        # 转换场景装饰物数据
        decoration_dict: dict = {}
        for theDecoration in self.__decorations:
            theDecorationInDict: dict = theDecoration.to_dict()
            if theDecoration.get_type() not in decoration_dict:
                decoration_dict[theDecoration.get_type()] = {}
            decoration_dict[theDecoration.get_type()][theDecoration.get_id()] = theDecorationInDict
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
            },
            "decoration": decoration_dict,
        }

    # 以百分比的形式获取本地坐标（一般用于存档数据）
    def get_local_pos_in_percentage(self) -> dict:
        return {
            "local_x": str(round(self.local_x * 100 / self.get_width(), 5)) + "%",
            "local_y": str(round(self.local_y * 100 / self.get_height(), 5)) + "%",
        }

    # 开发者模式
    def dev_mode(self) -> None:
        if self.__debug_win is None:
            self.__debug_win = RenderedWindow(
                self.row * self.__debug_win_unit + self.__debug_win_unit * (self.row + 1) // 4,
                self.column * self.__debug_win_unit + self.__debug_win_unit * (self.row + 1) // 4,
                "debug window",
                True,
            )
        else:
            self.__debug_win = None

    # 根据index寻找装饰物
    def find_decoration_with_id(self, index: int) -> DecorationObject:
        return self.__decorations[index]

    # 根据坐标寻找装饰物
    def find_decoration_on(self, pos: object) -> Optional[DecorationObject]:
        for decoration in self.__decorations:
            # 如果坐标一致，则应该是当前装饰物了
            if Coordinates.is_same(decoration.get_pos(), pos):
                return decoration
        return None

    # 与给定Index的场景装饰物进行互动
    def interact_decoration_with_id(self, index: int) -> None:
        if self.__decorations[index].get_type() == "campfire":
            self.__decorations[index].set_status("lit", not self.__decorations[index].get_status("lit"))

    # 新增装饰物
    def add_decoration(self, _data: dict, _type: str, _id: str, _sort: bool = False) -> None:
        if "status" not in _data:
            _data["status"] = {}
        if _type == "campfire":
            self.__decorations.append(CampfireObject(_data["x"], _data["y"], _id, _type, _data["range"], _data["status"]))
        elif _type == "chest":
            self.__decorations.append(
                ChestObject(
                    _data["x"],
                    _data["y"],
                    _id,
                    _type,
                    _data["items"] if "items" in _data else [],
                    _data["whitelist"] if "whitelist" in _data else [],
                    _data["status"],
                )
            )
        else:
            new_decoration: DecorationObject = DecorationObject(
                _data["x"], _data["y"], _id, _type, _data["image"], _data["status"]
            )
            if _type == "tree":
                new_decoration.scale = 0.75
            self.__decorations.append(new_decoration)
        if _sort is True:
            self.__decorations.sort()

    # 移除装饰物
    def remove_decoration(self, decoration: DecorationObject) -> None:
        for i in range(len(self.__decorations) - 1, -1, -1):
            if Coordinates.is_same(self.__decorations[i].get_pos(), decoration.get_pos()):
                self.__decorations.pop(i)
                break

    # 获取装饰物数量
    def count_decorations(self) -> int:
        return len(self.__decorations)

    # 是否夜战
    @property
    def night_mode(self) -> bool:
        return MapImageParameters.get_darkness() > 0

    # 控制地图放大缩小
    def set_tile_block_size(self, newPerBlockWidth: int_f, newPerBlockHeight: int_f) -> None:
        # 记录老尺寸
        old_width: int = self.get_width()
        old_height: int = self.get_height()
        # 更新尺寸
        self.set_size(
            newPerBlockWidth * 0.9 * ((self.row + self.column + 1) / 2),
            newPerBlockWidth * 0.45 * ((self.row + self.column + 1) / 2) + newPerBlockWidth,
        )
        TileMapImagesModule.update_size(round(newPerBlockWidth), round(newPerBlockHeight))
        if self.get_width() < Display.get_width():
            self.set_width(Display.get_width())
        if self.get_height() < Display.get_height():
            self.set_height(Display.get_height())
        # 自动校准坐标
        self.add_local_x((old_width - self.get_width()) / 2)
        self.add_local_y((old_height - self.get_height()) / 2)
        # 打上需要更新的标签
        self.__need_update_surface = True
        self.__need_to_recheck_block_on_surface = True

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
    def display_map(self, screen: ImageSurface, screen_to_move_x: int = 0, screen_to_move_y: int = 0) -> tuple:
        # 检测屏幕是不是移到了不移到的地方
        if self.local_x < screen.get_width() - self.get_width():
            self.set_local_x(screen.get_width() - self.get_width())
            screen_to_move_x = 0
        elif self.local_x > 0:
            self.set_local_x(0)
            screen_to_move_x = 0
        if self.local_y < screen.get_height() - self.get_height():
            self.set_local_y(screen.get_height() - self.get_height())
            screen_to_move_y = 0
        elif self.local_y > 0:
            self.set_local_y(0)
            screen_to_move_y = 0
        if self.__need_update_surface is True:
            self.__need_update_surface = False
            self.__update_map_surface(screen.get_size())
        # 显示调试窗口
        if self.__debug_win is not None and not self.__need_to_recheck_block_on_surface:
            self.__debug_win.clear()
            self.__debug_win.fill("black")
            x: int
            y: int
            start_x: int
            start_y: int
            for y in range(len(self.__block_on_surface)):
                for x in range(len(self.__block_on_surface[y])):
                    start_x = int(x * self.__debug_win_unit * 1.25 + self.__debug_win_unit / 4)
                    start_y = int(y * self.__debug_win_unit * 1.25 + self.__debug_win_unit / 4)
                    if self.__block_on_surface[y][x] == 0:
                        self.__debug_win.draw_rect((start_x, start_y, self.__debug_win_unit, self.__debug_win_unit), "white")
                    else:
                        self.__debug_win.fill_rect((start_x, start_y, self.__debug_win_unit, self.__debug_win_unit), "white")
            # 显示开发面板
            self.__debug_win.present()
        # 画出背景
        if self.__BACKGROUND_SURFACE is not None:
            self.__BACKGROUND_SURFACE.draw(screen)
        else:
            screen.fill(Colors.BLACK)
        if self.__MAP_SURFACE is not None:
            screen.blit(self.__MAP_SURFACE.subsurface((-self.local_x, -self.local_y), screen.get_size()), (0, 0))
        # 返回offset
        return screen_to_move_x, screen_to_move_y

    # 重新绘制地图
    def __update_map_surface(self, window_size: tuple) -> None:
        if self.__need_to_recheck_block_on_surface is True:
            if self.__BACKGROUND_SURFACE is not None:
                self.__BACKGROUND_SURFACE.set_size(window_size[0], window_size[1])
            if self.__MAP_SURFACE is not None:
                self.__MAP_SURFACE.fill(Colors.TRANSPARENT)
            else:
                self.__MAP_SURFACE = Surfaces.transparent(self.get_size())
            self.__block_on_surface.fill(0)
            self.__need_to_recheck_block_on_surface = False
        # 画出地图
        posTupleTemp: tuple
        evn_img: StaticImage
        for y in range(self.row):
            for x in range(self.column):
                posTupleTemp = self.calculate_position(x, y)
                if (
                    -MapImageParameters.get_block_width() <= posTupleTemp[0] < window_size[0]
                    and -MapImageParameters.get_block_width() <= posTupleTemp[1] < window_size[1]
                ):
                    if self.__block_on_surface[y][x] == 0:
                        evn_img = TileMapImagesModule.get_image(str(self.__MAP[y][x]), not self.is_coordinate_in_light_rea(x, y))
                        evn_img.set_pos(posTupleTemp[0] - self.local_x, posTupleTemp[1] - self.local_y)
                        if self.__MAP_SURFACE is not None:
                            evn_img.draw(self.__MAP_SURFACE)
                        self.__block_on_surface[y][x] = 1
                        if y < self.row - 1:
                            self.__block_on_surface[y + 1][x] = 0
                        if x < self.column - 1:
                            self.__block_on_surface[y][x + 1] = 0
                    else:
                        pass
                elif posTupleTemp[0] >= window_size[0] or posTupleTemp[1] >= window_size[1]:
                    break
            if self.calculate_position(0, y + 1)[1] >= window_size[1]:
                break

    # 把装饰物画到屏幕上
    def display_decoration(self, screen: ImageSurface, alliances_data: dict = {}, enemies_data: dict = {}) -> None:
        # 检测角色所占据的装饰物（即需要透明化，方便玩家看到角色）
        charactersPos: list = []
        for dataDic in {**alliances_data, **enemies_data}.values():
            charactersPos.append((int(dataDic.x), int(dataDic.y)))
            charactersPos.append((int(dataDic.x) + 1, int(dataDic.y) + 1))
        # 计算offSet
        offSet: tuple[int, int]
        offSet_normal: tuple[int, int] = (
            round(MapImageParameters.get_block_width() / 4),
            -round(MapImageParameters.get_block_width() / 8),
        )
        offSet_tree: tuple[int, int] = (
            round(MapImageParameters.get_block_width() * 0.125),
            -round(MapImageParameters.get_block_width() * 0.375),
        )
        # 计算需要画出的范围
        screen_min: int = -MapImageParameters.get_block_width()
        # 透明度
        decoration_alpha: int
        # 在地图的坐标
        thePosInMap: tuple[int, int]
        # 历遍装饰物列表里的物品
        for item in self.__decorations:
            thePosInMap = self.calculate_position(item.x, item.y)
            if screen_min <= thePosInMap[0] < screen.get_width() and screen_min <= thePosInMap[1] < screen.get_height():
                decoration_alpha = 255
                # 树
                if item.get_type() == "tree":
                    offSet = offSet_tree
                    if item.get_pos() in charactersPos and self.is_coordinate_in_light_rea(item.x, item.y):
                        decoration_alpha = 100
                else:
                    offSet = offSet_normal
                # 画出
                item.blit(
                    screen,
                    Coordinates.add(thePosInMap, offSet),
                    not self.is_coordinate_in_light_rea(item.x, item.y),
                    decoration_alpha,
                )

    # 更新方块
    def update_block(self, pos: dict, name: str) -> None:
        self.__MAP[pos["y"]][pos["x"]] = name
        self.__need_update_surface = True
        self.__need_to_recheck_block_on_surface = True

    # 是否角色能通过该方块
    def if_block_can_pass_through(self, pos: dict) -> bool:
        return bool(self.__BLOCKS_DATABASE[self.__MAP[pos["y"]][pos["x"]]]["canPassThrough"])

    # 计算在地图中的方块
    def calculate_coordinate(self, pos: tuple[int, int] = None) -> Optional[dict]:
        if pos is None:
            pos = Controller.mouse.pos
        guess_x: int = int(
            (
                (pos[0] - self.local_x - self.row * MapImageParameters.get_block_width() * 0.43) / 0.43
                + (pos[1] - self.local_y - MapImageParameters.get_block_width() * 0.4) / 0.22
            )
            // (MapImageParameters.get_block_width() * 2)
        )
        guess_y: int = (
            int(
                (pos[1] - self.local_y - MapImageParameters.get_block_width() * 0.4) / MapImageParameters.get_block_width() / 0.22
            )
            - guess_x
        )
        x: int
        y: int
        posTupleTemp: tuple
        lenUnitW: float = MapImageParameters.get_block_width() / 5
        lenUnitH: float = MapImageParameters.get_block_width() * 0.8 / 393 * 214
        block_get_click: Optional[dict] = None
        for y in range(guess_y - 1, guess_y + 4):
            for x in range(guess_x - 1, guess_x + 4):
                posTupleTemp = self.calculate_position(x, y)
                if (
                    lenUnitW < pos[0] - posTupleTemp[0] - MapImageParameters.get_block_width() * 0.05 < lenUnitW * 3
                    and 0 < pos[1] - posTupleTemp[1] < lenUnitH
                ):
                    if 0 <= x < self.column and 0 <= y < self.row:
                        block_get_click = {"x": x, "y": y}
                    break
        return block_get_click

    # 计算在地图中的位置
    def calculate_position(self, x: int_f, y: int_f, absolute_pos: bool = False) -> tuple[int, int]:
        widthTmp: float = MapImageParameters.get_block_width() * 0.43
        _pos: tuple[int, int] = (
            round((x - y) * widthTmp + self.row * widthTmp),
            round((y + x) * MapImageParameters.get_block_width() * 0.22 + MapImageParameters.get_block_width() * 0.4),
        )
        return Coordinates.add(_pos, self.local_pos) if not absolute_pos else _pos

    # 计算光亮区域
    def calculate_darkness(self, alliances_data: dict) -> None:
        lightArea: list = []
        x: int
        y: int
        for key in alliances_data:
            the_character_effective_range = 2
            if alliances_data[key].current_hp > 0:
                if alliances_data[key].effective_range["far"] is not None:
                    the_character_effective_range = alliances_data[key].effective_range["far"][1] + 1
                elif alliances_data[key].effective_range["middle"] is not None:
                    the_character_effective_range = alliances_data[key].effective_range["middle"][1] + 1
                elif alliances_data[key].effective_range["near"] is not None:
                    the_character_effective_range = alliances_data[key].effective_range["near"][1] + 1
            for y in range(
                int(alliances_data[key].y - the_character_effective_range),
                int(alliances_data[key].y + the_character_effective_range),
            ):
                if y < alliances_data[key].y:
                    for x in range(
                        int(alliances_data[key].x - the_character_effective_range - (y - alliances_data[key].y) + 1),
                        int(alliances_data[key].x + the_character_effective_range + (y - alliances_data[key].y)),
                    ):
                        if (x, y) not in lightArea:
                            lightArea.append((x, y))
                else:
                    for x in range(
                        int(alliances_data[key].x - the_character_effective_range + (y - alliances_data[key].y) + 1),
                        int(alliances_data[key].x + the_character_effective_range - (y - alliances_data[key].y)),
                    ):
                        if (x, y) not in lightArea:
                            lightArea.append((x, y))
        for item in self.__decorations:
            if isinstance(item, CampfireObject) and item.get_status("lit") is True:
                for y in range(int(item.y - item.range), int(item.y + item.range)):
                    if y < item.y:
                        for x in range(int(item.x - item.range - (y - item.y) + 1), int(item.x + item.range + (y - item.y))):
                            if (x, y) not in lightArea:
                                lightArea.append((x, y))
                    else:
                        for x in range(int(item.x - item.range + (y - item.y) + 1), int(item.x + item.range - (y - item.y))):
                            if (x, y) not in lightArea:
                                lightArea.append((x, y))
        self.__light_area = tuple(lightArea)
        self.__need_update_surface = True
        self.__need_to_recheck_block_on_surface = True

    # 查看坐标是否在光亮范围内
    def is_coordinate_in_light_rea(self, x: int_f, y: int_f) -> bool:
        return True if not self.night_mode else (int(x), int(y)) in self.__light_area

    # 寻找2点之间的最短路径
    def find_path(
        self, start: object, destination: object, alliances: dict, enemies: dict, routeLen: int = -1, ignored: list = []
    ) -> list:
        # 获取终点坐标
        end_pos: tuple[int, int] = Coordinates.convert(destination)
        # 初始化寻路地图
        self._map2d.fill(0)
        # 历遍地图，设置障碍方块
        """
        for y in range(theMap.row):
            for x in range(theMap.column):
                if not theMap.mapData[y][x].canPassThrough:
                    self._map2d[x][y]=1
        """
        # 历遍设施，设置障碍方块
        for item in self.__decorations:
            if item.get_type() == "obstacle" or item.get_type() == "campfire":
                self._map2d[item.x][item.y] = 1
        # 如果终点有我方角色，则不允许
        for key, value in alliances.items():
            if value.x == end_pos[0] and value.y == end_pos[1]:
                return []
        # 历遍所有角色，将角色的坐标点设置为障碍方块
        for key, value in enemies.items():
            if key not in ignored:
                self._map2d[value.x][value.y] = 1
        # 开始寻路
        pathList: list = self._startPathFinding(Coordinates.convert(start), end_pos)
        pathListLen: int = len(pathList)
        # 遍历路径点,讲指定数量的点放到路径列表中
        if pathListLen > 0:
            # 生成路径的长度
            if routeLen >= 0 and pathListLen < routeLen or routeLen <= 0:
                routeLen = pathListLen
            # 返回路径
            return [pathList[i].get_pos() for i in range(routeLen)]
        else:
            return []

from .astar import *

# 地图模块
class MapObject(SurfaceWithLocalPos, Rectangle, AStar):

    # 获取方块数据库
    __BLOCKS_DATABASE: dict = DataBase.get("Blocks")

    def __init__(self, mapDataDic: dict, perBlockWidth: int_f, perBlockHeight: int_f):
        # 转换原始的地图数据
        lookup_table: tuple
        MAP_t: list
        if isinstance(mapDataDic["map"], (list, tuple)):
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
        self.__MAP: numpy.ndarray = numpy.asarray(MAP_t)
        # 使用numpy的shape决定self.row和self.column
        self.row, self.column = self.__MAP.shape
        AStar.__init__(self, self.row, self.column)
        # 背景图片路径
        self.__background_image: str = str(mapDataDic["background_image"])
        # 暗度（仅黑夜场景有效）
        AbstractMapImagesModule.set_darkness(155 if "atNight" in mapDataDic and bool(mapDataDic["atNight"]) is True else 0)
        # 本地坐标模块
        SurfaceWithLocalPos.__init__(self)
        # Rectangle模块
        Rectangle.__init__(
            self,
            0,
            0,
            int(perBlockWidth * 0.9 * ((self.row + self.column + 1) / 2)),
            int(perBlockWidth * 0.45 * ((self.row + self.column + 1) / 2) + perBlockWidth),
        )
        # 设置本地坐标
        self.set_local_pos(mapDataDic["local_x"], mapDataDic["local_y"])
        # 装饰物
        self.__decorations: list = []
        # 加载装饰物
        for decorationType, itemsThatType in mapDataDic["decoration"].items():
            for itemId, itemData in itemsThatType.items():
                self.add_decoration(itemData, decorationType, itemId)
        # 对装饰物进行排序
        self.__decorations.sort()
        # 初始化环境图片管理模块
        self.__MAP_SURFACE: object = None
        # 背景图片
        self.__BACKGROUND_IMAGE: ImageSurface = (
            IMG.quickly_load(os.path.join("Assets", "image", "dialog_background", self.__background_image), False).convert()
            if self.__background_image is not None
            else None
        )
        # 更新尺寸
        AbstractMapImagesModule.set_block_size(round(perBlockWidth), round(perBlockHeight))
        # 加载图片
        for fileName in lookup_table:
            TileMapImagesModule.add_image(fileName)
        for decoration in self.__decorations:
            DecorationImagesModule.add_image(decoration.get_type(), decoration.image)
        # 处于光处的区域
        self.__light_area: numpy.ndarray = None
        # 追踪是否需要更新的参数
        self.__need_update_surface: bool = True
        # 追踪目前已经画出的方块
        self.__block_on_surface: numpy.ndarray = None
        # 开发者使用的窗口
        self.__debug_win = None

    @property
    def decorations(self) -> list:
        return self.__decorations

    # 获取方块宽度
    @property
    def block_width(self) -> int:
        return AbstractMapImagesModule.get_block_width()

    # 获取方块高度
    @property
    def block_height(self) -> int:
        return AbstractMapImagesModule.get_block_height()

    # 将地图模块所有数据以字典的形式返回
    def to_dict(self) -> dict:
        return {
            "background_image": self.__background_image,
            "local_x": self.local_x,
            "local_y": self.local_y,
            "atNight": self.night_mode,
        } | self.get_map_in_dict()

    # 以字典的形式获取地图的数据
    def get_map_in_dict(self) -> dict:
        # 转换场景装饰物数据
        decoration_dict = {}
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
        sorted_lookup_table: list = sorted(lookup_table, key=lookup_table.get, reverse=True)
        # 返回数据
        return {
            "map": {
                "array2d": [[sorted_lookup_table.index(item) for item in row] for row in MAP_t],
                "lookup_table": sorted_lookup_table,
            },
            "decoration": decoration_dict,
        }

    # 开发者模式
    def dev_mode(self) -> None:
        if self.__debug_win is None:
            unit: int = 10
            self.__debug_win = RenderedWindow(
                int(self.row * unit + unit / 4 * (self.row + 1)),
                int(self.column * unit + unit / 4 * (self.row + 1)),
                "debug window",
                True,
            )
            self.__debug_win.unit = unit
        else:
            self.__debug_win = None

    # 显示开发面板
    def __display_dev_panel(self) -> None:
        self.__debug_win.clear()
        self.__debug_win.fill("black")
        x: int
        y: int
        start_x: int
        start_y: int
        unit: int = self.__debug_win.unit
        for y in range(len(self.__block_on_surface)):
            for x in range(len(self.__block_on_surface[y])):
                start_x = int(x * unit * 1.25 + unit / 4)
                start_y = int(y * unit * 1.25 + unit / 4)
                if self.__block_on_surface[y][x] == 0:
                    self.__debug_win.draw_rect((start_x, start_y, unit, unit), "white")
                else:
                    self.__debug_win.fill_rect((start_x, start_y, unit, unit), "white")
        self.__debug_win.present()

    # 根据index寻找装饰物
    def find_decoration_with_id(self, index: int) -> DecorationObject:
        return self.__decorations[index]

    # 根据坐标寻找装饰物
    def find_decoration_on(self, pos: Any) -> DecorationObject:
        for decoration in self.__decorations:
            # 如果坐标一致，则应该是当前装饰物了
            if Positions.is_same(decoration.get_pos(), pos):
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
            new_decoration = CampfireObject(_data["x"], _data["y"], _id, _type, _data["range"], _data["status"])
        elif _type == "chest":
            new_decoration = ChestObject(
                _data["x"],
                _data["y"],
                _id,
                _type,
                _data["items"] if "items" in _data else [],
                _data["whitelist"] if "whitelist" in _data else [],
                _data["status"],
            )
        else:
            new_decoration = DecorationObject(_data["x"], _data["y"], _id, _type, _data["image"], _data["status"])
            if _type == "tree":
                new_decoration.scale = 0.75
        self.__decorations.append(new_decoration)
        if _sort is True:
            self.__decorations.sort()

    # 移除装饰物
    def remove_decoration(self, decoration: object) -> None:
        pos: tuple = decoration.get_pos()
        i: int
        for i in range(len(self.__decorations) - 1, -1):
            if self.__decorations[i].get_pos() == pos:
                self.__decorations.pop(i)
                break

    # 获取装饰物数量
    def count_decorations(self) -> int:
        return len(self.__decorations)

    # 是否夜战
    @property
    def night_mode(self) -> bool:
        return AbstractMapImagesModule.get_darkness() > 0

    # 控制地图放大缩小
    def changePerBlockSize(self, newPerBlockWidth: int_f, newPerBlockHeight: int_f) -> None:
        # 记录老尺寸
        old_width: int = self.get_width()
        old_height: int = self.get_height()
        # 更新尺寸
        self.set_width(newPerBlockWidth * 0.9 * ((self.row + self.column + 1) / 2))
        self.set_height(newPerBlockWidth * 0.45 * ((self.row + self.column + 1) / 2) + newPerBlockWidth)
        AbstractMapImagesModule.set_block_size(round(newPerBlockWidth), round(newPerBlockHeight))
        TileMapImagesModule.update_size()
        if self.get_width() < Display.get_width():
            self.set_width(Display.get_width())
        if self.get_height() < Display.get_height():
            self.set_height(Display.get_height())
        # 自动校准坐标
        self.add_local_x((old_width - self.get_width()) / 2)
        self.add_local_y((old_height - self.get_height()) / 2)
        # 打上需要更新的标签
        self.__need_update_surface = True
        self.__block_on_surface = None

    # 设置local坐标
    def set_local_x(self, value: number) -> None:
        old_local_x: int = self.local_x
        super().set_local_x(value)
        if self.local_x != old_local_x:
            self.__need_update_surface = True

    def set_local_y(self, value: number) -> None:
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
        if self.__debug_win is not None and isinstance(self.__block_on_surface, numpy.ndarray):
            self.__display_dev_panel()
        # 画出背景
        screen.blits(((self.__BACKGROUND_SURFACE, (0, 0)), (self.__MAP_SURFACE, self.get_local_pos())))
        # 返回offset
        return screen_to_move_x, screen_to_move_y

    # 重新绘制地图
    def __update_map_surface(self, window_size: tuple) -> None:
        if not isinstance(self.__block_on_surface, numpy.ndarray):
            self.__BACKGROUND_SURFACE = (
                IMG.resize(self.__BACKGROUND_IMAGE, window_size)
                if self.__BACKGROUND_IMAGE is not None
                else new_surface(window_size)
            )
            if self.__MAP_SURFACE is not None:
                self.__MAP_SURFACE.fill(Colors.TRANSPARENT)
            else:
                self.__MAP_SURFACE = new_transparent_surface(self.get_size())
            self.__block_on_surface = numpy.zeros((self.row, self.column), dtype=numpy.int8)
        # 画出地图
        posTupleTemp: tuple
        evn_img: StaticImage
        for y in range(self.row):
            for x in range(self.column):
                posTupleTemp = self.calPosInMap(x, y)
                if (
                    -self.block_width <= posTupleTemp[0] < window_size[0]
                    and -self.block_width <= posTupleTemp[1] < window_size[1]
                ):
                    if self.__block_on_surface[y][x] == 0:
                        evn_img = TileMapImagesModule.get_image(str(self.__MAP[y][x]), not self.isPosInLightArea(x, y))
                        evn_img.set_pos(posTupleTemp[0] - self.local_x, posTupleTemp[1] - self.local_y)
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
            if self.calPosInMap(0, y + 1)[1] >= window_size[1]:
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
        offSet_normal: tuple[int, int] = (round(self.block_width / 4), -round(self.block_width / 8))
        offSet_tree: tuple[int, int] = (round(self.block_width * 0.125), -round(self.block_width * 0.375))
        # 计算需要画出的范围
        screen_min: int = -self.block_width
        # 透明度
        decoration_alpha: int
        # 在地图的坐标
        thePosInMap: tuple[int, int]
        # 历遍装饰物列表里的物品
        for item in self.__decorations:
            thePosInMap = self.calPosInMap(item.x, item.y)
            if screen_min <= thePosInMap[0] < screen.get_width() and screen_min <= thePosInMap[1] < screen.get_height():
                decoration_alpha = 255
                # 树
                if item.get_type() == "tree":
                    offSet = offSet_tree
                    if item.get_pos() in charactersPos and self.inLightArea(item):
                        decoration_alpha = 100
                else:
                    offSet = offSet_normal
                # 画出
                item.blit(screen, Coordinates.add(thePosInMap, offSet), not self.inLightArea(item), decoration_alpha)

    # 更新方块
    def update_block(self, pos: dict, name: str) -> None:
        self.__MAP[pos["y"]][pos["x"]] = name
        self.__need_update_surface = True
        self.__block_on_surface = None

    # 是否角色能通过该方块
    def ifBlockCanPassThrough(self, pos: dict) -> bool:
        return bool(self.__BLOCKS_DATABASE[self.__MAP[pos["y"]][pos["x"]]]["canPassThrough"])

    # 计算在地图中的方块
    def calBlockInMap(self, pos: tuple[int, int] = None):
        if pos is None:
            pos = Controller.mouse.pos
        guess_x: int = int(
            (
                (pos[0] - self.local_x - self.row * self.block_width * 0.43) / 0.43
                + (pos[1] - self.local_y - self.block_width * 0.4) / 0.22
            )
            / 2
            / self.block_width
        )
        guess_y: int = int((pos[1] - self.local_y - self.block_width * 0.4) / self.block_width / 0.22) - guess_x
        x: int
        y: int
        posTupleTemp: tuple
        lenUnitW: float = self.block_width / 5
        lenUnitH: float = self.block_width * 0.8 / 393 * 214
        block_get_click = None
        for y in range(guess_y - 1, guess_y + 4):
            for x in range(guess_x - 1, guess_x + 4):
                posTupleTemp = self.calPosInMap(x, y)
                if (
                    lenUnitW < pos[0] - posTupleTemp[0] - self.block_width * 0.05 < lenUnitW * 3
                    and 0 < pos[1] - posTupleTemp[1] < lenUnitH
                ):
                    if 0 <= x < self.column and 0 <= y < self.row:
                        block_get_click = {"x": x, "y": y}
                    break
        return block_get_click

    # 计算方块被画出的位置
    def getBlockExactLocation(self, x: int, y: int) -> dict:
        xStart, yStart = self.calPosInMap(x, y)
        return {
            "xStart": xStart,
            "xEnd": xStart + self.block_width,
            "yStart": yStart,
            "yEnd": yStart + self.block_width * 0.5,
        }

    # 计算光亮区域
    def calculate_darkness(self, alliances_data: dict) -> None:
        lightArea: list = []
        x: int
        y: int
        for each_chara in alliances_data:
            the_character_effective_range = 2
            if alliances_data[each_chara].current_hp > 0:
                if alliances_data[each_chara].effective_range["far"] is not None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["far"][1] + 1
                elif alliances_data[each_chara].effective_range["middle"] is not None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["middle"][1] + 1
                elif alliances_data[each_chara].effective_range["near"] is not None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["near"][1] + 1
            for y in range(
                int(alliances_data[each_chara].y - the_character_effective_range),
                int(alliances_data[each_chara].y + the_character_effective_range),
            ):
                if y < alliances_data[each_chara].y:
                    for x in range(
                        int(
                            alliances_data[each_chara].x
                            - the_character_effective_range
                            - (y - alliances_data[each_chara].y)
                            + 1
                        ),
                        int(
                            alliances_data[each_chara].x + the_character_effective_range + (y - alliances_data[each_chara].y)
                        ),
                    ):
                        if [x, y] not in lightArea:
                            lightArea.append([x, y])
                else:
                    for x in range(
                        int(
                            alliances_data[each_chara].x
                            - the_character_effective_range
                            + (y - alliances_data[each_chara].y)
                            + 1
                        ),
                        int(
                            alliances_data[each_chara].x + the_character_effective_range - (y - alliances_data[each_chara].y)
                        ),
                    ):
                        if [x, y] not in lightArea:
                            lightArea.append([x, y])
        for item in self.__decorations:
            if item.get_type() == "campfire" and item.get_status("lit") is True:
                for y in range(int(item.y - item.range), int(item.y + item.range)):
                    if y < item.y:
                        for x in range(int(item.x - item.range - (y - item.y) + 1), int(item.x + item.range + (y - item.y))):
                            if [x, y] not in lightArea:
                                lightArea.append([x, y])
                    else:
                        for x in range(int(item.x - item.range + (y - item.y) + 1), int(item.x + item.range - (y - item.y))):
                            if [x, y] not in lightArea:
                                lightArea.append([x, y])
        self.__light_area = numpy.asarray(lightArea, dtype=numpy.int8)
        self.__need_update_surface = True
        self.__block_on_surface = None

    # 计算在地图中的位置
    def calPosInMap(self, x: int_f, y: int_f) -> tuple[int, int]:
        widthTmp: float = self.block_width * 0.43
        return round((x - y) * widthTmp + self.local_x + self.row * widthTmp), round(
            (y + x) * self.block_width * 0.22 + self.local_y + self.block_width * 0.4
        )

    def calAbsPosInMap(self, x: int_f, y: int_f) -> tuple[int, int]:
        widthTmp: float = self.block_width * 0.43
        return round((x - y) * widthTmp + self.row * widthTmp), round(
            (y + x) * self.block_width * 0.22 + self.block_width * 0.4
        )

    # 查看角色是否在光亮范围内
    def inLightArea(self, entity: object) -> bool:
        return self.isPosInLightArea(entity.x, entity.y)

    def isPosInLightArea(self, x: int_f, y: int_f) -> bool:
        return True if not self.night_mode else numpy.any(numpy.equal(self.__light_area, [int(x), int(y)]).all(1))

    # 以下是A星寻路功能
    def findPath(
        self,
        start_p: Any,
        end_p: Any,
        friendData: dict,
        enemyData: dict,
        routeLen: int = -1,
        ignoreEnemyCharacters: list = [],
    ) -> list:
        # 检测起点
        start_pos: tuple = Coordinates.convert(start_p)
        # 检测终点
        end_pos: tuple = Coordinates.convert(end_p)
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
        for key, value in friendData.items():
            if value.x == end_pos[0] and value.y == end_pos[1]:
                return []
        # 历遍所有角色，将角色的坐标点设置为障碍方块
        for key, value in enemyData.items():
            if key not in ignoreEnemyCharacters:
                self._map2d[value.x][value.y] = 1
        # 开始寻路
        pathList: list = self._startPathFinding(start_pos, end_pos)
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

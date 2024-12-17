from .battle import *


# 地图编辑器系统
class AbstractMapEditor(AbstractBattleSystem, metaclass=ABCMeta):
    # 修改模式
    @enum.verify(enum.UNIQUE)
    class _MODIFY(enum.IntEnum):
        DISABLE = enum.auto()
        DELETE_ENTITY = enum.auto()
        DELETE_ROW = enum.auto()
        DELETE_COLUMN = enum.auto()
        ADD_ROW_ABOVE = enum.auto()
        ADD_ROW_BELOW = enum.auto()
        ADD_COLUMN_BEFORE = enum.auto()
        ADD_COLUMN_AFTER = enum.auto()

    def __init__(self) -> None:
        # 初始化父类
        super().__init__()
        # 初始化ui
        self.__buttons_container: GameObjectsDictContainer = UI.generate_container("map_editor_buttons")
        self.__right_container_buttons: GameObjectsDictContainer = UI.generate_container("map_editor_right_container_buttons")
        self.__UIContainerRight: StaticImage = StaticImage("<&ui>container.png", 0, 0)
        self.__UIContainerRight.rotate(90)
        self.__UIContainerBottom: StaticImage = StaticImage("<&ui>container.png", 0, 0)
        self.__bottom_container_buttons: GameObjectsListContainer = GameObjectsListContainer(None, 0, 0, 0, 0)
        self.__entitiesImagesContainers: list = []
        self.__entitiesImagesContainerUsingIndex: int = -1
        self.__envImgContainer: SurfaceContainerWithScrollBar = SurfaceContainerWithScrollBar(None, 0, 0, 0, 0, Axis.VERTICAL)
        self.__decorationsImgContainer: SurfaceContainerWithScrollBar = SurfaceContainerWithScrollBar(None, 0, 0, 0, 0, Axis.VERTICAL)
        # 用于储存即将发下的物品的具体参数
        self.__object_to_put_down: dict = {}
        # 未保存离开时的警告
        self.__no_save_warning: GameObjectsDictContainer = UI.generate_container("leave_without_saving_warning")
        # 选中框
        self._select_rect: Rectangle = Rectangle(0, 0, 0, 0)
        self._select_pos: tuple = tuple()
        # 是否是修改模式
        self._modify_mode: AbstractMapEditor._MODIFY = self._MODIFY.DISABLE
        # 是否有ui容器被鼠标触碰
        self._no_container_is_hovered: bool = False
        # 是否展示barrier mask
        self._show_barrier_mask: bool = False
        # 关卡历史
        self.__level_data_history: list[dict] = []
        # 代表当前关卡历史的index
        self.__current_level_data_index: int = -1

    # 根据数据更新特定的角色 - 子类需实现
    @abstractmethod
    def update_entity(self, faction: str, key: str, data: dict) -> None:
        EXCEPTION.fatal("update_entity()", 1)

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return Config.load_file(self.get_data_file_path()) | super()._get_data_need_to_save()

    # 是否有物品被选中
    def is_any_object_selected(self) -> bool:
        return len(self.__object_to_put_down) > 0

    # 处理关键数据
    def _process_data(self, _data: dict) -> None:
        # 确保地图初始化
        _map_p: list | None = _data.get("map")
        if _map_p is None or len(_map_p) == 0:
            lookup_table: list[str] = ["snow:2", "snow:3", "snow:4", "snow:5", "snow:6", "snow:7"]
            tile_y: int = 50
            tile_x: int = 50
            _data["map"] = {
                "array2d": [[Numbers.get_random_int(0, len(lookup_table) - 1) for _ in range(tile_x)] for _ in range(tile_y)],
                "lookup_table": lookup_table,
            }
        _data["_mode"] = "dev"
        # 开始处理数据
        super()._process_data(_data)

    # 加载地图
    def __load_level(self, data: dict) -> None:
        tempLocal_x, tempLocal_y = self.get_map().get_local_pos()
        self._process_data(data)
        self.get_map().set_local_pos(tempLocal_x, tempLocal_y)

    # 重置地图历史
    def __reset_level_history(self) -> None:
        # 重置历史
        self.__level_data_history.clear()
        self.__current_level_data_index = -1
        self.__append_level_history()

    # 新增历史
    def __append_level_history(self) -> None:
        self.__level_data_history = self.__level_data_history[: self.__current_level_data_index + 1]
        self.__level_data_history.append(self._get_data_need_to_save())
        self.__current_level_data_index += 1

    # 初始化UI
    def _init_ui(self) -> None:
        """加载右侧的界面"""
        # 加载容器图片
        container_width: int = Display.get_width() // 5
        container_height: int = Display.get_height()
        button_width: int = Display.get_width() // 25
        button_height: int = Display.get_height() // 5
        padding: int = Display.get_height() // 100
        self.__right_container_buttons.get("select_tile").set_left(
            (
                container_width
                - self.__right_container_buttons.get("select_tile").get_width()
                - self.__right_container_buttons.get("select_decoration").get_width()
                - padding
            )
            // 2
        )
        self.__right_container_buttons.get("select_decoration").set_left(self.__right_container_buttons.get("select_tile").right + padding)
        self.__UIContainerRight.set_size(container_width, container_height)
        self.__UIContainerButtonRight = MovableStaticImage(
            "<&ui>container_button.png",
            Display.get_width() - button_width,
            (Display.get_height() - button_height) // 2,
            Display.get_width() - button_width - container_width,
            (Display.get_height() - button_height) // 2,
            container_width // 10,
            0,
            button_width,
            button_height,
        )
        self.__UIContainerButtonRight.rotate(90)
        # 加载背景图片
        self.__envImgContainer.set_pos(container_width * 3 // 40, Display.get_height() // 10)
        self.__envImgContainer.set_size(container_width * 17 // 20, Display.get_height() * 17 // 20)
        if TileMapImagesModule.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET is None:
            EXCEPTION.fatal("Image sprite sheet for tile map is not loaded correctly!")
        for key, value in TileMapImagesModule.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET.to_dict().items():
            if not isinstance(value, tuple):
                self.__envImgContainer.set(key, Images.resize(value, (self.get_map().tile_size / 3, None)))
            else:
                for i, _ref in enumerate(value):
                    self.__envImgContainer.set(f"{key}:{i}", Images.resize(_ref, (self.get_map().tile_size / 3, None)))
        self.__envImgContainer.set_item_per_line(4)
        self.__envImgContainer.set_scroll_bar_pos("right")
        self.__envImgContainer.set_visible(True)
        self.__envImgContainer.distance_between_item = padding
        # 加载所有的装饰品
        self.__decorationsImgContainer.set_pos(container_width * 3 // 40, Display.get_height() // 10)
        self.__decorationsImgContainer.set_size(container_width * 17 // 20, Display.get_height() * 17 // 20)
        # 确保装饰物材质模块已经初始化
        DecorationImagesModule.init()
        # 加载默认装饰物
        for key, value in DecorationImagesModule.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET.to_dict().items():
            if not isinstance(value, tuple):
                self.__decorationsImgContainer.set(key, Images.resize(value, (self.get_map().tile_size / 3, None)))
            else:
                for i, _ref in enumerate(value):
                    self.__decorationsImgContainer.set(f"{key}:{i}", Images.resize(_ref, (self.get_map().tile_size / 3, None)))
        # 加载自带的装饰物
        for key, value in DecorationImagesModule.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET.to_dict().items():
            if not isinstance(value, tuple):
                self.__decorationsImgContainer.set(key, Images.resize(value, (self.get_map().tile_size / 3, None)))
            else:
                for i, _ref in enumerate(value):
                    self.__decorationsImgContainer.set(f"{key}:{i}", Images.resize(_ref, (self.get_map().tile_size / 3, None)))
        # 设置容器参数
        self.__decorationsImgContainer.set_item_per_line(4)
        self.__decorationsImgContainer.set_scroll_bar_pos("right")
        self.__decorationsImgContainer.set_visible(False)
        self.__decorationsImgContainer.distance_between_item = padding
        """加载下方的界面"""
        container_width = Display.get_width() * 4 // 5
        container_height = Display.get_height() * 3 // 10
        button_width = Display.get_width() * 7 // 50
        button_height = Display.get_height() // 20
        self.__UIContainerBottom.set_size(container_width, container_height)
        self.__UIContainerButtonBottom = MovableStaticImage(
            "<&ui>container_button.png",
            (container_width - button_width) // 2,
            Display.get_height() - button_height,
            (container_width - button_width) // 2,
            Display.get_height() - button_height - container_height,
            0,
            container_height // 10,
            button_width,
            button_height,
        )
        # 加载所有角色的图片文件
        for faction in os.listdir(EntitySpriteImageManager.SPRITES_PATH):
            newContainer: SurfaceContainerWithScrollBar = SurfaceContainerWithScrollBar(
                None, container_width // 40, container_height * 3 // 10, container_width * 19 // 20, container_height * 3 // 5, Axis.HORIZONTAL, faction
            )
            for img_name in os.listdir(os.path.join(EntitySpriteImageManager.SPRITES_PATH, faction)):
                newContainer.set(
                    img_name,
                    Images.smoothly_resize(
                        EntitySpriteImageManager.try_get_image_references(faction, img_name, "wait").get_image(0).get_image_copy(),
                        (None, container_height // 3),
                    ),
                )
            newContainer.set_scroll_bar_pos("bottom")
            newContainer.distance_between_item = padding
            self.__entitiesImagesContainers.append(newContainer)
            newButton: Button = Button.load("<&ui>button.png", (0, 0), (0, 0), 100)
            newButton.set_text(ButtonComponent.text(Lang.get_text("General", faction), button_height // 2, Colors.BLACK, alpha_when_not_hover=100))
            newButton.set_auto_resize(True)
            if len(self.__bottom_container_buttons) > 0:
                newButton.set_left(self.__bottom_container_buttons[len(self.__bottom_container_buttons) - 1].right + padding)
            else:
                self.__entitiesImagesContainerUsingIndex = 0
            self.__bottom_container_buttons.append(newButton)
        self.__object_to_put_down.clear()
        # 设置按钮位置
        # ----- 第一行 -----
        self.__buttons_container.get("back").set_left(self.__buttons_container.get("save").get_right() + padding)
        self.__buttons_container.get("delete_entity").set_left(self.__buttons_container.get("back").get_right() + padding)
        self.__buttons_container.get("undo").set_left(self.__buttons_container.get("delete_entity").get_right() + padding)
        self.__buttons_container.get("redo").set_left(self.__buttons_container.get("undo").get_right() + padding)
        self.__buttons_container.get("reload").set_left(self.__buttons_container.get("redo").get_right() + padding)
        # ----- 第二行 -----
        self.__buttons_container.get("add_row_above").set_left(self.__buttons_container.get("save").get_left())
        self.__buttons_container.get("add_row_below").set_left(self.__buttons_container.get("add_row_above").get_right() + padding)
        self.__buttons_container.get("add_colum_before").set_left(self.__buttons_container.get("add_row_below").get_right() + padding)
        self.__buttons_container.get("add_colum_after").set_left(self.__buttons_container.get("add_colum_before").get_right() + padding)
        self.__buttons_container.get("delete_row").set_left(self.__buttons_container.get("add_colum_after").get_right() + padding)
        self.__buttons_container.get("delete_colum").set_left(self.__buttons_container.get("delete_row").get_right() + padding)
        # ----- 第三行 -----
        self.__buttons_container.get("auto_add_barriers").set_left(self.__buttons_container.get("save").get_left())
        self.__buttons_container.get("add_barrier").set_left(self.__buttons_container.get("auto_add_barriers").get_right() + padding)

    # 初始化并加载新场景
    def new(self, chapterType: str, chapterId: int, projectName: str | None = None) -> None:
        self._initialize(chapterType, chapterId, projectName)
        self._process_data(Config.load_file(self.get_data_file_path()))
        self._init_ui()
        self.__reset_level_history()

    # 重写load_progress - 功能上应和new一直，并忽略其他数据
    def load_progress(self, _data: dict) -> None:
        self.new(_data["chapter_type"], _data["chapter_id"], _data.get("project_name"))

    # 设置装饰物
    def set_decoration(self, _item: str | None, _pos: tuple[int, int]) -> None:
        # 查看当前位置是否有装饰物
        decoration: DecorationObject | None = self.get_map().get_decoration(self._tile_is_hovering)
        # 如果发现有冲突的装饰物
        if decoration is not None:
            # 则移除
            self.get_map().remove_decoration(decoration)
        # if _item is None, then it means remove only
        if _item is None:
            return
        self.get_map().add_decoration({"id": _item, "x": _pos[0], "y": _pos[1]})

    # 删除实体
    def delete_entity(self, _filter: Callable[[Entity], bool]) -> bool:
        delete_one: bool = False
        for _value in self._entities_data.values():
            for key in tuple(_value.keys()):
                if _filter(_value[key]):
                    _value.pop(key)
                    delete_one = True
        return delete_one

    # move the entity
    def move_entity(self, _filter: Callable[[Entity], bool], x: int, y: int) -> None:
        for vl in self._entities_data.values():
            for e in vl.values():
                if _filter(e):
                    e.set_x(round(e.x) + x)
                    e.set_y(round(e.y) + y)

    # 设置实体
    def set_entity(self, _item: str | None, _pos: tuple[int, int]) -> None:
        # 尝试移除坐标冲突的实体
        self.delete_entity(lambda e: Coordinates.is_same(e, _pos))
        # if _item is None, then it means remove only
        if _item is None:
            return
        # 生成需要更新的数据
        _new_data: dict = copy.deepcopy(Entity.get_entity_data(_item))
        _new_data.update({"x": _pos[0], "y": _pos[1], "type": _item})
        the_id: int = 0
        nameTemp: str = f"{_item}_{the_id}"
        while nameTemp in self._entities_data[_new_data["faction"]]:
            the_id += 1
            nameTemp = f"{_item}_{the_id}"
        self.update_entity(_new_data["faction"], nameTemp, _new_data)

    # 设置区块
    def set_tile(self, _item: str, _pos: tuple[int, int]) -> None:
        self.get_map().set_tile(*_pos, _item)

    # 删除指定坐标上的实体
    def delete_entity_on_tile(self, _pos: tuple[int, int]) -> None:
        # 优先移除barrier mask
        if not self.get_map().is_passable(_pos[0], _pos[1]):
            self.get_map().set_barrier_mask(_pos[0], _pos[1], 0)
        else:
            # 如果发现有冲突的装饰物
            if self.get_map().get_decoration(_pos) is not None:
                self.set_decoration(None, _pos)
            else:
                self.set_entity(None, _pos)

    # 将地图制作器的界面画到屏幕上
    def draw(self, _surface: ImageSurface) -> None:
        UIContainerRight_offset_pos: tuple[int, int] = (self.__UIContainerButtonRight.right, 0)
        UIContainerBottom_offset_pos: tuple[int, int] = (0, self.__UIContainerButtonBottom.bottom)
        self._no_container_is_hovered = not self.__UIContainerRight.is_hovered(UIContainerRight_offset_pos) and not self.__UIContainerBottom.is_hovered(
            UIContainerBottom_offset_pos
        )
        # 确保无选中
        if len(self._select_pos) > 0:
            pass
        # 如果鼠标confirm
        elif Controller.get_event("confirm"):
            # 显示或隐藏右侧的容器
            if self.__UIContainerButtonRight.is_hovered():
                self.__UIContainerButtonRight.switch()
                self.__UIContainerButtonRight.flip(True)
            # 显示或隐藏下侧的容器
            elif self.__UIContainerButtonBottom.is_hovered():
                self.__UIContainerButtonBottom.switch()
                self.__UIContainerButtonBottom.flip(False, True)
            elif self._tile_is_hovering is not None and self.__buttons_container.item_being_hovered is None:
                whether_add_history: bool = True
                _tile_is_hovering: tuple[int, int] = self._tile_is_hovering
                if self._modify_mode == self._MODIFY.DELETE_ENTITY:
                    self.delete_entity_on_tile(_tile_is_hovering)
                # 移除行
                elif self._modify_mode == self._MODIFY.DELETE_ROW:
                    self.get_map().remove_on_axis(_tile_is_hovering[1])
                    self.delete_entity(lambda e: round(e.y) == _tile_is_hovering[1])
                    self.move_entity(lambda e: round(e.y) > _tile_is_hovering[1], 0, -1)
                # 移除列
                elif self._modify_mode == self._MODIFY.DELETE_COLUMN:
                    self.get_map().remove_on_axis(_tile_is_hovering[0], 1)
                    self.delete_entity(lambda e: round(e.x) == _tile_is_hovering[0])
                    self.move_entity(lambda e: round(e.x) > _tile_is_hovering[0], -1, 0)
                elif self._modify_mode == self._MODIFY.ADD_ROW_ABOVE:
                    self.get_map().add_on_axis(_tile_is_hovering[1])
                    self.move_entity(lambda e: round(e.y) >= _tile_is_hovering[1], 0, 1)
                elif self._modify_mode == self._MODIFY.ADD_ROW_BELOW:
                    self.get_map().add_on_axis(_tile_is_hovering[1] + 1)
                    self.move_entity(lambda e: round(e.y) >= _tile_is_hovering[1] + 1, 0, 1)
                elif self._modify_mode == self._MODIFY.ADD_COLUMN_BEFORE:
                    self.get_map().add_on_axis(_tile_is_hovering[0], 1)
                    self.move_entity(lambda e: round(e.x) >= _tile_is_hovering[0], 1, 0)
                elif self._modify_mode == self._MODIFY.ADD_COLUMN_AFTER:
                    self.get_map().add_on_axis(_tile_is_hovering[0] + 1, 1)
                    self.move_entity(lambda e: round(e.x) >= _tile_is_hovering[0] + 1, 1, 0)
                elif self._modify_mode == self._MODIFY.DISABLE:
                    if self.is_any_object_selected() is True and self._no_container_is_hovered is True:
                        if self.__object_to_put_down["type"] == "tile":
                            self.set_tile(self.__object_to_put_down["id"], self._tile_is_hovering)
                        elif self.__object_to_put_down["type"] == "decoration":
                            self.set_decoration(self.__object_to_put_down["id"], self._tile_is_hovering)
                        elif self.__object_to_put_down["type"] == "entity":
                            self.set_entity(self.__object_to_put_down["id"], self._tile_is_hovering)
                    else:
                        whether_add_history = False
                else:
                    EXCEPTION.fatal(f"Unknown modify mode {self._modify_mode}")
                # 保存修改后的历史
                if whether_add_history is True:
                    self.__append_level_history()
        # 如果鼠标右键
        elif (
            Controller.get_event("hard_confirm")
            and self.is_any_object_selected() is True
            and self._no_container_is_hovered is True
            and self._tile_is_hovering is not None
            and self.__buttons_container.item_being_hovered is None
        ):
            if self.__object_to_put_down["type"] == "tile":
                self.get_map().replace_tiles(self.get_map().get_tile(*self._tile_is_hovering), self.__object_to_put_down["id"])
                self.__append_level_history()
        # 取消选中
        elif Controller.get_event("back") or (self._no_container_is_hovered is True and Controller.get_event("scroll_up")):
            self.__object_to_put_down.clear()
            self._modify_mode = self._MODIFY.DISABLE
            self._show_barrier_mask = False
        # 直接用del按键
        elif Controller.get_event("delete"):
            any_deleted: bool = False
            for theEntities in self._entities_data.values():
                for e in tuple(theEntities.keys()):
                    if theEntities[e].get_selected():
                        theEntities.pop(e)
                        any_deleted = True
            if not any_deleted and self._tile_is_hovering is not None:
                self.delete_entity_on_tile(self._tile_is_hovering)

        # 画出地图
        self._display_map(_surface)

        # 画出右侧容器的UI
        self.__UIContainerButtonRight.draw(_surface)
        if self.__UIContainerButtonRight.right < _surface.get_width():
            self.__UIContainerRight.display(_surface, UIContainerRight_offset_pos)
            self.__envImgContainer.display(_surface, UIContainerRight_offset_pos)
            self.__decorationsImgContainer.display(_surface, UIContainerRight_offset_pos)
            self.__right_container_buttons.display(_surface, UIContainerRight_offset_pos)
            if Controller.get_event("confirm") is True:
                if self.__right_container_buttons.item_being_hovered == "select_tile":
                    self.__envImgContainer.set_visible(True)
                    self.__decorationsImgContainer.set_visible(False)
                elif self.__right_container_buttons.item_being_hovered == "select_decoration":
                    self.__envImgContainer.set_visible(False)
                    self.__decorationsImgContainer.set_visible(True)
                else:
                    if self.__envImgContainer.is_visible() and self.__envImgContainer.item_being_hovered is not None:
                        self.__object_to_put_down = {"type": "tile", "id": self.__envImgContainer.item_being_hovered}
                    elif self.__decorationsImgContainer.is_visible() and self.__decorationsImgContainer.item_being_hovered is not None:
                        self.__object_to_put_down = {"type": "decoration", "id": self.__decorationsImgContainer.item_being_hovered}

        # 画出下方容器的UI
        self.__UIContainerButtonBottom.draw(_surface)
        if self.__UIContainerButtonBottom.bottom < _surface.get_height():
            self.__UIContainerBottom.display(_surface, UIContainerBottom_offset_pos)
            if self.__entitiesImagesContainerUsingIndex >= 0:
                self.__entitiesImagesContainers[self.__entitiesImagesContainerUsingIndex].display(_surface, UIContainerBottom_offset_pos)
            self.__bottom_container_buttons.display(_surface, UIContainerBottom_offset_pos)
            if Controller.get_event("confirm"):
                if self.__bottom_container_buttons.item_being_hovered >= 0:
                    self.__entitiesImagesContainerUsingIndex = self.__bottom_container_buttons.item_being_hovered
                elif (
                    self.__entitiesImagesContainerUsingIndex >= 0
                    and self.__entitiesImagesContainers[self.__entitiesImagesContainerUsingIndex].item_being_hovered is not None
                ):
                    self.__object_to_put_down = {
                        "type": "entity",
                        "container_id": self.__entitiesImagesContainerUsingIndex,
                        "id": self.__entitiesImagesContainers[self.__entitiesImagesContainerUsingIndex].item_being_hovered,
                    }

        # 画出选中框
        if self._no_container_is_hovered is True and Controller.mouse.get_pressed_since(0):
            if len(self._select_pos) <= 0:
                self._select_pos = Controller.mouse.get_pos()
            # 设置宽度
            new_width: int = Controller.mouse.x - self._select_pos[0]
            self._select_rect.set_width(abs(new_width))
            self._select_rect.set_left(self._select_pos[0] if new_width >= 0 else Controller.mouse.x)
            # 设置高度
            new_height: int = Controller.mouse.y - self._select_pos[1]
            self._select_rect.set_height(abs(new_height))
            self._select_rect.set_top(self._select_pos[1] if new_height >= 0 else Controller.mouse.y)
            # 将选中框画到屏幕上
            self._select_rect.draw_outline(_surface)
        else:
            self._select_pos = tuple()

        # 画出上方按钮
        self.__buttons_container.draw(_surface)
        if Controller.get_event("confirm") and len(self.__object_to_put_down) <= 0:
            show_barrier_mask: bool = False
            if self.__buttons_container.item_being_hovered is not None:
                self._modify_mode = self._MODIFY.DISABLE
            if self.__buttons_container.item_being_hovered == "save":
                self._save()
            elif self.__buttons_container.item_being_hovered == "back":
                if Config.load(self.get_data_file_path()) == self._get_data_need_to_save():
                    self.stop()
                else:
                    self.__no_save_warning.set_visible(True)
            elif self.__buttons_container.item_being_hovered == "delete_entity":
                self.__object_to_put_down.clear()
                self._modify_mode = self._MODIFY.DELETE_ENTITY
            elif self.__buttons_container.item_being_hovered == "reload":
                self.__load_level(Config.load_file(self.get_data_file_path()))
                self.__reset_level_history()
            elif self.__buttons_container.item_being_hovered == "undo":
                if self.__current_level_data_index > 0:
                    self.__current_level_data_index -= 1
                    self.__load_level(self.__level_data_history[self.__current_level_data_index])
            elif self.__buttons_container.item_being_hovered == "redo":
                if self.__current_level_data_index < len(self.__level_data_history) - 1:
                    self.__current_level_data_index += 1
                    self.__load_level(self.__level_data_history[self.__current_level_data_index])
            elif self.__buttons_container.item_being_hovered == "add_colum_before":
                self._modify_mode = self._MODIFY.ADD_COLUMN_BEFORE
            elif self.__buttons_container.item_being_hovered == "add_colum_after":
                self._modify_mode = self._MODIFY.ADD_COLUMN_AFTER
            elif self.__buttons_container.item_being_hovered == "add_row_above":
                self._modify_mode = self._MODIFY.ADD_ROW_ABOVE
            elif self.__buttons_container.item_being_hovered == "add_row_below":
                self._modify_mode = self._MODIFY.ADD_ROW_BELOW
            elif self.__buttons_container.item_being_hovered == "delete_row":
                self._modify_mode = self._MODIFY.DELETE_ROW
            elif self.__buttons_container.item_being_hovered == "delete_colum":
                self._modify_mode = self._MODIFY.DELETE_COLUMN
            elif self.__buttons_container.item_being_hovered == "auto_add_barriers":
                # 历遍地图，设置障碍区块
                for _x in range(self.get_map().column):
                    for _y in range(self.get_map().row):
                        if not self.get_map().is_passable(_x, _y, True):
                            self.get_map().set_barrier_mask(_x, _y, 1)
                self.__append_level_history()
            elif self.__buttons_container.item_being_hovered == "add_barrier":
                show_barrier_mask = True
            else:
                show_barrier_mask = self._show_barrier_mask
                if self._show_barrier_mask is True and self._tile_is_hovering is not None:
                    self.get_map().set_barrier_mask(self._tile_is_hovering[0], self._tile_is_hovering[1], 1)
                    self.__append_level_history()
            self._show_barrier_mask = show_barrier_mask

        # 跟随鼠标显示即将被放下的物品
        if self.is_any_object_selected() is True:
            if self.__object_to_put_down["type"] == "tile":
                _surface.blit(self.__envImgContainer.get(str(self.__object_to_put_down["id"])), Controller.mouse.get_pos())
            elif self.__object_to_put_down["type"] == "decoration":
                _surface.blit(self.__decorationsImgContainer.get(str(self.__object_to_put_down["id"])), Controller.mouse.get_pos())
            elif self.__object_to_put_down["type"] == "entity":
                _surface.blit(
                    self.__entitiesImagesContainers[int(self.__object_to_put_down["container_id"])].get(self.__object_to_put_down["id"]),
                    Controller.mouse.get_pos(),
                )

        # 未保存离开时的警告
        self.__no_save_warning.draw(_surface)
        if Controller.get_event("confirm"):
            # 保存并离开
            if self.__no_save_warning.item_being_hovered == "save":
                self._save()
                self.stop()
            # 取消
            elif self.__no_save_warning.item_being_hovered == "cancel":
                self.__no_save_warning.set_visible(False)
            # 不保存并离开
            elif self.__no_save_warning.item_being_hovered == "dont_save":
                self.stop()

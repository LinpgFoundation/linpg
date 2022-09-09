from .battle import *


# 地图编辑器系统
class AbstractMapEditor(AbstractBattleSystem, metaclass=ABCMeta):
    def __init__(self) -> None:
        # 初始化父类
        super().__init__()
        # 初始化ui
        self.__buttons_container: GameObjectsDictContainer = UI.generate_container("map_editor_buttons")
        self.__right_container_buttons: GameObjectsDictContainer = UI.generate_container("map_editor_right_container_buttons")
        self.__UIContainerRight: DynamicImage = DynamicImage("<&ui>container.png", 0, 0)
        self.__UIContainerRight.rotate(90)
        self.__UIContainerBottom: DynamicImage = DynamicImage("<&ui>container.png", 0, 0)
        self.__bottom_container_buttons: GameObjectsListContainer = GameObjectsListContainer(None, 0, 0, 0, 0)
        self.__entitiesImagesContainers: list = []
        self.__entitiesImagesContainerUsingIndex: int = -1
        self.__envImgContainer: SurfaceContainerWithScrollBar = SurfaceContainerWithScrollBar(None, 0, 0, 0, 0, Axis.VERTICAL)
        self.__decorationsImgContainer: SurfaceContainerWithScrollBar = SurfaceContainerWithScrollBar(None, 0, 0, 0, 0, Axis.VERTICAL)
        # 用于储存即将发下的物品的具体参数
        self.__object_to_put_down: dict = {}
        # 未保存离开时的警告
        self.__no_save_warning: GameObjectsDictContainer = UI.generate_container("leave_without_saving_warning")
        # 绿色方块/方块标准
        self.__range_green: ImageSurface = Surfaces.NULL
        self.__range_red: ImageSurface = Surfaces.NULL
        # 选中框
        self.__select_rect: Rectangle = Rectangle(0, 0, 0, 0)
        self.__select_pos: tuple = tuple()
        # 是否是delete模式
        self.__delete_mode: bool = False
        # 是否有ui容器被鼠标触碰
        self.__no_container_is_hovered: bool = False

    # 根据数据更新特定的角色 - 子类需实现
    @abstractmethod
    def update_entity(self, faction: str, key: str, data: dict) -> None:
        EXCEPTION.fatal("update_entity()", 1)

    # 实现父类需要实现的方法 - 画出所有角色
    def _display_entities(self, _surface: ImageSurface) -> None:
        # 展示范围
        if self._block_is_hovering is not None and self.__no_container_is_hovered is True:
            if self.__delete_mode is True:
                xTemp, yTemp = self._MAP.calculate_position(self._block_is_hovering[0], self._block_is_hovering[1])
                _surface.blit(self.__range_red, (xTemp + self._MAP.block_width // 10, yTemp))
            elif len(self.__object_to_put_down) > 0:
                xTemp, yTemp = self._MAP.calculate_position(self._block_is_hovering[0], self._block_is_hovering[1])
                _surface.blit(self.__range_green, (xTemp + self._MAP.block_width // 10, yTemp))
        # 角色动画
        for faction in self._entities_data:
            for value in self._entities_data[faction].values():
                value.draw(_surface, self._MAP)
                if len(self.__select_pos) > 0:
                    value.set_selected(value.is_overlapped_with(self.__select_rect))

    # 修改父类的 _check_key_down 方法
    def _check_key_down(self, event: PG_Event) -> None:
        super()._check_key_down(event)
        if event.key == Keys.ESCAPE:
            self.__object_to_put_down.clear()
            self.__delete_mode = False

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return Config.load_file(self.get_map_file_location()) | super()._get_data_need_to_save()

    # 移除在给定坐标上的角色
    def remove_entity_on_pos(self, target_pos: tuple[int, int]) -> None:
        for faction in self._entities_data.keys():
            for key in self._entities_data[faction].keys():
                if Coordinates.is_same(self._entities_data[faction][key], target_pos):
                    self._entities_data[faction].pop(key)
                    break

    # 处理关键数据
    def _process_data(self, _data: dict, _mode: str = "dev") -> None:
        # 确保地图初始化
        _map_p: Optional[list] = _data.get("map")
        if _map_p is None or len(_map_p) == 0:
            lookup_table: list[str] = ["TileSnow01", "TileSnow01ToStone01", "TileSnow01ToStone02", "TileSnow02", "TileSnow02ToStone01", "TileSnow02ToStone02"]
            block_y: int = 50
            block_x: int = 50
            _data["map"] = {
                "array2d": [[Numbers.get_random_int(0, len(lookup_table) - 1) for _ in range(block_x)] for _ in range(block_y)],
                "lookup_table": lookup_table,
            }
        # 开始处理数据
        super()._process_data(_data, _mode)

    # 初始化
    def load(self, _surface: ImageSurface, chapterType: str, chapterId: int, projectName: Optional[str] = None) -> None:
        self._initialize(chapterType, chapterId, projectName)
        self.folder_for_save_file, self.name_for_save_file = os.path.split(self.get_map_file_location())
        self._process_data(Config.load(self.get_map_file_location()))
        """加载右侧的界面"""
        # 加载容器图片
        container_width: int = _surface.get_width() // 5
        container_height: int = _surface.get_height()
        button_width: int = _surface.get_width() // 25
        button_height: int = _surface.get_height() // 5
        padding: int = _surface.get_height() // 100
        self.__right_container_buttons.get("select_block").set_left(
            (
                container_width
                - self.__right_container_buttons.get("select_block").get_width()
                - self.__right_container_buttons.get("select_decoration").get_width()
                - padding
            )
            // 2
        )
        self.__right_container_buttons.get("select_decoration").set_left(self.__right_container_buttons.get("select_block").right + padding)
        self.__UIContainerRight.set_size(container_width, container_height)
        self.__UIContainerButtonRight = MovableImage(
            "<&ui>container_button.png",
            _surface.get_width() - button_width,
            (_surface.get_height() - button_height) // 2,
            _surface.get_width() - button_width - container_width,
            (_surface.get_height() - button_height) // 2,
            container_width // 10,
            0,
            button_width,
            button_height,
        )
        self.__UIContainerButtonRight.rotate(90)
        # 加载背景图片
        self.__envImgContainer.set_pos(container_width * 3 // 40, _surface.get_height() // 10)
        self.__envImgContainer.set_size(container_width * 17 // 20, _surface.get_height() * 17 // 20)
        if TileMapImagesModule.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET is None:
            EXCEPTION.fatal("Image sprite sheet for tile map is not loaded correctly!")
        for key, value in TileMapImagesModule.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET.to_dict().items():
            self.__envImgContainer.set(key, Images.resize(value, (self._MAP.block_width / 3, None)))
        self.__envImgContainer.set_item_per_line(4)
        self.__envImgContainer.set_scroll_bar_pos("right")
        self.__envImgContainer.set_visible(True)
        self.__envImgContainer.distance_between_item = padding
        # 加载所有的装饰品
        self.__decorationsImgContainer.set_pos(container_width * 3 // 40, _surface.get_height() // 10)
        self.__decorationsImgContainer.set_size(container_width * 17 // 20, _surface.get_height() * 17 // 20)
        # 加载默认装饰物
        if DecorationImagesModule.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET is None:
            EXCEPTION.fatal("Image sprite sheet for default decorations is not loaded correctly!")
        for key, value in DecorationImagesModule.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET.to_dict().items():
            self.__decorationsImgContainer.set(key, Images.resize(value if not isinstance(value, tuple) else value[0], (self._MAP.block_width / 3, None)))
        # 加载自带的装饰物
        if DecorationImagesModule.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET is None:
            EXCEPTION.fatal("Image sprite sheet for custom decorations is not loaded correctly!")
        for key, value in DecorationImagesModule.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET.to_dict().items():
            self.__decorationsImgContainer.set(key, Images.resize(value if not isinstance(value, tuple) else value[0], (self._MAP.block_width / 3, None)))
        # 设置容器参数
        self.__decorationsImgContainer.set_item_per_line(4)
        self.__decorationsImgContainer.set_scroll_bar_pos("right")
        self.__decorationsImgContainer.set_visible(False)
        self.__decorationsImgContainer.distance_between_item = padding
        """加载下方的界面"""
        container_width = _surface.get_width() * 4 // 5
        container_height = _surface.get_height() * 3 // 10
        button_width = _surface.get_width() * 7 // 50
        button_height = _surface.get_height() // 20
        self.__UIContainerBottom.set_size(container_width, container_height)
        self.__UIContainerButtonBottom = MovableImage(
            "<&ui>container_button.png",
            (container_width - button_width) // 2,
            _surface.get_height() - button_height,
            (container_width - button_width) // 2,
            _surface.get_height() - button_height - container_height,
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
                        EntitySpriteImageManager.try_get_images(faction, img_name, "wait").get_image(0).get_image_copy(), (None, container_height // 3)
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
        # 绿色方块/方块标准
        self.__range_green = Images.load("<&ui>range_green.png", (self._MAP.block_width * 4 // 5, None))
        self.__range_green.set_alpha(150)
        self.__range_red = Images.load("<&ui>range_red.png", (self._MAP.block_width * 4 // 5, None))
        self.__range_red.set_alpha(150)
        self.__object_to_put_down.clear()
        # 设置按钮位置
        self.__buttons_container.get("back").set_left(self.__buttons_container.get("save").get_right() + padding)
        self.__buttons_container.get("delete").set_left(self.__buttons_container.get("back").get_right() + padding)
        self.__buttons_container.get("reload").set_left(self.__buttons_container.get("delete").get_right() + padding)

    # 将地图制作器的界面画到屏幕上
    def draw(self, _surface: ImageSurface) -> None:
        UIContainerRight_offset_pos: tuple[int, int] = (self.__UIContainerButtonRight.right, 0)
        UIContainerBottom_offset_pos: tuple[int, int] = (0, self.__UIContainerButtonBottom.bottom)
        self.__no_container_is_hovered = not self.__UIContainerRight.is_hovered(UIContainerRight_offset_pos) and not self.__UIContainerBottom.is_hovered(
            UIContainerBottom_offset_pos
        )
        # 如果鼠标与任何Container进行了互动
        if Controller.get_event("confirm") and len(self.__select_pos) <= 0:
            # 显示或隐藏右侧的容器
            if self.__UIContainerButtonRight.is_hovered():
                self.__UIContainerButtonRight.switch()
                self.__UIContainerButtonRight.flip(True)
            # 显示或隐藏下侧的容器
            elif self.__UIContainerButtonBottom.is_hovered():
                self.__UIContainerButtonBottom.switch()
                self.__UIContainerButtonBottom.flip(False, True)
            elif self._block_is_hovering is not None:
                if self.__delete_mode is True:
                    # 查看当前位置是否有装饰物
                    decoration: Optional[DecorationObject] = self._MAP.find_decoration_on(self._block_is_hovering)
                    # 如果发现有冲突的装饰物
                    if decoration is not None:
                        self._MAP.remove_decoration(decoration)
                    else:
                        self.remove_entity_on_pos(self._block_is_hovering)
                elif len(self.__object_to_put_down) > 0 and self.__no_container_is_hovered is True:
                    if self.__object_to_put_down["type"] == "block":
                        self._MAP.set_block(*self._block_is_hovering, self.__object_to_put_down["id"])
                    elif self.__object_to_put_down["type"] == "decoration":
                        # 查看当前位置是否有装饰物
                        decoration = self._MAP.find_decoration_on(self._block_is_hovering)
                        # 如果发现有冲突的装饰物
                        if decoration is not None:
                            self._MAP.remove_decoration(decoration)
                        self._MAP.add_decoration(
                            {"image": self.__object_to_put_down["id"], "x": self._block_is_hovering[0], "y": self._block_is_hovering[1]},
                            DataBase.get("Decorations", self.__object_to_put_down["id"]),
                            "{0}_{1}".format(self.__object_to_put_down["id"], self._MAP.count_decorations()),
                        )
                    elif self.__object_to_put_down["type"] == "entity":
                        # 移除坐标冲突的角色
                        self.remove_entity_on_pos(self._block_is_hovering)
                        # 生成需要更新的数据
                        _new_data: dict = copy.deepcopy(Entity.get_entity_data(self.__object_to_put_down["id"]))
                        _new_data.update({"x": self._block_is_hovering[0], "y": self._block_is_hovering[1], "type": self.__object_to_put_down["id"]})
                        the_id: int = 0
                        nameTemp: str = self.__object_to_put_down["id"] + "_" + str(the_id)
                        while nameTemp in self._entities_data[_new_data["faction"]]:
                            the_id += 1
                            nameTemp = self.__object_to_put_down["id"] + "_" + str(the_id)
                        self.update_entity(_new_data["faction"], nameTemp, _new_data)

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
                if self.__right_container_buttons.item_being_hovered == "select_block":
                    self.__envImgContainer.set_visible(True)
                    self.__decorationsImgContainer.set_visible(False)
                elif self.__right_container_buttons.item_being_hovered == "select_decoration":
                    self.__envImgContainer.set_visible(False)
                    self.__decorationsImgContainer.set_visible(True)
            if Controller.get_event("confirm") is True:
                if self.__envImgContainer.is_visible() and self.__envImgContainer.item_being_hovered is not None:
                    self.__object_to_put_down = {"type": "block", "id": self.__envImgContainer.item_being_hovered}
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
        if self.__no_container_is_hovered is True and Controller.mouse.get_pressed_since(0):
            if len(self.__select_pos) <= 0:
                self.__select_pos = Controller.mouse.get_pos()
            # 设置宽度
            new_width: int = Controller.mouse.x - self.__select_pos[0]
            self.__select_rect.set_width(abs(new_width))
            self.__select_rect.set_left(self.__select_pos[0] if new_width >= 0 else Controller.mouse.x)
            # 设置高度
            new_height: int = Controller.mouse.y - self.__select_pos[1]
            self.__select_rect.set_height(abs(new_height))
            self.__select_rect.set_top(self.__select_pos[1] if new_height >= 0 else Controller.mouse.y)
            # 将选中框画到屏幕上
            self.__select_rect.draw_outline(_surface)
        else:
            self.__select_pos = tuple()

        # 画出上方按钮
        self.__buttons_container.draw(_surface)
        if Controller.get_event("confirm") and len(self.__object_to_put_down) <= 0 and not self.__delete_mode:
            if self.__buttons_container.item_being_hovered is None:
                pass
            elif self.__buttons_container.item_being_hovered == "save":
                self.save_progress()
            elif self.__buttons_container.item_being_hovered == "back":
                if Config.load(self.get_map_file_location()) == self._get_data_need_to_save():
                    self.stop()
                else:
                    self.__no_save_warning.set_visible(True)
            elif self.__buttons_container.item_being_hovered == "delete":
                self.__object_to_put_down.clear()
                self.__delete_mode = True
            elif self.__buttons_container.item_being_hovered == "reload":
                tempLocal_x, tempLocal_y = self._MAP.get_local_pos()
                self._process_data(Config.load(self.get_map_file_location()))
                self._MAP.set_local_pos(tempLocal_x, tempLocal_y)

        # 跟随鼠标显示即将被放下的物品
        if len(self.__object_to_put_down) > 0:
            if self.__object_to_put_down["type"] == "block":
                _surface.blit(self.__envImgContainer.get(self.__object_to_put_down["id"]), Controller.mouse.get_pos())
            elif self.__object_to_put_down["type"] == "decoration":
                _surface.blit(self.__decorationsImgContainer.get(self.__object_to_put_down["id"]), Controller.mouse.get_pos())
            elif self.__object_to_put_down["type"] == "entity":
                _surface.blit(
                    self.__entitiesImagesContainers[self.__object_to_put_down["container_id"]].get(self.__object_to_put_down["id"]), Controller.mouse.get_pos()
                )

        # 未保存离开时的警告
        self.__no_save_warning.draw(_surface)
        if Controller.get_event("confirm") and self.__no_save_warning.item_being_hovered is not None:
            # 保存并离开
            if self.__no_save_warning.item_being_hovered == "save":
                self.save_progress()
                self.stop()
            # 取消
            elif self.__no_save_warning.item_being_hovered == "cancel":
                self.__no_save_warning.set_visible(False)
            # 不保存并离开
            elif self.__no_save_warning.item_being_hovered == "dont_save":
                self.stop()

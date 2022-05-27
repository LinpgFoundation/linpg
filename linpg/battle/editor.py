from .battle import *

# 地图编辑器系统
class AbstractMapEditor(AbstractBattleSystem):
    def __init__(self) -> None:
        # 初始化父类
        super().__init__()
        self.__buttons_container: GameObjectsDictContainer = UI.generate_container("map_editor_buttons")
        self.__right_container_buttons: GameObjectsDictContainer = UI.generate_container("map_editor_right_container_buttons")
        self.__UIContainerRight: DynamicImage = DynamicImage("<&ui>container.png", 0, 0)
        self.__UIContainerRight.rotate(90)
        self.__bottom_container_buttons: GameObjectsListContainer = GameObjectsListContainer(None, 0, 0, 0, 0)
        self.__entitiesImagesContainers: list = []
        self.__entitiesImagesContainerUsingIndex: int = -1
        self.__envImgContainer: SurfaceContainerWithScrollbar = SurfaceContainerWithScrollbar(None, 0, 0, 0, 0, "vertical")
        self.__decorationsImgContainer: SurfaceContainerWithScrollbar = SurfaceContainerWithScrollbar(
            None, 0, 0, 0, 0, "vertical"
        )
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

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return Config.load_file(self.get_map_file_location()) | super()._get_data_need_to_save()

    # 加载角色的数据
    def _load_characters_data(self, alliances: dict, enemies: dict) -> None:
        EXCEPTION.fatal("_load_characters_data()", 1)

    # 初始化
    def load(self, screen: ImageSurface, chapterType: str, chapterId: int, projectName: Optional[str] = None) -> None:
        self._initialize(chapterType, chapterId, projectName)
        self.folder_for_save_file, self.name_for_save_file = os.path.split(self.get_map_file_location())
        # 载入地图数据
        mapFileData: dict = Config.load(self.get_map_file_location())
        # 初始化角色信息
        self._load_characters_data(mapFileData["alliances"], mapFileData["enemies"])
        # 初始化地图
        if "map" not in mapFileData or mapFileData["map"] is None or len(mapFileData["map"]) == 0:
            SnowEnvImg = [
                "TileSnow01",
                "TileSnow01ToStone01",
                "TileSnow01ToStone02",
                "TileSnow02",
                "TileSnow02ToStone01",
                "TileSnow02ToStone02",
            ]
            block_y = 50
            block_x = 50
            default_map = [[SnowEnvImg[get_random_int(0, 5)] for a in range(block_x)] for i in range(block_y)]
            mapFileData["map"] = default_map
            Config.save(self.get_map_file_location(), mapFileData)
        # 加载地图
        self._initialize_map(mapFileData)
        del mapFileData
        """加载右侧的界面"""
        # 加载容器图片
        container_width: int = screen.get_width() // 5
        container_height: int = screen.get_height()
        button_width: int = screen.get_width() // 25
        button_height: int = screen.get_height() // 5
        panding: int = screen.get_height() // 100
        self.__right_container_buttons.get("select_block").set_left(
            (
                container_width
                - self.__right_container_buttons.get("select_block").get_width()
                - self.__right_container_buttons.get("select_decoration").get_width()
                - panding
            )
            // 2
        )
        self.__right_container_buttons.get("select_decoration").set_left(
            self.__right_container_buttons.get("select_block").right + panding
        )
        self.__UIContainerRight.set_size(container_width, container_height)
        self.__UIContainerButtonRight = MovableImage(
            "<&ui>container_button.png",
            screen.get_width() - button_width,
            (screen.get_height() - button_height) // 2,
            screen.get_width() - button_width - container_width,
            (screen.get_height() - button_height) // 2,
            container_width // 10,
            0,
            button_width,
            button_height,
        )
        self.__UIContainerButtonRight.rotate(90)
        # 加载背景图片
        self.__envImgContainer.set_pos(container_width * 3 // 40, screen.get_height() // 10)
        self.__envImgContainer.set_size(container_width * 17 // 20, screen.get_height() * 17 // 20)
        if TileMapImagesModule.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET is None:
            EXCEPTION.fatal("Image sprite sheet for tile map is not loaded correctly!")
        for key, value in TileMapImagesModule.DEFAULT_TILE_MAP_IMAGE_SPRITE_SHEET.to_dict().items():
            self.__envImgContainer.set(key, Images.resize(value, (self._MAP.block_width / 3, None)))
        self.__envImgContainer.set_item_per_line(4)
        self.__envImgContainer.set_scroll_bar_pos("right")
        self.__envImgContainer.set_visible(True)
        self.__envImgContainer.distance_between_item = panding
        # 加载所有的装饰品
        self.__decorationsImgContainer.set_pos(container_width * 3 // 40, screen.get_height() // 10)
        self.__decorationsImgContainer.set_size(container_width * 17 // 20, screen.get_height() * 17 // 20)
        # 加载默认装饰物
        if DecorationImagesModule.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET is None:
            EXCEPTION.fatal("Image sprite sheet for default decorations is not loaded correctly!")
        for key, value in DecorationImagesModule.DEFAULT_DECORATION_IMAGE_SPRITE_SHEET.to_dict().items():
            self.__decorationsImgContainer.set(
                key, Images.resize(value if not isinstance(value, tuple) else value[0], (self._MAP.block_width / 3, None))
            )
        # 加载自带的装饰物
        if DecorationImagesModule.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET is None:
            EXCEPTION.fatal("Image sprite sheet for custom decorations is not loaded correctly!")
        for key, value in DecorationImagesModule.CUSTOM_DECORATION_IMAGE_SPRITE_SHEET.to_dict().items():
            self.__decorationsImgContainer.set(
                key, Images.resize(value if not isinstance(value, tuple) else value[0], (self._MAP.block_width / 3, None))
            )
        # 设置容器参数
        self.__decorationsImgContainer.set_item_per_line(4)
        self.__decorationsImgContainer.set_scroll_bar_pos("right")
        self.__decorationsImgContainer.set_visible(False)
        self.__decorationsImgContainer.distance_between_item = panding
        """加载下方的界面"""
        container_width = screen.get_width() * 4 // 5
        container_height = screen.get_height() * 3 // 10
        button_width = screen.get_width() * 7 // 50
        button_height = screen.get_height() // 20
        self.__UIContainerBottom = DynamicImage("<&ui>container.png", 0, 0, container_width, container_height)
        self.__UIContainerButtonBottom = MovableImage(
            "<&ui>container_button.png",
            (container_width - button_width) // 2,
            screen.get_height() - button_height,
            (container_width - button_width) // 2,
            screen.get_height() - button_height - container_height,
            0,
            container_height // 10,
            button_width,
            button_height,
        )
        # 加载所有角色的图片文件
        for faction in os.listdir(EntitySpriteImageManager.SPRITES_PATH):
            newContainer: SurfaceContainerWithScrollbar = SurfaceContainerWithScrollbar(
                None,
                container_width // 40,
                container_height * 3 // 10,
                container_width * 19 // 20,
                container_height * 3 // 5,
                "horizontal",
                faction,
            )
            for img_name in os.listdir(os.path.join(EntitySpriteImageManager.SPRITES_PATH, faction)):
                newContainer.set(
                    img_name,
                    Images.smoothly_resize(
                        EntitySpriteImageManager.try_get_images(faction, img_name, "wait").get_image(0).get_image_copy(),
                        (None, container_height // 3),
                    ),
                )
            newContainer.set_scroll_bar_pos("bottom")
            newContainer.distance_between_item = panding
            self.__entitiesImagesContainers.append(newContainer)
            newButton: Button = Button.load("<&ui>button.png", (0, 0), (0, 0), 100)
            newButton.set_text(
                ButtonComponent.text(
                    Lang.get_text("General", faction), button_height // 2, Colors.BLACK, alpha_when_not_hover=100
                )
            )
            newButton.set_auto_resize(True)
            if len(self.__bottom_container_buttons) > 0:
                newButton.set_left(self.__bottom_container_buttons[len(self.__bottom_container_buttons) - 1].right + panding)
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
        self.__buttons_container.get("back").set_left(self.__buttons_container.get("save").get_right() + panding)
        self.__buttons_container.get("delete").set_left(self.__buttons_container.get("back").get_right() + panding)
        self.__buttons_container.get("reload").set_left(self.__buttons_container.get("delete").get_right() + panding)
        # 用于储存即将发下的物品的具体参数
        self.data_to_edit = None

    # 将地图制作器的界面画到屏幕上
    def draw(self, screen: ImageSurface) -> None:
        block_get_click = self._MAP.calculate_coordinate()
        for event in Controller.events:
            if event.type == Key.DOWN:
                if event.key == Key.ESCAPE:
                    self.__object_to_put_down.clear()
                    self.data_to_edit = None
                    self.__delete_mode = False
                self._check_key_down(event)
            elif event.type == Key.UP:
                self._check_key_up(event)
        if Controller.get_event("confirm") and len(self.__select_pos) <= 0:
            # 显示或隐藏右侧的容器
            if self.__UIContainerButtonRight.is_hovered():
                self.__UIContainerButtonRight.switch()
                self.__UIContainerButtonRight.flip(True)
            # 显示或隐藏下侧的容器
            elif self.__UIContainerButtonBottom.is_hovered():
                self.__UIContainerButtonBottom.switch()
                self.__UIContainerButtonBottom.flip(False, True)
            elif block_get_click is not None:
                if self.__delete_mode is True:
                    # 查看当前位置是否有装饰物
                    decoration: Optional[DecorationObject] = self._MAP.find_decoration_on(
                        (block_get_click["x"], block_get_click["y"])
                    )
                    # 如果发现有冲突的装饰物
                    if decoration is not None:
                        self._MAP.remove_decoration(decoration)
                    else:
                        decoration_collided: Optional[str] = None
                        for key, value in {
                            **self._alliances_data,
                            **self._enemies_data,
                        }.items():
                            if value.x == block_get_click["x"] and value.y == block_get_click["y"]:
                                decoration_collided = key
                                break
                        if decoration_collided is not None:
                            if decoration_collided in self._alliances_data:
                                self._alliances_data.pop(decoration_collided)
                            elif decoration_collided in self._enemies_data:
                                self._enemies_data.pop(decoration_collided)
                elif (
                    len(self.__object_to_put_down) > 0
                    and not self.__UIContainerRight.is_hovered((self.__UIContainerButtonRight.right, 0))
                    and not self.__UIContainerBottom.is_hovered((0, self.__UIContainerButtonBottom.bottom))
                ):
                    if self.__object_to_put_down["type"] == "block":
                        self._MAP.update_block(block_get_click, self.__object_to_put_down["id"])
                    elif self.__object_to_put_down["type"] == "decoration":
                        # 查看当前位置是否有装饰物
                        decoration = self._MAP.find_decoration_on((block_get_click["x"], block_get_click["y"]))
                        # 如果发现有冲突的装饰物
                        if decoration is not None:
                            self._MAP.remove_decoration(decoration)
                        self._MAP.add_decoration(
                            {"image": self.__object_to_put_down["id"], "x": block_get_click["x"], "y": block_get_click["y"]},
                            DataBase.get("Decorations")[self.__object_to_put_down["id"]],
                            "{0}_{1}".format(self.__object_to_put_down["id"], self._MAP.count_decorations()),
                        )
                    elif self.__object_to_put_down["type"] == "entity":
                        # 移除坐标冲突的角色
                        character_collided: Optional[str] = None
                        for key in self._alliances_data:
                            if Coordinates.is_same(self._alliances_data[key], block_get_click):
                                character_collided = key
                                break
                        if character_collided is None:
                            for key in self._enemies_data:
                                if Coordinates.is_same(self._enemies_data[key], block_get_click):
                                    character_collided = key
                                    break
                            if character_collided is not None:
                                self._enemies_data.pop(character_collided)
                        else:
                            self._alliances_data.pop(character_collided)
                        the_id: int = 0
                        _new_data: dict = deepcopy(Entity.get_enity_data(self.__object_to_put_down["id"]))
                        if _new_data["faction"] in DataBase.get("Faction", "alliances"):
                            while self.__object_to_put_down["id"] + "_" + str(the_id) in self._alliances_data:
                                the_id += 1
                            nameTemp = self.__object_to_put_down["id"] + "_" + str(the_id)
                            self._alliances_data[nameTemp] = FriendlyCharacter(
                                _new_data
                                | {
                                    "x": block_get_click["x"],
                                    "y": block_get_click["y"],
                                    "type": self.__object_to_put_down["id"],
                                    "bullets_carried": 100,
                                },
                                "dev",
                            )
                        else:
                            while self.__object_to_put_down["id"] + "_" + str(the_id) in self._enemies_data:
                                the_id += 1
                            nameTemp = self.__object_to_put_down["id"] + "_" + str(the_id)
                            self._enemies_data[nameTemp] = HostileCharacter(
                                _new_data
                                | {
                                    "x": block_get_click["x"],
                                    "y": block_get_click["y"],
                                    "type": self.__object_to_put_down["id"],
                                    "bullets_carried": 100,
                                },
                                "dev",
                            )
        # 其他移动的检查
        self._check_right_click_move()
        self._check_jostick_events()

        # 画出地图
        self._display_map(screen)
        if (
            block_get_click is not None
            and not self.__UIContainerRight.is_hovered((self.__UIContainerButtonRight.right, 0))
            and not self.__UIContainerBottom.is_hovered((0, self.__UIContainerButtonBottom.bottom))
        ):
            if self.__delete_mode is True:
                xTemp, yTemp = self._MAP.calculate_position(block_get_click["x"], block_get_click["y"])
                screen.blit(self.__range_red, (xTemp + self._MAP.block_width // 10, yTemp))
            elif len(self.__object_to_put_down) > 0:
                xTemp, yTemp = self._MAP.calculate_position(block_get_click["x"], block_get_click["y"])
                screen.blit(self.__range_green, (xTemp + self._MAP.block_width // 10, yTemp))

        # 角色动画
        for value in self._alliances_data.values():
            value.draw(screen, self._MAP)
            if len(self.__select_pos) > 0:
                value.set_selected(value.is_overlapped_with(self.__select_rect))
            elif len(self.__object_to_put_down) <= 0 and Controller.get_event("confirm") and value.is_hovered() is True:
                self.data_to_edit = value
        for value in self._enemies_data.values():
            value.draw(screen, self._MAP)
            if len(self.__select_pos) > 0:
                value.set_selected(value.is_overlapped_with(self.__select_rect))
            elif len(self.__object_to_put_down) <= 0 and Controller.get_event("confirm") and value.is_hovered() is True:
                self.data_to_edit = value

        # 展示设施
        self._display_decoration(screen)

        # 画出右侧容器的UI
        self.__UIContainerButtonRight.draw(screen)
        if self.__UIContainerButtonRight.right < screen.get_width():
            self.__UIContainerRight.display(screen, (self.__UIContainerButtonRight.right, 0))
            self.__envImgContainer.display(screen, (self.__UIContainerButtonRight.right, 0))
            self.__decorationsImgContainer.display(screen, (self.__UIContainerButtonRight.right, 0))
            self.__right_container_buttons.display(screen, (self.__UIContainerButtonRight.right, 0))
            if Controller.get_event("confirm") is True:
                if self.__right_container_buttons.item_being_hovered == "select_block":
                    self.__envImgContainer.set_visible(True)
                    self.__decorationsImgContainer.set_visible(False)
                elif self.__right_container_buttons.item_being_hovered == "select_decoration":
                    self.__envImgContainer.set_visible(False)
                    self.__decorationsImgContainer.set_visible(True)
            if Controller.get_event("confirm"):
                if self.__envImgContainer.is_visible() and self.__envImgContainer.item_being_hovered is not None:
                    self.__object_to_put_down = {"type": "block", "id": self.__envImgContainer.item_being_hovered}
                elif (
                    self.__decorationsImgContainer.is_visible() and self.__decorationsImgContainer.item_being_hovered is not None
                ):
                    self.__object_to_put_down = {"type": "decoration", "id": self.__decorationsImgContainer.item_being_hovered}
        # 画出下方容器的UI
        self.__UIContainerButtonBottom.draw(screen)
        if self.__UIContainerButtonBottom.bottom < screen.get_height():
            self.__UIContainerBottom.display(screen, (0, self.__UIContainerButtonBottom.bottom))
            if self.__entitiesImagesContainerUsingIndex >= 0:
                self.__entitiesImagesContainers[self.__entitiesImagesContainerUsingIndex].display(
                    screen, (0, self.__UIContainerButtonBottom.bottom)
                )
            self.__bottom_container_buttons.display(screen, (0, self.__UIContainerButtonBottom.bottom))
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
        if Controller.mouse.get_pressed(0) and Controller.mouse.get_pressed_previously(0):
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
            self.__select_rect.draw_outline(screen)
        else:
            self.__select_pos = tuple()

        # 画出上方按钮
        self.__buttons_container.draw(screen)
        if Controller.get_event("confirm") and len(self.__object_to_put_down) <= 0 and not self.__delete_mode:
            if self.__buttons_container.item_being_hovered == "save":
                self.save_progress()
            elif self.__buttons_container.item_being_hovered == "back":
                if Config.load(self.get_map_file_location()) == self._get_data_need_to_save():
                    self.stop()
                else:
                    self.__no_save_warning.set_visible(True)
            elif self.__buttons_container.item_being_hovered == "delete":
                self.__object_to_put_down.clear()
                self.data_to_edit = None
                self.__delete_mode = True
            elif self.__buttons_container.item_being_hovered == "reload":
                tempLocal_x, tempLocal_y = self._MAP.get_local_pos()
                # 读取地图数据
                mapFileData = Config.load(self.get_map_file_location())
                # 初始化角色信息
                self._load_characters_data(mapFileData["alliances"], mapFileData["enemies"])
                # 加载地图
                self._initialize_map(mapFileData)
                del mapFileData
                self._MAP.set_local_pos(tempLocal_x, tempLocal_y)

        # 跟随鼠标显示即将被放下的物品
        if len(self.__object_to_put_down) > 0:
            if self.__object_to_put_down["type"] == "block":
                screen.blit(self.__envImgContainer.get(self.__object_to_put_down["id"]), Controller.mouse.pos)
            elif self.__object_to_put_down["type"] == "decoration":
                screen.blit(self.__decorationsImgContainer.get(self.__object_to_put_down["id"]), Controller.mouse.pos)
            elif self.__object_to_put_down["type"] == "entity":
                screen.blit(
                    self.__entitiesImagesContainers[self.__object_to_put_down["container_id"]].get(
                        self.__object_to_put_down["id"]
                    ),
                    Controller.mouse.pos,
                )

        # 未保存离开时的警告
        self.__no_save_warning.draw(screen)
        if Controller.get_event("confirm") and self.__no_save_warning.item_being_hovered != "":
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

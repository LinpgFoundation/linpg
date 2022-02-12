from .battle import *

# 地图编辑器系统
class AbstractMapEditor(AbstractBattleSystem):
    def __init__(self) -> None:
        # 初始化父类
        super().__init__()
        self.__buttons_container: GameObjectsDictContainer = UI.generate_container("map_editor_buttons")
        self.__right_container_buttons: GameObjectsDictContainer = UI.generate_container("map_editor_right_container_buttons")
        self.__bottom_container_buttons: GameObjectsDictContainer = UI.generate_container("map_editor_bottom_container_buttons")
        self.__UIContainerRight: DynamicImage = DynamicImage("<!ui>container.png", 0, 0)
        self.__UIContainerRight.rotate(90)
        self.__hostileCharactersImagesContainer: SurfaceContainerWithScrollbar = SurfaceContainerWithScrollbar(
            None, 0, 0, 0, 0, "horizontal"
        )
        self.__friendlyCharactersImagesContainer: SurfaceContainerWithScrollbar = SurfaceContainerWithScrollbar(
            None, 0, 0, 0, 0, "horizontal"
        )
        self.__envImgContainer: SurfaceContainerWithScrollbar = SurfaceContainerWithScrollbar(None, 0, 0, 0, 0, "vertical")
        self.__decorationsImgContainer: SurfaceContainerWithScrollbar = SurfaceContainerWithScrollbar(
            None, 0, 0, 0, 0, "vertical"
        )
        self.__object_to_put_down: dict = {}
        # 未保存离开时的警告
        self.__no_save_warning: GameObjectsDictContainer = UI.generate_container("leave_without_saving_warning")
        # 绿色方块/方块标准
        self.__range_green: ImageSurface = NULL_SURFACE
        self.__range_red: ImageSurface = NULL_SURFACE
        # 是否是delete模式
        self.__delete_mode: bool = False

    # 返回需要保存数据
    def _get_data_need_to_save(self) -> dict:
        return Config.load_file(self.get_map_file_location()) | super()._get_data_need_to_save()

    # 加载角色的数据
    def _load_characters_data(self, mapFileData: dict) -> None:
        EXCEPTION.fatal("_load_characters_data()", 1)

    # 初始化
    def load(self, screen: ImageSurface, chapterType: str, chapterId: int, projectName: str = None) -> None:
        self._initialize(chapterType, chapterId, projectName)
        self.folder_for_save_file, self.name_for_save_file = os.path.split(self.get_map_file_location())
        # 载入地图数据
        mapFileData: dict = Config.load(self.get_map_file_location())
        # 初始化角色信息
        self._load_characters_data(mapFileData)
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
        container_width: int = int(screen.get_width() * 0.2)
        container_height: int = int(screen.get_height())
        button_width: int = int(screen.get_width() * 0.04)
        button_height: int = int(screen.get_height() * 0.2)
        panding: int = int(screen.get_height() * 0.01)
        self.__right_container_buttons.get("select_block").set_left(
            int(
                (
                    container_width
                    - self.__right_container_buttons.get("select_block").get_width()
                    - self.__right_container_buttons.get("select_decoration").get_width()
                    - panding
                )
                / 2
            )
        )
        self.__right_container_buttons.get("select_decoration").set_left(
            self.__right_container_buttons.get("select_block").right + panding
        )
        self.__UIContainerRight.set_size(container_width, container_height)
        self.__UIContainerButtonRight = MovableImage(
            "<!ui>container_button.png",
            int(screen.get_width() - button_width),
            int((screen.get_height() - button_height) / 2),
            int(screen.get_width() - button_width - container_width),
            int((screen.get_height() - button_height) / 2),
            int(container_width / 10),
            0,
            button_width,
            button_height,
        )
        self.__UIContainerButtonRight.rotate(90)
        # 加载背景图片
        self.__envImgContainer.set_pos(container_width * 0.075, screen.get_height() * 0.1)
        self.__envImgContainer.set_size(container_width * 0.85, screen.get_height() * 0.85)
        for imgPath in glob(os.path.join(ASSET.get_internal_environment_image_path("block"), "*.png")):
            self.__envImgContainer.set(
                os.path.basename(imgPath).replace(".png", ""), IMG.load(imgPath, (self._MAP.block_width / 3, None))
            )
        self.__envImgContainer.set_item_per_line(4)
        self.__envImgContainer.set_scroll_bar_pos("right")
        self.__envImgContainer.set_visible(True)
        self.__envImgContainer.distance_between_item = panding
        # 加载所有的装饰品
        self.__decorationsImgContainer.set_pos(container_width * 0.075, screen.get_height() * 0.1)
        self.__decorationsImgContainer.set_size(container_width * 0.85, screen.get_height() * 0.85)
        for imgPath in glob(os.path.join(ASSET.get_internal_environment_image_path("decoration"), "*.png")):
            self.__decorationsImgContainer.set(
                os.path.basename(imgPath).replace(".png", ""), IMG.load(imgPath, (self._MAP.block_width / 3, None))
            )
        self.__decorationsImgContainer.set_item_per_line(4)
        self.__decorationsImgContainer.set_scroll_bar_pos("right")
        self.__decorationsImgContainer.set_visible(False)
        self.__decorationsImgContainer.distance_between_item = panding
        """加载下方的界面"""
        container_width = int(screen.get_width() * 0.8)
        container_height = int(screen.get_height() * 0.3)
        button_width = int(screen.get_width() * 0.14)
        button_height = int(screen.get_height() * 0.05)
        self.__bottom_container_buttons.get("select_hostile_characters").set_left(
            self.__bottom_container_buttons.get("select_friendly_characters").right + panding
        )
        self.__UIContainerBottom = DynamicImage("<!ui>container.png", 0, 0, container_width, container_height)
        self.__UIContainerButtonBottom = MovableImage(
            "<!ui>container_button.png",
            int((container_width - button_width) / 2),
            int(screen.get_height() - button_height),
            int((container_width - button_width) / 2),
            int(screen.get_height() - button_height - container_height),
            0,
            int(container_height / 10),
            button_width,
            button_height,
        )
        # 加载所有友方的角色的图片文件
        self.__friendlyCharactersImagesContainer.set_pos(container_width * 0.025, container_height * 0.2)
        self.__friendlyCharactersImagesContainer.set_size(container_width * 0.95, container_height * 0.7)
        img_name: str
        temp_image: ImageSurface
        for imgPath in glob(os.path.join("Assets", "image", "character", "*")):
            img_name = os.path.basename(imgPath)
            temp_image = IMG.load(os.path.join(imgPath, "wait", "{}_wait_0.png".format(img_name)), (None, container_height * 1.5))
            self.__friendlyCharactersImagesContainer.set(img_name, temp_image.subsurface(temp_image.get_bounding_rect()))
        self.__friendlyCharactersImagesContainer.set_scroll_bar_pos("bottom")
        self.__friendlyCharactersImagesContainer.set_visible(True)
        self.__friendlyCharactersImagesContainer.distance_between_item = panding
        # 加载所有敌对角色的图片文件
        self.__hostileCharactersImagesContainer.set_pos(container_width * 0.025, container_height * 0.2)
        self.__hostileCharactersImagesContainer.set_size(container_width * 0.95, container_height * 0.7)
        for imgPath in glob(os.path.join("Assets", "image", "sangvisFerri", "*")):
            img_name = os.path.basename(imgPath)
            temp_image = IMG.load(os.path.join(imgPath, "wait", "{}_wait_0.png".format(img_name)), (None, container_height * 1.5))
            self.__hostileCharactersImagesContainer.set(img_name, temp_image.subsurface(temp_image.get_bounding_rect()))
        self.__hostileCharactersImagesContainer.set_scroll_bar_pos("bottom")
        self.__hostileCharactersImagesContainer.set_visible(False)
        self.__hostileCharactersImagesContainer.distance_between_item = panding
        # 绿色方块/方块标准
        self.__range_green = IMG.load("<!ui>range_green.png", (self._MAP.block_width * 0.8, None))
        self.__range_green.set_alpha(150)
        self.__range_red = IMG.load("<!ui>range_red.png", (self._MAP.block_width * 0.8, None))
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
        block_get_click = self._MAP.calBlockInMap()
        for event in Controller.events:
            if event.type == Key.DOWN:
                if event.key == Key.ESCAPE:
                    self.__object_to_put_down.clear()
                    self.data_to_edit = None
                    self.__delete_mode = False
                self._check_key_down(event)
            elif event.type == Key.UP:
                self._check_key_up(event)
            elif event.type == MOUSE_BUTTON_DOWN:
                # 上下滚轮-放大和缩小地图
                if self.__UIContainerButtonRight.is_hovered():
                    self.__UIContainerButtonRight.switch()
                    self.__UIContainerButtonRight.flip(True)
                elif self.__UIContainerButtonBottom.is_hovered():
                    self.__UIContainerButtonBottom.switch()
                    self.__UIContainerButtonBottom.flip(False, True)
                elif self.__delete_mode is True and block_get_click is not None:
                    # 查看当前位置是否有装饰物
                    decoration = self._MAP.find_decoration_on((block_get_click["x"], block_get_click["y"]))
                    # 如果发现有冲突的装饰物
                    if decoration is not None:
                        self._MAP.remove_decoration(decoration)
                    else:
                        any_chara_replace = None
                        for key, value in {
                            **self._alliances_data,
                            **self._enemies_data,
                        }.items():
                            if value.x == block_get_click["x"] and value.y == block_get_click["y"]:
                                any_chara_replace = key
                                break
                        if any_chara_replace is not None:
                            if any_chara_replace in self._alliances_data:
                                self._alliances_data.pop(any_chara_replace)
                            elif any_chara_replace in self._enemies_data:
                                self._enemies_data.pop(any_chara_replace)
                else:
                    if (
                        Controller.get_event("confirm")
                        and block_get_click is not None
                        and len(self.__object_to_put_down) > 0
                        and not self.__UIContainerRight.is_hovered((self.__UIContainerButtonRight.right, 0))
                        and not self.__UIContainerBottom.is_hovered((self.__UIContainerButtonBottom.bottom, 0))
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
                                {
                                    "image": self.__object_to_put_down["id"],
                                    "x": block_get_click["x"],
                                    "y": block_get_click["y"],
                                },
                                DataBase.get("Decorations")[self.__object_to_put_down["id"]],
                                "{0}_{1}".format(self.__object_to_put_down["id"], self._MAP.count_decorations()),
                            )
                        elif (
                            self.__object_to_put_down["type"] == "character"
                            or self.__object_to_put_down["type"] == "sangvisFerri"
                        ):
                            any_chara_replace = None
                            for key, value in {**self._alliances_data, **self._enemies_data}.items():
                                if value.x == block_get_click["x"] and value.y == block_get_click["y"]:
                                    any_chara_replace = key
                                    break
                            if any_chara_replace is not None:
                                if any_chara_replace in self._alliances_data:
                                    self._alliances_data.pop(any_chara_replace)
                                elif any_chara_replace in self._enemies_data:
                                    self._enemies_data.pop(any_chara_replace)
                            the_id = 0
                            if self.__object_to_put_down["type"] == "character":
                                while self.__object_to_put_down["id"] + "_" + str(the_id) in self._alliances_data:
                                    the_id += 1
                                nameTemp = self.__object_to_put_down["id"] + "_" + str(the_id)
                                self._alliances_data[nameTemp] = FriendlyCharacter(
                                    deepcopy(CHARACTER_DATABASE[self.__object_to_put_down["id"]])
                                    | {
                                        "x": block_get_click["x"],
                                        "y": block_get_click["y"],
                                        "type": self.__object_to_put_down["id"],
                                        "bullets_carried": 100,
                                    },
                                    "dev",
                                )
                            elif self.__object_to_put_down["type"] == "sangvisFerri":
                                while self.__object_to_put_down["id"] + "_" + str(the_id) in self._enemies_data:
                                    the_id += 1
                                nameTemp = self.__object_to_put_down["id"] + "_" + str(the_id)
                                self._enemies_data[nameTemp] = HostileCharacter(
                                    deepcopy(CHARACTER_DATABASE[self.__object_to_put_down["id"]])
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
            and not self.__UIContainerBottom.is_hovered((self.__UIContainerButtonBottom.bottom, 0))
        ):
            if self.__delete_mode is True:
                xTemp, yTemp = self._MAP.calPosInMap(block_get_click["x"], block_get_click["y"])
                screen.blit(self.__range_red, (xTemp + self._MAP.block_width * 0.1, yTemp))
            elif len(self.__object_to_put_down) > 0:
                xTemp, yTemp = self._MAP.calPosInMap(block_get_click["x"], block_get_click["y"])
                screen.blit(self.__range_green, (xTemp + self._MAP.block_width * 0.1, yTemp))

        # 角色动画
        for key in self._alliances_data:
            self._alliances_data[key].draw(screen, self._MAP)
            if (
                len(self.__object_to_put_down) <= 0
                and Controller.get_event("confirm")
                and self._alliances_data[key].x == int(Controller.mouse.x / self.__range_green.get_width())
                and self._alliances_data[key].y == int(Controller.mouse.y / self.__range_green.get_height())
            ):
                self.data_to_edit = self._alliances_data[key]
        for key in self._enemies_data:
            self._enemies_data[key].draw(screen, self._MAP)
            if (
                len(self.__object_to_put_down) <= 0
                and Controller.get_event("confirm")
                and self._enemies_data[key].x == int(Controller.mouse.x / self.__range_green.get_width())
                and self._enemies_data[key].y == int(Controller.mouse.y / self.__range_green.get_height())
            ):
                self.data_to_edit = self._enemies_data[key]

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
                    self.__object_to_put_down = {
                        "type": "block",
                        "id": self.__envImgContainer.item_being_hovered,
                    }
                elif (
                    self.__decorationsImgContainer.is_visible() and self.__decorationsImgContainer.item_being_hovered is not None
                ):
                    self.__object_to_put_down = {
                        "type": "decoration",
                        "id": self.__decorationsImgContainer.item_being_hovered,
                    }
        # 画出下方容器的UI
        self.__UIContainerButtonBottom.draw(screen)
        if self.__UIContainerButtonBottom.bottom < screen.get_height():
            self.__UIContainerBottom.display(screen, (0, self.__UIContainerButtonBottom.bottom))
            self.__friendlyCharactersImagesContainer.display(screen, (0, self.__UIContainerButtonBottom.bottom))
            self.__hostileCharactersImagesContainer.display(screen, (0, self.__UIContainerButtonBottom.bottom))
            self.__bottom_container_buttons.display(screen, (0, self.__UIContainerButtonBottom.bottom))
            if Controller.get_event("confirm"):
                if self.__bottom_container_buttons.item_being_hovered == "select_friendly_characters":
                    self.__friendlyCharactersImagesContainer.set_visible(True)
                    self.__hostileCharactersImagesContainer.set_visible(False)
                elif self.__bottom_container_buttons.item_being_hovered == "select_hostile_characters":
                    self.__friendlyCharactersImagesContainer.set_visible(False)
                    self.__hostileCharactersImagesContainer.set_visible(True)
                if (
                    self.__friendlyCharactersImagesContainer.is_visible()
                    and self.__friendlyCharactersImagesContainer.item_being_hovered is not None
                ):
                    self.__object_to_put_down = {
                        "type": "character",
                        "id": self.__friendlyCharactersImagesContainer.item_being_hovered,
                    }
                elif (
                    self.__hostileCharactersImagesContainer.is_visible()
                    and self.__hostileCharactersImagesContainer.item_being_hovered is not None
                ):
                    self.__object_to_put_down = {
                        "type": "sangvisFerri",
                        "id": self.__hostileCharactersImagesContainer.item_being_hovered,
                    }

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
                self._load_characters_data(mapFileData)
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
            elif self.__object_to_put_down["type"] == "character":
                screen.blit(self.__friendlyCharactersImagesContainer.get(self.__object_to_put_down["id"]), Controller.mouse.pos)
            elif self.__object_to_put_down["type"] == "sangvisFerri":
                screen.blit(self.__hostileCharactersImagesContainer.get(self.__object_to_put_down["id"]), Controller.mouse.pos)

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

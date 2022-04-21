from .component import *

# 角色立绘系统
class CharacterImageManager:

    # 立绘配置信息数据库
    __CHARACTER_IMAGE_DATABASE: dict = DataBase.get("Npc")
    # 是否立绘配置信息数据库
    __IS_CHARACTER_IMAGE_DATABASE_ENABLED: bool = len(__CHARACTER_IMAGE_DATABASE) > 0

    def __init__(self) -> None:
        # 用于存放立绘的字典
        self.__character_image: dict = {}
        # 如果是开发模式，则在初始化时加载所有图片
        self.__previous_characters: tuple = tuple()
        self.__last_round_image_alpha: int = 255
        self.__current_characters: tuple = tuple()
        self.__this_round_image_alpha: int = 0
        self.__darkness: int = 50
        self.__img_width: int = Display.get_width() // 2
        self.__communication_surface_rect: Rectangle = Rectangle(
            self.__img_width // 4, 0, self.__img_width // 2, self.__img_width * 56 // 100
        )
        self.__communication: Optional[StaticImage] = None
        self.__communication_dark: Optional[StaticImage] = None
        try:
            self.__communication = StaticImage(
                os.path.join(r"Assets/image/UI/communication.png"),
                0,
                0,
                self.__communication_surface_rect.width,
                self.__communication_surface_rect.height,
            )
            self.__communication_dark = self.__communication.copy()
            self.__communication_dark.add_darkness(self.__darkness)
        except Exception:
            self.__communication = None
            self.__communication_dark = None
        # 移动的x
        self.__move_x: int = 0
        # x轴offset
        self.__x_offset_for_this_round: int = 0
        self.__x_offset_for_last_round: int = 0
        # y轴坐标
        self.__NPC_Y: int = Display.get_height() - self.__img_width
        # 开发者模式
        self.dev_mode: bool = False
        # 被点击的角色
        self.character_get_click: Optional[str] = None
        # npc立绘路径
        self.image_folder_path: str = os.path.join("Assets", "image", "npc")

    # 确保角色存在
    def __ensure_the_existence_of(self, name: str) -> None:
        if name not in self.__character_image:
            self.__load_character(os.path.join(self.image_folder_path, name))

    # 加载角色
    def __load_character(self, path: str) -> None:
        name = os.path.basename(path)
        self.__character_image[name] = {}
        self.__character_image[name]["normal"] = StaticImage(path, 0, 0, self.__img_width, self.__img_width)
        # 生成深色图片
        self.__character_image[name]["dark"] = self.__character_image[name]["normal"].copy()
        self.__character_image[name]["dark"].add_darkness(self.__darkness)

    # 画出角色
    def __display_character(self, name: str, x: int, alpha: int, surface: ImageSurface) -> None:
        if alpha > 0:
            nameTemp: str = name.replace("<c>", "").replace("<d>", "")
            self.__ensure_the_existence_of(nameTemp)
            # 加载npc的基础立绘
            img: StaticImage = (
                self.__character_image[nameTemp]["dark"] if "<d>" in name else self.__character_image[nameTemp]["normal"]
            )
            img.set_size(self.__img_width, self.__img_width)
            img.set_alpha(alpha)
            img.set_pos(x, self.__NPC_Y)
            if "<c>" in name:
                img.set_crop_rect(self.__communication_surface_rect)
                img.draw(surface)
                if "<d>" in name:
                    if self.__communication_dark is not None:
                        self.__communication_dark.set_pos(
                            img.x + self.__communication_surface_rect.x, self.__NPC_Y + self.__communication_surface_rect.y
                        )
                        self.__communication_dark.draw(surface)
                    else:
                        EXCEPTION.fatal("The communication_dark surface is not initialized!")
                else:
                    if self.__communication is not None:
                        self.__communication.set_pos(
                            img.x + self.__communication_surface_rect.x, self.__NPC_Y + self.__communication_surface_rect.y
                        )
                        self.__communication.draw(surface)
                    else:
                        EXCEPTION.fatal("The communication surface is not initialized!")
            else:
                img.set_crop_rect(None)
                img.draw(surface)
            # 如果是开发模式
            if self.dev_mode is True and img.is_hovered():
                img.draw_outline(surface)
                self.character_get_click = name

    # 根据文件名判断是否是同一角色名下的图片
    @classmethod
    def __is_the_same_character(cls, fileName1: str, fileName2: str, must_be_the_same: bool = False) -> bool:
        if fileName1 == fileName2:
            return True
        elif cls.__IS_CHARACTER_IMAGE_DATABASE_ENABLED and not must_be_the_same:
            fileName1 = fileName1.replace("<c>", "").replace("<d>", "")
            fileName2 = fileName2.replace("<c>", "").replace("<d>", "")
            for key in cls.__CHARACTER_IMAGE_DATABASE:
                if fileName1 in cls.__CHARACTER_IMAGE_DATABASE[key]:
                    return fileName2 in cls.__CHARACTER_IMAGE_DATABASE[key]
                elif fileName2 in cls.__CHARACTER_IMAGE_DATABASE[key]:
                    return fileName1 in cls.__CHARACTER_IMAGE_DATABASE[key]
        return False

    # 根据参数计算立绘的x坐标
    @staticmethod
    def __estimate_x(_width: int, _num: int, index: int) -> int:
        if _num == 1:
            return _width // 4
        elif _num == 2:
            return index * _width // _num
        elif _num > 2:
            return (
                int((index + 1) * _width / (_num + 1) - _width / 4)
                if _num % 2 == 0
                else int((index - _num // 2) * _width / _num + _width / 4)
            )
        else:
            return 0

    # 渐入name1角色的同时淡出name2角色
    def __fade_in_and_out_characters(self, name1: str, name2: str, x: int, surface: ImageSurface) -> None:
        self.__display_character(name1, x, self.__last_round_image_alpha, surface)
        self.__display_character(name2, x, self.__this_round_image_alpha, surface)

    # 渐入所有当前的角色
    def __fade_in_all_characters_this_round(self, surface: ImageSurface) -> None:
        for i in range(len(self.__current_characters)):
            self.__display_character(
                self.__current_characters[i],
                self.__estimate_x(surface.get_width(), len(self.__current_characters), i) + self.__x_offset_for_this_round,
                self.__this_round_image_alpha,
                surface,
            )

    # 淡出所有之前的角色
    def __fade_out_all_characters_last_round(self, surface: ImageSurface) -> None:
        for i in range(len(self.__previous_characters)):
            self.__display_character(
                self.__previous_characters[i],
                self.__estimate_x(surface.get_width(), len(self.__previous_characters), i) + self.__x_offset_for_last_round,
                self.__last_round_image_alpha,
                surface,
            )

    def draw(self, surface: ImageSurface) -> None:
        # 更新alpha值，并根据alpha值计算offset
        self.__x_offset_for_last_round = 0
        if self.__last_round_image_alpha > 0:
            self.__last_round_image_alpha -= 15
            self.__x_offset_for_last_round = int(
                self.__img_width / 4 - self.__img_width / 4 * self.__last_round_image_alpha / 255
            )
        self.__x_offset_for_this_round = 0
        if self.__this_round_image_alpha < 255:
            self.__this_round_image_alpha += 25
            self.__x_offset_for_this_round = int(
                self.__img_width / 4 * self.__this_round_image_alpha / 255 - self.__img_width / 4
            )
        # 初始化被选择的角色名字
        self.character_get_click = None
        # 画上上一幕的立绘
        if len(self.__previous_characters) == len(self.__current_characters):
            for i in range(len(self.__previous_characters)):
                npcImg_x: int = self.__estimate_x(surface.get_width(), len(self.__previous_characters), i)
                # 渲染立绘
                if self.__is_the_same_character(self.__previous_characters[i], self.__current_characters[i], True):
                    self.__display_character(self.__current_characters[i], npcImg_x, 255, surface)
                else:
                    self.__display_character(self.__previous_characters[i], npcImg_x, self.__last_round_image_alpha, surface)
                    self.__display_character(self.__current_characters[i], npcImg_x, self.__this_round_image_alpha, surface)
        elif len(self.__current_characters) == 0:
            self.__fade_out_all_characters_last_round(surface)
        elif len(self.__previous_characters) == 0:
            self.__fade_in_all_characters_this_round(surface)
        elif len(self.__previous_characters) == 1 and len(self.__current_characters) == 2:
            # 如果之前的中间变成了现在的左边，则立绘应该先向左移动
            if self.__is_the_same_character(self.__previous_characters[0], self.__current_characters[0]):
                if self.__move_x + surface.get_width() / 4 > 0:
                    self.__move_x -= surface.get_width() // 40
                # 渐入左边立绘
                self.__fade_in_and_out_characters(
                    self.__previous_characters[0],
                    self.__current_characters[0],
                    self.__move_x + surface.get_width() // 4,
                    surface,
                )
                # 显示右边立绘
                self.__display_character(
                    self.__current_characters[1], surface.get_width() // 2, self.__this_round_image_alpha, surface
                )
            # 如果之前的中间变成了现在的右边，则立绘应该先向右移动
            elif self.__is_the_same_character(self.__previous_characters[0], self.__current_characters[1]):
                if self.__move_x + surface.get_width() / 4 < surface.get_width() / 2:
                    self.__move_x += surface.get_width() // 40
                # 显示左边立绘
                self.__display_character(self.__current_characters[0], 0, self.__this_round_image_alpha, surface)
                # 渐入右边立绘
                self.__fade_in_and_out_characters(
                    self.__previous_characters[0],
                    self.__current_characters[1],
                    self.__move_x + surface.get_width() // 4,
                    surface,
                )
            # 之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘
            else:
                if self.__last_round_image_alpha > 0:
                    self.__this_round_image_alpha -= 25
                    self.__fade_out_all_characters_last_round(surface)
                else:
                    self.__fade_in_all_characters_this_round(surface)
        elif len(self.__previous_characters) == 2 and len(self.__current_characters) == 1:
            # 如果之前的左边变成了现在的中间，则立绘应该先向右边移动
            if self.__is_the_same_character(self.__previous_characters[0], self.__current_characters[0]):
                if self.__move_x < surface.get_width() / 4:
                    self.__move_x += surface.get_width() // 40
                # 左边立绘向右移动
                self.__fade_in_and_out_characters(
                    self.__previous_characters[0],
                    self.__current_characters[0],
                    self.__move_x,
                    surface,
                )
                # 右边立绘消失
                self.__display_character(
                    self.__previous_characters[1], surface.get_width() // 2, self.__last_round_image_alpha, surface
                )
            # 如果之前的右边变成了现在的中间，则立绘应该先向左边移动
            elif self.__is_the_same_character(self.__previous_characters[1], self.__current_characters[0]):
                if self.__move_x + surface.get_width() / 2 > surface.get_width() / 4:
                    self.__move_x -= surface.get_width() // 40
                # 左边立绘消失
                self.__display_character(self.__previous_characters[0], 0, self.__last_round_image_alpha, surface)
                # 右边立绘向左移动
                self.__fade_in_and_out_characters(
                    self.__previous_characters[1],
                    self.__current_characters[0],
                    self.__move_x + surface.get_width() // 2,
                    surface,
                )
            else:
                if self.__last_round_image_alpha > 0:
                    self.__this_round_image_alpha -= 25
                    self.__fade_out_all_characters_last_round(surface)
                else:
                    self.__fade_in_all_characters_this_round(surface)
        else:
            if self.__last_round_image_alpha > 0:
                self.__this_round_image_alpha -= 25
                self.__fade_out_all_characters_last_round(surface)
            else:
                self.__fade_in_all_characters_this_round(surface)

    # 更新立绘
    def update(self, characterNameList: Optional[Sequence[str]]) -> None:
        self.__previous_characters = self.__current_characters
        self.__current_characters = tuple(characterNameList) if characterNameList is not None else tuple()
        self.__last_round_image_alpha = 255
        self.__this_round_image_alpha = 5
        self.__move_x = 0

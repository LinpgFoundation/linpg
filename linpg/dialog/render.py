from .component import *

_DARKNESS: int = 50

# 角色立绘名称预处理模块
class CharacterImageNameMetaData:

    # 立绘配置信息数据库
    __CHARACTER_IMAGE_DATABASE: dict = DataBase.get("Npc")
    # 是否立绘配置信息数据库
    __IS_CHARACTER_IMAGE_DATABASE_ENABLED: bool = len(__CHARACTER_IMAGE_DATABASE) > 0

    def __init__(self, _name: str) -> None:
        _name_data: list[str] = _name.split("&")
        self.__name: str = _name_data[0]
        self.__tags: tuple[str, ...] = tuple(_name_data[1:])

    @property
    def name(self) -> str:
        return self.__name

    # 根据文件名判断是否是同一角色名下的图片
    def equal(self, otherNameData: "CharacterImageNameMetaData", must_be_the_same: bool = False) -> bool:
        if self.__name == otherNameData.name:
            return True
        elif self.__IS_CHARACTER_IMAGE_DATABASE_ENABLED and not must_be_the_same:
            for key in self.__CHARACTER_IMAGE_DATABASE:
                if self.__name in self.__CHARACTER_IMAGE_DATABASE[key]:
                    return otherNameData.name in self.__CHARACTER_IMAGE_DATABASE[key]
                elif otherNameData.name in self.__CHARACTER_IMAGE_DATABASE[key]:
                    return self.__name in self.__CHARACTER_IMAGE_DATABASE[key]
        return False

    # 是否有tag
    def has_tag(self, _tag: str) -> bool:
        return _tag in self.__tags

    # 移除tag
    def remove_tag(self, _tag: str) -> None:
        new_tags: list[str] = []
        for original_tag in self.__tags:
            if original_tag != _tag:
                new_tags.append(original_tag)
        self.__tags = tuple(new_tags)

    # 增加tag
    def add_tag(self, _tag: str) -> None:
        new_tags: list[str] = []
        for original_tag in self.__tags:
            if original_tag != _tag:
                new_tags.append(original_tag)
        new_tags.append(_tag)
        self.__tags = tuple(new_tags)

    # 获取tag和名称结合后的数据名称
    def get_raw_name(self) -> str:
        raw_name: str = self.__name
        for tag in self.__tags:
            raw_name += "&" + tag
        return raw_name


# 角色立绘滤镜
class FilterEffect:
    def __init__(self, path: str) -> None:
        self.__N_IMAGE: StaticImage = StaticImage(path, 0, 0)
        self.__D_IMAGE: StaticImage = self.__N_IMAGE.copy()
        self.__D_IMAGE.add_darkness(_DARKNESS)

    # 设置rect
    def set_rect(self, _x: int, _y: int, _width: int, _height: int) -> None:
        self.__N_IMAGE.set_pos(_x, _y)
        self.__N_IMAGE.set_size(_width, _height)
        self.__D_IMAGE.set_pos(_x, _y)
        self.__D_IMAGE.set_size(_width, _height)

    # 将滤镜应用到立绘上并渲染到屏幕上
    def render(self, characterImage: StaticImage, surface: ImageSurface, is_silent: bool) -> None:
        if not is_silent:
            characterImage.set_crop_rect(self.__N_IMAGE.get_rectangle())
            characterImage.draw(surface)
            self.__N_IMAGE.set_alpha(characterImage.get_alpha())
            self.__N_IMAGE.display(surface, characterImage.get_pos())
        else:
            characterImage.set_crop_rect(self.__D_IMAGE.get_rectangle())
            characterImage.draw(surface)
            self.__D_IMAGE.set_alpha(characterImage.get_alpha())
            self.__D_IMAGE.display(surface, characterImage.get_pos())


# 角色立绘系统
class CharacterImageManager:

    __filters: dict[str, FilterEffect] = {}

    def __init__(self) -> None:
        # 用于存放立绘的字典
        self.__character_image: dict = {}
        # 如果是开发模式，则在初始化时加载所有图片
        self.__previous_characters: tuple[CharacterImageNameMetaData, ...] = tuple()
        self.__last_round_image_alpha: int = 255
        self.__current_characters: tuple[CharacterImageNameMetaData, ...] = tuple()
        self.__this_round_image_alpha: int = 00
        self.__img_width: int = Display.get_width() // 2
        if "communicating" not in self.__filters:
            self.__filters["communicating"] = FilterEffect("Assets/image/UI/communication.png")
        self.__filters["communicating"].set_rect(self.__img_width // 4, 0, self.__img_width // 2, self.__img_width * 56 // 100)
        # 移动的x
        self.__x_correction_offset_index: int = 0
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
        self.__character_image[name]["dark"].add_darkness(_DARKNESS)

    # 画出角色
    def __display_character(self, _name_data: CharacterImageNameMetaData, x: int, alpha: int, surface: ImageSurface) -> None:
        if alpha > 0:
            self.__ensure_the_existence_of(_name_data.name)
            # 加载npc的基础立绘
            img: StaticImage = (
                self.__character_image[_name_data.name]["dark"]
                if _name_data.has_tag("silent")
                else self.__character_image[_name_data.name]["normal"]
            )
            img.set_size(self.__img_width, self.__img_width)
            img.set_alpha(alpha)
            img.set_pos(x, self.__NPC_Y)
            if _name_data.has_tag("communicating"):
                self.__filters["communicating"].render(img, surface, _name_data.has_tag("silent"))
            else:
                img.set_crop_rect(None)
                img.draw(surface)
            # 如果是开发模式
            if self.dev_mode is True and img.is_hovered():
                img.draw_outline(surface)
                self.character_get_click = _name_data.get_raw_name()

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
    def __fade_in_and_out_characters(
        self, name1: CharacterImageNameMetaData, name2: CharacterImageNameMetaData, x: int, surface: ImageSurface
    ) -> None:
        self.__display_character(name1, x, self.__last_round_image_alpha, surface)
        self.__display_character(name2, x, self.__this_round_image_alpha, surface)

    # 渐入所有当前的角色
    def __fade_in_characters_this_round(self, surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(self.__current_characters)):
            self.__display_character(
                self.__current_characters[i],
                self.__estimate_x(surface.get_width(), len(self.__current_characters), i) + self.__x_offset_for_this_round,
                self.__this_round_image_alpha,
                surface,
            )

    # 淡出所有之前的角色
    def __fade_out_characters_last_round(self, surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(self.__previous_characters)):
            self.__display_character(
                self.__previous_characters[i],
                self.__estimate_x(surface.get_width(), len(self.__previous_characters), i) + self.__x_offset_for_last_round,
                self.__last_round_image_alpha,
                surface,
            )

    # 将立绘画到屏幕上
    def draw(self, surface: ImageSurface) -> None:
        # 更新alpha值，并根据alpha值计算offset
        if self.__last_round_image_alpha > 0:
            self.__last_round_image_alpha -= 15
            self.__x_offset_for_last_round = int(
                self.__img_width / 4 - self.__img_width / 4 * self.__last_round_image_alpha / 255
            )
        else:
            self.__x_offset_for_last_round = 0
        if self.__this_round_image_alpha < 255:
            self.__this_round_image_alpha += 25
            self.__x_offset_for_this_round = int(
                self.__img_width / 4 * self.__this_round_image_alpha / 255 - self.__img_width / 4
            )
        else:
            self.__x_offset_for_this_round = 0
        # 初始化被选择的角色名字
        self.character_get_click = None
        # 画上上一幕的立绘
        if len(self.__previous_characters) == len(self.__current_characters):
            for i in range(len(self.__previous_characters)):
                npcImg_x: int = self.__estimate_x(surface.get_width(), len(self.__previous_characters), i)
                # 渲染立绘
                if self.__previous_characters[i].equal(self.__current_characters[i], True):
                    self.__display_character(self.__current_characters[i], npcImg_x, 255, surface)
                else:
                    self.__display_character(self.__previous_characters[i], npcImg_x, self.__last_round_image_alpha, surface)
                    self.__display_character(self.__current_characters[i], npcImg_x, self.__this_round_image_alpha, surface)
        elif len(self.__current_characters) == 0:
            self.__fade_out_characters_last_round(surface)
        elif len(self.__previous_characters) == 0:
            self.__fade_in_characters_this_round(surface)
        else:
            # 初始化previous_x坐标
            previous_x: int = 0
            if len(self.__previous_characters) == 1 and len(self.__current_characters) == 2:
                previous_x = self.__estimate_x(surface.get_width(), len(self.__previous_characters), 0)
                # 如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if self.__previous_characters[0].equal(self.__current_characters[0]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                    # 渐入左边立绘
                    self.__fade_in_and_out_characters(
                        self.__previous_characters[0],
                        self.__current_characters[0],
                        self.__x_correction_offset_index
                        * (self.__estimate_x(surface.get_width(), len(self.__current_characters), 0) - previous_x)
                        // 100
                        + previous_x,
                        surface,
                    )
                    # 显示右边立绘
                    self.__display_character(
                        self.__current_characters[1], surface.get_width() // 2, self.__this_round_image_alpha, surface
                    )
                # 如果之前的中间变成了现在的右边，则立绘应该先向右移动
                elif self.__previous_characters[0].equal(self.__current_characters[1]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                    # 显示左边立绘
                    self.__display_character(self.__current_characters[0], 0, self.__this_round_image_alpha, surface)
                    # 渐入右边立绘
                    self.__fade_in_and_out_characters(
                        self.__previous_characters[0],
                        self.__current_characters[1],
                        self.__x_correction_offset_index
                        * (self.__estimate_x(surface.get_width(), len(self.__current_characters), 1) - previous_x)
                        // 100
                        + previous_x,
                        surface,
                    )
                # 之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘
                elif self.__last_round_image_alpha > 0:
                    self.__this_round_image_alpha -= 25
                    self.__fade_out_characters_last_round(surface)
                else:
                    self.__fade_in_characters_this_round(surface)
            elif len(self.__previous_characters) == 2 and len(self.__current_characters) == 1:
                current_x: int = self.__estimate_x(surface.get_width(), len(self.__current_characters), 0)
                # 如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if self.__previous_characters[0].equal(self.__current_characters[0]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                        previous_x = self.__estimate_x(surface.get_width(), len(self.__previous_characters), 0)
                        # 左边立绘向右移动
                        self.__fade_in_and_out_characters(
                            self.__previous_characters[0],
                            self.__current_characters[0],
                            self.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            surface,
                        )
                    else:
                        # 显示左方立绘
                        self.__display_character(self.__current_characters[0], current_x, self.__this_round_image_alpha, surface)
                    # 右边立绘消失
                    self.__display_character(
                        self.__previous_characters[1], surface.get_width() // 2, self.__last_round_image_alpha, surface
                    )
                # 如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif self.__previous_characters[1].equal(self.__current_characters[0]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                        previous_x = self.__estimate_x(surface.get_width(), len(self.__previous_characters), 1)
                        # 右边立绘向左移动
                        self.__fade_in_and_out_characters(
                            self.__previous_characters[1],
                            self.__current_characters[0],
                            self.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            surface,
                        )
                    else:
                        # 显示右方立绘
                        self.__display_character(self.__current_characters[0], current_x, self.__this_round_image_alpha, surface)
                    # 左边立绘消失
                    self.__display_character(self.__previous_characters[0], 0, self.__last_round_image_alpha, surface)
                elif self.__last_round_image_alpha > 0:
                    self.__this_round_image_alpha -= 25
                    self.__fade_out_characters_last_round(surface)
                else:
                    self.__fade_in_characters_this_round(surface)
            elif self.__last_round_image_alpha > 0:
                self.__this_round_image_alpha -= 25
                self.__fade_out_characters_last_round(surface)
            else:
                self.__fade_in_characters_this_round(surface)

    # 更新立绘
    def update(self, characterNameList: Optional[Sequence[str]]) -> None:
        self.__previous_characters = self.__current_characters
        self.__current_characters = (
            tuple([CharacterImageNameMetaData(_name) for _name in characterNameList])
            if characterNameList is not None
            else tuple()
        )
        self.__last_round_image_alpha = 255
        self.__this_round_image_alpha = 5
        self.__x_correction_offset_index = 0

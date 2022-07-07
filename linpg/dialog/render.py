from .component import *

_DARKNESS: int = 50

# 角色立绘名称预处理模块
class CharacterImageNameMetaData:

    # 立绘配置信息数据库
    __CHARACTER_IMAGE_DATABASE: Final[dict] = DataBase.get("Npc")
    # 是否立绘配置信息数据库
    __IS_CHARACTER_IMAGE_DATABASE_ENABLED: bool = len(__CHARACTER_IMAGE_DATABASE) > 0

    def __init__(self, _name: str) -> None:
        _name_data: list[str] = _name.split("&")
        self.__name: str = _name_data[0]
        self.__tags: set[str] = set(_name_data[1:])
        self.__slient: bool = False
        if "silent" in self.__tags:
            self.__slient = True
            self.__tags.remove("silent")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def tags(self) -> set[str]:
        return self.__tags

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
        if _tag == "silent":
            return self.__slient
        else:
            return _tag in self.__tags

    # 移除tag
    def remove_tag(self, _tag: str) -> None:
        if _tag == "silent":
            self.__slient = False
        else:
            new_tags: list[str] = []
            for original_tag in self.__tags:
                if original_tag != _tag:
                    new_tags.append(original_tag)
            self.__tags = set(new_tags)

    # 增加tag
    def add_tag(self, _tag: str) -> None:
        if _tag == "silent":
            self.__slient = True
        else:
            new_tags: list[str] = []
            for original_tag in self.__tags:
                if original_tag != _tag:
                    new_tags.append(original_tag)
            new_tags.append(_tag)
            self.__tags = set(new_tags)

    # 获取tag和名称结合后的数据名称
    def get_raw_name(self) -> str:
        raw_name: str = self.__name
        if self.__slient is True:
            raw_name += "&silent"
        for tag in self.__tags:
            raw_name += "&" + tag
        return raw_name


# 角色立绘滤镜
class _FilterEffect:
    def __init__(self, path: str, _x: int, _y: int, _width: int, _height: int) -> None:
        self.__N_IMAGE: StaticImage = StaticImage(path, _x, _y, _width, _height)
        self.__D_IMAGE: StaticImage = self.__N_IMAGE.copy()
        self.__D_IMAGE.add_darkness(_DARKNESS)
        self.__crop_rect: Optional[Rectangle] = None

    def get_rect(self) -> Rectangle:
        return self.__N_IMAGE.get_rectangle()

    def set_crop_rect(self, rect: Optional[Rectangle]) -> None:
        self.__crop_rect = rect

    # 将滤镜应用到立绘上并渲染到屏幕上
    def render(self, characterImage: StaticImage, surface: ImageSurface, is_silent: bool) -> None:
        # 如果自定义的crop_rect为None，则以self.__N_IMAGE的rect为中心
        characterImage.set_crop_rect(self.__crop_rect if self.__crop_rect is not None else self.get_rect())
        # 画出立绘
        characterImage.draw(surface)
        # 画出滤镜
        if not is_silent:
            self.__N_IMAGE.set_alpha(characterImage.get_alpha())
            self.__N_IMAGE.display(surface, characterImage.get_pos())
        else:
            self.__D_IMAGE.set_alpha(characterImage.get_alpha())
            self.__D_IMAGE.display(surface, characterImage.get_pos())


# 角色立绘系统
class CharacterImageManager:

    # 用于存放立绘的字典
    __character_image: Final[dict[str, tuple[StaticImage, ...]]] = {}
    # 存放前一对话的参与角色名称
    __previous_characters: tuple[CharacterImageNameMetaData, ...] = tuple()
    __last_round_image_alpha: int = 255
    # 存放当前对话的参与角色名称
    __current_characters: tuple[CharacterImageNameMetaData, ...] = tuple()
    __this_round_image_alpha: int = 0
    # 立绘边长
    _WIDTH: int = Display.get_width() // 2
    # 加载滤镜
    __filters: Final[dict[str, _FilterEffect]] = {}
    # 移动的x
    __x_correction_offset_index: int = 0
    # x轴offset
    __x_offset_for_this_round: int = 0
    __x_offset_for_last_round: int = 0
    # y轴坐标
    __NPC_Y: int = Display.get_height() - _WIDTH
    # 开发者模式
    dev_mode: bool = False
    # 被点击的角色
    character_get_click: Optional[str] = None

    # 重新加载滤镜
    @classmethod
    def init(cls) -> None:
        cls.unload()
        for key, value in DataBase.get("Filters").items():
            if value.get("type") == "image":
                cls.__filters[key] = _FilterEffect(
                    value["path"],
                    round(Display.get_width() * convert_percentage(value["rect"][0])),
                    round(Display.get_width() * convert_percentage(value["rect"][1])),
                    round(Display.get_width() * convert_percentage(value["rect"][2])),
                    round(Display.get_width() * convert_percentage(value["rect"][3])),
                )
                _crop: Optional[list] = value.get("crop")
                if _crop is not None:
                    _rect: Rectangle = cls.__filters[key].get_rect()
                    cls.__filters[key].set_crop_rect(
                        Rectangle(
                            _rect.x + round(_rect.width * convert_percentage(_crop[0])),
                            _rect.y + round(_rect.height * convert_percentage(_crop[1])),
                            round(_rect.width * convert_percentage(_crop[2])),
                            round(_rect.height * convert_percentage(_crop[3])),
                        )
                    )

    # 卸载占用的内存
    @classmethod
    def unload(cls) -> None:
        cls.__previous_characters = tuple()
        cls.__last_round_image_alpha = 255
        cls.__current_characters = tuple()
        cls.__this_round_image_alpha = 0
        cls.__filters.clear()
        cls.__character_image.clear()

    # 画出角色
    @classmethod
    def __display_character(cls, _name_data: CharacterImageNameMetaData, x: int, alpha: int, surface: ImageSurface) -> None:
        if alpha > 0:
            # 确保角色存在
            if _name_data.name not in cls.__character_image:
                # 如果不能存在，则加载角色
                imgTemp: StaticImage = StaticImage(
                    Specification.get_directory("character_image", _name_data.name), 0, 0, cls._WIDTH, cls._WIDTH
                )
                # 以tuple的形式保存立绘，index 0 是正常图片， index 1 是深色图片
                cls.__character_image[_name_data.name] = (imgTemp, imgTemp.copy())
                # 生成深色图片
                cls.__character_image[_name_data.name][1].add_darkness(_DARKNESS)
            # 获取npc立绘的指针
            img: StaticImage = cls.__character_image[_name_data.name][1 if _name_data.has_tag("silent") else 0]
            img.set_size(cls._WIDTH, cls._WIDTH)
            img.set_alpha(alpha)
            img.set_pos(x, cls.__NPC_Y)
            if len(_name_data.tags) > 0:
                for _tag in _name_data.tags:
                    cls.__filters[_tag].render(img, surface, _name_data.has_tag("silent"))
            else:
                img.set_crop_rect(None)
                img.draw(surface)
            # 如果是开发模式
            if cls.dev_mode is True and img.is_hovered():
                img.draw_outline(surface)
                cls.character_get_click = _name_data.get_raw_name()

    # 根据参数计算立绘的x坐标
    @staticmethod
    def __estimate_x(_width: int, _num: int, _index: int) -> int:
        if _num == 1:
            return _width // 4
        elif _num == 2:
            return _index * _width // _num
        elif _num > 2:
            return (
                int((_index + 1) * _width / (_num + 1) - _width / 4)
                if _num % 2 == 0
                else int((_index - _num // 2) * _width / _num + _width / 4)
            )
        else:
            return 0

    # 渐入name1角色的同时淡出name2角色
    @classmethod
    def __fade_in_and_out_characters(
        cls, name1: CharacterImageNameMetaData, name2: CharacterImageNameMetaData, x: int, surface: ImageSurface
    ) -> None:
        cls.__display_character(name1, x, cls.__last_round_image_alpha, surface)
        cls.__display_character(name2, x, cls.__this_round_image_alpha, surface)

    # 渐入所有当前的角色
    @classmethod
    def __fade_in_characters_this_round(cls, surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(cls.__current_characters)):
            cls.__display_character(
                cls.__current_characters[i],
                cls.__estimate_x(surface.get_width(), len(cls.__current_characters), i) + cls.__x_offset_for_this_round,
                cls.__this_round_image_alpha,
                surface,
            )

    # 淡出所有之前的角色
    @classmethod
    def __fade_out_characters_last_round(cls, surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(cls.__previous_characters)):
            cls.__display_character(
                cls.__previous_characters[i],
                cls.__estimate_x(surface.get_width(), len(cls.__previous_characters), i) + cls.__x_offset_for_last_round,
                cls.__last_round_image_alpha,
                surface,
            )

    # 更新立绘
    @classmethod
    def update(cls, characterNameList: Optional[Sequence[str]]) -> None:
        cls.__previous_characters = cls.__current_characters
        cls.__current_characters = (
            tuple([CharacterImageNameMetaData(_name) for _name in characterNameList])
            if characterNameList is not None
            else tuple()
        )
        cls.__last_round_image_alpha = 255
        cls.__this_round_image_alpha = 5
        cls.__x_correction_offset_index = 0

    # 将立绘画到屏幕上
    @classmethod
    def draw(cls, surface: ImageSurface) -> None:
        # 更新alpha值，并根据alpha值计算offset
        if cls.__last_round_image_alpha > 0:
            cls.__last_round_image_alpha -= 15
            cls.__x_offset_for_last_round = int(cls._WIDTH / 4 - cls._WIDTH / 4 * cls.__last_round_image_alpha / 255)
        else:
            cls.__x_offset_for_last_round = 0
        if cls.__this_round_image_alpha < 255:
            cls.__this_round_image_alpha += 25
            cls.__x_offset_for_this_round = int(cls._WIDTH / 4 * cls.__this_round_image_alpha / 255 - cls._WIDTH / 4)
        else:
            cls.__x_offset_for_this_round = 0
        # 初始化被选择的角色名字
        cls.character_get_click = None
        # 画上上一幕的立绘
        if len(cls.__previous_characters) == len(cls.__current_characters):
            for i in range(len(cls.__previous_characters)):
                npcImg_x: int = cls.__estimate_x(surface.get_width(), len(cls.__previous_characters), i)
                # 渲染立绘
                if cls.__previous_characters[i].equal(cls.__current_characters[i], True):
                    cls.__display_character(cls.__current_characters[i], npcImg_x, 255, surface)
                else:
                    cls.__display_character(cls.__previous_characters[i], npcImg_x, cls.__last_round_image_alpha, surface)
                    cls.__display_character(cls.__current_characters[i], npcImg_x, cls.__this_round_image_alpha, surface)
        elif len(cls.__current_characters) == 0:
            cls.__fade_out_characters_last_round(surface)
        elif len(cls.__previous_characters) == 0:
            cls.__fade_in_characters_this_round(surface)
        else:
            # 初始化previous_x坐标
            previous_x: int = 0
            if len(cls.__previous_characters) == 1 and len(cls.__current_characters) == 2:
                previous_x = cls.__estimate_x(surface.get_width(), len(cls.__previous_characters), 0)
                # 如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if cls.__previous_characters[0].equal(cls.__current_characters[0]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                    # 渐入左边立绘
                    cls.__fade_in_and_out_characters(
                        cls.__previous_characters[0],
                        cls.__current_characters[0],
                        cls.__x_correction_offset_index
                        * (cls.__estimate_x(surface.get_width(), len(cls.__current_characters), 0) - previous_x)
                        // 100
                        + previous_x,
                        surface,
                    )
                    # 显示右边立绘
                    cls.__display_character(
                        cls.__current_characters[1], surface.get_width() // 2, cls.__this_round_image_alpha, surface
                    )
                # 如果之前的中间变成了现在的右边，则立绘应该先向右移动
                elif cls.__previous_characters[0].equal(cls.__current_characters[1]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                    # 显示左边立绘
                    cls.__display_character(cls.__current_characters[0], 0, cls.__this_round_image_alpha, surface)
                    # 渐入右边立绘
                    cls.__fade_in_and_out_characters(
                        cls.__previous_characters[0],
                        cls.__current_characters[1],
                        cls.__x_correction_offset_index
                        * (cls.__estimate_x(surface.get_width(), len(cls.__current_characters), 1) - previous_x)
                        // 100
                        + previous_x,
                        surface,
                    )
                # 之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘
                elif cls.__last_round_image_alpha > 0:
                    cls.__this_round_image_alpha -= 25
                    cls.__fade_out_characters_last_round(surface)
                else:
                    cls.__fade_in_characters_this_round(surface)
            elif len(cls.__previous_characters) == 2 and len(cls.__current_characters) == 1:
                current_x: int = cls.__estimate_x(surface.get_width(), len(cls.__current_characters), 0)
                # 如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if cls.__previous_characters[0].equal(cls.__current_characters[0]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                        previous_x = cls.__estimate_x(surface.get_width(), len(cls.__previous_characters), 0)
                        # 左边立绘向右移动
                        cls.__fade_in_and_out_characters(
                            cls.__previous_characters[0],
                            cls.__current_characters[0],
                            cls.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            surface,
                        )
                    else:
                        # 显示左方立绘
                        cls.__display_character(cls.__current_characters[0], current_x, cls.__this_round_image_alpha, surface)
                    # 右边立绘消失
                    cls.__display_character(
                        cls.__previous_characters[1], surface.get_width() // 2, cls.__last_round_image_alpha, surface
                    )
                # 如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif cls.__previous_characters[1].equal(cls.__current_characters[0]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                        previous_x = cls.__estimate_x(surface.get_width(), len(cls.__previous_characters), 1)
                        # 右边立绘向左移动
                        cls.__fade_in_and_out_characters(
                            cls.__previous_characters[1],
                            cls.__current_characters[0],
                            cls.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            surface,
                        )
                    else:
                        # 显示右方立绘
                        cls.__display_character(cls.__current_characters[0], current_x, cls.__this_round_image_alpha, surface)
                    # 左边立绘消失
                    cls.__display_character(cls.__previous_characters[0], 0, cls.__last_round_image_alpha, surface)
                elif cls.__last_round_image_alpha > 0:
                    cls.__this_round_image_alpha -= 25
                    cls.__fade_out_characters_last_round(surface)
                else:
                    cls.__fade_in_characters_this_round(surface)
            elif cls.__last_round_image_alpha > 0:
                cls.__this_round_image_alpha -= 25
                cls.__fade_out_characters_last_round(surface)
            else:
                cls.__fade_in_characters_this_round(surface)

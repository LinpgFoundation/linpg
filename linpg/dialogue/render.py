from .component import *


# 角色立绘滤镜
class AbstractVisualNovelCharacterImageFilterEffect(ABC):
    # 将滤镜应用到立绘上并渲染到屏幕上
    @abstractmethod
    def render(self, characterImage: StaticImage, _surface: ImageSurface, is_silent: bool) -> None:
        EXCEPTION.fatal("render()", 1)


# 角色立绘系统
class VisualNovelCharacterImageManager:
    # 用于存放立绘的字典
    __character_image: Final[dict[str, tuple[StaticImage, ...]]] = {}
    # 存放前一对话的参与角色名称
    __previous_characters: tuple[pyvns.Naming, ...] = tuple()
    __last_round_image_alpha: int = 2550
    # 存放当前对话的参与角色名称
    __current_characters: tuple[pyvns.Naming, ...] = tuple()
    __this_round_image_alpha: int = 0
    # 滤镜
    FILTERS: Final[dict[str, AbstractVisualNovelCharacterImageFilterEffect]] = {}
    # 暗度
    DARKNESS: int = 50
    # 移动的x
    __x_correction_offset_index: int = 0
    # x轴offset
    __x_offset_for_this_round: int = 0
    __x_offset_for_last_round: int = 0
    # 开发者模式
    dev_mode: bool = False
    # 被点击的角色
    character_get_click: str | None = None

    # 立绘边长
    @staticmethod
    def __GET_WIDTH() -> int:
        return Display.get_width() // 2

    # 重置并卸载占用的内存
    @classmethod
    def reset(cls) -> None:
        cls.__previous_characters = tuple()
        cls.__last_round_image_alpha = 2550
        cls.__current_characters = tuple()
        cls.__this_round_image_alpha = 0
        cls.__character_image.clear()

    # 画出角色
    @classmethod
    def __display_character(cls, _name_data: pyvns.Naming, x: int, alpha: int, _surface: ImageSurface) -> None:
        if alpha > 0:
            # 确保角色存在
            if _name_data.name not in cls.__character_image:
                # 如果不能存在，则加载角色
                imgTemp: StaticImage = StaticImage(Specification.get_directory("character_image", _name_data.name), 0, 0, cls.__GET_WIDTH(), cls.__GET_WIDTH())
                # 以tuple的形式保存立绘，index 0 是正常图片， index 1 是深色图片
                cls.__character_image[_name_data.name] = (imgTemp, imgTemp.copy())
                # 生成深色图片
                cls.__character_image[_name_data.name][1].add_darkness(cls.DARKNESS)
            # 是否角色沉默
            isNpcSilent: bool = "silent" in _name_data.tags
            # 获取npc立绘的指针
            img: StaticImage = cls.__character_image[_name_data.name][1 if isNpcSilent else 0]
            img.set_size(cls.__GET_WIDTH(), cls.__GET_WIDTH())
            img.set_alpha(alpha)
            img.set_pos(x, Display.get_height() - cls.__GET_WIDTH())
            # 获取tag长度
            _tags_len = len(_name_data.tags)
            # 不需要渲染silent标签
            if isNpcSilent is True:
                _tags_len -= 1
            if _tags_len > 0:
                for _tag in _name_data.tags:
                    if _tag != "silent":
                        cls.FILTERS[_tag].render(img, _surface, isNpcSilent)
            else:
                img.set_crop_rect(None)
                img.draw(_surface)
            # 如果是开发模式
            if cls.dev_mode is True and img.is_hovered():
                img.draw_outline(_surface)
                cls.character_get_click = str(_name_data)

    # 根据参数计算立绘的x坐标
    @staticmethod
    def __estimate_x(_width: int, _num: int, _index: int) -> int:
        if _num == 1:
            return _width // 4
        elif _num == 2:
            return _index * _width // _num
        elif _num > 2:
            return int((_index + 1) * _width / (_num + 1) - _width / 4) if _num % 2 == 0 else int((_index - _num // 2) * _width / _num + _width / 4)
        else:
            return 0

    # 渐入name1角色的同时淡出name2角色
    @classmethod
    def __fade_in_and_out_characters(cls, name1: pyvns.Naming, name2: pyvns.Naming, x: int, _surface: ImageSurface) -> None:
        cls.__display_character(name1, x, cls.__last_round_image_alpha // 10, _surface)
        cls.__display_character(name2, x, cls.__this_round_image_alpha // 10, _surface)

    # 渐入所有当前的角色
    @classmethod
    def __fade_in_characters_this_round(cls, _surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(cls.__current_characters)):
            cls.__display_character(
                cls.__current_characters[i],
                cls.__estimate_x(_surface.get_width(), len(cls.__current_characters), i) + cls.__x_offset_for_this_round,
                cls.__this_round_image_alpha // 10,
                _surface,
            )

    # 淡出所有之前的角色
    @classmethod
    def __fade_out_characters_last_round(cls, _surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(cls.__previous_characters)):
            cls.__display_character(
                cls.__previous_characters[i],
                cls.__estimate_x(_surface.get_width(), len(cls.__previous_characters), i) + cls.__x_offset_for_last_round,
                cls.__last_round_image_alpha // 10,
                _surface,
            )

    # 更新立绘
    @classmethod
    def update(cls, characterNameList: Sequence[str] | None) -> None:
        cls.__previous_characters = cls.__current_characters
        cls.__current_characters = tuple(pyvns.Naming(_name) for _name in characterNameList) if characterNameList is not None else tuple()
        cls.__last_round_image_alpha = 2550
        cls.__this_round_image_alpha = 50
        cls.__x_correction_offset_index = 0

    # 将立绘画到屏幕上
    @classmethod
    def draw(cls, _surface: ImageSurface) -> None:
        # 更新alpha值，并根据alpha值计算offset
        if cls.__last_round_image_alpha > 0:
            cls.__last_round_image_alpha -= Display.get_delta_time() * 8
            cls.__x_offset_for_last_round = int(cls.__GET_WIDTH() / 4 - cls.__GET_WIDTH() / 4 * cls.__last_round_image_alpha / 2550)
        else:
            cls.__x_offset_for_last_round = 0
        if cls.__this_round_image_alpha < 2550:
            cls.__this_round_image_alpha += Display.get_delta_time() * 15
            cls.__x_offset_for_this_round = int(cls.__GET_WIDTH() / 4 * cls.__this_round_image_alpha / 2550 - cls.__GET_WIDTH() / 4)
        else:
            cls.__x_offset_for_this_round = 0
        # 初始化被选择的角色名字
        cls.character_get_click = None
        # 画上上一幕的立绘
        if len(cls.__previous_characters) == len(cls.__current_characters):
            for i, _characterName in enumerate(cls.__previous_characters):
                npcImg_x: int = cls.__estimate_x(_surface.get_width(), len(cls.__previous_characters), i)
                # 渲染立绘
                if _characterName.equal(cls.__current_characters[i], True):
                    cls.__display_character(cls.__current_characters[i], npcImg_x, 255, _surface)
                else:
                    cls.__display_character(_characterName, npcImg_x, cls.__last_round_image_alpha // 10, _surface)
                    cls.__display_character(cls.__current_characters[i], npcImg_x, cls.__this_round_image_alpha // 10, _surface)
        elif len(cls.__current_characters) == 0:
            cls.__fade_out_characters_last_round(_surface)
        elif len(cls.__previous_characters) == 0:
            cls.__fade_in_characters_this_round(_surface)
        else:
            # 初始化previous_x坐标
            previous_x: int
            if len(cls.__previous_characters) == 1 and len(cls.__current_characters) == 2:
                previous_x = cls.__estimate_x(_surface.get_width(), len(cls.__previous_characters), 0)
                # 如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if cls.__previous_characters[0].equal(cls.__current_characters[0]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                    # 渐入左边立绘
                    cls.__fade_in_and_out_characters(
                        cls.__previous_characters[0],
                        cls.__current_characters[0],
                        cls.__x_correction_offset_index * (cls.__estimate_x(_surface.get_width(), len(cls.__current_characters), 0) - previous_x) // 100
                        + previous_x,
                        _surface,
                    )
                    # 显示右边立绘
                    cls.__display_character(cls.__current_characters[1], _surface.get_width() // 2, cls.__this_round_image_alpha // 10, _surface)
                # 如果之前的中间变成了现在的右边，则立绘应该先向右移动
                elif cls.__previous_characters[0].equal(cls.__current_characters[1]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                    # 显示左边立绘
                    cls.__display_character(cls.__current_characters[0], 0, cls.__this_round_image_alpha // 10, _surface)
                    # 渐入右边立绘
                    cls.__fade_in_and_out_characters(
                        cls.__previous_characters[0],
                        cls.__current_characters[1],
                        cls.__x_correction_offset_index * (cls.__estimate_x(_surface.get_width(), len(cls.__current_characters), 1) - previous_x) // 100
                        + previous_x,
                        _surface,
                    )
                # 之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘
                elif cls.__last_round_image_alpha > 0:
                    cls.__this_round_image_alpha -= Display.get_delta_time() * 15
                    cls.__fade_out_characters_last_round(_surface)
                else:
                    cls.__fade_in_characters_this_round(_surface)
            elif len(cls.__previous_characters) == 2 and len(cls.__current_characters) == 1:
                current_x: int = cls.__estimate_x(_surface.get_width(), len(cls.__current_characters), 0)
                # 如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if cls.__previous_characters[0].equal(cls.__current_characters[0]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                        previous_x = cls.__estimate_x(_surface.get_width(), len(cls.__previous_characters), 0)
                        # 左边立绘向右移动
                        cls.__fade_in_and_out_characters(
                            cls.__previous_characters[0],
                            cls.__current_characters[0],
                            cls.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            _surface,
                        )
                    else:
                        # 显示左方立绘
                        cls.__display_character(cls.__current_characters[0], current_x, cls.__this_round_image_alpha // 10, _surface)
                    # 右边立绘消失
                    cls.__display_character(cls.__previous_characters[1], _surface.get_width() // 2, cls.__last_round_image_alpha // 10, _surface)
                # 如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif cls.__previous_characters[1].equal(cls.__current_characters[0]):
                    if cls.__x_correction_offset_index < 100:
                        cls.__x_correction_offset_index += 10
                        previous_x = cls.__estimate_x(_surface.get_width(), len(cls.__previous_characters), 1)
                        # 右边立绘向左移动
                        cls.__fade_in_and_out_characters(
                            cls.__previous_characters[1],
                            cls.__current_characters[0],
                            cls.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            _surface,
                        )
                    else:
                        # 显示右方立绘
                        cls.__display_character(cls.__current_characters[0], current_x, cls.__this_round_image_alpha // 10, _surface)
                    # 左边立绘消失
                    cls.__display_character(cls.__previous_characters[0], 0, cls.__last_round_image_alpha // 10, _surface)
                elif cls.__last_round_image_alpha > 0:
                    cls.__this_round_image_alpha -= Display.get_delta_time() * 15
                    cls.__fade_out_characters_last_round(_surface)
                else:
                    cls.__fade_in_characters_this_round(_surface)
            elif cls.__last_round_image_alpha > 0:
                cls.__this_round_image_alpha -= Display.get_delta_time() * 15
                cls.__fade_out_characters_last_round(_surface)
            else:
                cls.__fade_in_characters_this_round(_surface)

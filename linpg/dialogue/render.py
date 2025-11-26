from .component import *


# 角色立绘滤镜
class AbstractVisualNovelCharacterImageFilterEffect(ABC):
    # 将滤镜应用到立绘上并渲染到屏幕上
    @abstractmethod
    def render(self, characterImage: StaticImage, _surface: ImageSurface, is_silent: bool) -> None:
        Exceptions.fatal("render()", 1)


# 角色立绘系统
class VisualNovelCharacterImageManager:
    # is character image pixelated
    IS_PIXELATED = False
    # 立绘宽高比例
    IMAGE_SCALE_W: int = 50
    # 暗度
    DARKNESS: int = 50
    # 滤镜
    FILTERS: Final[dict[str, AbstractVisualNovelCharacterImageFilterEffect]] = {}

    def __init__(self) -> None:
        # 用于存放立绘的字典
        self.__character_image: Final[dict[str, tuple[StaticImage, ...]]] = {}
        # 存放前一对话的参与角色名称
        self.__previous_characters: tuple[pyvns.Naming, ...] = tuple()
        self.__last_round_image_alpha: int = 2550
        # 存放当前对话的参与角色名称
        self._current_characters: tuple[pyvns.Naming, ...] = tuple()
        self.__this_round_image_alpha: int = 0
        # 移动的x
        self.__x_correction_offset_index: int = 0
        # x轴offset
        self.__x_offset_for_this_round: int = 0
        self.__x_offset_for_last_round: int = 0
        # 开发者模式
        self.__dev_mode: bool = False
        # 被点击的角色
        self.character_get_hover: str | None = None

    # 设置开发者模式
    def set_dev_mode(self, is_dev: bool) -> None:
        self.__dev_mode = is_dev

    # 重置并卸载占用的内存
    def reset(self) -> None:
        self.__previous_characters = tuple()
        self.__last_round_image_alpha = 2550
        self._current_characters = tuple()
        self.__this_round_image_alpha = 0
        self.__character_image.clear()

    # 画出角色
    def _display_character(
        self,
        _name_data: pyvns.Naming,
        x: int,
        alpha: int,
        _surface: ImageSurface,
        y_alignment: Literal["center", "bottom"] = "center",
    ) -> None:
        if alpha > 0:
            # 确保角色存在
            if _name_data.get_name() not in self.__character_image:
                # 如果不能存在，则加载角色
                imgTemp: StaticImage = StaticImage(
                    Specifications.get_directory("character_image", _name_data.get_name()),
                    enable_cropping=True,
                    is_pixelated=self.IS_PIXELATED,
                )
                # 以tuple的形式保存立绘，index 0 是正常图片， index 1 是深色图片
                self.__character_image[_name_data.get_name()] = (imgTemp, imgTemp.copy())
                # 生成深色图片
                self.__character_image[_name_data.get_name()][1].add_darkness(self.DARKNESS)
            # 是否角色沉默
            isNpcSilent: bool = _name_data.contains_tag("silent")
            # 获取npc立绘的指针
            img: StaticImage = self.__character_image[_name_data.get_name()][1 if isNpcSilent else 0]
            img.set_width_with_original_image_size_locked(_surface.get_width() * self.IMAGE_SCALE_W // 100)
            img.set_alpha(alpha)
            img.set_left(x)
            if y_alignment == "center":
                img.set_pos(x, (Display.get_height() - img.get_height()) // 2)
            elif y_alignment == "bottom":
                img.set_bottom(_surface.get_height())
            else:
                raise ValueError("y_alignment must be 'center' or 'bottom'")
            # 获取tag长度
            _tags_len = len(_name_data.get_tags())
            # 不需要渲染silent标签
            if isNpcSilent is True:
                _tags_len -= 1
            if _tags_len > 0:
                for _tag in _name_data.get_tags():
                    if _tag != "silent":
                        self.FILTERS[_tag].render(img, _surface, isNpcSilent)
            else:
                img.set_crop_rect(None)
                img.draw(_surface)
            # 如果是开发模式
            if self.__dev_mode is True and img.is_hovered():
                img.draw_outline(_surface)
                self.character_get_hover = _name_data.to_string()

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
    def __fade_in_and_out_characters(self, name1: pyvns.Naming, name2: pyvns.Naming, x: int, _surface: ImageSurface) -> None:
        self._display_character(name1, x, self.__last_round_image_alpha // 10, _surface)
        self._display_character(name2, x, self.__this_round_image_alpha // 10, _surface)

    # 渐入所有当前的角色
    def __fade_in_characters_this_round(self, _surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(self._current_characters)):
            self._display_character(
                self._current_characters[i],
                self.__estimate_x(_surface.get_width(), len(self._current_characters), i) + self.__x_offset_for_this_round,
                self.__this_round_image_alpha // 10,
                _surface,
            )

    # 淡出所有之前的角色
    def __fade_out_characters_last_round(self, _surface: ImageSurface, _start: int = 0) -> None:
        for i in range(_start, len(self.__previous_characters)):
            self._display_character(
                self.__previous_characters[i],
                self.__estimate_x(_surface.get_width(), len(self.__previous_characters), i) + self.__x_offset_for_last_round,
                self.__last_round_image_alpha // 10,
                _surface,
            )

    # 更新立绘
    def update(self, characterNameList: Sequence[str] | None) -> None:
        self.__previous_characters = self._current_characters
        self._current_characters = (
            tuple(pyvns.Naming(_name) for _name in characterNameList) if characterNameList is not None else tuple()
        )
        self.__last_round_image_alpha = 2550
        self.__this_round_image_alpha = 50
        self.__x_correction_offset_index = 0

    # 将立绘画到屏幕上
    def draw(self, _surface: ImageSurface) -> None:
        current_w: float = _surface.get_width() * self.IMAGE_SCALE_W / 100
        # 更新alpha值，并根据alpha值计算offset
        if self.__last_round_image_alpha > 0:
            self.__last_round_image_alpha -= Display.get_delta_time() * 8
            self.__x_offset_for_last_round = int(current_w / 4 - current_w / 4 * self.__last_round_image_alpha / 2550)
        else:
            self.__x_offset_for_last_round = 0
        if self.__this_round_image_alpha < 2550:
            self.__this_round_image_alpha += Display.get_delta_time() * 15
            self.__x_offset_for_this_round = int(current_w / 4 * self.__this_round_image_alpha / 2550 - current_w / 4)
        else:
            self.__x_offset_for_this_round = 0
        # 初始化被选择的角色名字
        self.character_get_hover = None
        # 画上上一幕的立绘
        if len(self.__previous_characters) == len(self._current_characters):
            for i, _characterName in enumerate(self.__previous_characters):
                npcImg_x: int = self.__estimate_x(_surface.get_width(), len(self.__previous_characters), i)
                # 渲染立绘
                if _characterName.equal(self._current_characters[i], True):
                    self._display_character(self._current_characters[i], npcImg_x, 255, _surface)
                else:
                    self._display_character(_characterName, npcImg_x, self.__last_round_image_alpha // 10, _surface)
                    self._display_character(
                        self._current_characters[i], npcImg_x, self.__this_round_image_alpha // 10, _surface
                    )
        elif len(self._current_characters) == 0:
            self.__fade_out_characters_last_round(_surface)
        elif len(self.__previous_characters) == 0:
            self.__fade_in_characters_this_round(_surface)
        else:
            # 初始化previous_x坐标
            previous_x: int
            if len(self.__previous_characters) == 1 and len(self._current_characters) == 2:
                previous_x = self.__estimate_x(_surface.get_width(), len(self.__previous_characters), 0)
                # 如果之前的中间变成了现在的左边，则立绘应该先向左移动
                if self.__previous_characters[0].equal(self._current_characters[0]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                    # 渐入左边立绘
                    self.__fade_in_and_out_characters(
                        self.__previous_characters[0],
                        self._current_characters[0],
                        self.__x_correction_offset_index
                        * (self.__estimate_x(_surface.get_width(), len(self._current_characters), 0) - previous_x)
                        // 100
                        + previous_x,
                        _surface,
                    )
                    # 显示右边立绘
                    self._display_character(
                        self._current_characters[1], _surface.get_width() // 2, self.__this_round_image_alpha // 10, _surface
                    )
                # 如果之前的中间变成了现在的右边，则立绘应该先向右移动
                elif self.__previous_characters[0].equal(self._current_characters[1]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                    # 显示左边立绘
                    self._display_character(self._current_characters[0], 0, self.__this_round_image_alpha // 10, _surface)
                    # 渐入右边立绘
                    self.__fade_in_and_out_characters(
                        self.__previous_characters[0],
                        self._current_characters[1],
                        self.__x_correction_offset_index
                        * (self.__estimate_x(_surface.get_width(), len(self._current_characters), 1) - previous_x)
                        // 100
                        + previous_x,
                        _surface,
                    )
                # 之前的中间和现在两边无任何关系，先隐藏之前的立绘，然后显示现在的立绘
                elif self.__last_round_image_alpha > 0:
                    self.__this_round_image_alpha -= Display.get_delta_time() * 15
                    self.__fade_out_characters_last_round(_surface)
                else:
                    self.__fade_in_characters_this_round(_surface)
            elif len(self.__previous_characters) == 2 and len(self._current_characters) == 1:
                current_x: int = self.__estimate_x(_surface.get_width(), len(self._current_characters), 0)
                # 如果之前的左边变成了现在的中间，则立绘应该先向右边移动
                if self.__previous_characters[0].equal(self._current_characters[0]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                        previous_x = self.__estimate_x(_surface.get_width(), len(self.__previous_characters), 0)
                        # 左边立绘向右移动
                        self.__fade_in_and_out_characters(
                            self.__previous_characters[0],
                            self._current_characters[0],
                            self.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            _surface,
                        )
                    else:
                        # 显示左方立绘
                        self._display_character(
                            self._current_characters[0], current_x, self.__this_round_image_alpha // 10, _surface
                        )
                    # 右边立绘消失
                    self._display_character(
                        self.__previous_characters[1], _surface.get_width() // 2, self.__last_round_image_alpha // 10, _surface
                    )
                # 如果之前的右边变成了现在的中间，则立绘应该先向左边移动
                elif self.__previous_characters[1].equal(self._current_characters[0]):
                    if self.__x_correction_offset_index < 100:
                        self.__x_correction_offset_index += 10
                        previous_x = self.__estimate_x(_surface.get_width(), len(self.__previous_characters), 1)
                        # 右边立绘向左移动
                        self.__fade_in_and_out_characters(
                            self.__previous_characters[1],
                            self._current_characters[0],
                            self.__x_correction_offset_index * (current_x - previous_x) // 100 + previous_x,
                            _surface,
                        )
                    else:
                        # 显示右方立绘
                        self._display_character(
                            self._current_characters[0], current_x, self.__this_round_image_alpha // 10, _surface
                        )
                    # 左边立绘消失
                    self._display_character(self.__previous_characters[0], 0, self.__last_round_image_alpha // 10, _surface)
                elif self.__last_round_image_alpha > 0:
                    self.__this_round_image_alpha -= Display.get_delta_time() * 15
                    self.__fade_out_characters_last_round(_surface)
                else:
                    self.__fade_in_characters_this_round(_surface)
            elif self.__last_round_image_alpha > 0:
                self.__this_round_image_alpha -= Display.get_delta_time() * 15
                self.__fade_out_characters_last_round(_surface)
            else:
                self.__fade_in_characters_this_round(_surface)

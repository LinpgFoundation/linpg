from .progressbar import *


# ui编译器
class UiGenerator:
    # 获取默认ui模板
    __UI_TEMPLATES: Final[dict] = Config.load_internal_file("ui.json")
    # 加载自定义的ui数据（如果存在）
    for key, value in Config.resolve_path_and_load_file(os.path.join("Data", "ui")).items():
        if key not in __UI_TEMPLATES:
            __UI_TEMPLATES[key] = {}
        __UI_TEMPLATES[key].update(value)

    # 尝试转换特殊的string
    @classmethod
    def __try_convert_string_to_number(cls, value: str, value_in_case_percentage: int, custom_values: dict) -> int:
        # 如果是百分比
        if value.endswith("%"):
            try:
                return int(Numbers.convert_percentage(value) * value_in_case_percentage)
            except Exception:
                EXCEPTION.fatal(f'Cannot convert "{value}" because it is not a valid percentage.')
        # 如果是需要从lookup表里寻找的参数
        elif value.startswith("<!") and value.endswith(">"):
            the_value = custom_values[value.removeprefix("<!").removesuffix(">")]
            if isinstance(the_value, str):
                return cls.__try_convert_string_to_number(the_value, value_in_case_percentage, custom_values)
            else:
                try:
                    return int(the_value)
                except Exception:
                    EXCEPTION.fatal(f'Cannot convert string "{value}".')
        # 尝试将
        else:
            try:
                return int(value)
            except Exception:
                EXCEPTION.fatal(f'Cannot convert string "{value}".')

    # 检测尺寸是否合法
    @classmethod
    def __convert_number(cls, item: dict, key: str, value_in_case_percentage: int, custom_values: dict) -> int:
        if key not in item:
            EXCEPTION.fatal(f'You have to set "{key}" for "{item["name"]}".' if "name" in item else f'You have to set "{key}".')
        elif isinstance(item[key], float):
            return int(item[key])
        elif not isinstance(item[key], int):
            if isinstance(item[key], str):
                return cls.__try_convert_string_to_number(item[key], value_in_case_percentage, custom_values)
            else:
                try:
                    return int(item[key])
                except Exception:
                    EXCEPTION.fatal(
                        f'The "{key}" for "{item["name"]}" needs to an integer instead of "{item[key]}".'
                        if "name" in item
                        else f'The "{key}" needs to an integer instead of "{item[key]}".'
                    )
        else:
            return int(item[key])

    # 检测坐标是否合法
    @classmethod
    def __convert_coordinate(cls, item: dict, key: str, value_in_case_center: int, value_in_case_percentage: int, custom_values: dict) -> int:
        if key not in item:
            return 0
        elif not isinstance(item[key], int):
            if item[key] == "center":
                return value_in_case_center
            elif isinstance(item[key], str):
                return cls.__try_convert_string_to_number(item[key], value_in_case_percentage, custom_values)
            else:
                try:
                    return int(item[key])
                except Exception:
                    EXCEPTION.fatal(f"Valid value for {key}: {item[key]}.")
        else:
            return int(item[key])

    # 转换文字
    @staticmethod
    def __load_text(text: str) -> str:
        if text.startswith("{") and text.endswith("}"):
            final_text_list: list = []
            text_index: int = 0
            find_close_bracket: bool = False
            while text_index < len(text):
                if text[text_index] == "{":
                    # 寻找 "}"
                    a: int = 0
                    for a in range(text_index + 1, len(text)):
                        if text[a] == "}":
                            find_close_bracket = True
                            break
                    if find_close_bracket is True:
                        find_close_bracket = False
                        final_text_list.append(Lang.get_text_by_keys(tuple(b.strip() for b in text[text_index + 1 : a].split("."))))
                        text_index = a
                    else:
                        EXCEPTION.fatal(f"Cannot find close bracket for text: {text}")
                else:
                    final_text_list.append(text[text_index])
                text_index += 1
            return "".join(final_text_list)
        # 加载自定义参数
        elif text.startswith("<") and text.startswith(">"):
            _key: str = text[1 : len(text) - 1]
            if _key != "NULL":
                return Specification.get_str(*(b.strip() for b in _key.split(".")))
        return text

    # 生成容器类
    @classmethod
    def __generate_container(cls, data: dict, custom_values: dict, max_width: int = -1, max_height: int = -1) -> GameObjectsDictContainer:
        # 如果没有提供最大高度，则默认使用屏幕高度
        if max_height < 0:
            max_height = Display.get_height()  # 如果没有提供最大宽度，则默认使用屏幕宽度
        if max_width < 0:
            max_width = Display.get_width()
        # 转换尺寸
        object_width: int = cls.__convert_number(data, "width", max_width, custom_values)
        object_height: int = cls.__convert_number(data, "height", max_height, custom_values)
        # 如果对象是容器
        if "src" not in data:
            data["src"] = None
        # 生成容器
        container_t: GameObjectsDictContainer = GameObjectsDictContainer(
            data["src"],
            cls.__convert_coordinate(data, "x", (max_width - object_width) // 2, max_width, custom_values),
            cls.__convert_coordinate(data, "y", (max_height - object_height) // 2, max_height, custom_values),
            object_width,
            object_height,
            data["name"] if "name" in data else "",
        )
        # 加载数据
        if "visibility" in data:
            container_t.set_visible(data["visibility"])
        if "items" in data:
            for each_item in data["items"]:
                item_r = cls.__generate(each_item, custom_values, container_t.get_width(), container_t.get_height())
                if item_r.tag != "":
                    container_t.set(item_r.tag, item_r)
                else:
                    container_t.set(f"item{container_t.item_num}", item_r)
        return container_t

    # 生成UI主模块
    @classmethod
    def __generate(cls, data: dict, custom_values: dict, max_width: int = -1, max_height: int = -1) -> GameObject2d:
        # 如果对象是容器
        if data["type"] == "container":
            return cls.__generate_container(data, custom_values, max_width, max_height)
        else:
            # 如果没有提供最大高度，则默认使用屏幕高度
            if max_height < 0:
                max_height = Display.get_height()
            item_t: GameObject2d
            # 如果对象是文字
            if data["type"] == "text" or data["type"] == "text&resize_when_hovered" or data["type"] == "drop_down_single_choice_list":
                # 转换字体大小
                font_size: int = cls.__convert_number(data, "font_size", max_height, custom_values)
                # 补充可选参数
                if "color" not in data:
                    data["color"] = Colors.BLACK
                if "bold" not in data:
                    data["bold"] = False
                if "italic" not in data:
                    data["italic"] = False
                if "src" not in data:
                    data["src"] = None
                elif data["src"] is not None:
                    data["src"] = cls.__load_text(str(data["src"]))
                # 生成文字图层
                if isinstance(data["type"], str) and data["type"].startswith("text"):
                    _info: list[str] = data["type"].split("&")
                    if len(_info) < 2:
                        item_t = TextSurface(data["src"], 0, 0, font_size, data["color"], data["bold"], data["italic"])
                    elif _info[1] == "resize_when_hovered":
                        item_t = ResizeWhenHoveredTextSurface(data["src"], 0, 0, font_size, font_size * 3 / 2, data["color"], data["bold"], data["italic"])
                    else:
                        EXCEPTION.fatal(f'Unrecognized text format "{_info[1]}"')
                    if (outline_thickness := data.get("outline_thickness", 0)) > 0:
                        item_t.set_outline_thickness(outline_thickness)
                    if (outline_color := data.get("outline_color")) is not None:
                        item_t.set_outline_color(outline_color)
                else:
                    item_t = DropDownList(data["src"], 0, 0, font_size, data["color"])
            else:
                # 如果没有提供最大宽度，则默认使用屏幕宽度
                if max_width < 0:
                    max_width = Display.get_width()
                # 转换尺寸
                object_width: int = cls.__convert_number(data, "width", max_width, custom_values)
                object_height: int = cls.__convert_number(data, "height", max_height, custom_values)
                match data["type"]:
                    case "button":
                        if "alpha_when_not_hover" not in data:
                            data["alpha_when_not_hover"] = 255
                        item_t = Button.load(data["src"], ORIGIN, (object_width, object_height), data["alpha_when_not_hover"])
                        if "text" in data:
                            item_t.set_text(
                                ButtonComponent.text(
                                    cls.__load_text(data["text"]["src"]),
                                    object_height / 2,
                                    data["text"]["color"],
                                    alpha_when_not_hover=data["alpha_when_not_hover"],
                                )
                            )
                        if "icon" in data:
                            # 转换尺寸
                            _icon_width: int = cls.__convert_number(data["icon"], "width", max_width, custom_values)
                            _icon_height: int = cls.__convert_number(data["icon"], "height", max_height, custom_values)
                            item_t.set_icon(ButtonComponent.icon(data["icon"]["src"], (_icon_width, _icon_height), data["alpha_when_not_hover"]))
                        if "scale_for_resizing_width" in data:
                            item_t.set_scale_for_resizing_width(data["scale_for_resizing_width"])
                        if "scale_for_resizing_height" in data:
                            item_t.set_scale_for_resizing_height(data["scale_for_resizing_height"])
                        if "auto_resize" in data:
                            item_t.set_auto_resize(data["auto_resize"])
                        if "description" in data:
                            item_t.set_description(cls.__load_text(data["description"]))
                        if "name" not in data:
                            EXCEPTION.fatal("You have to set a name for button type.")
                    case "progress_bar_adjuster":
                        # 确认按钮存在
                        if "indicator" not in data:
                            EXCEPTION.fatal("You need to set a indicator for progress_bar_adjuster!")
                        # 设置模式
                        if "mode" not in data:
                            data["mode"] = Axis.HORIZONTAL
                        # 生成ProgressBarAdjuster
                        item_t = ProgressBarAdjuster(
                            data["src"][0],
                            data["src"][1],
                            data["indicator"]["src"],
                            0,
                            0,
                            object_width,
                            object_height,
                            cls.__convert_number(data["indicator"], "width", object_width, custom_values),
                            cls.__convert_number(data["indicator"], "height", object_height, custom_values),
                            data["mode"],
                        )
                        if "name" not in data:
                            EXCEPTION.fatal("You have to set a name for button type.")
                    case "image":
                        item_t = StaticImage(data["src"], 0, 0, object_width, object_height)
                    case _:
                        EXCEPTION.fatal("Current type is not supported")
            # 如果有名字，则以tag的形式进行标注
            item_t.tag = data["name"] if "name" in data else ""
            # 透明度
            if "visibility" in data:
                if isinstance(item_t, Hidable):
                    item_t.set_visible(data["visibility"])
                else:
                    EXCEPTION.fatal("This is not a subtype of Hidable!")
            # 设置坐标
            item_t.set_pos(
                cls.__convert_coordinate(data, "x", (max_width - item_t.get_width()) // 2, max_width, custom_values),
                cls.__convert_coordinate(data, "y", (max_height - item_t.get_height()) // 2, max_height, custom_values),
            )
            return item_t

    # 将数据以dict的形式返回
    @classmethod
    def __get_data_in_dict(cls, data: str | dict) -> dict:
        if isinstance(data, str):
            result: dict | None = cls.__UI_TEMPLATES.get(data)
            if result is None:
                EXCEPTION.fatal(f'The ui called "{data}" does not exist!')
            return copy.deepcopy(result)
        else:
            return copy.deepcopy(data)

    # 生成GameObject2d - 如果目标是str则视为是名称，尝试从ui数据库中加载对应的模板，否则则视为模板
    @classmethod
    def generate(cls, data: str | dict, custom_values: dict = {}) -> GameObject2d:
        return cls.__generate(cls.__get_data_in_dict(data), custom_values)

    # 生成container - 如果目标是str则视为是名称，尝试从ui数据库中加载对应的模板，否则则视为模板
    @classmethod
    def generate_container(cls, data: str | dict, custom_values: dict = {}) -> GameObjectsDictContainer:
        data_dict: dict = cls.__get_data_in_dict(data)
        if data_dict["type"] != "container":
            EXCEPTION.fatal(f'The target has to be a container, not "{data_dict["type"]}".')
        return cls.__generate_container(data_dict, custom_values)


UI: UiGenerator = UiGenerator()

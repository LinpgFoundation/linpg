from collections import deque
from .progressbar import *


class UiGenerator:
    def __init__(self) -> None:
        self.__default_pos: int = 0
        self.__DEFAULT_UI: dict = Config.load_internal("ui.json")

    # 检测尺寸是否合法
    def __make_sure_size(self, item: dict, key: str, value_in_case_percentage: int) -> None:
        if key not in item:
            EXCEPTION.fatal(
                'You have to set "{0}" for "{1}".'.format(key, item["name"])
                if "name" in item
                else 'You have to set "{}".'.format(key)
            )
        elif isinstance(item[key], float):
            item[key] = int(item[key])
        elif not isinstance(item[key], int):
            if isinstance(item[key], str) and item[key].endswith("%"):
                try:
                    item[key] = int(convert_percentage(item[key]) * value_in_case_percentage)
                except Exception:
                    EXCEPTION.fatal(
                        'Cannot convert "{0}" because it is not a valid percentage for "{1}".'.format(
                            item[key], item["name"]
                        )
                        if "name" in item
                        else 'Cannot convert "{}" because it is not a valid percentage.'.format(item[key])
                    )
            else:
                try:
                    item[key] = int(item[key])
                except Exception:
                    EXCEPTION.fatal(
                        'The "{0}" for "{1}" needs to an interger instead of "{2}".'.format(key, item["name"], item[key])
                        if "name" in item
                        else 'The "{0}" needs to an interger instead of "{1}".'.format(key, item[key])
                    )

    # 检测坐标是否合法
    def __make_sure_pos(
        self,
        item: dict,
        key: str,
        value_in_case_center: int,
        value_in_case_percentage: int,
    ) -> None:
        if key not in item:
            item[key] = self.__default_pos
        elif not isinstance(item[key], int):
            if item[key] == "center":
                item[key] = value_in_case_center
            elif item[key].endswith("%"):
                try:
                    item[key] = int(convert_percentage(item[key]) * value_in_case_percentage)
                except Exception:
                    EXCEPTION.fatal(
                        'Cannot convert "{0}" because it is not a valid percentage for "{1}".'.format(
                            item[key], item["name"]
                        )
                        if "name" in item
                        else 'Cannot convert "{}" because it is not a valid percentage.'.format(item[key])
                    )
            else:
                EXCEPTION.fatal("Valid value for {0}: {1}.".format(key, item[key]))

    # 转换文字
    def convert_text(self, text: str) -> str:
        final_text_list: deque = deque()
        text_index: int = 0
        find_close_bracket: bool = False
        while text_index < len(text):
            if text[text_index] == "{":
                # 寻找 "}"
                for a in range(text_index + 1, len(text)):
                    if text[a] == "}":
                        find_close_bracket = True
                        break
                if find_close_bracket is True:
                    find_close_bracket = False
                    final_text_list.append(Lang.get_text_by_keys((b.strip() for b in text[text_index + 1 : a].split(","))))
                    text_index = a
                else:
                    EXCEPTION.fatal("Cannot find close bracket for text: {}".format())
            else:
                final_text_list.append(text[text_index])
            text_index += 1
        return "".join(final_text_list)

    # 生成引擎自带的默认UI
    def generate_deault(self, name: str) -> GameObject2d:
        try:
            ui_dict_t: dict = self.__DEFAULT_UI[name]
        except KeyError:
            EXCEPTION.fatal('The ui called "{}" does not exist!'.format(name))
        return self.generate(deepcopy(ui_dict_t))

    # 生成UI
    def generate(self, data: dict, max_width: int = -1, max_height: int = -1) -> GameObject2d:
        # 如果没有提供最大高度，则默认使用屏幕高度
        if max_height < 0:
            max_height = Display.get_height()
        # 如果对象是文字
        if data["type"] == "text" or data["type"] == "dynamic_text" or data["type"] == "drop_down_single_choice_list":
            # 转换字体大小
            self.__make_sure_size(data, "font_size", max_height)
            # 补充可选参数
            if "color" not in data:
                data["color"] = "black"
            if "bold" not in data:
                data["bold"] = False
            if "italic" not in data:
                data["italic"] = False
            if "src" not in data:
                data["src"] = None
            else:
                data["src"] = self.convert_text(data["src"])
            # 生成文字图层
            if data["type"] == "text":
                item_t = TextSurface(
                    Font.render(
                        data["src"],
                        data["color"],
                        data["font_size"],
                        data["bold"],
                        data["italic"],
                    ),
                    0,
                    0,
                )
            elif data["type"] == "dynamic_text":
                item_t = load_dynamic_text(
                    data["src"],
                    data["color"],
                    (0, 0),
                    data["font_size"],
                    data["bold"],
                    data["italic"],
                )
            else:
                item_t = DropDownSingleChoiceList(data["src"], 0, 0, data["font_size"], data["color"])
        else:
            # 如果没有提供最大宽度，则默认使用屏幕宽度
            if max_width < 0:
                max_width = Display.get_width()
            # 转换尺寸
            self.__make_sure_size(data, "width", max_width)
            self.__make_sure_size(data, "height", max_height)
            # 如果对象是容器
            if data["type"] == "container":
                # 转换坐标
                self.__make_sure_pos(data, "x", int((max_width - data["width"]) / 2), max_width)
                self.__make_sure_pos(data, "y", int((max_height - data["height"]) / 2), max_height)
                if "src" not in data:
                    data["src"] = None
                # 生成容器
                container_t = GameObjectsContainer(data["src"], data["x"], data["y"], data["width"], data["height"])
                # 加载数据
                if "hidden" in data:
                    container_t.hidden = data["hidden"]
                if "items" in data:
                    for each_item in data["items"]:
                        item_r = self.generate(each_item, container_t.get_width(), container_t.get_height())
                        if item_r.tag != "":
                            container_t.set(item_r.tag, item_r)
                        else:
                            container_t.set("item{}".format(container_t.item_num), item_r)
                return container_t
            elif data["type"] == "button":
                if "alpha_when_not_hover" not in data:
                    data["alpha_when_not_hover"] = 255
                item_t = (
                    load_button_with_text_in_center(
                        IMG.load(data["src"]),
                        self.convert_text(data["text"]["src"]),
                        data["text"]["color"],
                        data["height"],
                        Pos.ORIGIN,
                        data["alpha_when_not_hover"],
                    )
                    if "text" in data
                    else load_button(
                        IMG.load(data["src"]),
                        Pos.ORIGIN,
                        (data["width"], data["height"]),
                        data["alpha_when_not_hover"],
                    )
                )
                if not "name" in data:
                    EXCEPTION.fatal("You have to set a name for button type.")
            elif data["type"] == "progress_bar_adjuster":
                # 确认按钮存在
                try:
                    assert "indicator" in data
                except AssertionError:
                    EXCEPTION.fatal("You need to set a indicator for progress_bar_adjuster!")
                # 确认按钮有长宽
                self.__make_sure_size(data["indicator"], "width", data["width"])
                self.__make_sure_size(data["indicator"], "height", data["height"])
                if "mode" not in data:
                    data["mode"] = "horizontal"
                # 生成ProgressBarAdjuster
                item_t = ProgressBarAdjuster(
                    data["src"][0],
                    data["src"][1],
                    data["indicator"]["src"],
                    0,
                    0,
                    data["width"],
                    data["height"],
                    data["indicator"]["width"],
                    data["indicator"]["height"],
                    data["mode"],
                )
                if not "name" in data:
                    EXCEPTION.fatal("You have to set a name for button type.")
            elif data["type"] == "image":
                item_t = DynamicImage(data["src"], 0, 0, data["width"], data["height"])
            else:
                EXCEPTION.fatal("Current type is not supported")
        # 如果有名字，则以tag的形式进行标注
        item_t.tag = data["name"] if "name" in data else ""
        # 转换坐标
        self.__make_sure_pos(data, "x", int((max_width - item_t.get_width()) / 2), max_width)
        self.__make_sure_pos(data, "y", int((max_height - item_t.get_height()) / 2), max_height)
        item_t.set_pos(data["x"], data["y"])
        return item_t


UI: UiGenerator = UiGenerator()

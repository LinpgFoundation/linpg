# cython: language_level=3
from .function import *

class Converter:
    def __init__(self) -> None:
        self.__default_pos:int = 0
    #检测尺寸是否合法
    def __make_sure_size(self, item:dict, key:str, value_in_case_percentage:int) -> None:
        if key not in item:
            if "name" in item:
                throwException("error",'You have to set "{0}" for "{1}".'.format(key, item["name"]))
            else:
                throwException("error",'You have to set "{}".'.format(key))
        elif isinstance(item[key], float):
            item[key] = int(item[key])
        elif not isinstance(item[key], int):
            if isinstance(item[key], str) and item[key].endswith("%"):
                try:
                    item[key] = int(convert_percentage(item[key])*value_in_case_percentage)
                except:
                    if "name" in item:
                        throwException("error",'Cannot convert "{0}" because it is not a valid percentage for "{1}".'.format(item[key], item["name"]))
                    else:
                        throwException("error",'Cannot convert "{}" because it is not a valid percentage.'.format(item[key]))
            else:
                if "name" in item:
                    throwException("error",'The "{0}" for "{1}" needs to an interger instead of "{2}".'.format(key, item["name"], item[key]))
                else:
                    throwException("error",'The "{0}" needs to an interger instead of "{1}".'.format(key, item[key]))
    #检测坐标是否合法
    def __make_sure_pos(self, item:dict, key:str, value_in_case_center:int, value_in_case_percentage:int) -> None:
        if key not in item:
            item[key] = self.__default_pos
        elif not isinstance(item[key], int):
            if item[key] == "center":
                item[key] = value_in_case_center
            elif item[key].endswith("%"):
                try:
                    item[key] = int(convert_percentage(item[key])*value_in_case_percentage)
                except:
                    if "name" in item:
                        throwException("error",'Cannot convert "{0}" because it is not a valid percentage for "{1}".'.format(item[key], item["name"]))
                    else:
                        throwException("error",'Cannot convert "{}" because it is not a valid percentage.'.format(item[key]))
            else:
                throwException("error","Valid value for {0}: {1}.".format(key, item[key]))
    #生成UI
    def generate_ui(self, data:dict, max_width:int=-1, max_height:int=-1) -> GameObject2d:
        #如果没有提供最大高度，则默认使用屏幕高度
        if max_height < 0: max_height = display.get_height()
        #如果对象是文字
        if data["type"] == "text":
            #转换字体大小
            self.__make_sure_size(data, "font_size", max_height)
            #补充可选参数
            if "color" not in data: data["color"] = "black"
            if "bold" not in data: data["bold"] = False
            if "italic" not in data: data["italic"] = False
            #生成文字图层
            text_t = TextSurface(
                fontRenderWithoutBound(data["src"], data["color"], data["font_size"], data["bold"], data["italic"]), 0, 0
                )
            #转换坐标
            self.__make_sure_pos(data, "x", int((max_width-text_t.get_width())/2), max_width)
            self.__make_sure_pos(data, "y", int((max_height-text_t.get_height())/2), max_height)
            text_t.set_pos(data["x"], data["y"])
            return text_t
        else:
            #如果没有提供最大宽度，则默认使用屏幕宽度
            if max_width < 0: max_width = display.get_width()
            #转换尺寸
            self.__make_sure_size(data, "width", max_width)
            self.__make_sure_size(data, "height", max_height)
            #如果对象是容器
            if data["type"] == "container":
                #转换坐标
                self.__make_sure_pos(data, "x", int((max_width-data["width"])/2), max_width)
                self.__make_sure_pos(data, "y", int((max_height-data["height"])/2), max_height)
                #生成容器
                container_t = GameObjectContainer(data["src"],data["x"],data["y"],data["width"],data["height"])
                #加载数据
                if "hidden" in data:
                    container_t.hidden = data["hidden"]
                if "items" in data:
                    for each_item in data["items"]:
                        container_t.append(self.generate_ui(each_item, container_t.get_width(), container_t.get_height()))
                elif "item" in data:
                    #警告用户是items而不是item
                    throwException("warning", 'I think you mean "items" instead of "item", right?\
                        We will try to load it this time, but please double check ASAP!')
                    #好吧，我们还是会至少尝试加载
                    for each_item in data["item"]:
                        container_t.append(self.generate_ui(each_item, container_t.get_width(), container_t.get_height()))
                return container_t
            elif data["type"] == "button":
                if "alpha_when_not_hover" not in data: data["alpha_when_not_hover"] = 255
                button_t = loadButtonWithTextInCenter(
                    loadImg(data["src"]), data["text"]["scr"], data["text"]["color"], data["height"], (0,0), data["alpha_when_not_hover"]
                    ) if "text" in data else loadButton(
                        loadImg(data["src"]), (0,0), (data["width"], data["height"]), data["alpha_when_not_hover"]
                    )
                if "name" in data:
                    button_t.tag = data["name"]
                else:
                    throwException("error", "You have to set a name for button type.")
                #转换坐标
                self.__make_sure_pos(data, "x", int((max_width-button_t.get_width())/2), max_width)
                self.__make_sure_pos(data, "y", int((max_height-button_t.get_height())/2), max_height)
                #设置坐标
                button_t.set_pos(data["x"],data["y"])
                #返回按钮
                return button_t
            elif data["type"] == "image":
                image_t = loadImage(loadImg(data["src"]),(0,0),data["width"],data["height"])
                if "name" in data: image_t.tag = data["name"]
                #转换坐标
                self.__make_sure_pos(data, "x", int((max_width-image_t.get_width())/2), max_width)
                self.__make_sure_pos(data, "y", int((max_height-image_t.get_height())/2), max_height)
                #设置坐标
                image_t.set_pos(data["x"],data["y"])
                #返回图片
                return image_t
            else:
                throwException("error", "Current type is not supported")

converter:Converter = Converter()
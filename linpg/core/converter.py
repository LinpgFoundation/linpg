# cython: language_level=3
from .function import *

class Converter:
    def __init__(self) -> None:
        self.__default_pos:int = 0
    #检测尺寸是否合法
    def __make_sure_size(self, item:dict, key:str, value_in_case_percentage:int):
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
    #检测尺寸是否合法
    def __make_sure_pos(self, item:dict, key:str, value_in_case_center:int, value_in_case_percentage:int):
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
    #生成容器
    def generate_container(self, data:dict) -> GameObjectContainer:
        if "src" not in data: data["src"] = None
        #检查长宽
        self.__make_sure_size(data, "width", display.get_width())
        self.__make_sure_size(data, "height", display.get_height())
        #转换坐标
        self.__make_sure_pos(data, "x", int((display.get_width()-data["width"])/2), display.get_width())
        self.__make_sure_pos(data, "y", int((display.get_height()-data["height"])/2), display.get_height())
        #生成容器
        container = GameObjectContainer(data["src"],data["x"],data["y"],data["width"],data["height"])
        if "hidden" in data: container.hidden = data["hidden"]
        item_of_container:object = None
        for item in data["items"]:
            #初始化并生成图层
            if item["type"] == "text":
                #字体大小
                self.__make_sure_size(item, "font_size", container.get_height())
                #补充可选参数
                if "color" not in item: item["color"] = "black"
                if "bold" not in item: item["bold"] = False
                if "italic" not in item: item["italic"] = False
                #生成文字图层
                item_of_container = TextSurface(
                    fontRenderWithoutBound(item["src"], item["color"], item["font_size"], item["bold"], item["italic"]), 0, 0
                    )
            else:
                #检查长宽
                self.__make_sure_size(item, "width", container.get_width())
                self.__make_sure_size(item, "height", container.get_height())
                #生成图片图层
                if item["type"] == "image":
                    item_of_container = loadImage(loadImg(item["src"]),(0,0),item["width"],item["height"])
                    if "name" in item: item_of_container.tag = item["name"]
                elif item["type"] == "button":
                    item_of_container = loadButton(loadImg(item["src"]),(0,0),(item["width"],item["height"]))
                    if "name" in item:
                        item_of_container.tag = item["name"]
                    else:
                        throwException("error", "You have to set a name for button type.")

            #转换坐标
            self.__make_sure_pos(item, "x", int((container.get_width()-item_of_container.get_width())/2), container.get_width())
            self.__make_sure_pos(item, "y", int((container.get_height()-item_of_container.get_height())/2), container.get_height())
            item_of_container.set_pos(item["x"],item["y"])
            container.append(item_of_container)
        return container
    def load_container_from_config(self, path:str) -> GameObjectContainer: return self.generate_container(loadConfig(path))

converter:Converter = Converter()
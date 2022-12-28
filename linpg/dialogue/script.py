from typing import NoReturn
from .content import *

# 视觉小说脚本编译器
class _ScriptProcessor:

    # 立绘配置信息数据库
    __CHARACTER_IMAGE_DATABASE: Final[dict] = DataBase.get("Npc")
    # 文件格式后缀
    FILE_EXTENSION: Final[str] = ".linpg.script"

    def __init__(self) -> None:
        self.__path_in: str = ""
        self.__line_index: int = 0
        self.__output: dict = {}
        self.__current_data: DialogContent = DialogContent({}, "head")
        self.__id: int = -1
        self.__lang: str = ""
        self.__section: Optional[str] = None
        self.__last_dialog_id: Optional[str] = None
        self.__lines: list[str] = []
        self.__branch_labels: dict[str, str] = {}
        self.__dialog_associate_key: dict[str, str] = {}
        self.__accumulated_comments: list[str] = []
        self.__head_place: bool = False

    # 生成一个标准id
    @staticmethod
    def __generate_id(index: int) -> str:
        if index >= 10:
            return "id_" + str(index)
        elif index > 0:
            return "id_0" + str(index)
        else:
            return "head"

    # 转换一个str
    @staticmethod
    def __ensure_not_null(text: str) -> Optional[str]:
        return None if text.lower() == "null" or text.lower() == "none" else text

    # 将参数分离出来
    @classmethod
    def __extract_parameter(cls, text: str, prefix: str) -> Optional[str]:
        return cls.__ensure_not_null(cls.__extract_string(text, prefix))

    # 将字符串内容分离出来
    @staticmethod
    def __extract_string(text: str, prefix: str) -> str:
        sharp_index: int = text.find("#")
        return text.removeprefix(prefix) if sharp_index < 0 else text[:sharp_index].removeprefix(prefix)

    # 编译失败
    def __terminated(self, _reason: str) -> NoReturn:
        EXCEPTION.fatal(
            'File "{0}", line {1}\n  {2}\nFail to compile due to {3}'.format(self.__path_in, self.__line_index + 1, self.__get_current_line(), _reason)
        )

    # 获取当前行
    def __get_current_line(self) -> str:
        return self.__lines[self.__line_index].lstrip()

    # 获取输出
    def get_output(self) -> dict:
        return self.__output

    # 处理数据
    def process(self, _path: str) -> None:
        self.__path_in = _path
        if self.__path_in.endswith(self.FILE_EXTENSION):
            with open(self.__path_in, "r", encoding="utf-8") as f:
                self.__lines = f.readlines()
        # 如果文件为空
        if len(self.__lines) <= 0:
            self.__terminated("Cannot convert an empty script file!")
        else:
            last_label: Optional[str] = None
            # 预处理文件
            for index in range(len(self.__lines)):
                self.__lines[index] = self.__lines[index].removesuffix("\n")
                if self.__lines[index].startswith("[label]"):
                    if last_label is not None:
                        self.__terminated("The label is overwriting the previous one")
                    last_label = self.__extract_parameter(self.__lines[index], "[label]")
                if self.__lines[index].startswith("[section]"):
                    self.__head_place = False
                elif not self.__lines[index].startswith("[") and ":" in self.__lines[index]:
                    if self.__head_place is True:
                        self.__dialog_associate_key[str(index)] = self.__generate_id(len(self.__dialog_associate_key))
                    else:
                        self.__dialog_associate_key[str(index)] = "head"
                        self.__head_place = True
                    # 将id与label关联
                    if last_label is not None:
                        self.__branch_labels[last_label] = self.__dialog_associate_key[str(index)]
                        last_label = None
            if last_label is not None:
                EXCEPTION.warn("The last label call {} is not necessary!".format(last_label))
        self.__convert(0)
        self.__lines.clear()
        # 确保重要参数已被初始化
        if self.__id < 0:
            EXCEPTION.fatal("You have to set a nonnegative id!")
        elif len(self.__lang) <= 0:
            EXCEPTION.fatal("You have to set lang!")
        elif self.__section is None:
            EXCEPTION.fatal("You have to set section!")

    # 转换
    def __convert(self, staring_index: int) -> None:
        self.__line_index = staring_index
        while self.__line_index < len(self.__lines):
            _currentLine: str = self.__get_current_line()
            if len(_currentLine) <= 0 or self.__lines[self.__line_index].startswith("#"):
                pass
            elif _currentLine.startswith("//"):
                self.__accumulated_comments.append(_currentLine.lstrip("//").lstrip())
            else:
                # 背景图片
                if _currentLine.startswith("[bgi]"):
                    self.__current_data.background_image = self.__extract_parameter(_currentLine, "[bgi]")
                # 背景音乐
                elif _currentLine.startswith("[bgm]"):
                    self.__current_data.background_music = self.__extract_parameter(_currentLine, "[bgm]")
                # 角色进场
                elif _currentLine.startswith("[show]"):
                    for _name in self.__extract_string(_currentLine, "[show]").split():
                        self.__current_data.character_images.append(_name)
                # 角色退场
                elif _currentLine.startswith("[hide]"):
                    for _name in self.__extract_string(_currentLine, "[hide]").split():
                        # 清空角色列表
                        if _name == "*":
                            self.__current_data.character_images.clear()
                            break
                        # 移除角色
                        for i in range(len(self.__current_data.character_images)):
                            if VisualNovelCharacterImageNameMetaData(self.__current_data.character_images[i]).equal(
                                VisualNovelCharacterImageNameMetaData(_name)
                            ):
                                self.__current_data.character_images.pop(i)
                                break
                # 清空角色列表，然后让角色重新进场
                elif _currentLine.startswith("[display]"):
                    self.__current_data.character_images.clear()
                    for _name in self.__extract_string(_currentLine, "[display]").split():
                        self.__current_data.character_images.append(_name)
                # 章节id
                elif _currentLine.startswith("[id]"):
                    _id: Optional[str] = self.__extract_parameter(_currentLine, "[id]")
                    if _id is not None:
                        self.__id = int(_id)
                    else:
                        self.__terminated("Chapter id cannot be None!")
                # 语言
                elif _currentLine.startswith("[lang]"):
                    self.__lang = self.__extract_string(_currentLine, "[lang]")
                # 部分
                elif _currentLine.startswith("[section]"):
                    if self.__last_dialog_id is not None:
                        self.__output[self.__section][self.__last_dialog_id]["next_dialog_id"] = None
                    self.__section = self.__extract_string(_currentLine, "[section]")
                    self.__output[self.__section] = {}
                    self.__output[self.__section]["head"] = {}
                    self.__current_data = DialogContent({}, "head")
                    self.__last_dialog_id = None
                # 结束符
                elif _currentLine.startswith("[end]"):
                    self.__output[self.__section][self.__last_dialog_id]["next_dialog_id"] = None
                    break
                # 转换场景
                elif _currentLine.startswith("[scene]"):
                    self.__output[self.__section][self.__last_dialog_id]["next_dialog_id"]["type"] = "changeScene"
                    self.__current_data.background_image = self.__extract_parameter(_currentLine, "[scene]")
                    self.__last_dialog_id = None
                    self.__current_data.last = None
                # 选项
                elif _currentLine.startswith("[opt]"):
                    # 确认在接下来的一行有branch的label
                    if not self.__lines[self.__line_index + 1].startswith("[br]"):
                        self.__terminated("For option on line {}, a branch label is not found on the following line".format(self.__line_index + 1))
                    # 如果next_dialog_id没被初始化，则初始化
                    if self.__output[self.__section][self.__last_dialog_id].get("next_dialog_id") is None:
                        self.__output[self.__section][self.__last_dialog_id]["next_dialog_id"] = {}
                    # 获取对应的下一个对话字典的指针
                    dialog_next: dict = self.__output[self.__section][self.__last_dialog_id]["next_dialog_id"]
                    if dialog_next.get("type") != "option":
                        dialog_next["type"] = "option"
                        dialog_next["target"] = []
                    dialog_next["target"].append(
                        {
                            "text": self.__extract_string(_currentLine, "[opt]"),
                            "id": self.__branch_labels[self.__extract_string(self.__lines[self.__line_index + 1], "[br]")],
                        }
                    )
                    self.__line_index += 1
                elif not _currentLine.startswith("[") and ":" in _currentLine:
                    _narrator: Optional[str] = self.__ensure_not_null(_currentLine.removesuffix(" ").removesuffix(":"))
                    self.__current_data.narrator = _narrator if _narrator is not None else ""
                    # 获取讲述人可能的立绘名称
                    narrator_possible_images: tuple = tuple()
                    if self.__current_data.narrator.lower() in self.__CHARACTER_IMAGE_DATABASE:
                        narrator_possible_images = tuple(self.__CHARACTER_IMAGE_DATABASE[self.__current_data.narrator.lower()])
                    # 检查名称列表，更新character_images以确保不在说话的人处于黑暗状态
                    for i in range(len(self.__current_data.character_images)):
                        _name_data: VisualNovelCharacterImageNameMetaData = VisualNovelCharacterImageNameMetaData(self.__current_data.character_images[i])
                        if _name_data.name in narrator_possible_images:
                            _name_data.remove_tag("silent")
                        else:
                            _name_data.add_tag("silent")
                        self.__current_data.character_images[i] = _name_data.get_raw_name()
                    # 更新对话内容
                    self.__current_data.contents.clear()
                    for sub_index in range(self.__line_index + 1, len(self.__lines)):
                        if self.__lines[sub_index].startswith("- "):
                            self.__current_data.contents.append(self.__extract_string(self.__lines[sub_index], "- "))
                        else:
                            break
                    # 确认section不为None，如果为None，则警告
                    if self.__section is None:
                        self.__terminated("You have to specify section before script")
                    # 如果section未在字典中，则初始化对应section的数据
                    elif self.__section not in self.__output:
                        self.__output[self.__section] = {}
                    # 如果上个dialog存在（不一定非得能返回）
                    if self.__last_dialog_id is not None:
                        self.__current_data.last = self.__last_dialog_id
                        # 生成数据
                        last_ref: Optional[dict] = self.__output[self.__section].get(self.__last_dialog_id)
                        if last_ref is not None:
                            if last_ref.get("next_dialog_id") is not None:
                                last_ref["next_dialog_id"]["target"] = self.__dialog_associate_key[str(self.__line_index)]
                                if "type" not in last_ref["next_dialog_id"]:
                                    last_ref["next_dialog_id"]["type"] = "default"
                            else:
                                last_ref["next_dialog_id"] = {
                                    "target": self.__dialog_associate_key[str(self.__line_index)],
                                    "type": "default",
                                }
                        else:
                            self.__terminated("KeyError: {}".format(self.__last_dialog_id))
                    else:
                        self.__current_data.last = None
                    # 添加注释
                    if len(self.__accumulated_comments) > 0:
                        self.__current_data.notes = self.__accumulated_comments
                        self.__accumulated_comments = []
                    # 更新key
                    self.__last_dialog_id = self.__dialog_associate_key[str(self.__line_index)]
                    # 更新缓存参数
                    self.__line_index += len(self.__current_data.contents)
                    self.__output[self.__section][self.__last_dialog_id] = copy.deepcopy(self.__current_data.to_dict())
                    # 移除注释
                    self.__current_data.notes.clear()
                else:
                    self.__terminated("unexpected reason")
            self.__line_index += 1

    # 保存至
    def save_to(self, out_folder: str) -> None:
        Config.save(os.path.join(out_folder, "chapter{0}_dialogs_{1}.{2}".format(self.__id, self.__lang, Config.get_file_type())), {"dialogs": self.__output})


class ScriptCompiler:

    # 如果输入字符串为None，则将其转换为null
    @staticmethod
    def __to_str_in_case_null(text: Optional[str]) -> str:
        return text if text is not None else "null"

    # 从有效的视觉小说文件路径中读取信息
    @staticmethod
    def extract_info_from_path(_path: str) -> tuple[int, str]:
        _path = os.path.basename(_path)
        if not _path.startswith("chapter"):
            EXCEPTION.fatal("Invalid path!")
        # 返回 id, 语言
        return int(_path[7 : _path.index("_")]), _path[_path.rfind("_") + 1 : _path.rfind(".")]

    # 直接加载
    def load(self, path: str) -> dict:
        processor: _ScriptProcessor = _ScriptProcessor()
        processor.process(path)
        return processor.get_output()

    # 编译
    @staticmethod
    def compile(path: str, out_folder: str) -> None:
        processor: _ScriptProcessor = _ScriptProcessor()
        processor.process(path)
        processor.save_to(out_folder)

    # 编译文件夹内的所有原始视觉小说文件
    @classmethod
    def compile_files_in_directory(cls, _path: str) -> None:
        for _file in glob(os.path.join(_path, "*")):
            if os.path.isdir(_file):
                cls.compile_files_in_directory(_file)
            elif _file.endswith(_ScriptProcessor.FILE_EXTENSION):
                cls.compile(_file, _path)

    # 反编译
    @classmethod
    def decompile(cls, path: str, out: str) -> None:
        # 初始化视觉小说数据管理模块
        _content: DialogContentManager = DialogContentManager()
        # 获取视觉小说脚本数据
        dialogs_data: Optional[dict] = Config.load_file(path).get("dialogs")
        # 如果数据不为空
        if dialogs_data is not None and len(dialogs_data) > 0:
            # 把数据更新到管理模块中
            _content.update(dialogs_data)
            # 用于储存结果的列表
            _results: list[str] = ["# Fundamental parameters\n[id]{0}\n[lang]{1}\n".format(*cls.extract_info_from_path(path))]

            for _section in dialogs_data:
                # 更新视觉小说数据管理模块的当前位置
                _content.set_id("head")
                _content.set_section(_section)
                # 写入当前部分的名称
                _results.append("\n[section]" + _section + "\n")

                while True:
                    _current_dialog: dict = _content.get_dialog()
                    # 处理注释
                    notes: list[str] = _current_dialog.pop("notes", [])
                    if len(notes) > 0:
                        _results.append("\n")
                        for _note in notes:
                            _results.append("// " + _note + "\n")
                    # 写入讲话人名称
                    _results.append("null:\n" if len(_content.current.narrator) == 0 else _content.current.narrator + ":\n")
                    # 写入对话
                    for _sentence in _content.current.contents:
                        _results.append("- " + _sentence + "\n")

                    """如果下列内容有变化，则写入"""
                    # 写入背景
                    if _content.previous is None or _content.current.background_image != _content.previous.background_image:
                        if _content.previous is None or _content.previous.next.get("type") != "changeScene":
                            _results.append("[bgi]" + cls.__to_str_in_case_null(_content.current.background_image) + "\n")
                        else:
                            _results.append("[scene]" + cls.__to_str_in_case_null(_content.current.background_image) + "\n")
                    # 写入背景音乐
                    if _content.previous is None or _content.previous.background_music != _content.current.background_music:
                        _results.append("[bgm]" + cls.__to_str_in_case_null(_content.current.background_music) + "\n")
                    # 写入当前立绘
                    if _content.previous is None or _content.previous.character_images != _content.current.character_images:
                        if len(_content.current.character_images) == 0:
                            _results.append("[hide]*\n")
                        elif _content.previous is None or len(_content.previous.character_images) == 0:
                            _line: str = "[display]"
                            for _characterName in _content.current.character_images:
                                _line += VisualNovelCharacterImageNameMetaData(_characterName).name + " "
                            _results.append(_line.rstrip() + "\n")

                    if _content.current.has_next():
                        _content.set_id(_content.current.next["target"])
                    else:
                        break

            # 写入停止符
            _results.append("\n[end]\n")

            # 保存反编译好的脚本
            with open(out, "w+", encoding="utf-8") as f:
                f.writelines(_results)
from .character import *


class ScriptConverter:

    # 立绘配置信息数据库
    __CHARACTER_IMAGE_DATABASE: dict = DataBase.get("Npc")

    def __init__(self) -> None:
        self.__output: dict = {}
        self.__current_data: dict = dict(Template.get("dialog_example")["head"])
        self.__id: Optional[int] = None
        self.__lang: Optional[str] = None
        self.__part: Optional[str] = None
        self.__last_dialog_id: Optional[str] = None
        self.__lines: list[str] = []
        self.__branch_flags: dict[str, str] = {}
        self.__dialog_associate_key: dict[str, str] = {}

    # 生成一个标准id
    @staticmethod
    def __generate_id(index: int) -> str:
        if index >= 100:
            return "id_" + str(index)
        elif index >= 10:
            return "id_0" + str(index)
        elif index > 0:
            return "id_00" + str(index)
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

    # 转换
    def convert(self, path: str, out_folder: str) -> None:
        if path.endswith(".linpg.script"):
            with open(path, "r", encoding="utf-8") as f:
                self.__lines = f.readlines()
        # 如果文件为空
        if len(self.__lines) <= 0:
            EXCEPTION.fatal("Cannot convert an empty script file!")
        else:
            last_flag: Optional[str] = None
            # 预处理文件
            for index in range(len(self.__lines)):
                self.__lines[index] = self.__lines[index].removesuffix("\n")
                if self.__lines[index].startswith("[flag]"):
                    if last_flag is not None:
                        EXCEPTION.fatal("The flag on line {} is overwriting the previous".format(index))
                    last_flag = self.__extract_parameter(self.__lines[index], "[flag]")
                elif not self.__lines[index].startswith("[") and ":" in self.__lines[index]:
                    self.__dialog_associate_key[str(index)] = (
                        self.__generate_id(len(self.__dialog_associate_key)) if len(self.__dialog_associate_key) > 0 else "head"
                    )
                    # 将id与flag关联
                    if last_flag is not None:
                        self.__branch_flags[last_flag] = self.__dialog_associate_key[str(index)]
                        last_flag = None
            if last_flag is not None:
                EXCEPTION.warn("The last flag call {} is not necessary!".format(last_flag))
        self.__convert(0)
        self.__lines.clear()
        if self.__id is None:
            EXCEPTION.fatal("You have to set id!")
        elif self.__lang is None:
            EXCEPTION.fatal("You have to set lang!")
        elif self.__part is None:
            EXCEPTION.fatal("You have to set part!")
        else:
            Config.save(
                os.path.join(out_folder, "chapter{0}_dialogs_{1}.{2}".format(self.__id, self.__lang, Config.get_file_type())),
                {"dialogs": self.__output},
            )

    def __try_handle_data(self, index: int, parameter_short: str, parameter_full: str) -> bool:
        if self.__lines[index].startswith(parameter_short):
            self.__current_data[parameter_full] = self.__extract_parameter(self.__lines[index], parameter_short)
            return True
        return False

    def __convert(self, staring_index: int) -> None:
        index: int = staring_index
        while index < len(self.__lines):
            if (
                not self.__lines[index].startswith("#")
                and len(self.__lines[index]) > 0
                and not self.__try_handle_data(index, "[bgi]", "background_image")
                and not self.__try_handle_data(index, "[bgm]", "background_music")
            ):
                # 角色进场
                if self.__lines[index].startswith("[cin]"):
                    self.__current_data["character_images"].append(self.__extract_string(self.__lines[index], "[cin]"))
                # 角色退场
                elif self.__lines[index].startswith("[cout]"):
                    self.__current_data["character_images"].remove(self.__extract_string(self.__lines[index], "[cout]"))
                # 清空角色列表
                elif self.__lines[index].startswith("[cempty]"):
                    self.__current_data["character_images"].clear()
                # 章节id
                elif self.__lines[index].startswith("[id]"):
                    _id: Optional[str] = self.__extract_parameter(self.__lines[index], "[id]")
                    if _id is not None:
                        self.__id = int(_id)
                    else:
                        EXCEPTION.fatal("Chapter id cannot be None!")
                # 语言
                elif self.__lines[index].startswith("[lang]"):
                    self.__lang = self.__extract_string(self.__lines[index], "[lang]")
                # 部分
                elif self.__lines[index].startswith("[part]"):
                    self.__part = self.__extract_string(self.__lines[index], "[part]")
                # 结束符
                elif self.__lines[index].startswith("[end]"):
                    self.__output[self.__part][self.__last_dialog_id]["next_dialog_id"] = None
                    break
                # 转换场景
                elif self.__lines[index].startswith("[ns]"):
                    self.__output[self.__part][self.__last_dialog_id]["next_dialog_id"]["type"] = "changeScene"
                    self.__current_data["background_image"] = self.__extract_parameter(self.__lines[index], "[ns]")
                # 选项
                elif self.__lines[index].startswith("[opt]"):
                    # 确认在接下来的一行有branch的flag
                    if not self.__lines[index + 1].startswith("[br]"):
                        EXCEPTION.fatal(
                            "For option on line {}, a branch flag is not found on the following line".format(index + 1)
                        )
                    # 如果next_dialog_id没被初始化，则初始化
                    if self.__output[self.__part][self.__last_dialog_id].get("next_dialog_id") is None:
                        self.__output[self.__part][self.__last_dialog_id]["next_dialog_id"] = {}
                    # 获取对应的下一个对话字典的指针
                    dialog_next: dict = self.__output[self.__part][self.__last_dialog_id]["next_dialog_id"]
                    if dialog_next.get("type") != "option":
                        dialog_next["type"] = "option"
                        dialog_next["target"] = []
                    dialog_next["target"].append(
                        {
                            "text": self.__extract_string(self.__lines[index], "[opt]"),
                            "id": self.__branch_flags[self.__extract_string(self.__lines[index + 1], "[br]")],
                        }
                    )
                    index += 1
                elif not self.__lines[index].startswith("[") and ":" in self.__lines[index]:
                    narrator: str = self.__lines[index].removesuffix(" ").removesuffix(":")
                    self.__current_data["narrator"] = self.__ensure_not_null(narrator)
                    # 获取讲述人可能的立绘名称
                    narrator_possible_images: tuple = tuple()
                    if self.__current_data["narrator"] is not None:
                        if self.__current_data["narrator"].lower() in self.__CHARACTER_IMAGE_DATABASE:
                            narrator_possible_images = tuple(
                                self.__CHARACTER_IMAGE_DATABASE[self.__current_data["narrator"].lower()]
                            )
                    else:
                        self.__current_data["narrator"] = ""
                    # 检查名称列表，更新character_images以确保不在说话的人处于黑暗状态
                    for i in range(len(self.__current_data["character_images"])):
                        if (
                            self.__current_data["character_images"][i].replace("<d>", "").replace("<c>", "")
                            in narrator_possible_images
                        ):
                            self.__current_data["character_images"][i] = self.__current_data["character_images"][i].replace(
                                "<d>", ""
                            )
                        elif "<d>" not in self.__current_data["character_images"][i]:
                            self.__current_data["character_images"][i] += "<d>"
                    # 更新对话内容
                    self.__current_data["contents"] = []
                    for sub_index in range(index + 1, len(self.__lines)):
                        if self.__lines[sub_index].startswith("- "):
                            self.__current_data["contents"].append(self.__extract_string(self.__lines[sub_index], "- "))
                        else:
                            break
                    # 确认part不为None，如果为None，则警告
                    if self.__part is None:
                        EXCEPTION.fatal("You have to specify part before script")
                    # 如果part未在字典中，则初始化对应part的数据
                    elif self.__part not in self.__output:
                        self.__output[self.__part] = {}
                    # 如果上个dialog存在（不一定非得能返回）
                    if self.__last_dialog_id is not None:
                        self.__current_data["last_dialog_id"] = self.__last_dialog_id
                        # 生成数据
                        if self.__output[self.__part][self.__last_dialog_id].get("next_dialog_id") is not None:
                            self.__output[self.__part][self.__last_dialog_id]["next_dialog_id"][
                                "target"
                            ] = self.__dialog_associate_key[str(index)]
                        else:
                            self.__output[self.__part][self.__last_dialog_id]["next_dialog_id"] = {
                                "target": self.__dialog_associate_key[str(index)],
                                "type": "default",
                            }
                    else:
                        self.__current_data["last_dialog_id"] = None
                    # 更新key
                    self.__last_dialog_id = self.__dialog_associate_key[str(index)]
                    # 更新缓存参数
                    index += len(self.__current_data["contents"])
                    self.__output[self.__part][self.__last_dialog_id] = deepcopy(self.__current_data)
                else:
                    EXCEPTION.fatal("Cannot process script on line {}!".format(index))
            index += 1
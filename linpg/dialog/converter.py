from .dialog import *

# dialog修复转换器（希望任何功能都永远不需要被调用）
class DialogConverter(AbstractDialogSystem):
    def _check_and_fix_non_str_key(self, part: str) -> None:
        while True:
            looping: bool = False
            index: int = 0
            for key, value in self._dialog_data[part].items():
                if value["next_dialog_id"] is not None and "target" in value["next_dialog_id"]:
                    if isinstance(value["next_dialog_id"]["target"], list):
                        for index in range(len(value["next_dialog_id"]["target"])):
                            if not isinstance(value["next_dialog_id"]["target"][index]["id"], str):
                                old_key = deepcopy(value["next_dialog_id"]["target"][index]["id"])
                                looping = True
                                break
                        if looping is True:
                            break
                    elif not isinstance(value["next_dialog_id"]["target"], str):
                        old_key = deepcopy(value["next_dialog_id"]["target"])
                        looping = True
                        break
            if looping is True:
                new_key: str
                try:
                    new_key = self.generate_a_new_recommended_key(int(old_key))
                except Exception:
                    new_key = self.generate_a_new_recommended_key()
                if not isinstance(self._dialog_data[part][key]["next_dialog_id"]["target"], list):
                    self._dialog_data[part][key]["next_dialog_id"]["target"] = new_key
                else:
                    self._dialog_data[part][key]["next_dialog_id"]["target"][index]["id"] = new_key
                self._dialog_data[part][new_key] = deepcopy(self._dialog_data[part][old_key])
                del self._dialog_data[part][old_key]
            else:
                break


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
        self.__lines: list = []
        self.__last_valid: int = -1

    def __generate_id(self, index: int) -> str:
        if index >= 100:
            return "id_" + str(index)
        elif index >= 10:
            return "id_0" + str(index)
        elif index > 0:
            return "id_00" + str(index)
        else:
            return "head"

    def convert(self, path: str) -> None:
        if path.endswith(".rvns"):
            with open(path, "r", encoding="utf-8") as f:
                self.__lines = f.readlines()
        if len(self.__lines) <= 0:
            EXCEPTION.fatal("The file is empty!")
        self.__convert(0)
        if self.__id is None:
            EXCEPTION.fatal("You have to set id!")
        elif self.__lang is None:
            EXCEPTION.fatal("You have to set lang!")
        elif self.__part is None:
            EXCEPTION.fatal("You have to set part!")
        else:
            Config.save(
                "chapter{0}_dialogs_{1}.{2}".format(self.__id, self.__lang, Config.get_file_type()), {"dialogs": self.__output}
            )

    @staticmethod
    def __convert_str(text: str) -> Optional[str]:
        return None if text.lower() == "null" or text.lower() == "none" else text

    @classmethod
    def __extract_parameter(cls, text: str, prefix: str) -> Optional[str]:
        sharp_index: int = text.find("#")
        if sharp_index < 0:
            return cls.__convert_str(text.removeprefix(prefix).removesuffix("\n"))
        else:
            return cls.__convert_str(text[:sharp_index].removeprefix(prefix))

    def __convert(self, staring_index: int) -> None:
        for index in range(staring_index, len(self.__lines)):
            if not self.__lines[index].startswith("#") and len(self.__lines[index]) > 0:
                if self.__lines[index].startswith("<!bgi>"):
                    self.__current_data["background_image"] = self.__extract_parameter(self.__lines[index], "<!bgi>")
                elif self.__lines[index].startswith("<!bgm>"):
                    self.__current_data["background_music"] = self.__extract_parameter(self.__lines[index], "<!bgm>")
                elif self.__lines[index].startswith("<!cin>"):
                    self.__current_data["character_images"].append(self.__extract_parameter(self.__lines[index], "<!cin>"))
                elif self.__lines[index].startswith("<!cout>"):
                    self.__current_data["character_images"].remove(self.__extract_parameter(self.__lines[index], "<!cout>"))
                elif self.__lines[index].startswith("<!cempty>"):
                    self.__current_data["character_images"].clear()
                elif self.__lines[index].startswith("<!id>"):
                    _id: Optional[str] = self.__extract_parameter(self.__lines[index], "<!id>")
                    if _id is not None:
                        self.__id = int(_id)
                    else:
                        EXCEPTION.fatal("Chapter id cannot be None!")
                elif self.__lines[index].startswith("<!lang>"):
                    self.__lang = self.__extract_parameter(self.__lines[index], "<!lang>")
                elif self.__lines[index].startswith("<!part>"):
                    self.__part = self.__extract_parameter(self.__lines[index], "<!part>")
                elif self.__lines[index].startswith("<!end>"):
                    self.__output[self.__part][self.__generate_id(self.__last_valid)]["next_dialog_id"] = None
                    break
                elif ":" in self.__lines[index]:
                    _data: list[str] = self.__lines[index].removesuffix("\n").split(":")
                    self.__current_data["narrator"] = self.__convert_str(str(_data[0]))

                    narrator_possible_images: list = []
                    if (
                        self.__current_data["narrator"] is not None
                        and self.__current_data["narrator"].lower() in self.__CHARACTER_IMAGE_DATABASE
                    ):
                        narrator_possible_images = self.__CHARACTER_IMAGE_DATABASE[self.__current_data["narrator"].lower()]

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

                    self.__current_data["contents"] = [str(_data[1])]

                    if self.__part is None:
                        EXCEPTION.fatal("You have to specify part before script")
                    elif self.__part not in self.__output:
                        self.__output[self.__part] = {}

                    this_dialog_id: str = (
                        self.__generate_id(len(self.__output[self.__part])) if len(self.__output[self.__part]) > 0 else "head"
                    )

                    if self.__last_dialog_id is not None:
                        self.__current_data["last_dialog_id"] = self.__last_dialog_id
                        self.__output[self.__part][self.__last_dialog_id]["next_dialog_id"] = {
                            "target": this_dialog_id,
                            "type": "default",
                        }
                    else:
                        self.__current_data["last_dialog_id"] = None

                    self.__last_valid = len(self.__output[self.__part])
                    self.__last_dialog_id = this_dialog_id
                    self.__output[self.__part][self.__last_dialog_id] = deepcopy(self.__current_data)

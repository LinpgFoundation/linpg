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

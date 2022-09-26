from .dialog import *


# dialog修复转换器（希望任何功能都永远不需要被调用）
class DialogConverter(AbstractDialogSystem):
    def _check_and_fix_non_str_key(self, section: str) -> None:
        while True:
            index: int = 0
            old_key: Optional[str] = None
            for key, value in self._content.get_section_content(section).items():
                if value["next_dialog_id"] is not None and "target" in value["next_dialog_id"]:
                    if isinstance(value["next_dialog_id"]["target"], list):
                        for index in range(len(value["next_dialog_id"]["target"])):
                            if not isinstance(value["next_dialog_id"]["target"][index]["id"], str):
                                old_key = copy.deepcopy(value["next_dialog_id"]["target"][index]["id"])
                                break
                        if old_key is not None:
                            break
                    elif not isinstance(value["next_dialog_id"]["target"], str):
                        old_key = copy.deepcopy(value["next_dialog_id"]["target"])
                        break
            if old_key is not None:
                new_key: str
                try:
                    new_key = self.generate_a_new_recommended_key(int(old_key))
                except Exception:
                    new_key = self.generate_a_new_recommended_key()
                if not isinstance(self._content.get_dialog(section, key)["next_dialog_id"]["target"], list):
                    self._content.get_dialog(section, key)["next_dialog_id"]["target"] = new_key
                else:
                    self._content.get_dialog(section, key)["next_dialog_id"]["target"][index]["id"] = new_key
                self._content.get_dialog(section, new_key).clear()
                self._content.get_dialog(section, new_key).update(self._content.get_dialog(section, old_key))
                self._content.remove_dialog(section, old_key)
            else:
                break

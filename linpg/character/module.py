from .sound import *

# 计算最远攻击距离
def calculate_range(effective_range_dic: dict) -> int:
    if effective_range_dic is not None and len(effective_range_dic) > 0:
        max_attack_range: int = 0
        if (
            "far" in effective_range_dic
            and effective_range_dic["far"] is not None
            and max_attack_range < effective_range_dic["far"][-1]
        ):
            return effective_range_dic["far"][-1]
        if (
            "middle" in effective_range_dic
            and effective_range_dic["middle"] is not None
            and max_attack_range < effective_range_dic["middle"][-1]
        ):
            return effective_range_dic["middle"][-1]
        if (
            "near" in effective_range_dic
            and effective_range_dic["near"] is not None
            and max_attack_range < effective_range_dic["near"][-1]
        ):
            return effective_range_dic["near"][-1]
        return max_attack_range
    else:
        return 0


# 加载并更新更新位于Data中的角色数据配置文件-character_data.yaml
def loadCharacterData() -> dict:
    _path: str = os.path.join("Data", "character_data.yaml")
    if os.path.exists(_path):
        loadData: dict = Config.load_file(_path)
        ifAnythingChange: bool = False
        for path in glob(r"Assets/image/character/*"):
            name = os.path.basename(path)
            if name not in loadData:
                loadData[name] = {
                    "max_action_point": 1,
                    "skill_coverage": 1,
                    "effective_range": {
                        "far": [5, 6],
                        "middle": [3, 4],
                        "near": [1, 2],
                    },
                    "kind": None,
                    "magazine_capacity": 1,
                    "max_damage": 1,
                    "max_hp": 1,
                    "min_damage": 1,
                    "skill_coverage": 1,
                    "skill_effective_range": None,
                }
                ifAnythingChange = True
                EXCEPTION.inform("A new character call {} has been updated to the data file.".format(name))
        for path in glob(r"Assets/image/sangvisFerri/*"):
            name = os.path.basename(path)
            if name not in loadData:
                loadData[name] = {
                    "max_action_point": 1,
                    "skill_coverage": 1,
                    "effective_range": {
                        "far": [5, 6],
                        "middle": [3, 4],
                        "near": [1, 2],
                    },
                    "kind": None,
                    "magazine_capacity": 1,
                    "max_damage": 1,
                    "max_hp": 1,
                    "min_damage": 1,
                }
                ifAnythingChange = True
                EXCEPTION.inform("A new character call {} has been updated to the data file.".format(name))
        if ifAnythingChange is True:
            Config.save("Data/character_data.yaml", loadData)
        EntitySoundManager.mkdir()
    else:
        return {}
    return loadData


# 用于存放角色做出的决定
class DecisionHolder:
    def __init__(self, action: str, data: Any):
        self.action = action
        self.data = data

    @property
    def route(self) -> list:
        if self.action == "move":
            return list(self.data)
        else:
            EXCEPTION.fatal("The character does not decide to move!")

    @property
    def target(self) -> str:
        if self.action == "attack":
            return str(self.data[0])
        else:
            EXCEPTION.fatal("The character does not decide to attack!")

    @property
    def target_area(self) -> str:
        if self.action == "attack":
            return str(self.data[1])
        else:
            EXCEPTION.fatal("The character does not decide to attack!")

from ..map import *

# 角色受伤立绘图形模块
class EntityGetHurtImage(Square):

    # 存储角色受伤立绘的常量
    __CHARACTERS_GET_HURT_IMAGE_DICT: dict = {}
    __IMAGE_FOLDER_PATH: str = os.path.join("Assets", "image", "npc")

    def __init__(self, self_type: str, y: number, width: int):
        super().__init__(0, y, width)
        self.delay: int = 255
        self.alpha: int = 0
        self.add(self_type)

    def draw(self, screen: ImageSurface, characterType: str) -> None:  # type: ignore[override]
        _image = RawImg.resize(self.__CHARACTERS_GET_HURT_IMAGE_DICT[characterType], self.size)
        if self.alpha != 255:
            _image.set_alpha(self.alpha)
        screen.blit(_image, self.pos)

    def add(self, characterType: str) -> None:
        if characterType not in self.__CHARACTERS_GET_HURT_IMAGE_DICT:
            self.__CHARACTERS_GET_HURT_IMAGE_DICT[characterType] = RawImg.quickly_load(
                os.path.join(self.__IMAGE_FOLDER_PATH, "{}_hurt.png".format(characterType))
            )


# 角色图片管理模块
class EntityImageManager:

    __CHARACTERS_IMAGE_DICT: dict = {}

    @classmethod
    def get_img(cls, characterType: str, action: str, imgId: int) -> StaticImage:
        _temp: StaticImage = cls.__CHARACTERS_IMAGE_DICT[characterType][action]["img"][imgId]
        return _temp

    @classmethod
    def get_img_num(cls, characterType: str, action: str) -> int:
        return int(cls.__CHARACTERS_IMAGE_DICT[characterType][action]["imgNum"])

    # 动图字典制作模块：接受一个友方角色名，返回对应的动图字典
    @classmethod
    def createGifDict(cls, characterType: str, faction: str, mode: str) -> dict:
        if mode == "default":
            imgId_dict = {
                "attack": cls.loadImageCollection(characterType, "attack", faction),
                "attack2": cls.loadImageCollection(characterType, "attack2", faction),
                "move": cls.loadImageCollection(characterType, "move", faction),
                "reload": cls.loadImageCollection(characterType, "reload", faction),
                "repair": cls.loadImageCollection(characterType, "reload", faction),
                "set": cls.loadImageCollection(characterType, "set", faction),
                "skill": cls.loadImageCollection(characterType, "skill", faction),
                "victory": cls.loadImageCollection(characterType, "victory", faction),
                "victoryloop": cls.loadImageCollection(characterType, "victoryloop", faction),
                "wait": cls.loadImageCollection(characterType, "wait", faction),
                "wait2": cls.loadImageCollection(characterType, "wait2", faction),
            }
            if faction != "sangvisFerri":
                imgId_dict["die"] = cls.loadImageCollection(characterType, "die", faction)
            else:
                imgId_dict["die"] = cls.loadImageCollection(characterType, "die", faction)
                """
                temp_list = ["","2","3"]
                imgId_dict["die"] = cls.loadImageCollection(characterType,"die"+temp_list[get_random_int(0,2)],faction)
                if imgId_dict["die"] is None:
                    imgId_dict["die"] = cls.loadImageCollection(characterType,"die",faction)
                """
        elif mode == "dev":
            imgId_dict = {"wait": cls.loadImageCollection(characterType, "wait", faction)}
        else:
            EXCEPTION.fatal("Mode is not supported")
        return imgId_dict

    # 动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
    # 810*810 position:405/567
    @classmethod
    def loadImageCollection(cls, characterType: str, action: str, faction: str) -> dict:
        if characterType not in cls.__CHARACTERS_IMAGE_DICT:
            cls.__CHARACTERS_IMAGE_DICT[characterType] = {}
        elif action in cls.__CHARACTERS_IMAGE_DICT[characterType]:
            return {"imgId": 0, "alpha": 255}
        if os.path.exists("Assets/image/{0}/{1}/{2}".format(faction, characterType, action)):
            files_amount = len(glob("Assets/image/{0}/{1}/{2}/*.png".format(faction, characterType, action)))
            if files_amount > 0:
                cls.__CHARACTERS_IMAGE_DICT[characterType][action] = {
                    "img": numpy.asarray(
                        [
                            StaticImage(
                                "Assets/image/{0}/{1}/{2}/{3}_{4}_{5}.png".format(
                                    faction, characterType, action, characterType, action, i
                                ),
                                0,
                                0,
                            )
                            for i in range(files_amount)
                        ]
                    ),
                    "imgNum": files_amount,
                }
                if faction == "sangvisFerri":
                    for img in cls.__CHARACTERS_IMAGE_DICT[characterType][action]["img"]:
                        img.flip_original_img()
                return {"imgId": 0, "alpha": 255}
            else:
                return {}
        else:
            return {}

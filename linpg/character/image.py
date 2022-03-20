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
class EntitySpriteImageManager:

    __CHARACTERS_IMAGE_DICT: dict = {}

    @classmethod
    def get_img(cls, characterType: str, action: str, imgId: int) -> StaticImage:
        _temp: StaticImage = cls.__CHARACTERS_IMAGE_DICT[characterType][action]["img"][imgId]
        return _temp

    @classmethod
    def get_img_num(cls, characterType: str, action: str) -> int:
        return int(cls.__CHARACTERS_IMAGE_DICT[characterType][action]["imgNum"])

    class __EntitySpriteImage(StaticImage):
        def __init__(self, img: ImageSurface, current_rect: list[int], original_img_rect: list[int]) -> None:
            super().__init__(img, current_rect[0], current_rect[1], current_rect[2], current_rect[3])
            self.__original_width = img.get_width()
            self.__original_height = img.get_height()
            self.__offset_x: int = original_img_rect[0]
            self.__offset_y: int = original_img_rect[1]
            self.__real_width: int = original_img_rect[2]
            self.__real_height: int = original_img_rect[3]
            self.disable_croping()

        def set_width(self, value: int_f) -> None:
            super().set_width(value * self.__original_width / self.__real_width)

        def set_height(self, value: int_f) -> None:
            super().set_height(value * self.__original_height / self.__real_height)

        def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
            return super().display(
                surface,
                Coordinates.add(
                    offSet,
                    (
                        self.__offset_x * self.get_width() // self.__original_width,
                        self.__offset_y * self.get_height() // self.__original_height,
                    ),
                ),
            )

    # 生成Sprite图片
    @staticmethod
    def generate(entityFaction: str, entityType: str, resultFileType: str = "png") -> None:
        # 储存数据的字典
        _data: dict = {}
        # sprite图宽度
        sprite_surface_width: int = 0
        # 当前y坐标
        current_y: int = 0
        # 目录路径
        folder_path: str = os.path.join(Specification.get("FolderPath", "Sprite"), entityFaction, entityType)
        # 暂时存放图片的列表
        imgTempList: list = []
        # 最大高度
        max_block_height: int = 0
        # 最终sprite图
        sprite_surface: ImageSurface
        # 历遍目标文件夹中的图片
        for _action_folder in os.listdir(folder_path):
            # 重置参数
            imgTempList.clear()
            sprite_surface_width = 0
            max_block_height = 0
            # 获取所有当前动作图片的目录
            img_list: list[str] = glob(os.path.join(folder_path, _action_folder, "*.png"))
            img_list.sort(key=lambda f: int("".join(filter(str.isdigit, f))))
            # 加载所有图片
            for _path in img_list:
                _image: ImageSurface = RawImg.quickly_load(_path)
                # 获取图片的bounding
                _bounding: Rect = _image.get_bounding_rect()
                # 增加宽度
                sprite_surface_width += _bounding.width
                # 确认最大高度
                if max_block_height < _bounding.height:
                    max_block_height = _bounding.height
                # 放入图片
                imgTempList.append(
                    {
                        "img": _image.subsurface(_bounding),
                        "original": [_bounding.x, _bounding.y, _image.get_width(), _image.get_height()],
                    }
                )
            # 最终sprite图
            sprite_surface = Surface.transparent((sprite_surface_width, max_block_height))
            _data[_action_folder] = []
            current_y = 0
            # 生成当前动作的sprite图
            for _img in imgTempList:
                sprite_surface.blit(_img["img"], (current_y, 0))
                _data[_action_folder].append([[current_y, 0, _img["img"].get_width(), _img["img"].get_width()], _img["original"]])
                current_y += _img["img"].get_width()
            # 保存当前动作的sprite图
            target_file_name: str = "{0}.{1}".format(_action_folder, resultFileType)
            RawImg.save(sprite_surface, os.path.join(folder_path, target_file_name))
            # 删除原先的文件夹
            shutil.rmtree(os.path.join(folder_path, _action_folder))
        # 保存sprite图数据
        Config.save(os.path.join(folder_path, entityType + ".linpg.meta"), _data)

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
        _character_sprite_image_folder: str = os.path.join(Specification.get("FolderPath", "Sprite"), faction, characterType)
        if os.path.exists(os.path.join(_character_sprite_image_folder, action)):
            files_amount = len(glob(os.path.join(_character_sprite_image_folder, action, "*.png")))
            if files_amount > 0:
                cls.__CHARACTERS_IMAGE_DICT[characterType][action] = {
                    "img": numpy.asarray(
                        [
                            StaticImage(
                                os.path.join(
                                    _character_sprite_image_folder, action, "{0}_{1}_{1}.png".format(characterType, action, i)
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

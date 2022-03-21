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

    class __EntitySpriteImage(StaticImage):
        def __init__(self, img: ImageSurface, current_size: list[int], offset: list[int], original_img_size: list[int]) -> None:
            super().__init__(img, 0, 0, current_size[0], current_size[1])
            self.__original_width = img.get_width()
            self.__original_height = img.get_height()
            self.__offset_x: int = offset[0]
            self.__offset_y: int = offset[1]
            self.__real_width: int = original_img_size[0]
            self.__real_height: int = original_img_size[1]

        def set_width(self, value: int_f) -> None:
            super().set_width(value * self.__original_width / self.__real_width)

        def set_height(self, value: int_f) -> None:
            super().set_height(value * self.__original_height / self.__real_height)

        # 展示
        def display(self, surface: ImageSurface, offSet: tuple = ORIGIN) -> None:
            super().display(
                surface,
                Coordinates.add(
                    offSet,
                    (
                        self.__offset_x * self.get_width() // self.__original_width,
                        self.__offset_y * self.get_height() // self.__original_height,
                    ),
                ),
            )

    # 获取图片
    @classmethod
    def get_img(cls, characterType: str, action: str, imgId: int) -> __EntitySpriteImage:
        return cls.__CHARACTERS_IMAGE_DICT[characterType][action][imgId]  # type: ignore

    # 尝试获取图片
    @classmethod
    def try_get_img(cls, faction: str, characterType: str, action: str, imgId: int) -> __EntitySpriteImage:
        if characterType not in cls.__CHARACTERS_IMAGE_DICT or action not in cls.__CHARACTERS_IMAGE_DICT[characterType]:
            cls.load(faction, characterType, "dev")
        return cls.get_img(characterType, action, imgId)

    # 获取图片数量
    @classmethod
    def get_img_num(cls, characterType: str, action: str) -> int:
        return len(cls.__CHARACTERS_IMAGE_DICT[characterType][action])

    # 是否图片存在
    @classmethod
    def does_action_exist(cls, characterType: str, action: str) -> bool:
        return action in cls.__CHARACTERS_IMAGE_DICT[characterType]

    # 生成Sprite图片
    @staticmethod
    def generate(entityFaction: str, entityType: str, resultFileType: str = "png") -> None:
        # 储存数据的字典
        _data: dict = {}
        # 目录路径
        folder_path: str = os.path.join(Specification.get("FolderPath", "Sprite"), entityFaction, entityType)
        # 暂时存放图片的列表
        imgTempList: list = []
        # 历遍目标文件夹中的图片
        for _action_folder in os.listdir(folder_path):
            _action_folder_path: str = os.path.join(folder_path, _action_folder)
            if os.path.isdir(_action_folder_path):
                # 单个sprite图切割点
                crop_rect: list[int] = []
                # 重置存放图片的列表
                imgTempList.clear()
                # 获取所有当前动作图片的目录
                img_list: list[str] = glob(os.path.join(_action_folder_path, "*.png"))
                if len(img_list) > 0:
                    img_list.sort(key=lambda f: int("".join(filter(str.isdigit, f))))
                    # 加载所有图片
                    for _path in img_list:
                        # 加载单个图片
                        _image: ImageSurface = RawImg.quickly_load(_path)
                        # 如果切割rect未被初始化
                        if len(crop_rect) <= 0:
                            crop_rect = [_image.get_width(), _image.get_height(), 0, 0]
                        # 获取图片的bounding，并和现有的bounding进行比较
                        _bounding: Rect = _image.get_bounding_rect()
                        if _bounding.x < crop_rect[0]:
                            crop_rect[0] = _bounding.x
                        if _bounding.y < crop_rect[1]:
                            crop_rect[1] = _bounding.x
                        if _bounding.right > crop_rect[2]:
                            crop_rect[2] = _bounding.right
                        if _bounding.bottom > crop_rect[3]:
                            crop_rect[3] = _bounding.bottom
                        # 放入图片
                        imgTempList.append(_image)
                    # 计算universal的尺寸
                    crop_rect[2] -= crop_rect[0]
                    crop_rect[3] -= crop_rect[1]
                    # 写入信息
                    _data[_action_folder] = {"count": len(imgTempList), "subrect": crop_rect, "size": list(_image.get_size())}
                    # 最终sprite图
                    sprite_surface: ImageSurface = Surface.transparent((crop_rect[2] * len(imgTempList), crop_rect[3]))
                    # 生成当前动作的sprite图
                    for i in range(len(imgTempList)):
                        sprite_surface.blit(imgTempList[i].subsurface(crop_rect), (i * crop_rect[2], 0))
                    # 保存当前动作的sprite图
                    target_file_name: str = "{0}.{1}".format(_action_folder, resultFileType)
                    RawImg.save(sprite_surface, os.path.join(folder_path, target_file_name))
                    # 删除原先的文件夹
                    shutil.rmtree(os.path.join(folder_path, _action_folder))
        # 保存sprite图数据
        if len(_data) > 0:
            Config.save(os.path.join(folder_path, entityType + ".linpg.meta"), _data)

    # 加载sprite图片模块：接受一个友方角色名，返回对应的动图字典
    @classmethod
    def load(cls, faction: str, characterType: str, mode: str) -> dict:
        sprite_image_meta_data: dict = Config.load_file(
            os.path.join(Specification.get("FolderPath", "Sprite"), faction, characterType, characterType + ".linpg.meta")
        )
        imgId_dict: dict = {}
        # 默认模式下，加载所有动作
        if mode == "default":
            for key in sprite_image_meta_data:
                imgId_dict[key] = cls.__load_action(faction, characterType, key, sprite_image_meta_data[key])
        # 在开发模式下仅加载idle动作
        elif mode == "dev":
            imgId_dict["wait"] = cls.__load_action(faction, characterType, "wait", sprite_image_meta_data["wait"])
        else:
            EXCEPTION.fatal("Mode is not supported")
        return imgId_dict

    # 动图制作模块：接受一个友方角色名和动作,当前的方块标准长和高，返回对应角色动作list或者因为没图片而返回None
    # 810*810 position:405/567
    @classmethod
    def __load_action(cls, faction: str, characterType: str, action: str, action_meta_data: dict) -> dict:
        # 为尚未初始化的角色init一个字典
        if characterType not in cls.__CHARACTERS_IMAGE_DICT:
            cls.__CHARACTERS_IMAGE_DICT[characterType] = {}
        # 如果动作已被初始化，则返回对应字典
        elif action in cls.__CHARACTERS_IMAGE_DICT[characterType]:
            return {"imgId": 0, "alpha": 255}
        # 加载原始sprite图片
        character_sprite_image: ImageSurface = RawImg.quickly_load(
            os.path.join(Specification.get("FolderPath", "Sprite"), faction, characterType, action + ".png")
        )
        # 根据meta信息切割图片并保存数据
        cls.__CHARACTERS_IMAGE_DICT[characterType][action] = [
            cls.__EntitySpriteImage(
                character_sprite_image.subsurface(
                    i * action_meta_data["subrect"][2], 0, action_meta_data["subrect"][2], action_meta_data["subrect"][3]
                ),
                action_meta_data["subrect"][2:],
                action_meta_data["subrect"][:2],
                action_meta_data["size"],
            )
            for i in range(action_meta_data["count"])
        ]
        if faction == "sangvisFerri":
            for img in cls.__CHARACTERS_IMAGE_DICT[characterType][action]:
                img.flip_original_img()
        return {"imgId": 0, "alpha": 255}

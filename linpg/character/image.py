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

    # 管理单个动作所有对应图片的模块
    class EntityImagesCollection:
        def __init__(
            self, imagesList: tuple[StaticImage, ...], crop_size: list[int], offset: list[int], original_img_size: list[int]
        ) -> None:
            self.__images: tuple[StaticImage, ...] = imagesList
            self.__current_image_pointer: StaticImage = self.__images[0]
            self.__width: number = 0
            self.__height: number = 0
            self.__cropped_image_width: int = crop_size[0]
            self.__cropped_image_height: int = crop_size[1]
            self.__left_offset_x: int = offset[0]
            self.__offset_y: int = offset[1]
            self.__real_width: int = original_img_size[0]
            self.__real_height: int = original_img_size[1]
            self.__right_offset_x: int = self.__real_width - self.__cropped_image_width - self.__left_offset_x

        def __len__(self) -> int:
            return len(self.__images)

        # 获取指定index的图片
        def get_image(self, index: int) -> StaticImage:
            return self.__images[index]

        # 设置尺寸
        def set_size(self, width: number, height: number) -> None:
            self.__width = width * self.__cropped_image_width / self.__real_width
            self.__height = height * self.__cropped_image_height / self.__real_height

        # 设置要播放图片的index
        def set_index(self, index: int) -> None:
            self.__current_image_pointer = self.__images[index]

        # 反转所有列表内的图片
        def flip_all(self) -> None:
            for _image in self.__images:
                _image.flip_original_img()
            temp: int = self.__right_offset_x
            self.__right_offset_x = self.__left_offset_x
            self.__left_offset_x = temp

        # 是否角色被鼠标触碰
        def is_hovered(self) -> bool:
            return self.__current_image_pointer.is_hovered()

        def is_collided_with(self, _rect: Rectangle) -> bool:
            return (
                0 <= self.__current_image_pointer.x - _rect.x <= _rect.width
                and 0 <= self.__current_image_pointer.y - _rect.y <= _rect.height
            ) or (
                0 <= _rect.x - self.__current_image_pointer.x <= self.__current_image_pointer.width
                and 0 <= _rect.y - self.__current_image_pointer.y <= self.__current_image_pointer.height
            )

        # 展示
        def draw_onto(self, surface: ImageSurface, alpha: int, ifFlip: bool, pos: tuple, draw_outline: bool) -> None:
            self.__current_image_pointer.set_size(self.__width, self.__height)
            self.__current_image_pointer.set_alpha(alpha)  # 翻转图片
            self.__current_image_pointer.set_top(self.__offset_y * self.__height / self.__cropped_image_height + pos[1])
            if ifFlip:
                self.__current_image_pointer.flip_if_not()
                self.__current_image_pointer.set_left(self.__right_offset_x * self.__width / self.__cropped_image_width + pos[0])
            else:
                self.__current_image_pointer.flip_back_to_normal()
                self.__current_image_pointer.set_left(self.__left_offset_x * self.__width / self.__cropped_image_width + pos[0])
            self.__current_image_pointer.draw(surface)
            if draw_outline is True:
                self.__current_image_pointer.draw_outline(surface)

    # 获取图片
    @classmethod
    def get_images(cls, characterType: str, action: str) -> EntityImagesCollection:
        return cls.__CHARACTERS_IMAGE_DICT[characterType][action]  # type: ignore

    # 尝试获取图片
    @classmethod
    def try_get_images(cls, faction: str, characterType: str, action: str) -> EntityImagesCollection:
        if characterType not in cls.__CHARACTERS_IMAGE_DICT or action not in cls.__CHARACTERS_IMAGE_DICT[characterType]:
            cls.load(faction, characterType, "dev")
        return cls.get_images(characterType, action)

    # 是否图片存在
    @classmethod
    def does_action_exist(cls, characterType: str, action: str) -> bool:
        return action in cls.__CHARACTERS_IMAGE_DICT[characterType]

    # 生成webp动态图片
    @staticmethod
    def generate(entityFaction: str, entityType: str) -> None:
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
                            crop_rect[1] = _bounding.y
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
                    # 生成当前动作的webp图
                    for i in range(len(imgTempList)):
                        imgTempList[i] = PILImage.fromarray(Surface.to_array(imgTempList[i].subsurface(crop_rect)))
                    # 保存当前动作的webp图
                    target_file_name: str = _action_folder + ".webp"
                    imgTempList[0].save(
                        os.path.join(folder_path, target_file_name),
                        save_all=True,
                        append_images=imgTempList[1:],
                        duration=0,
                        lossless=True,
                    )
                    # 删除原先的文件夹
                    shutil.rmtree(os.path.join(folder_path, _action_folder))
        # 保存sprite图数据
        if len(_data) > 0:
            Config.save(os.path.join(folder_path, entityType + ".linpg.meta"), _data)

    # 为Sprite文件夹中的所有角色生成webp动态图片
    @classmethod
    def generate_all(cls) -> None:
        _path: str = Specification.get("FolderPath", "Sprite")
        for faction in os.listdir(_path):
            for key in os.listdir(os.path.join(_path, faction)):
                cls.generate(faction, key)

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
        # 加载图片
        cls.__CHARACTERS_IMAGE_DICT[characterType][action] = cls.EntityImagesCollection(
            tuple(
                [
                    StaticImage(surf, 0, 0)
                    for surf in RawImg.load_animated(
                        os.path.join(Specification.get("FolderPath", "Sprite"), faction, characterType, action + ".webp")
                    )
                ]
            ),
            action_meta_data["subrect"][2:],
            action_meta_data["subrect"][:2],
            action_meta_data["size"],
        )
        # 如果是敌人模块，则flip所有图片
        if faction == "enemy":
            cls.__CHARACTERS_IMAGE_DICT[characterType][action].flip_all()
        # 返回数据
        return {"imgId": 0, "alpha": 255}

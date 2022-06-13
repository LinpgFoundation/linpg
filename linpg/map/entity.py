from collections import deque
from .astar import *

# 人形模块
class Entity(Position):

    # 存放音效的字典
    __SOUNDS: dict[str, dict[str, list]] = {}
    # 角色数据库
    __DATABASE: dict[str, dict] = {}
    # 尝试加载角色数据
    _path: str = os.path.join("Data", "character_data." + Config.get_file_type())
    if os.path.exists(_path):
        __DATABASE.update(Config.load_file(_path))
    del _path
    # idle动作
    __IDLE_ACTION: str = "wait"

    def __init__(self, DATA: dict, mode: str):
        super().__init__(DATA["x"], DATA["y"])
        # 最大行动值
        self.__max_action_point: int = int(DATA["max_action_point"])
        # 当前行动值
        self.__current_action_point: int = int(DATA.get("current_action_point", self.__max_action_point))
        # 攻击范围
        self.__attack_coverage: int = int(DATA["attack_coverage"])
        # 弹夹容量
        self.__magazine_capacity: int = int(DATA["magazine_capacity"])
        # 最大血量
        self.__max_hp: int = max(int(DATA["max_hp"]), 1)
        # 当前血量
        self.__current_hp: int = int(DATA.get("current_hp", self.__max_hp))
        # 不可再生的护甲值
        self.__irrecoverable_armor: int = int(DATA.get("irrecoverable_armor", 0))
        # 最大可再生的护甲值
        self.__max_recoverable_armor: int = int(DATA.get("max_recoverable_armor", 0))
        # 当前可再生的护甲值
        self.__current_recoverable_armor: int = int(DATA.get("current_recoverable_armor", self.__max_recoverable_armor))
        # 攻击范围
        self.__effective_range: tuple[int, ...] = tuple(DATA["effective_range"])
        # 最大攻击力
        self.__max_damage: int = int(DATA["max_damage"])
        # 最小攻击力
        self.__min_damage: int = int(DATA["min_damage"])
        # 武器类型
        self.__kind: str = str(DATA["kind"])
        # 阵营
        self.__faction: str = str(DATA["faction"])
        # 态度： 友方 - 1；敌对 - -1；中立 - 0
        self.__attitude: int = 0
        # 角色武器名称
        self.__type: str = str(DATA["type"])
        # 是否图片镜像
        self._if_flip: bool = bool(DATA.get("if_flip", False))
        # 当前动作
        self.__current_action: str = str(DATA.get("current_action", self.__IDLE_ACTION))
        # 动作是否重复
        self.__if_action_loop: bool = bool(DATA.get("if_action_loop", True))
        # 是否动作完成后返回idle
        self.__if_switch_to_idle_afterwards: bool = bool(DATA.get("if_switch_to_idle_afterwards", True))
        # 动作是正序列播放还是反序播放
        self._if_play_action_in_reversing: bool = bool(DATA.get("if_play_action_in_reversing", False))
        # 需要移动的路径
        self.__moving_path: deque = deque(DATA.get("moving_path", []))
        self.__moving_complete: bool = bool(DATA.get("moving_complete", len(self.__moving_path) <= 0))
        # 是否无敌
        self.__if_invincible: bool = bool(DATA.get("if_invincible", False))
        # gif图片管理
        self.__imgId_dict: dict = EntitySpriteImageManager.load(self.__faction, self.__type, mode)
        # 加载角色的音效
        if mode != "dev":
            if self.__type not in self.__SOUNDS and os.path.exists(Specification.get_directory("character_sound", self.__type)):
                self.__SOUNDS[self.__type] = {}
                for soundType in os.listdir(Specification.get_directory("character_sound", self.__type)):
                    self.__SOUNDS[self.__type][soundType] = []
                    for soundPath in glob(Specification.get_directory("character_sound", self.__type, soundType, "*")):
                        self.__SOUNDS[self.__type][soundType].append(Sound.load(soundPath))
        # 是否需要重新渲染地图
        self.__if_map_need_update: bool = False
        # 当前图片的rect
        self.__current_image_rect: Optional[Rectangle] = None
        # 是否被选中
        self.__is_selected: bool = False

    def to_dict(self) -> dict:
        data: dict = {
            "x": self.x,
            "y": self.y,
            "max_action_point": self.__max_action_point,
            "attack_coverage": self.__attack_coverage,
            "magazine_capacity": self.__magazine_capacity,
            "max_hp": self.__max_hp,
            "effective_range": list(self.__effective_range),
            "kind": self.__kind,
            "type": self.__type,
            "max_damage": self.__max_damage,
            "min_damage": self.__min_damage,
        }
        """以下是可选数据"""
        if self._if_flip is True:
            data["if_flip"] = self._if_flip
        if self.__current_action_point != self.__max_action_point:
            data["current_action_point"] = self.__current_action_point
        if self.__current_action != self.__IDLE_ACTION:
            data["current_action"] = self.__current_action
            data["if_action_loop"] = self.__if_action_loop
            data["if_play_action_in_reversing"] = self._if_play_action_in_reversing
            data["if_switch_to_idle_afterwards"] = self.__if_switch_to_idle_afterwards
        if self.__current_hp != self.__max_hp:
            data["current_hp"] = self.__current_hp
        if self.__max_recoverable_armor > 0:
            data["max_recoverable_armor"] = self.__max_recoverable_armor
        if self.__irrecoverable_armor > 0:
            data["irrecoverable_armor"] = self.__irrecoverable_armor
        if self.__current_recoverable_armor > 0:
            data["current_recoverable_armor"] = self.__current_recoverable_armor
        if self.__if_invincible is True:
            data["if_invincible"] = self.__if_invincible
        if len(self.__moving_path) > 0:
            data["moving_path"] = [list(pos) for pos in self.__moving_path]
        if not self.__moving_complete:
            data["moving_complete"] = self.__moving_complete
        return data

    # 查询特点角色的数据
    @classmethod
    def get_enity_data(cls, _type: str) -> dict:
        return cls.__DATABASE[_type]

    # 阵营
    @property
    def faction(self) -> str:
        return self.__faction

    # 态度
    @property
    def attitude(self) -> int:
        return self.__attitude

    def set_attitude(self, value: int) -> None:
        self.__attitude = keep_int_in_range(value, -1, 1)

    # 武器类型
    @property
    def kind(self) -> str:
        return self.__kind

    # 角色武器名称
    @property
    def type(self) -> str:
        return self.__type

    """
    攻击
    """

    # 弹夹容量
    @property
    def magazine_capacity(self) -> int:
        return self.__magazine_capacity

    # 攻击覆盖范围
    @property
    def attack_coverage(self) -> int:
        return self.__attack_coverage

    # 攻击范围
    @property
    def effective_range(self) -> tuple[int, ...]:
        return self.__effective_range

    # 最大攻击力
    @property
    def max_damage(self) -> int:
        return self.__max_damage

    # 最小攻击力
    @property
    def min_damage(self) -> int:
        return self.__min_damage

    # 攻击另一个Entity
    def attack(self, another_entity: "Entity") -> int:
        damage = get_random_int(self.__min_damage, self.__max_damage)
        another_entity.injury(damage)
        return damage

    # 设置选中状态
    def set_selected(self, value: bool) -> None:
        self.__is_selected = value

    # 是否角色被鼠标触碰
    def is_hovered(self) -> bool:
        return self.__current_image_rect.is_hovered() if self.__current_image_rect is not None else False

    # 是否角色纹理与另一个物体overlap
    def is_overlapped_with(self, _rect: Rectangle) -> bool:
        return self.__current_image_rect.is_overlapped_with(_rect) if self.__current_image_rect is not None else False

    """
    角色动作参数管理
    """

    # 当前动作
    @property
    def action(self) -> str:
        return self.__current_action

    # 设置动作
    def set_action(self, action: str = "wait", ifLoop: bool = True, ifSwitchToIdleAfterwards: bool = True) -> None:
        self.reset_imgId(self.__current_action)
        self.__current_action = action
        self.__if_action_loop = ifLoop
        self.__if_switch_to_idle_afterwards = ifSwitchToIdleAfterwards

    # 是否闲置
    def is_idle(self) -> bool:
        return self.__current_action == self.__IDLE_ACTION

    # 获取角色特定动作的图片播放ID
    def get_imgId(self, action: str) -> int:
        action_dict: Optional[dict] = self.__imgId_dict.get(action)
        return int(action_dict["imgId"]) if action_dict is not None else -1

    # 获取角色特定动作的图片总数量
    def get_imgNum(self, action: str) -> int:
        return len(EntitySpriteImageManager.get_images(self.__type, action))

    # 设定角色特定动作的图片播放ID
    def set_imgId(self, action: str, imgId: int) -> None:
        self.__imgId_dict[action]["imgId"] = imgId

    # 重置角色特定动作的图片播放ID
    def reset_imgId(self, action: str) -> None:
        self.set_imgId(action, 0)

    # 增加角色特定动作的图片播放ID
    def add_imgId(self, action: str, amount: int = 1) -> None:
        self.__imgId_dict[action]["imgId"] += amount

    # 获取角色特定动作的图片透明度
    def get_imgAlpaha(self, action: str) -> int:
        return int(self.__imgId_dict[action]["alpha"])

    # 设定角色特定动作的图片透明度
    def set_imgAlpaha(self, action: str, alpha: int) -> None:
        self.__imgId_dict[action]["alpha"] = alpha

    """
    角色行动值参数管理
    """

    # 当前行动值
    @property
    def max_action_point(self) -> int:
        return self.__max_action_point

    # 设置当前行动值，不建议非开发者使用
    def set_max_action_point(self, point: int) -> None:
        self.__max_action_point = point

    # 当前行动值
    @property
    def current_action_point(self) -> int:
        return self.__current_action_point

    # 设置当前行动值，不建议非开发者使用
    def set_current_action_point(self, point: int) -> None:
        self.__current_action_point = point

    # 重置行动点数
    def reset_action_point(self) -> None:
        self.set_current_action_point(self.__max_action_point)

    # 是否有足够的开发点数
    def have_enough_action_point(self, value: int) -> bool:
        return self.__current_action_point >= value

    # 尝试减少行动值，如果成功，返回true,失败则返回false
    def try_reduce_action_point(self, value: int) -> bool:
        # 有足够的行动值来减去
        if self.__current_action_point >= value:
            self.__current_action_point -= value
            return True
        # 没有足够的行动值来减去
        else:
            return False

    """
    角色血量护甲参数管理
    """

    # 是否角色还活着
    def is_alive(self) -> bool:
        return self.__current_hp > 0

    # 当前血量
    @property
    def current_hp(self) -> int:
        return self.__current_hp

    # 最大血量
    @property
    def max_hp(self) -> int:
        return self.__max_hp

    # 当前血量百分比
    @property
    def hp_precentage(self) -> float:
        return float(round(self.__current_hp / self.__max_hp, 5))

    # 治愈
    def heal(self, hpHealed: int) -> None:
        if hpHealed > 0:
            self.__current_hp += hpHealed
        elif hpHealed == 0:
            pass
        else:
            EXCEPTION.fatal("You cannot heal a negative value")

    # 降低血量
    def injury(self, damage: int) -> None:
        if not self.__if_invincible and damage > 0:
            # 如果有可再生的护甲
            if self.__current_recoverable_armor > 0:
                # 如果伤害大于护甲值,则以护甲值为最大护甲将承受的伤害
                if damage > self.__current_recoverable_armor:
                    damage_take_by_armor = get_random_int(0, self.__current_recoverable_armor)
                # 如果伤害小于护甲值,则以伤害为最大护甲将承受的伤害
                else:
                    damage_take_by_armor = get_random_int(0, damage)
                self.__current_recoverable_armor -= damage_take_by_armor
                damage -= damage_take_by_armor
            # 如果有不可再生的护甲
            if self.__irrecoverable_armor > 0 and damage > 0:
                if damage > self.__irrecoverable_armor:
                    damage_take_by_armor = get_random_int(0, self.__irrecoverable_armor)
                # 如果伤害小于护甲值,则以伤害为最大护甲将承受的伤害
                else:
                    damage_take_by_armor = get_random_int(0, damage)
                self.__irrecoverable_armor -= damage_take_by_armor
                damage -= damage_take_by_armor
            # 如果还有伤害,则扣除血量
            if damage > 0:
                self.__current_hp -= damage
            # 如果角色血量小等于0，进入死亡状态
            if self.__current_hp <= 0:
                self.__current_hp = 0
                self.set_action("die", False, False)
        elif self.__if_invincible or damage == 0:
            pass
        else:
            EXCEPTION.fatal("You cannot do a negative damage")

    # 回复可再生护甲
    def recover_armor(self, value: int) -> None:
        self.__current_recoverable_armor += value
        # 防止可再生护甲的数值越界
        if self.__current_recoverable_armor > self.__max_recoverable_armor:
            self.__current_recoverable_armor = self.__max_recoverable_armor
        elif self.__current_recoverable_armor < 0:
            self.__current_recoverable_armor = 0

    """
    其他
    """

    # 设置反转
    def set_flip(self, theBool: bool) -> None:
        self._if_flip = theBool

    # 播放角色声音
    def play_sound(self, kind_of_sound: str) -> None:
        if LINPG_RESERVED_SOUND_EFFECTS_CHANNEL is not None:
            _point: Optional[dict] = self.__SOUNDS.get(self.__type)
            if _point is not None:
                sound_list: Optional[list] = _point.get(kind_of_sound)
                if sound_list is not None and len(sound_list) > 0:
                    sound = sound_list[get_random_int(0, len(sound_list) - 1) if len(sound_list) > 1 else 0]
                    sound.set_volume(Media.volume.effects / 100.0)
                    LINPG_RESERVED_SOUND_EFFECTS_CHANNEL.play(sound)

    # 设置需要移动的路径
    def move_follow(self, path: list) -> None:
        if isinstance(path, list) and len(path) > 0:
            self.__moving_path = deque(path)
            self.__moving_complete = False
            self.set_action("move")
        else:
            EXCEPTION.fatal("Character cannot move to a invalid path!")

    # 查看是否需要重新渲染地图
    def needUpdateMap(self) -> bool:
        if self.__if_map_need_update:
            self.__if_map_need_update = False
            return True
        else:
            return False

    # 查看是否一个Entity在该角色的附近
    def near(self, otherEntity: "Entity") -> bool:
        if self.x == otherEntity.x:
            return abs(self.y - otherEntity.y) <= 1
        elif self.y == otherEntity.y:
            return abs(self.x - otherEntity.x) <= 1
        else:
            return False

    # 根据给定的坐标和范围列表生成范围坐标列表
    @classmethod
    def generate_range_coordinates(
        cls, _x: int, _y: int, _ranges: tuple[int, ...], MAP_P: AbstractMap, ifFlip: bool, ifHalfMode: bool = False
    ) -> list[list[tuple[int, int]]]:
        # 初始化数据
        start_point: int = 0
        end_point: int = 0
        max_effective_range: int = sum(_ranges)
        # 确定范围
        if not ifHalfMode:
            start_point = _y - max_effective_range
            end_point = _y + max_effective_range + 1
        elif not ifFlip:
            start_point = _y - max_effective_range
            end_point = _y + 1
        else:
            start_point = _y
            end_point = _y + max_effective_range + 1
        # 所在的区域
        attack_range: list[list[tuple[int, int]]] = [[] for i in range(len(_ranges))]
        the_range_in: int = -1
        row_start: int = _x - max_effective_range
        row_end: int = _x + max_effective_range + 1
        # append坐标
        for y in range(start_point, end_point):
            y_offset: int = abs(y - _y)
            for x in range(row_start + y_offset, row_end - y_offset):
                if (
                    MAP_P.row > y >= 0
                    and MAP_P.column > x >= 0
                    and (the_range_in := cls.__identify_range(_ranges, abs(x - _x) + abs(y - _y))) >= 0
                ):
                    attack_range[the_range_in].append((x, y))
        return attack_range

    # 根据距离确定对象所在区域
    @staticmethod
    def __identify_range(_ranges: tuple[int, ...], distanceBetween: int) -> int:
        if distanceBetween > 0:
            _total: int = 0
            for i in range(len(_ranges)):
                _total += _ranges[i]
                if distanceBetween <= _total:
                    return i
        return -1

    # 获取角色的攻击范围
    def get_effective_range_coordinates(self, MAP_P: AbstractMap, ifHalfMode: bool = False) -> list[list[tuple[int, int]]]:
        return self.generate_range_coordinates(int(self.x), int(self.y), self.__effective_range, MAP_P, self._if_flip, ifHalfMode)

    # 获取对象所在区域
    def range_target_in(self, otherEntity: "Entity") -> int:
        return self.__identify_range(
            self.__effective_range, abs(round(otherEntity.x) - round(self.x)) + abs(round(otherEntity.y) - round(self.y))
        )

    # 根据给定的坐标和半径生成覆盖范围坐标列表
    @staticmethod
    def generate_coverage_coordinates(_x: int, _y: int, _radius: int, MAP_P: AbstractMap) -> list[tuple[int, int]]:
        the_attacking_range_area: list[tuple[int, int]] = []
        for y in range(_y - _radius + 1, _y + _radius):
            for x in range(_x - _radius + abs(y - _y) + 1, _x + _radius - abs(y - _y)):
                if MAP_P.if_block_can_pass_through(x, y):
                    the_attacking_range_area.append((x, y))
        return the_attacking_range_area

    # 获取角色的攻击覆盖范围
    def get_attack_coverage_coordinates(self, _x: int, _y: int, MAP_P: AbstractMap) -> list[tuple[int, int]]:
        if self.__identify_range(self.__effective_range, abs(_x - round(self.x)) + abs(_y - round(self.y))) >= 0:
            return list(
                filter(
                    lambda pos: self.__identify_range(
                        self.__effective_range, abs(pos[0] - round(self.x)) + abs(pos[1] - round(self.y))
                    )
                    >= 0,
                    self.generate_coverage_coordinates(_x, _y, self.__attack_coverage, MAP_P),
                )
            )
        return []

    # 根据坐标反转角色
    def set_flip_based_on_pos(self, pos: object) -> None:
        # 转换坐标
        x, y = Positions.convert(pos)
        # 检测坐标
        if self.x > x:
            self.set_flip(True)
        elif self.x == x:
            self.set_flip(self.y <= y)
        else:
            self.set_flip(False)

    """画出角色"""
    # 角色画到surface上
    def __blit_entity_img(
        self,
        surface: ImageSurface,
        MAP_P: AbstractMap,
        alpha: int,
        action: Optional[str] = None,
        pos: Optional[tuple[int, int]] = None,
    ) -> None:
        # 如果没有指定action,则默认使用当前的动作
        if action is None:
            action = self.__current_action
        # 获取对应动作的图片管理模块
        _image = EntitySpriteImageManager.get_images(self.__type, action)
        _image.set_index(self.__imgId_dict[action]["imgId"])
        # 调整小人图片的尺寸
        img_width: float = round(MapImageParameters.get_block_width() * 8 / 5, 2)
        _image.set_size(img_width, img_width)
        # 如果没有指定pos,则默认使用当前的动作
        if pos is None:
            pos = MAP_P.calculate_position(self.x, self.y)
        # 把角色图片画到屏幕上
        _image.draw_onto(
            surface,
            alpha,
            self._if_flip,
            (pos[0] - MapImageParameters.get_block_width() * 0.3, pos[1] - MapImageParameters.get_block_width() * 0.85),
            self.__is_selected,
        )
        # 更新角色的rect
        self.__current_image_rect = _image.get_rectangle()

    # 把角色画到surface上，并操控imgId以跟踪判定下一帧的动画
    def draw(self, surface: ImageSurface, MAP_P: AbstractMap, update_id_only: bool = False) -> None:
        # 画出角色
        if not update_id_only:
            self.__blit_entity_img(surface, MAP_P, self.get_imgAlpaha(self.__current_action))
        """计算imgId"""
        # 如果正在播放移动动作，则需要根据现有路径更新坐标
        if self.__current_action == "move" and not self.__moving_complete:
            if len(self.__moving_path) > 0:
                if self.x < self.__moving_path[0][0]:
                    self.x += 0.05
                    self.set_flip(False)
                    if self.x >= self.__moving_path[0][0]:
                        self.x = self.__moving_path[0][0]
                        self.__moving_path.popleft()
                        self.__if_map_need_update = True
                elif self.x > self.__moving_path[0][0]:
                    self.x -= 0.05
                    self.set_flip(True)
                    if self.x <= self.__moving_path[0][0]:
                        self.x = self.__moving_path[0][0]
                        self.__moving_path.popleft()
                        self.__if_map_need_update = True
                elif self.y < self.__moving_path[0][1]:
                    self.y += 0.05
                    self.set_flip(True)
                    if self.y >= self.__moving_path[0][1]:
                        self.y = self.__moving_path[0][1]
                        self.__moving_path.popleft()
                        self.__if_map_need_update = True
                elif self.y > self.__moving_path[0][1]:
                    self.y -= 0.05
                    self.set_flip(False)
                    if self.y <= self.__moving_path[0][1]:
                        self.y = self.__moving_path[0][1]
                        self.__moving_path.popleft()
                        self.__if_map_need_update = True
            elif not self.__moving_complete:
                self.__moving_complete = True
                if EntitySpriteImageManager.does_action_exist(self.type, "set") is True:
                    self.set_action("set", False)
                else:
                    self.set_action()
        # 如果是正序播放
        if not self._if_play_action_in_reversing:
            # 如果角色图片还没播放完，则增加id by 1
            if self.__imgId_dict[self.__current_action]["imgId"] < self.get_imgNum(self.__current_action) - 1:
                self.__imgId_dict[self.__current_action]["imgId"] += 1
            # 如果角色图片播放完需要重新播
            elif self.__if_action_loop is True:
                self.__imgId_dict[self.__current_action]["imgId"] = 0
            # 如果角色图片播放完但不打算重新播
            elif not self.__if_switch_to_idle_afterwards:
                pass
            # 如果角色图片播放完需要回到待机状态
            elif not self.__if_action_loop:
                self.set_action()
            else:
                EXCEPTION.fatal("The self.__if_action_loop data error: {}".format(self.__if_action_loop))
        # 如果是颠倒播放，但id还未降至0，则减去1
        elif self.__imgId_dict[self.__current_action]["imgId"] > 0:
            self.__imgId_dict[self.__current_action]["imgId"] -= 1
        # 如果是颠倒播放，但id已经降至0
        else:
            self._if_play_action_in_reversing = False
            self.set_action()

    def draw_custom(
        self,
        action: str,
        pos: tuple[int, int],
        surface: ImageSurface,
        MAP_P: AbstractMap,
        isContinue: bool = True,
        alpha: int = 155,
    ) -> bool:
        self.__blit_entity_img(surface, MAP_P, alpha, action, pos)
        # 调整id，并返回对应的bool状态
        if self.__imgId_dict[action]["imgId"] < self.get_imgNum(action) - 1:
            self.__imgId_dict[action]["imgId"] += 1
            return True
        # 如果需要循环，则重设播放的index
        elif isContinue is True:
            self.__imgId_dict[action]["imgId"] = 0
        return isContinue

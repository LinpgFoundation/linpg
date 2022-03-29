from collections import deque
from .sound import *

# 人形模块
class Entity(Position):

    # 储存角色音效的常量
    __CHARACTERS_SOUND_SYSTEM: EntitySoundManager = EntitySoundManager(5)
    # idle动作
    __IDLE_ACTION: str = "wait"

    def __init__(self, DATA: dict, mode: str):
        super().__init__(DATA["x"], DATA["y"])
        # 最大行动值
        self.__max_action_point: int = int(DATA["max_action_point"])
        # 当前行动值
        self.__current_action_point: int = (
            int(DATA["current_action_point"]) if "current_action_point" in DATA else self.__max_action_point
        )
        # 攻击范围
        self.__attack_coverage: int = int(DATA["attack_coverage"])
        # 弹夹容量
        self.__magazine_capacity: int = int(DATA["magazine_capacity"])
        # 最大血量
        self.__max_hp: int = max(int(DATA["max_hp"]), 1)
        # 当前血量
        self.__current_hp: int = int(DATA["current_hp"]) if "current_hp" in DATA else self.__max_hp
        # 不可再生的护甲值
        self.__irrecoverable_armor: int = int(DATA["irrecoverable_armor"]) if "irrecoverable_armor" in DATA else 0
        # 最大可再生的护甲值
        self.__max_recoverable_armor: int = int(DATA["max_recoverable_armor"]) if "max_recoverable_armor" in DATA else 0
        # 当前可再生的护甲值
        self.__current_recoverable_armor: int = (
            int(DATA["current_recoverable_armor"]) if "current_recoverable_armor" in DATA else self.__max_recoverable_armor
        )
        # 攻击范围
        self.__effective_range: dict = dict(DATA["effective_range"])
        # 最大攻击距离
        self.__max_effective_range: int = self._calculate_range(self.__effective_range)
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
        self.__if_flip: bool = bool(DATA["if_flip"]) if "if_flip" in DATA else False
        # 当前动作
        self.__current_action: str = str(DATA["current_action"]) if "current_action" in DATA else self.__IDLE_ACTION
        # 动作是否重复
        self.__if_action_loop: bool = bool(DATA["if_action_loop"]) if "if_action_loop" in DATA else True
        # 是否动作完成后返回idle
        self.__if_switch_to_idle_afterwards: bool = (
            bool(DATA["if_switch_to_idle_afterwards"]) if "if_switch_to_idle_afterwards" in DATA else True
        )
        # 动作是正序列播放还是反序播放
        self._if_play_action_in_reversing: bool = (
            bool(DATA["if_play_action_in_reversing"]) if "if_play_action_in_reversing" in DATA else False
        )
        # 需要移动的路径
        self.__moving_path: deque = deque(DATA["moving_path"]) if "moving_path" in DATA else deque()
        self.__moving_complete: bool = (
            len(self.__moving_path) <= 0 if "moving_complete" not in DATA else bool(DATA["moving_complete"])
        )
        # 是否无敌
        self.__if_invincible: bool = bool(DATA["if_invincible"]) if "if_invincible" in DATA else False
        # gif图片管理
        self.__imgId_dict: dict = EntitySpriteImageManager.load(self.__faction, self.__type, mode)
        # 加载角色的音效
        if mode != "dev":
            self.__CHARACTERS_SOUND_SYSTEM.add(self.__type)
        # 是否需要重新渲染地图
        self.__if_map_need_update: bool = False
        # 攻击范围
        self.__attack_range: dict[str, list] = {"near": [], "middle": [], "far": []}
        # 血条图片
        self.__hp_bar: EntityHpBar = EntityHpBar()
        self.__status_font: StaticTextSurface = StaticTextSurface("", 0, 0, Display.get_width() / 192)
        # 当前图片的rect
        self.__current_image_rect: Optional[Rectangle] = None
        # 是否被选中
        self.__is_selected: bool = False

    # 计算最远攻击距离
    @staticmethod
    def _calculate_range(effective_range_dic: dict) -> int:
        if effective_range_dic is not None and len(effective_range_dic) > 0:
            max_attack_range: int = 0
            if effective_range_dic.get("far") is not None and max_attack_range < effective_range_dic["far"][-1]:
                return int(effective_range_dic["far"][-1])
            elif effective_range_dic.get("middle") is not None and max_attack_range < effective_range_dic["middle"][-1]:
                return int(effective_range_dic["middle"][-1])
            elif effective_range_dic.get("near") is not None and max_attack_range < effective_range_dic["near"][-1]:
                return int(effective_range_dic["near"][-1])
            return max_attack_range
        else:
            return 0

    def to_dict(self) -> dict:
        data: dict = {
            "x": self.x,
            "y": self.y,
            "max_action_point": self.__max_action_point,
            "attack_coverage": self.__attack_coverage,
            "magazine_capacity": self.__magazine_capacity,
            "max_hp": self.__max_hp,
            "effective_range": self.__effective_range,
            "kind": self.__kind,
            "type": self.__type,
            "max_damage": self.__max_damage,
            "min_damage": self.__min_damage,
        }
        """以下是可选数据"""
        if self.__if_flip is True:
            data["if_flip"] = self.__if_flip
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
    def effective_range(self) -> dict:
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
        self.__max_action_point = int(point)

    # 当前行动值
    @property
    def current_action_point(self) -> int:
        return self.__current_action_point

    # 设置当前行动值，不建议非开发者使用
    def set_current_action_point(self, point: int) -> None:
        self.__current_action_point = int(point)

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
        self.__current_recoverable_armor += int(value)
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
        self.__if_flip = theBool

    # 播放角色声音
    def play_sound(self, kind_of_sound: str) -> None:
        self.__CHARACTERS_SOUND_SYSTEM.play(self.__type, kind_of_sound)

    # 设置需要移动的路径
    def move_follow(self, path: list) -> None:
        if isinstance(path, list) and len(path) > 0:
            self.__moving_path = deque(path)
            self.__moving_complete = False
            self.set_action("move")
        else:
            EXCEPTION.fatal("Character cannot move to a invalid path!")

    # 根据路径移动
    def __move_based_on_path(self) -> None:
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

    # 根据距离确定对象所在区域
    def __identify_range(self, distanceBetween: int) -> Optional[str]:
        if (
            self.__effective_range.get("near") is not None
            and self.__effective_range["near"][0] <= distanceBetween <= self.__effective_range["near"][1]
        ):
            return "near"
        elif (
            self.__effective_range.get("middle") is not None
            and self.__effective_range["middle"][0] <= distanceBetween <= self.__effective_range["middle"][1]
        ):
            return "middle"
        elif (
            self.__effective_range.get("far") is not None
            and self.__effective_range["far"][0] <= distanceBetween <= self.__effective_range["far"][1]
        ):
            return "far"
        else:
            return None

    # 获取角色的攻击范围
    def getAttackRange(self, MAP_POINTER: MapObject, ifHalfMode: bool = False) -> dict:
        # 初始化列表
        for value in self.__attack_range.values():
            value.clear()
        start_point: int = 0
        end_point: int = 0
        # 确定范围
        if not ifHalfMode:
            start_point = int(self.y) - self.__max_effective_range
            end_point = int(self.y) + self.__max_effective_range + 1
        elif not self.__if_flip:
            start_point = int(self.y) - self.__max_effective_range
            end_point = int(self.y) + 1
        else:
            start_point = int(self.y)
            end_point = int(self.y) + self.__max_effective_range + 1
        # 所在的区域
        the_range_in: Optional[str] = None
        # append坐标
        for y in range(start_point, end_point):
            if y <= self.y:
                for x in range(
                    round(self.x) - self.__max_effective_range - (y - round(self.y)),
                    round(self.x) + self.__max_effective_range + (y - round(self.y)) + 1,
                ):
                    if (
                        not (x == round(self.x) and y == round(self.y))
                        and MAP_POINTER.row > y >= 0
                        and MAP_POINTER.column > x >= 0
                    ):
                        the_range_in = self.__identify_range(int(abs(x - self.x) + abs(y - self.y)))
                        if the_range_in is not None:
                            self.__attack_range[the_range_in].append((x, y))
            else:
                for x in range(
                    round(self.x) - self.__max_effective_range + (y - round(self.y)),
                    round(self.x) + self.__max_effective_range - (y - round(self.y)) + 1,
                ):
                    if MAP_POINTER.row > y >= 0 and MAP_POINTER.column > x >= 0:
                        the_range_in = self.__identify_range(int(abs(x - self.x) + abs(y - self.y)))
                        if the_range_in is not None:
                            self.__attack_range[the_range_in].append((x, y))
        return self.__attack_range

    # 目标角色所在的攻击范围内
    def range_target_in(self, otherEntity: "Entity", custom_pos: Optional[Sequence] = None) -> Optional[str]:
        return self.__identify_range(
            abs(int(otherEntity.x - self.x)) + abs(int(otherEntity.y - self.y))
            if custom_pos is None
            else abs(int(otherEntity.x - custom_pos[0])) + abs(int(otherEntity.y - custom_pos[1]))
        )

    # 判断是否在攻击范围内
    def can_attack(self, otherEntity: "Entity") -> bool:
        return self.range_target_in(otherEntity) is not None

    # 返回该角色的理想攻击范围
    @property
    def ideal_attack_range(self) -> int:
        if self.__effective_range.get("near") is not None:
            return int(self.__effective_range["near"][-1])
        elif self.__effective_range.get("middle") is not None:
            return int(self.__effective_range["middle"][-1])
        elif self.__effective_range.get("far") is not None:
            return int(self.__effective_range["far"][-1])
        else:
            EXCEPTION.fatal("This character has no valid effective range!")

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
        self, surface: ImageSurface, MAP_POINTER: MapObject, alpha: int, action: Optional[str] = None, pos: tuple = tuple()
    ) -> None:
        # 如果没有指定action,则默认使用当前的动作
        if action is None:
            action = self.__current_action
        # 获取对应动作的图片管理模块
        _image = EntitySpriteImageManager.get_images(self.__type, action)
        _image.set_index(self.__imgId_dict[action]["imgId"])
        # 调整小人图片的尺寸
        img_width: float = round(MAP_POINTER.block_width * 8 / 5, 2)
        _image.set_size(img_width, img_width)
        # 如果没有指定pos,则默认使用当前的动作
        if len(pos) < 1:
            pos = MAP_POINTER.calculate_position(self.x, self.y)
        # 把角色图片画到屏幕上
        _image.draw_onto(
            surface,
            alpha,
            self.__if_flip,
            (pos[0] - MAP_POINTER.block_width * 0.3, pos[1] - MAP_POINTER.block_width * 0.85),
            self.__is_selected,
        )
        # 更新角色的rect
        self.__current_image_rect = _image.get_rectangle()

    # 把角色画到surface上，并操控imgId以跟踪判定下一帧的动画
    def draw(self, surface: ImageSurface, MAP_POINTER: MapObject, update_id_only: bool = False) -> None:
        # 画出角色
        if not update_id_only:
            self.__blit_entity_img(surface, MAP_POINTER, self.get_imgAlpaha(self.__current_action))
        """计算imgId"""
        # 如果正在播放移动动作，则需要根据现有路径更新坐标
        if self.__current_action == "move" and not self.__moving_complete:
            self.__move_based_on_path()
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
        self, action: str, pos: tuple, surface: ImageSurface, MAP_POINTER: MapObject, isContinue: bool = True, alpha: int = 155
    ) -> bool:
        self.__blit_entity_img(surface, MAP_POINTER, alpha, action, pos)
        # 调整id，并返回对应的bool状态
        if self.__imgId_dict[action]["imgId"] < self.get_imgNum(action) - 1:
            self.__imgId_dict[action]["imgId"] += 1
            return True
        # 如果需要循环，则重设播放的index
        elif isContinue is True:
            self.__imgId_dict[action]["imgId"] = 0
        return isContinue

    # 把角色ui画到屏幕上
    def _drawUI(self, surface: ImageSurface, MAP_POINTER: MapObject, customHpData: Optional[tuple] = None) -> tuple:
        xTemp, yTemp = MAP_POINTER.calculate_position(self.x, self.y)
        xTemp += int(MAP_POINTER.block_width / 4)
        yTemp -= int(MAP_POINTER.block_width / 5)
        self.__hp_bar.set_size(MAP_POINTER.block_width / 2, MAP_POINTER.block_width / 10)
        self.__hp_bar.set_pos(xTemp, yTemp)
        # 预处理血条图片
        if customHpData is None:
            self.__hp_bar.set_percentage(self.__current_hp / self.__max_hp)
            self.__hp_bar.set_dying(False)
            self.__status_font.set_text("{0}/{1}".format(self.__current_hp, self.__max_hp))
        else:
            self.__hp_bar.set_percentage(customHpData[0] / customHpData[1])
            self.__hp_bar.set_dying(customHpData[2])
            self.__status_font.set_text("{0}/{1}".format(customHpData[0], customHpData[1]))
        # 把血条画到屏幕上
        self.__hp_bar.draw(surface)
        self.__status_font.set_pos(
            self.__hp_bar.x + int((self.__hp_bar.get_width() - self.__status_font.get_width()) / 2),
            self.__hp_bar.y + int((self.__hp_bar.get_height() - self.__status_font.get_height()) / 2),
        )
        self.__status_font.draw(surface)
        # 返回坐标以供子类进行处理
        return xTemp, yTemp

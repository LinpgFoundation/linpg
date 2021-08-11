from .entityModule import *

# 储存角色图片的常量
_CHARACTERS_IMAGE_SYS: object = EntityImageManager()
# 储存角色音效的常量
_CHARACTERS_SOUND_SYSTEM: object = EntitySoundManager(5)
# 角色UI的文字数据
_ENTITY_UI_FONT: object = Font.create(Display.get_width() / 192)

# 濒死回合限制
DYING_ROUND_LIMIT: int = 3

# 人形模块
class Entity:
    def __init__(self, DATA: dict, faction: str, mode: str):
        # 坐标（注意，与传统GameObject不同，Entity坐标使用浮点数）
        self.x: number = DATA["x"]
        self.y: number = DATA["y"]
        # 最大行动值
        self.max_action_point = DATA["action_point"]
        # 当前行动值
        self.__current_action_point: int = int(DATA["action_point"])
        # 攻击范围
        self.attack_range = DATA["attack_range"]
        # 当前弹夹的子弹数
        self.current_bullets = DATA["current_bullets"] if "current_bullets" in DATA else DATA["magazine_capacity"]
        # 当前血量
        self.__current_hp = DATA["current_hp"] if "current_hp" in DATA else DATA["max_hp"]
        # 最大血量
        self.__max_hp = max(DATA["max_hp"], 1)
        # 不可再生的护甲值
        self.__irrecoverable_armor = DATA["irrecoverable_armor"] if "irrecoverable_armor" in DATA else 0
        # 当前可再生的护甲值
        self.__current_recoverable_armor = DATA["recoverable_armor"] if "recoverable_armor" in DATA else 0
        # 最大可再生的护甲值
        self.__max_recoverable_armor = DATA["recoverable_armor"] if "recoverable_armor" in DATA else 0
        # 是否濒死
        self.dying = False if self.is_alive() else DYING_ROUND_LIMIT
        # 攻击距离
        self.effective_range = DATA["effective_range"]
        # 最大攻击距离
        self._max_effective_range = calculate_range(self.effective_range)
        # 武器类型
        self.kind = DATA["kind"]
        # 阵营
        self.faction = faction
        # 角色武器名称
        self.type = DATA["type"]
        # gif图片管理
        self.__imgId_dict = _CHARACTERS_IMAGE_SYS.createGifDict(self.type, faction, mode)
        # 加载角色的音效
        if mode != "dev":
            _CHARACTERS_SOUND_SYSTEM.add(self.type)
        # 弹夹容量
        self.magazine_capacity = DATA["magazine_capacity"]
        # 最大攻击力
        self.max_damage = DATA["max_damage"]
        # 最小攻击力
        self.min_damage = DATA["min_damage"]
        # 是否图片镜像
        self.if_flip = False
        # idle动作
        self.idle_action = "wait"
        # 当前动作
        self.__current_action = self.idle_action
        # 动作是否重复
        self.__if_action_loop: bool = True
        # 动作是正序列播放还是反序播放
        self._if_play_action_in_reversing: bool = False
        # 需要移动的路径
        self.__moving_path = None
        # 是否需要重新渲染地图
        self.__if_map_need_update: bool = False
        # 攻击范围
        self.__attack_range: dict = {"near": [], "middle": [], "far": []}
        # 是否无敌
        self.__if_invincible: bool = False
        # 血条图片
        self.__hp_bar = EntityHpBar()

    """坐标参数"""

    @property
    def pos(self) -> tuple[number]:
        return self.x, self.y

    def get_pos(self) -> tuple[number]:
        return self.x, self.y

    def set_pos(self, x: number, y: number) -> None:
        self.x = x
        self.y = y

    """角色动作参数管理"""
    # 当前动作
    @property
    def action(self) -> str:
        return self.__current_action

    # 获取当前动作，建议使用self.action
    def get_action(self) -> str:
        return self.__current_action

    # 设置动作
    def set_action(self, action: str = "wait", ifLoop: bool = True) -> None:
        self.reset_imgId(self.__current_action)
        self.__current_action = action
        self.__if_action_loop = ifLoop

    # 是否闲置
    def is_idle(self) -> bool:
        return self.__current_action == self.idle_action

    # 获取角色特定动作的图片播放ID
    def get_imgId(self, action: str) -> int:
        try:
            action_dict: dict = self.__imgId_dict[action]
        except KeyError:
            EXCEPTION.fatal('Action "{}" is invalid!'.format(action))
        return action_dict["imgId"] if action_dict is not None else -1

    # 获取角色特定动作的图片总数量
    def get_imgNum(self, action: str) -> int:
        return _CHARACTERS_IMAGE_SYS.get_img_num(self.type, action)

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
        return self.__imgId_dict[action]["alpha"]

    # 设定角色特定动作的图片透明度
    def set_imgAlpaha(self, action: str, alpha: int) -> None:
        self.__imgId_dict[action]["alpha"] = alpha

    """角色行动值参数管理"""
    # 当前行动值
    @property
    def current_action_point(self) -> int:
        return self.__current_action_point

    # 获取当前行动值,建议使用self.current_action_point
    def get_current_action_point(self) -> int:
        return self.__current_action_point

    # 设置当前行动值，不建议非开发者使用
    def set_current_action_point(self, point: int) -> None:
        self.__current_action_point = int(point)

    # 重置行动点数
    def reset_action_point(self) -> None:
        self.set_current_action_point(self.max_action_point)

    # 是否有足够的开发点数
    def have_enough_action_point(self, value: int) -> bool:
        return self.__current_action_point >= value

    # 尝试减少行动值，如果成功，返回true,失败则返回false
    def try_reduce_action_point(self, value: int) -> bool:
        if isinstance(value, int):
            if self.__current_action_point >= value:
                # 有足够的行动值来减去
                self.__current_action_point -= value
                return True
            else:
                # 没有足够的行动值来减去
                return False
        else:
            EXCEPTION.fatal("While you reduce the action points, the module cannot reduce a non-int value!")

    """角色血量护甲参数管理"""
    # 是否角色还活着
    @property
    def isAlive(self) -> bool:
        return self.__current_hp > 0

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
    def hp_precentage(self) -> bool:
        return self.__current_hp / self.__max_hp

    # 治愈
    def heal(self, hpHealed: int) -> None:
        if hpHealed > 0:
            self.__current_hp += hpHealed
        elif hpHealed == 0:
            pass
        else:
            EXCEPTION.fatal("You cannot heal a negative value")

    # 降低血量
    def decreaseHp(self, damage: int):
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
                self.set_action("die", None)
        elif self.__if_invincible or damage == 0:
            pass
        else:
            EXCEPTION.fatal("You cannot do a negative damage")

    # 攻击另一个Entity
    def attack(self, another_entity: object) -> int:
        damage = get_random_int(self.min_damage, self.max_damage)
        another_entity.decreaseHp(damage)
        return damage

    # 回复可再生护甲
    def recover_armor(self, value: int) -> None:
        self.__current_recoverable_armor += int(value)
        # 防止可再生护甲的数值越界
        if self.__current_recoverable_armor > self.__max_recoverable_armor:
            self.__current_recoverable_armor = self.__max_recoverable_armor
        elif self.__current_recoverable_armor < 0:
            self.__current_recoverable_armor = 0

    """其他"""
    # 设置反转
    def set_flip(self, theBool: bool) -> None:
        self.if_flip = theBool

    # 播放角色声音
    def play_sound(self, kind_of_sound: str) -> None:
        _CHARACTERS_SOUND_SYSTEM.play(self.type, kind_of_sound)

    # 设置需要移动的路径
    def move_follow(self, path: Iterable) -> None:
        if isinstance(path, Iterable) and len(path) > 0:
            self.__moving_path = deque(path)
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
        else:
            self.__moving_path = None
            if self.get_imgId("set") >= 0:
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

    # 加载图片
    def load_image(self) -> None:
        for theAction in self.__imgId_dict:
            _CHARACTERS_IMAGE_SYS.loadImageCollection(self.type, theAction, self.faction)
        _CHARACTERS_SOUND_SYSTEM.add(self.type)
        self.__hp_bar.load_image()

    # 查看是否一个Entity在该角色的附近
    def near(self, otherEntity: object) -> bool:
        if self.x == otherEntity.x:
            return abs(self.y - otherEntity.y) <= 1
        elif self.y == otherEntity.y:
            return abs(self.x - otherEntity.x) <= 1
        else:
            return False

    # 获取角色的攻击范围
    def getAttackRange(self, Map: object, ifHalfMode: bool = False) -> dict:
        # 初始化列表
        for value in self.__attack_range.values():
            value.clear()
        # 确定范围
        if not ifHalfMode:
            start_point = self.y - self._max_effective_range
            end_point = self.y + self._max_effective_range + 1
        elif not self.if_flip:
            start_point = self.y - self._max_effective_range
            end_point = self.y + 1
        else:
            start_point = self.y
            end_point = self.y + self._max_effective_range + 1
        # append坐标
        for y in range(start_point, end_point):
            if y <= self.y:
                for x in range(
                    self.x - self._max_effective_range - (y - self.y), self.x + self._max_effective_range + (y - self.y) + 1
                ):
                    if x == self.x and y == self.y:
                        pass
                    if Map.row > y >= 0 and Map.column > x >= 0:
                        if (
                            "far" in self.effective_range
                            and self.effective_range["far"] is not None
                            and self.effective_range["far"][0]
                            <= abs(x - self.x) + abs(y - self.y)
                            <= self.effective_range["far"][1]
                        ):
                            self.__attack_range["far"].append((x, y))
                        elif (
                            "middle" in self.effective_range
                            and self.effective_range["middle"] is not None
                            and self.effective_range["middle"][0]
                            <= abs(x - self.x) + abs(y - self.y)
                            <= self.effective_range["middle"][1]
                        ):
                            self.__attack_range["middle"].append((x, y))
                        elif (
                            "near" in self.effective_range
                            and self.effective_range["near"] is not None
                            and self.effective_range["near"][0]
                            <= abs(x - self.x) + abs(y - self.y)
                            <= self.effective_range["near"][1]
                        ):
                            self.__attack_range["near"].append((x, y))
            else:
                for x in range(
                    self.x - self._max_effective_range + (y - self.y), self.x + self._max_effective_range - (y - self.y) + 1
                ):
                    if Map.row > y >= 0 and Map.column > x >= 0:
                        if (
                            "far" in self.effective_range
                            and self.effective_range["far"] is not None
                            and self.effective_range["far"][0]
                            <= abs(x - self.x) + abs(y - self.y)
                            <= self.effective_range["far"][1]
                        ):
                            self.__attack_range["far"].append((x, y))
                        elif (
                            "middle" in self.effective_range
                            and self.effective_range["middle"] is not None
                            and self.effective_range["middle"][0]
                            <= abs(x - self.x) + abs(y - self.y)
                            <= self.effective_range["middle"][1]
                        ):
                            self.__attack_range["middle"].append((x, y))
                        elif (
                            "near" in self.effective_range
                            and self.effective_range["near"] is not None
                            and self.effective_range["near"][0]
                            <= abs(x - self.x) + abs(y - self.y)
                            <= self.effective_range["near"][1]
                        ):
                            self.__attack_range["near"].append((x, y))
        return self.__attack_range

    # 目标角色所在的攻击范围内
    def range_target_in(self, otherEntity: object, custom_pos: any = None) -> str:
        distanceBetween: int = (
            abs(int(otherEntity.x - self.x)) + abs(int(otherEntity.y - self.y))
            if custom_pos is None
            else abs(int(otherEntity.x - custom_pos[0])) + abs(int(otherEntity.y - custom_pos[1]))
        )
        if (
            "near" in self.effective_range
            and self.effective_range["near"] is not None
            and self.effective_range["near"][0] <= distanceBetween <= self.effective_range["near"][1]
        ):
            return "near"
        elif (
            "middle" in self.effective_range
            and self.effective_range["middle"] is not None
            and self.effective_range["middle"][0] <= distanceBetween <= self.effective_range["middle"][1]
        ):
            return "middle"
        elif (
            "far" in self.effective_range
            and self.effective_range["far"] is not None
            and self.effective_range["far"][0] <= distanceBetween <= self.effective_range["far"][1]
        ):
            return "far"
        else:
            return None

    # 判断是否在攻击范围内
    def can_attack(self, otherEntity: object) -> bool:
        return self.range_target_in(otherEntity) is not None

    # 返回该角色的理想攻击范围
    @property
    def ideal_attack_range(self) -> int:
        if "near" in self.effective_range and self.effective_range["near"] is not None:
            return self.effective_range["near"][-1]
        elif "middle" in self.effective_range and self.effective_range["middle"] is not None:
            return self.effective_range["middle"][-1]
        elif "far" in self.effective_range and self.effective_range["far"] is not None:
            return self.effective_range["far"][-1]
        else:
            EXCEPTION.fatal("This character has no valid effective range!")

    # 根据坐标反转角色
    def set_flip_based_on_pos(self, pos: any):
        # 转换坐标
        x, y = Pos.convert(pos)
        # 检测坐标
        if self.x > x:
            self.set_flip(True)
        elif self.x == x:
            if self.y > y:
                self.set_flip(False)
            else:
                self.set_flip(True)
        else:
            self.set_flip(False)

    """画出角色"""
    # 角色画到surface上
    def __blit_entity_img(
        self, surface: ImageSurface, MapClass: object, action: str = None, pos: any = None, alpha: int = 155
    ) -> None:
        # 如果没有指定action,则默认使用当前的动作
        if action is None:
            action = self.__current_action
        # 调整小人图片的尺寸
        img_of_char = _CHARACTERS_IMAGE_SYS.get_img(self.type, action, self.__imgId_dict[action]["imgId"])
        img_width = round(MapClass.block_width * 1.6)
        img_of_char.set_size(img_width, img_width)
        # 调整alpha值
        img_of_char.set_alpha(alpha)
        # 反转图片
        if self.if_flip:
            img_of_char.flip_if_not()
        else:
            img_of_char.flip_back_to_normal()
        # 如果没有指定pos,则默认使用当前的动作
        if pos is None:
            pos = MapClass.calPosInMap(self.x, self.y)
        # 把角色图片画到屏幕上
        img_of_char.set_pos(pos[0] - MapClass.block_width * 0.3, pos[1] - MapClass.block_width * 0.85)
        img_of_char.draw(surface)
        # 如果是开发者模式，则开启轮廓
        if Setting.developer_mode:
            img_of_char.draw_outline(surface)

    # 把角色画到surface上，并操控imgId以跟踪判定下一帧的动画
    def draw(self, surface: ImageSurface, MapClass: object) -> None:
        self.__blit_entity_img(surface, MapClass, alpha=self.get_imgAlpaha(self.__current_action))
        # 计算imgId
        self.draw_nothing()

    # 不画出任何内容，只计算imgId
    def draw_nothing(self) -> None:
        # 如果当前动作是移动
        if self.__current_action == "move" and self.__moving_path is not None:
            self.__move_based_on_path()
        # 如果角色图片还没播放完
        if not self._if_play_action_in_reversing:
            if self.__imgId_dict[self.__current_action]["imgId"] < self.get_imgNum(self.__current_action) - 1:
                self.__imgId_dict[self.__current_action]["imgId"] += 1
            # 如果角色图片播放完需要重新播
            elif self.__if_action_loop is True:
                self.__imgId_dict[self.__current_action]["imgId"] = 0
            # 如果角色图片播放完但不打算重新播
            elif self.__if_action_loop is None:
                pass
            # 如果角色图片播放完需要回到待机状态
            elif not self.__if_action_loop:
                self.set_action()
            else:
                EXCEPTION.fatal("The self.__if_action_loop data error: {}".format(self.__if_action_loop))
        else:
            if self.__imgId_dict[self.__current_action]["imgId"] > 0:
                self.__imgId_dict[self.__current_action]["imgId"] -= 1
            else:
                self._if_play_action_in_reversing = False
                self.set_action()

    def draw_custom(self, action: str, pos: any, surface: ImageSurface, MapClass: object, isContinue: bool = True) -> bool:
        self.__blit_entity_img(surface, MapClass, action, pos)
        # 调整id，并返回对应的bool状态
        if self.__imgId_dict[action]["imgId"] < self.get_imgNum(action) - 1:
            self.__imgId_dict[action]["imgId"] += 1
            return True
        else:
            if isContinue is True:
                self.__imgId_dict[action]["imgId"] = 0
                return True
            else:
                return False

    def drawUI(self, surface: ImageSurface, MapClass: object) -> tuple:
        # 把角色图片画到屏幕上
        xTemp, yTemp = MapClass.calPosInMap(self.x, self.y)
        xTemp += MapClass.block_width * 0.25
        yTemp -= MapClass.block_width * 0.2
        self.__hp_bar.set_size(MapClass.block_width / 2, MapClass.block_width / 10)
        self.__hp_bar.set_pos(xTemp, yTemp)
        if not self.dying:
            self.__hp_bar.set_percentage(self.__current_hp / self.__max_hp)
            self.__hp_bar.draw(surface, False)
            display_in_center(
                _ENTITY_UI_FONT.render("{0}/{1}".format(self.__current_hp, self.__max_hp), Color.BLACK),
                self.__hp_bar,
                xTemp,
                yTemp,
                surface,
            )
        else:
            self.__hp_bar.set_percentage(self.dying / DYING_ROUND_LIMIT)
            self.__hp_bar.draw(surface, True)
            display_in_center(
                _ENTITY_UI_FONT.render("{0}/{1}".format(self.dying, DYING_ROUND_LIMIT), Color.BLACK),
                self.__hp_bar,
                xTemp,
                yTemp,
                surface,
            )
        return xTemp, yTemp

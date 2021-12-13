from .entity import *

# 攻击所需的AP
AP_IS_NEEDED_TO_ATTACK: int = 5
AP_IS_NEEDED_TO_MOVE_ONE_BLOCK: int = 2
# 濒死回合限制
DYING_ROUND_LIMIT: int = 3

# 友方角色类
class FriendlyCharacter(Entity):
    def __init__(self, characterData: dict, mode: str) -> None:
        super().__init__(characterData, "character", mode)
        # 是否濒死
        self.__down_time: int = (
            int(characterData["down_time"])
            if "down_time" in characterData
            else (-1 if self.is_alive() else DYING_ROUND_LIMIT)
        )
        # 当前弹夹的子弹数
        self.__current_bullets: int = (
            int(characterData["current_bullets"]) if "current_bullets" in characterData else self.magazine_capacity
        )
        # 当前携带子弹数量
        self.__bullets_carried: int = int(characterData["bullets_carried"])
        # 技能覆盖范围
        self.__skill_coverage: int = int(characterData["skill_coverage"])
        # 技能施展范围
        self.__skill_effective_range: dict = dict(characterData["skill_effective_range"])
        # 最远技能施展范围
        self.__max_skill_range: int = calculate_range(self.__skill_effective_range)
        # 被察觉程度
        self.__detection: int = (
            int(characterData["detection"]) if "detection" in characterData and characterData["detection"] is not None else 0
        )
        # 生成被察觉的图标
        self.__beNoticedImage: EntityDynamicProgressBarSurface = EntityDynamicProgressBarSurface()
        self.__beNoticedImage.set_percentage(self.__detection / 100)
        # 重创立绘
        self.__getHurtImage: Optional[EntityGetHurtImage]
        # 尝试加载重创立绘
        try:
            self.__getHurtImage = EntityGetHurtImage(self.type, Display.get_height() / 4, Display.get_height() / 2)
        except Exception:
            EXCEPTION.inform("Character {} does not have damaged artwork!".format(self.type))
            self.__getHurtImage = None
            if not os.path.exists(os.path.join("Assets/image/npc_icon", "{}.png".format(self.type))):
                print("And also its icon.")

    def to_dict(self) -> dict:
        return super().to_dict() | {
            "down_time": self.__down_time,
            "current_bullets": self.__current_bullets,
            "bullets_carried": self.__bullets_carried,
            "skill_coverage": self.__skill_coverage,
            "skill_effective_range": self.__skill_effective_range,
            "detection": self.__detection,
        }

    """
    子弹
    """

    # 当前子弹携带数量
    @property
    def bullets_carried(self) -> int:
        return self.__bullets_carried

    # 增加当前子弹携带数量
    def add_bullets_carried(self, value: int) -> None:
        self.__bullets_carried += value

    # 当前子弹数量
    @property
    def current_bullets(self) -> int:
        return self.__current_bullets

    # 减少当前子弹数量
    def subtract_current_bullets(self, value: int = 1) -> None:
        self.__current_bullets -= value

    # 是否需要换弹
    def is_reload_needed(self) -> int:
        return self.magazine_capacity - self.__current_bullets > 0

    # 换弹
    def reload_magazine(self) -> None:
        bullets_to_add: int = self.magazine_capacity - self.__current_bullets
        # 当所剩子弹足够换弹的时候
        if bullets_to_add < self.__bullets_carried:
            self.__current_bullets += bullets_to_add
            self.__bullets_carried -= bullets_to_add
        # 当所剩子弹不足以换弹的时候
        else:
            self.__current_bullets += self.__bullets_carried
            self.__bullets_carried = 0

    """
    技能
    """

    # 技能覆盖范围
    @property
    def skill_coverage(self) -> int:
        self.__skill_coverage

    # 技能施展范围
    @property
    def skill_effective_range(self) -> dict:
        self.__skill_effective_range

    # 最远技能施展范围
    @property
    def max_skill_range(self) -> int:
        self.__max_skill_range

    # 是否处于濒死状态
    def is_dying(self) -> bool:
        return self.__down_time > 0

    # 更加面临死亡
    def get_closer_to_death(self) -> None:
        self.__down_time -= 1

    # 角色彻底死亡
    def is_dead(self) -> bool:
        return self.__down_time == 0

    @property
    def detection(self) -> int:
        return self.__detection

    @property
    def is_detected(self) -> bool:
        return self.__detection >= 100

    # 调整角色的隐蔽度
    def notice(self, value: int = 10) -> None:
        self.__detection += value
        if self.__detection > 100:
            self.__detection = 100
        elif self.__detection < 0:
            self.__detection = 0
        self.__beNoticedImage.set_percentage(self.__detection / 100)

    def injury(self, damage: int) -> None:
        super().injury(damage)
        # 如果角色在被攻击后处于濒死状态
        if not self.is_alive() and self.__down_time < 0 and self.__kind != "HOC":
            self.__down_time = DYING_ROUND_LIMIT
            if self.__getHurtImage is not None:
                self.__getHurtImage.x = -self.__getHurtImage.width
                self.__getHurtImage.alpha = 255
                self.__getHurtImage.yToGo = 255
                self.play_sound("injured")

    def heal(self, hpHealed: int) -> None:
        super().heal(hpHealed)
        if self.__down_time >= 0:
            self.__down_time = -1
            self._if_play_action_in_reversing = True

    # 把角色血条画到屏幕上
    def _draw_health_bar(self, surface: ImageSurface) -> None:
        if self.__down_time < 0:
            super()._draw_health_bar(surface)
        else:
            self.__hp_bar.set_percentage(self.__down_time / DYING_ROUND_LIMIT)
            self.__hp_bar.draw(surface, True)
            display_in_center(
                self.__ENTITY_UI_FONT.render("{0}/{1}".format(self.__down_time, DYING_ROUND_LIMIT), Colors.BLACK),
                self.__hp_bar,
                self.__hp_bar.x,
                self.__hp_bar.y,
                surface,
            )

    def drawUI(self, surface: ImageSurface, MapClass: object) -> None:
        blit_pos = super().drawUI(surface, MapClass)
        # 展示被察觉的程度
        if self.__detection > 0:
            # 参数
            eyeImgWidth: int = round(MapClass.block_width / 6)
            eyeImgHeight: int = round(MapClass.block_width / 10)
            numberX: float = (eyeImgWidth - MapClass.block_width / 6) / 2
            numberY: float = (eyeImgHeight - MapClass.block_width / 10) / 2
            # 根据参数调整图片
            self.__beNoticedImage.set_size(eyeImgWidth, eyeImgHeight)
            self.__beNoticedImage.set_pos(blit_pos[0] + MapClass.block_width * 0.51 - numberX, blit_pos[1] - numberY)
            self.__beNoticedImage.draw(surface)
        # 重创立绘
        if self.__getHurtImage is not None and self.__getHurtImage.x is not None:
            self.__getHurtImage.draw(surface, self.type)
            if self.__getHurtImage.x < self.__getHurtImage.width / 4:
                self.__getHurtImage.x += self.__getHurtImage.width / 25
            else:
                if self.__getHurtImage.yToGo > 0:
                    self.__getHurtImage.yToGo -= 5
                else:
                    if self.__getHurtImage.alpha > 0:
                        self.__getHurtImage.alpha -= 2
                    else:
                        self.__getHurtImage.x = None


# 敌对角色类
class HostileCharacter(Entity):
    def __init__(self, characterData: dict, mode: str):
        super().__init__(characterData, "sangvisFerri", mode)
        self.__patrol_path: deque = deque(characterData["patrol_path"]) if "patrol_path" in characterData else deque()
        self.__vigilance: int = int(characterData["vigilance"]) if "vigilance" in characterData else 0
        self.__vigilanceImage: EntityDynamicProgressBarSurface = EntityDynamicProgressBarSurface("vertical")
        self.__vigilanceImage.set_percentage(self.__vigilance / 100)

    def to_dict(self) -> dict:
        return super().to_dict() | {"patrol_path": list(self.__patrol_path), "vigilance": self.__vigilance}

    def alert(self, value: int = 10) -> None:
        self.__vigilance += value
        # 防止警觉度数值超过阈值
        if self.__vigilance > 100:
            self.__vigilance = 100
        elif self.__vigilance < 0:
            self.__vigilance = 0
        else:
            pass
        self.__vigilanceImage.set_percentage(self.__vigilance / 100)

    @property
    def vigilance(self) -> int:
        return self.__vigilance

    @property
    def is_alert(self) -> bool:
        return self.__vigilance >= 100

    # 画UI - 列如血条
    def drawUI(self, surface: ImageSurface, MapClass: object) -> None:
        blit_pos = super().drawUI(surface, MapClass)
        # 展示警觉的程度
        if self.__vigilance > 0:
            # 参数
            eyeImgWidth: int = round(MapClass.block_width / 6)
            eyeImgHeight: int = round(MapClass.block_width / 6)
            numberX: float = (eyeImgWidth - MapClass.block_width / 6) / 2
            numberY: float = (eyeImgHeight - MapClass.block_width / 10) / 2
            # 根据参数调整图片
            self.__vigilanceImage.set_size(eyeImgWidth, eyeImgHeight)
            self.__vigilanceImage.set_pos(blit_pos[0] + MapClass.block_width * 0.51 - numberX, blit_pos[1] - numberY)
            self.__vigilanceImage.draw(surface, False)

    def make_decision(
        self, Map: object, friendlyCharacterData: dict, hostileCharacterData: dict, the_characters_detected_last_round: dict
    ) -> deque:
        # 存储友方角色价值榜
        target_value_board = []
        for name, theCharacter in friendlyCharacterData.items():
            if theCharacter.is_alive() and theCharacter.is_detected:
                weight = 0
                # 计算距离的分数
                weight += abs(self.x - theCharacter.x) + abs(self.y - theCharacter.y)
                # 计算血量分数
                weight += self.current_hp * self.hp_precentage
                target_value_board.append((name, weight))
        # 最大移动距离
        blocks_can_move: int = int(self.max_action_point / AP_IS_NEEDED_TO_MOVE_ONE_BLOCK)
        # 角色将会在该回合采取的行动
        actions: deque = deque()
        # 如果角色有可以攻击的对象，且角色至少有足够的行动点数攻击
        if len(target_value_board) > 0 and self.max_action_point > AP_IS_NEEDED_TO_ATTACK:
            action_point_can_use = self.max_action_point
            # 筛选分数最低的角色作为目标
            target = target_value_board[0][0]
            min_weight = target_value_board[0][1]
            for data in target_value_board[1:]:
                if data[1] < min_weight:
                    min_weight = data[1]
                    target = data[0]
            targetCharacterData = friendlyCharacterData[target]
            if self.can_attack(targetCharacterData):
                actions.append(DecisionHolder("attack", tuple((target, self.range_target_in(targetCharacterData)))))
                action_point_can_use -= AP_IS_NEEDED_TO_ATTACK
                """
                if action_point_can_use > AP_IS_NEEDED_TO_ATTACK:
                    if self.hp_precentage > 0.2:
                        #如果自身血量正常，则应该考虑再次攻击角色
                        actions.append(DecisionHolder("attack",target))
                        action_point_can_use -= AP_IS_NEEDED_TO_ATTACK
                    else:
                        pass
                """
            else:
                # 寻找一条能到达该角色附近的线路
                the_route = Map.findPath(
                    self.pos, targetCharacterData.pos, hostileCharacterData, friendlyCharacterData, blocks_can_move, [target]
                )
                if len(the_route) > 0:
                    potential_attacking_pos_index = {}
                    for i in range(len(the_route) - int(AP_IS_NEEDED_TO_ATTACK / AP_IS_NEEDED_TO_MOVE_ONE_BLOCK + 1)):
                        # 当前正在处理的坐标
                        pos_on_route = the_route[i]
                        # 获取可能的攻击范围
                        range_target_in_if_can_attack = self.range_target_in(targetCharacterData, pos_on_route)
                        if (
                            range_target_in_if_can_attack is not None
                            and range_target_in_if_can_attack not in potential_attacking_pos_index
                        ):
                            potential_attacking_pos_index[range_target_in_if_can_attack] = i + 1
                            if range_target_in_if_can_attack == "near":
                                break
                    if "near" in potential_attacking_pos_index:
                        actions.append(DecisionHolder("move", the_route[: potential_attacking_pos_index["near"]]))
                        actions.append(DecisionHolder("attack", tuple((target, "near"))))
                    elif "middle" in potential_attacking_pos_index:
                        actions.append(DecisionHolder("move", the_route[: potential_attacking_pos_index["middle"]]))
                        actions.append(DecisionHolder("attack", tuple((target, "middle"))))
                    elif "far" in potential_attacking_pos_index:
                        actions.append(DecisionHolder("move", the_route[: potential_attacking_pos_index["far"]]))
                        actions.append(DecisionHolder("attack", tuple((target, "far"))))
                    else:
                        actions.append(DecisionHolder("move", the_route))
                else:
                    EXCEPTION.fatal("A hostile character cannot find a valid path when trying to attack {}!".format(target))
        # 如果角色没有可以攻击的对象，则查看角色是否需要巡逻
        elif len(self.__patrol_path) > 0:
            # 如果巡逻坐标点只有一个（意味着角色需要在该坐标上长期镇守）
            if len(self.__patrol_path) == 1:
                if not Coordinates.is_same(self.pos, self.__patrol_path[0]):
                    the_route = Map.findPath(
                        self.pos, self.__patrol_path[0], hostileCharacterData, friendlyCharacterData, blocks_can_move
                    )
                    if len(the_route) > 0:
                        actions.append(DecisionHolder("move", the_route))
                    else:
                        EXCEPTION.fatal("A hostile character cannot find a valid path!")
                else:
                    # 如果角色在该点上，则原地待机
                    pass
            # 如果巡逻坐标点有多个
            else:
                the_route = Map.findPath(
                    self.pos, self.__patrol_path[0], hostileCharacterData, friendlyCharacterData, blocks_can_move
                )
                if len(the_route) > 0:
                    actions.append(DecisionHolder("move", the_route))
                    # 如果角色在这次移动后到达了最近的巡逻点，则应该更新最近的巡逻点
                    if Coordinates.is_same(the_route[-1], self.__patrol_path[0]):
                        self.__patrol_path.append(self.__patrol_path.popleft())
                else:
                    EXCEPTION.fatal("A hostile character cannot find a valid path!")
        else:
            pass
        # 放回一个装有指令的列表
        return actions


# 初始化角色信息
class CharacterDataLoader(threading.Thread):
    def __init__(self, alliances: dict, enemies: dict, mode: str) -> None:
        super().__init__()
        self.DATABASE = loadCharacterData()
        self.alliances = deepcopy(alliances)
        self.enemies = deepcopy(enemies)
        self.totalNum = len(alliances) + len(enemies)
        self.currentID = 0
        self.mode = mode

    def run(self) -> None:
        data_t: dict
        for key, value in self.alliances.items():
            data_t = deepcopy(self.DATABASE[value["type"]])
            data_t.update(value)
            self.alliances[key] = FriendlyCharacter(data_t, self.mode)
            self.currentID += 1
            if Setting.developer_mode:
                print("total: {0}, current: {1}".format(self.totalNum, self.currentID))
        for key, value in self.enemies.items():
            data_t = deepcopy(self.DATABASE[value["type"]])
            data_t.update(value)
            self.enemies[key] = HostileCharacter(data_t, self.mode)
            self.currentID += 1
            if Setting.developer_mode:
                print("total: {0}, current: {1}".format(self.totalNum, self.currentID))

    def getResult(self) -> tuple[dict, dict]:
        return self.alliances, self.enemies
# cython: language_level=3
from .mapModule import *

#地图场景图片管理
_MAP_ENV_IMAGE:object = None
#方块数据
_BLOCKS_DATABASE:dict = None
try:
    _BLOCKS_DATABASE = load_config(os.path.join("Data", "blocks.yaml"), "blocks")
except BaseException:
    _BLOCKS_DATABASE = {}

#地图模块
class MapObject(AdvancedAbstractImage):
    def __init__(self, mapDataDic:dict, perBlockWidth:int_f, perBlockHeight:int_f):
        #初始化地图数据
        self.__Map_Data = mapDataDic["map"]
        for y in range(len(self.__Map_Data)):
            for x in range(len(self.__Map_Data[y])):
                item = self.__Map_Data[y][x]
                self.__Map_Data[y][x] = BlockObject(item,_BLOCKS_DATABASE[item]["canPassThrough"])
        self.__Map_Data = numpy.asarray(self.__Map_Data)
        #使用numpy的shape决定self.row和self.column
        self.row,self.column = self.__Map_Data.shape
        #现已可以计算尺寸，初始化父类
        super().__init__(
            mapDataDic["backgroundImage"], #self.img:str储存了背景图片的信息
            0, 0,
            int(perBlockWidth*0.9*((self.row+self.column+1)/2)), int(perBlockWidth*0.45*((self.row+self.column+1)/2)+perBlockWidth)
            )
        #设置本地坐标
        self.set_local_pos(mapDataDic["local_x"], mapDataDic["local_y"])
        #是否夜战
        self.__night_mode:bool = bool(mapDataDic["atNight"]) if "atNight" in mapDataDic else False
        #装饰物
        self.__decorations:numpy.ndarray = None
        self.load_decorations(mapDataDic["decoration"])
        #加载环境
        self.load_env_img((perBlockWidth,perBlockHeight))
        #处于光处的区域
        self.__light_area:numpy.ndarray = None
        #追踪是否需要更新的参数
        self.__need_update_surface:bool = True
        #追踪目前已经画出的方块
        self.__block_on_surface:numpy.ndarray = None
        #开发者使用的窗口
        self.__debug_win = None
    @property
    def block_width(self) -> int: return _MAP_ENV_IMAGE.get_block_width()
    @property
    def block_height(self) -> int: return _MAP_ENV_IMAGE.get_block_height()
    @property
    def decorations(self) -> numpy.ndarray: return self.__decorations
    #加载环境图片，一般被视为初始化的一部分
    def load_env_img(self, block_size:tuple) -> None:
        global _MAP_ENV_IMAGE
        _MAP_ENV_IMAGE = EnvImagesManagement(self.__Map_Data, self.__decorations, self.img, block_size, self.__night_mode)
    #开发者模式
    def dev_mode(self) -> None:
        if self.__debug_win is None:
            unit:int = 10
            self.__debug_win = RenderedWindow("debug window",(int(self.row*unit+unit/4*(self.row+1)),int(self.column*unit+unit/4*(self.row+1))),True)
            self.__debug_win.unit = unit
        else:
            self.__debug_win = None
    #显示开发面板
    def __display_dev_panel(self) -> None:
        self.__debug_win.clear()
        self.__debug_win.fill("black")
        x:int; y:int; start_x:int; start_y:int
        unit:int = self.__debug_win.unit
        for y in range(len(self.__block_on_surface)):
            for x in range(len(self.__block_on_surface[y])):
                start_x = int(x*unit*1.25+unit/4)
                start_y = int(y*unit*1.25+unit/4)
                if self.__block_on_surface[y][x] == 0:
                    self.__debug_win.draw_rect((start_x,start_y,unit,unit),"white")
                else:
                    self.__debug_win.fill_rect((start_x,start_y,unit,unit),"white")
        self.__debug_win.present()
    #加载装饰物
    def load_decorations(self, decorationData:dict) -> None:
        decorations:list = []
        new_decoration:DecorationObject = None
        for decorationType,itemsThatType in decorationData.items():
            for itemData in itemsThatType.values():
                if decorationType == "campfire":
                    new_decoration = DecorationObject(itemData["x"],itemData["y"],decorationType,decorationType)
                    new_decoration.imgId = get_random_int(0,9)
                    new_decoration.range = itemData["range"]
                    new_decoration.alpha = 255
                elif decorationType == "chest":
                    new_decoration = DecorationObject(itemData["x"],itemData["y"],decorationType,decorationType)
                    new_decoration.items = itemData["items"] if "items" in itemData else []
                    #是否箱子有白名单（只能被特定角色拾取）
                    new_decoration.whitelist = itemData["whitelist"] if "whitelist" in itemData else None
                else:
                    new_decoration = DecorationObject(itemData["x"],itemData["y"],decorationType,itemData["image"])
                decorations.append(new_decoration)
        self.__decorations = numpy.sort(numpy.asarray(decorations))
    #根据index寻找装饰物
    def find_decoration_with_id(self, index:int) -> DecorationObject: return self.__decorations[index]
    #根据坐标寻找装饰物
    def find_decoration_on(self, pos:any) -> Union[DecorationObject,None]:
        for decoration in self.__decorations:
            #如果坐标一致，则应该是当前装饰物了
            if is_same_pos(decoration.get_pos(),pos): return decoration
        return None
    #与给定Index的场景装饰物进行互动
    def interact_decoration_with_id(self, index:int) -> None: self.__decorations[index].switch()
    #移除装饰物
    def remove_decoration(self, decoration:object) -> None:
        pos:tuple = decoration.get_pos()
        i:int
        for i in range(len(self.__decorations)):
            if self.__decorations[i].get_pos() == pos:
                self.__decorations = numpy.delete(self.__decorations,i)
                break
    #是否夜战
    @property
    def night_mode(self) -> bool: return self.__night_mode
    #控制地图放大缩小
    def changePerBlockSize(self, newPerBlockWidth:int_f, newPerBlockHeight:int_f) -> None:
        #记录老尺寸
        old_width:int = self._width
        old_height:int = self._height
        #更新尺寸
        self.set_width(newPerBlockWidth*0.9*((self.row+self.column+1)/2))
        self.set_height(newPerBlockWidth*0.45*((self.row+self.column+1)/2)+newPerBlockWidth)
        _MAP_ENV_IMAGE.set_block_size(newPerBlockWidth,newPerBlockHeight)
        if self._width < display.get_width():
            self._width = display.get_width()
        if self._height < display.get_height():
            self._height = display.get_height()
        #自动校准坐标
        self.add_local_x((old_width-self._width)/2)
        self.add_local_y((old_height-self._height)/2)
        #打上需要更新的标签
        self.__need_update_surface = True
        self.__block_on_surface = None
    #设置local坐标
    def set_local_x(self, value:Union[int, float]) -> None:
        old_local_x:int = self._local_x
        super().set_local_x(value)
        if self._local_x != old_local_x: self.__need_update_surface = True
    def set_local_y(self, value:Union[int, float]) -> None:
        old_local_y:int = self._local_y
        super().set_local_y(value)
        if self._local_y != old_local_y: self.__need_update_surface = True
    #把地图画到屏幕上
    def display_map(self, screen:ImageSurface, screen_to_move_x:int=0, screen_to_move_y:int=0) -> tuple:
        #检测屏幕是不是移到了不移到的地方
        if self._local_x < screen.get_width()-self._width:
            self._local_x = screen.get_width()-self._width
            screen_to_move_x = 0
        elif self._local_x > 0:
            self._local_x = 0
            screen_to_move_x = 0
        if self._local_y < screen.get_height()-self._height:
            self._local_y = screen.get_height()-self._height
            screen_to_move_y = 0
        elif self._local_y > 0:
            self._local_y = 0
            screen_to_move_y = 0
        if self.__need_update_surface is True:
            self.__need_update_surface = False
            self.__update_map_surface(screen.get_size())
        #显示调试窗口
        if self.__debug_win is not None and isinstance(self.__block_on_surface, numpy.ndarray): self.__display_dev_panel()
        #画出背景
        _MAP_ENV_IMAGE.display_background_surface(screen,self.get_local_pos())
        #返回offset
        return screen_to_move_x, screen_to_move_y
    #重新绘制地图
    def __update_map_surface(self, window_size:tuple) -> None:
        posTupleTemp:tuple
        x:int; y:int
        yRange:int = self.row
        xRange:int = self.column
        screen_min:int = -self.block_width
        if not isinstance(self.__block_on_surface, numpy.ndarray):
            mapSurface = _MAP_ENV_IMAGE.new_surface(window_size,(self._width,self._height))
            self.__block_on_surface = numpy.zeros((self.row,self.column), dtype=numpy.int8)
        mapSurface = _MAP_ENV_IMAGE.get_surface()
        #画出地图
        for y in range(yRange):
            for x in range(xRange):
                posTupleTemp = self.calPosInMap(x,y)
                if screen_min<=posTupleTemp[0]<window_size[0] and screen_min<=posTupleTemp[1]<window_size[1]:
                    if self.__block_on_surface[y][x] == 0:
                        if not self.isPosInLightArea(x,y):
                            evn_img = _MAP_ENV_IMAGE.get_env_image(self.__Map_Data[y][x].name,True)
                        else:
                            evn_img = _MAP_ENV_IMAGE.get_env_image(self.__Map_Data[y][x].name,False)
                        evn_img.set_pos(posTupleTemp[0]-self._local_x,posTupleTemp[1]-self._local_y)
                        evn_img.draw(mapSurface)
                        self.__block_on_surface[y][x] = 1
                        if y < yRange-1:
                            self.__block_on_surface[y+1][x] = 0
                        if x < xRange-1:
                            self.__block_on_surface[y][x+1] = 0
                    else:
                        pass
                elif posTupleTemp[0] >= window_size[0] or posTupleTemp[1] >= window_size[1]:
                    break
            if self.calPosInMap(0,y+1)[1] >= window_size[1]:
                break
    #把装饰物画到屏幕上
    def display_decoration(self, screen:ImageSurface, alliances_data:dict={}, enemies_data:dict={}) -> None:
        thePosInMap:tuple
        #检测角色所占据的装饰物（即需要透明化，方便玩家看到角色）
        charactersPos:list = []
        for dataDic in {**alliances_data, **enemies_data}.values():
            charactersPos.append((int(dataDic.x),int(dataDic.y)))
            charactersPos.append((int(dataDic.x)+1,int(dataDic.y)+1))
        #计算offSet
        offSetX:int = round(self.block_width/4)
        offSetY:int = round(self.block_width/8)
        offSetX_tree:int = round(self.block_width*0.125)
        offSetY_tree:int = round(self.block_width*0.25)
        #计算需要画出的范围
        screen_min:int = -self.block_width
        #历遍装饰物列表里的物品
        for item in self.__decorations:
            imgToBlit = None
            thePosInMap = self.calPosInMap(item.x,item.y)
            if screen_min <= thePosInMap[0] < screen.get_width() and screen_min <= thePosInMap[1] < screen.get_height():
                if not self.inLightArea(item):
                    keyWordTemp = True
                else:
                    keyWordTemp = False
                #篝火
                if item.type == "campfire":
                    #查看篝火的状态是否正在变化，并调整对应的alpha值
                    if item.triggered is True and item.alpha < 255:
                        item.alpha += 15
                    elif not item.triggered and item.alpha > 0:
                        item.alpha -= 15
                    #根据alpha值生成对应的图片
                    if item.alpha >= 255:
                        imgToBlit = _MAP_ENV_IMAGE.get_decoration_image("campfire",int(item.imgId),False)
                        imgToBlit.set_alpha(255)
                        if item.imgId >= _MAP_ENV_IMAGE.get_decoration_num("campfire")-2:
                            item.imgId = 0
                        else:
                            item.imgId += 0.1
                    elif item.alpha <= 0:
                        if not keyWordTemp:
                            imgToBlit = _MAP_ENV_IMAGE.get_decoration_image("campfire",-1,False)
                            imgToBlit.set_alpha(255)
                        else:
                            imgToBlit = _MAP_ENV_IMAGE.get_decoration_image("campfire","campfire",True)
                            imgToBlit.set_alpha(255)
                    else:
                        imgToBlit = _MAP_ENV_IMAGE.get_decoration_image("campfire",-1,False)
                        imgToBlit.set_alpha(255)
                        imgToBlit.set_size(self.block_width/2,self.block_width/2)
                        imgToBlit.set_pos(thePosInMap[0]+offSetX,thePosInMap[1]-offSetY)
                        imgToBlit.draw(screen)
                        imgToBlit = _MAP_ENV_IMAGE.get_decoration_image("campfire",int(item.imgId),False)
                        imgToBlit.set_alpha(item.alpha)
                        if item.imgId >= _MAP_ENV_IMAGE.get_decoration_num("campfire")-2:
                            item.imgId = 0
                        else:
                            item.imgId += 0.1
                    imgToBlit.set_size(self.block_width/2,self.block_width/2)
                #树
                elif item.type == "tree":
                    imgToBlit = _MAP_ENV_IMAGE.get_decoration_image("tree",item.image,keyWordTemp)
                    imgToBlit.set_size(self.block_width*0.75,self.block_width*0.75)
                    thePosInMap = (thePosInMap[0]-offSetX_tree,thePosInMap[1]-offSetY_tree)
                    if item.get_pos() in charactersPos and self.inLightArea(item):
                        imgToBlit.set_alpha(100)
                    else:
                        imgToBlit.set_alpha(255)
                #其他装饰物
                elif item.type == "decoration" or item.type == "obstacle" or item.type == "chest":
                    imgToBlit = _MAP_ENV_IMAGE.get_decoration_image(item.type,item.image,keyWordTemp)
                    imgToBlit.set_size(self.block_width/2,self.block_width/2)
                #画上装饰物
                if imgToBlit is not None:
                    imgToBlit.set_pos(thePosInMap[0]+offSetX,thePosInMap[1]-offSetY)
                    imgToBlit.draw(screen)
    #更新方块
    def update_block(self, pos:dict, name:str) -> None:
        self.__Map_Data[pos["y"]][pos["x"]].update(name,_BLOCKS_DATABASE[name]["canPassThrough"])
        self.__need_update_surface = True
        self.__block_on_surface = None
    #是否角色能通过该方块
    def ifBlockCanPassThrough(self, pos:dict) -> bool: return self.__Map_Data[pos["y"]][pos["x"]].canPassThrough
    #计算在地图中的方块
    def calBlockInMap(self, mouse_x:int, mouse_y:int):
        guess_x:int = int(((mouse_x-self._local_x-self.row*self.block_width*0.43)/0.43+(mouse_y-self._local_y-self.block_width*0.4)/0.22)/2/self.block_width)
        guess_y:int = int((mouse_y-self._local_y-self.block_width*0.4)/self.block_width/0.22) - guess_x
        x:int; y:int
        posTupleTemp:tuple
        lenUnitW:float = self.block_width/5
        lenUnitH:float = self.block_width*0.8/393*214
        block_get_click = None
        for y in range(guess_y-1,guess_y+4):
            for x in range(guess_x-1,guess_x+4):
                posTupleTemp = self.calPosInMap(x,y)
                if lenUnitW<mouse_x-posTupleTemp[0]-self.block_width*0.05<lenUnitW*3 and 0<mouse_y-posTupleTemp[1]<lenUnitH:
                    if 0 <= x < self.column and 0 <= y < self.row:
                        block_get_click = {"x":x,"y":y}
                    break
        return block_get_click
    #计算方块被画出的位置
    def getBlockExactLocation(self, x:int, y:int) -> dict:
        xStart,yStart = self.calPosInMap(x,y)
        return {
        "xStart": xStart,
        "xEnd": xStart + self.block_width,
        "yStart": yStart,
        "yEnd": yStart + self.block_width*0.5
        }
    #计算光亮区域
    def calculate_darkness(self, alliances_data:dict) -> None:
        lightArea:list = []
        x:int; y:int
        for each_chara in alliances_data:
            the_character_effective_range = 2
            if alliances_data[each_chara].current_hp > 0 :
                if alliances_data[each_chara].effective_range["far"] is not None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["far"][1]+1
                elif alliances_data[each_chara].effective_range["middle"] is not None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["middle"][1]+1
                elif alliances_data[each_chara].effective_range["near"] is not None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["near"][1]+1
            for y in range(int(alliances_data[each_chara].y-the_character_effective_range),int(alliances_data[each_chara].y+the_character_effective_range)):
                if y < alliances_data[each_chara].y:
                    for x in range(int(alliances_data[each_chara].x-the_character_effective_range-(y-alliances_data[each_chara].y)+1),int(alliances_data[each_chara].x+the_character_effective_range+(y-alliances_data[each_chara].y))):
                        if [x,y] not in lightArea:
                            lightArea.append([x,y])
                else:
                    for x in range(int(alliances_data[each_chara].x-the_character_effective_range+(y-alliances_data[each_chara].y)+1),int(alliances_data[each_chara].x+the_character_effective_range-(y-alliances_data[each_chara].y))):
                        if [x,y] not in lightArea:
                            lightArea.append([x,y])
        for item in self.__decorations:
            if item.type == "campfire" and item.triggered is True:
                for y in range(int(item.y-item.range),int(item.y+item.range)):
                    if y < item.y:
                        for x in range(int(item.x-item.range-(y-item.y)+1),int(item.x+item.range+(y-item.y))):
                            if [x,y] not in lightArea:
                                lightArea.append([x,y])
                    else:
                        for x in range(int(item.x-item.range+(y-item.y)+1),int(item.x+item.range-(y-item.y))):
                            if [x,y] not in lightArea:
                                lightArea.append([x,y])
        self.__light_area = numpy.asarray(lightArea,dtype=numpy.int8)
        self.__need_update_surface = True
        self.__block_on_surface = None
    #计算在地图中的位置
    def calPosInMap(self, x:int_f, y:int_f) -> tuple:
        widthTmp:float = self.block_width*0.43
        return round((x-y)*widthTmp+self._local_x+self.row*widthTmp),round((y+x)*self.block_width*0.22+self._local_y+self.block_width*0.4)
    def calAbsPosInMap(self, x:int_f, y:int_f) -> tuple:
        widthTmp:float = self.block_width*0.43
        return round((x-y)*widthTmp+self.row*widthTmp),round((y+x)*self.block_width*0.22+self.block_width*0.4)
    #查看角色是否在光亮范围内
    def inLightArea(self, entity:object) -> bool: return self.isPosInLightArea(entity.x,entity.y)
    def isPosInLightArea(self, x:int_f, y:int_f) -> bool:
        return True if not self.__night_mode else numpy.any(numpy.equal(self.__light_area,[int(x),int(y)]).all(1))
    #以下是A星寻路功能
    def findPath(self, startPosition:any, endPosition:any, friendData:dict, enemyData:dict, routeLen:int=-1, ignoreEnemyCharacters:list=[]) -> list:
        #检测起点
        start_pos:tuple = convert_pos(startPosition)
        #检测终点
        end_pos:tuple = convert_pos(endPosition)
        #建立寻路地图
        self.map2d = numpy.zeros((self.column,self.row), dtype=numpy.int8)
        # 可行走标记
        self.passTag = 0
        #历遍地图，设置障碍方块
        """
        for y in range(theMap.row):
            for x in range(theMap.column):
                if not theMap.mapData[y][x].canPassThrough:
                    self.map2d[x][y]=1
        """
        #历遍设施，设置障碍方块
        for item in self.__decorations:
            if item.type == "obstacle" or item.type == "campfire":
                self.map2d[item.x][item.y] = 1
        #如果终点有我方角色，则不允许
        for key,value in friendData.items():
            if value.x == end_pos[0] and value.y == end_pos[1]:
                return []
        #历遍所有角色，将角色的坐标点设置为障碍方块
        for key,value in enemyData.items():
            if key not in ignoreEnemyCharacters:
                self.map2d[value.x][value.y] = 1
        #如果终点是障碍物
        if self.map2d[end_pos[0]][end_pos[1]] != self.passTag:
            return []
        # 起点终点
        self.startPoint = Point(start_pos[0],start_pos[1])
        self.endPoint = Point(end_pos[0],end_pos[1])
        #开始寻路
        pathList:list = self.__startFindingPath()
        pathListLen:int = int(len(pathList))
        #遍历路径点,讲指定数量的点放到路径列表中
        if pathListLen > 0:
            #生成路径的长度
            if routeLen >= 0 and pathListLen < routeLen or routeLen <= 0: routeLen = pathListLen
            #返回路径
            return [pathList[i].get_pos() for i in range(routeLen)]
        else:
            return []
    def __getMinNode(self) -> Node:
        """
        获得OpenList中F值最小的节点
        :return: Node
        """
        currentNode = self.openList[0]
        for node in self.openList:
            if node.g + node.h < currentNode.g + currentNode.h:
                currentNode = node
        return currentNode
    def __pointInCloseList(self, point:Point) -> bool:
        for node in self.closeList:
            if node.point == point:
                return True
        return False
    def __pointInOpenList(self, point:Point) -> Union[Node,None]:
        for node in self.openList:
            if node.point == point:
                return node
        return None
    def __endPointInCloseList(self) -> Union[Node,None]:
        for node in self.openList:
            if node.point == self.endPoint:
                return node
        return None
    def __searchNear(self, minF:Node, offSetX:int, offSetY:int) -> None:
        """
        搜索节点周围的点
        :param minF:F值最小的节点
        :param offSetX:坐标偏移量
        :param offSetY:
        :return:
        """
        # 越界检测
        mapRow,mapCol = self.map2d.shape
        if minF.point.x + offSetX < 0 or minF.point.x + offSetX > mapCol - 1 or minF.point.y + offSetY < 0 or minF.point.y + offSetY > mapRow - 1:
            return
        # 如果是障碍，就忽略
        if self.map2d[minF.point.x + offSetX][minF.point.y + offSetY] != self.passTag:
            return
        # 如果在关闭表中，就忽略
        currentPoint = Point(minF.point.x + offSetX, minF.point.y + offSetY)
        if self.__pointInCloseList(currentPoint):
            return
        # 设置单位花费
        if offSetX == 0 or offSetY == 0:
            step = 10
        else:
            step = 14
        # 如果不再openList中，就把它加入OpenList
        currentNode = self.__pointInOpenList(currentPoint)
        if not currentNode:
            currentNode = Node(currentPoint, self.endPoint, g=minF.g + step)
            currentNode.father = minF
            self.openList.append(currentNode)
            return None
        # 如果在openList中，判断minF到当前点的G是否更小
        if minF.g + step < currentNode.g:  # 如果更小，就重新计算g值，并且改变father
            currentNode.g = minF.g + step
            currentNode.father = minF
    def __startFindingPath(self) -> list:
        """
        开始寻路
        :return: None或Point列表（路径）
        """
        # 开启表
        self.openList = []
        # 关闭表
        self.closeList = []
        # 判断寻路终点是否是障碍
        mapRow,mapCol = self.map2d.shape
        if self.endPoint.y < 0 or self.endPoint.y >= mapRow or self.endPoint.x < 0 or self.endPoint.x >= mapCol or self.map2d[self.endPoint.x][self.endPoint.y] != self.passTag:
            return []
        # 1.将起点放入开启列表
        startNode = Node(self.startPoint, self.endPoint)
        self.openList.append(startNode)
        # 2.主循环逻辑
        while True:
            # 找到F值最小的点
            minF = self.__getMinNode()
            # 把这个点加入closeList中，并且在openList中删除它
            self.closeList.append(minF)
            self.openList.remove(minF)
            # 判断这个节点的上下左右节点
            self.__searchNear(minF, 0, -1)
            self.__searchNear(minF, 0, 1)
            self.__searchNear(minF, -1, 0)
            self.__searchNear(minF, 1, 0)
            # 判断是否终止
            point = self.__endPointInCloseList()
            if point:  # 如果终点在关闭表中，就返回结果
                cPoint = point
                pathList:list = []
                while True:
                    if cPoint.father:
                        pathList.append(cPoint.point)
                        cPoint = cPoint.father
                    else:
                        return list(reversed(pathList))
            if len(self.openList) == 0:
                return []
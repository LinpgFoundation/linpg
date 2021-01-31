# cython: language_level=3
from .mapModule import *
from ..scr_core.experimental import RenderedWindow

_MAP_ENV_IMAGE = None
#方块数据
cdef dict _BLOCKS_DATABASE = loadConfig("Data/blocks.yaml","blocks")

#地图模块
class MapObject:
    def  __init__(self,mapDataDic,int perBlockWidth,int perBlockHeight,darkMode=None):
        #加载地图设置
        self.__darkMode = mapDataDic["darkMode"] if darkMode == None else darkMode
        #初始化地图数据
        self.__MapData = mapDataDic["map"]
        self.backgroundImageName = mapDataDic["backgroundImage"]
        for y in range(len(self.__MapData)):
            for x in range(len(self.__MapData[y])):
                item = self.__MapData[y][x]
                self.__MapData[y][x] = BlockObject(item,_BLOCKS_DATABASE[item]["canPassThrough"])
        self.__MapData = numpy.asarray(self.__MapData)
        #使用numpy的shape决定self.row和self.column
        self.row,self.column = self.__MapData.shape
        self.load_decorations(mapDataDic["decoration"])
        self.load_env_img((perBlockWidth,perBlockHeight))
        self.__LightArea = []
        self.surface_width = int(perBlockWidth*0.9*((self.row+self.column+1)/2))
        self.surface_height = int(perBlockWidth*0.45*((self.row+self.column+1)/2)+perBlockWidth)
        self.__local_x = mapDataDic["local_x"]
        self.__local_y = mapDataDic["local_y"]
        self.__needUpdateMapSurface = True
        self.__block_on_surface = None
        self.__debug_win = None
    @property
    def block_width(self):
        return _MAP_ENV_IMAGE.get_block_width()
    @property
    def block_height(self):
        return _MAP_ENV_IMAGE.get_block_height()
    @property
    def decorations(self):
        return self.__decorations.copy().tolist()
    #加载环境图片，一般被视为初始化的一部分
    def load_env_img(self,block_size):
        global _MAP_ENV_IMAGE
        _MAP_ENV_IMAGE = EnvImagesManagement(self.__MapData,self.__decorations,self.backgroundImageName,block_size,self.__darkMode)
    #开发者模式
    def dev_mode(self):
        if self.__debug_win == None:
            unit = 10
            self.__debug_win = RenderedWindow("debug window",(self.row*unit+unit/4*(self.row+1),self.column*unit+unit/4*(self.row+1)),True)
            self.__debug_win.unit = unit
        else:
            self.__debug_win = None
    #显示开发面板
    def __display_dev_panel(self):
        self.__debug_win.clear()
        self.__debug_win.fill("black")
        cdef int x,y
        cpdef int start_x,start_y
        cpdef int unit = self.__debug_win.unit
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
    def load_decorations(self,decorationData):
        self.__decorations = []
        for decorationType,itemsThatType in decorationData.items():
            for itemKey,itemData in itemsThatType.items():
                if decorationType == "campfire":
                    self.__decorations.append(DecorationObject(itemData["x"],itemData["y"],decorationType,decorationType))
                    self.__decorations[-1].imgId = randomInt(0,9)
                    self.__decorations[-1].range = itemData["range"]
                    self.__decorations[-1].alpha = 255
                elif decorationType == "chest":
                    self.__decorations.append(DecorationObject(itemData["x"],itemData["y"],decorationType,decorationType))
                    self.__decorations[-1].items = itemData["items"]
                else:
                    self.__decorations.append(DecorationObject(itemData["x"],itemData["y"],decorationType,itemData["image"]))
        self.__decorations = numpy.sort(numpy.asarray(self.__decorations))
    #根据index寻找装饰物
    def find_decoration_with_id(self,int index):
        return self.__decorations[index]
    #根据坐标寻找装饰物
    def find_decoration_on(self,pos):
        for decoration in self.__decorations:
            if is_same_pos(decoration.get_pos(),pos):
                return decoration
        return None
    def interact_decoration_with_id(self,int index):
        self.__decorations[index].switch()
    #移除装饰物
    def remove_decoration(self,decoration):
        cdef (int,int) pos = decoration.get_pos()
        cdef int i
        for i in range(len(self.__decorations)):
            if self.__decorations[i].get_pos() == pos:
                self.__decorations = numpy.delete(self.__decorations,i)
                break
    #控制地图放大缩小
    def changePerBlockSize(self,newPerBlockWidth,newPerBlockHeight):
        self.addPos_x((self.block_width-newPerBlockWidth)*self.column/2)
        self.addPos_y((self.block_height-newPerBlockHeight)*self.row/2)
        self.surface_width = int(newPerBlockWidth*0.9*((self.row+self.column+1)/2))
        self.surface_height = int(newPerBlockWidth*0.45*((self.row+self.column+1)/2)+newPerBlockWidth)
        _MAP_ENV_IMAGE.resize(newPerBlockWidth,newPerBlockHeight)
        if self.surface_width < display.get_width():
            self.surface_width = display.get_width()
        if self.surface_height < display.get_height():
            self.surface_height = display.get_height()
        self.__needUpdateMapSurface = True
        self.__block_on_surface = None
    #获取local坐标
    def getPos(self):
        return self.__local_x,self.__local_y
    def getPos_x(self):
        return self.__local_x
    def getPos_y(self):
        return self.__local_y
    def isAtNight(self):
        return self.__darkMode
    #设置local坐标
    def setPos(self,int x, int y):
        self.setPos_x(x)
        self.setPos_y(y)
    def setPos_x(self,float value):
        if self.__local_x != value:
            self.__local_x = value
            self.__needUpdateMapSurface = True
    def setPos_y(self,float value):
        if self.__local_y != value:
            self.__local_y = value
            self.__needUpdateMapSurface = True
    #增加local坐标
    def addPos_x(self,float value):
        self.setPos_x(self.__local_x+value)
    def addPos_y(self,float value):
        self.setPos_y(self.__local_y+value)
    #把地图画到屏幕上
    def display_map(self,screen,screen_to_move_x=0,screen_to_move_y=0):
        #检测屏幕是不是移到了不移到的地方
        if self.__local_x < screen.get_width()-self.surface_width:
            self.__local_x = screen.get_width()-self.surface_width
            screen_to_move_x = 0
        elif self.__local_x > 0:
            self.__local_x = 0
            screen_to_move_x = 0
        if self.__local_y < screen.get_height()-self.surface_height:
            self.__local_y = screen.get_height()-self.surface_height
            screen_to_move_y = 0
        elif self.__local_y > 0:
            self.__local_y = 0
            screen_to_move_y = 0
        if self.__needUpdateMapSurface:
            self.__needUpdateMapSurface = False
            self.__update_map_surface(screen.get_size())
        #显示调试窗口
        if self.__debug_win != None and isinstance(self.__block_on_surface, numpy.ndarray):
            self.__display_dev_panel()
        _MAP_ENV_IMAGE.display_background_surface(screen,self.getPos())
        return (screen_to_move_x,screen_to_move_y)
    #重新绘制地图
    def __update_map_surface(self,window_size):
        cdef (int, int) posTupleTemp
        cdef int x,y
        cdef int yRange = self.row
        cdef int xRange = self.column
        cdef int screen_min = -self.block_width
        cdef (int,int) screen_size = window_size
        if not isinstance(self.__block_on_surface, numpy.ndarray):
            mapSurface = _MAP_ENV_IMAGE.new_surface(window_size,(self.surface_width,self.surface_height))
            self.__block_on_surface = numpy.zeros((self.row,self.column), dtype=numpy.int8)
        mapSurface = _MAP_ENV_IMAGE.get_surface()
        #画出地图
        for y in range(yRange):
            for x in range(xRange):
                posTupleTemp = self.calPosInMap(x,y)
                if screen_min<=posTupleTemp[0]<screen_size[0] and screen_min<=posTupleTemp[1]<screen_size[1]:
                    if self.__block_on_surface[y][x] == 0:
                        if not self.isPosInLightArea(x,y):
                            evn_img = _MAP_ENV_IMAGE.get_env_image(self.__MapData[y][x].name,True)
                        else:
                            evn_img = _MAP_ENV_IMAGE.get_env_image(self.__MapData[y][x].name,False)
                        evn_img.set_pos(posTupleTemp[0]-self.__local_x,posTupleTemp[1]-self.__local_y)
                        evn_img.draw(mapSurface)
                        self.__block_on_surface[y][x] = 1
                        if y < yRange-1:
                            self.__block_on_surface[y+1][x] = 0
                        if x < xRange-1:
                            self.__block_on_surface[y][x+1] = 0
                    else:
                        pass
                elif posTupleTemp[0] >= screen_size[0] or posTupleTemp[1] >= screen_size[1]:
                    break
            if self.calPosInMap(0,y+1)[1] >= screen_size[1]:
                break
    #把装饰物画到屏幕上
    def display_decoration(self,screen,alliances_data={},enemies_data={}):
        cdef (int,int) thePosInMap
        #检测角色所占据的装饰物（即需要透明化，方便玩家看到角色）
        cdef list charactersPos = []
        for name,dataDic in {**alliances_data, **enemies_data}.items():
            charactersPos.append((int(dataDic.x),int(dataDic.y)))
            charactersPos.append((int(dataDic.x)+1,int(dataDic.y)+1))
        #计算offSet
        cdef int offSetX = round(self.block_width/4)
        cdef int offSetY = round(self.block_width/8)
        cdef int offSetX_tree = round(self.block_width*0.125)
        cdef int offSetY_tree = round(self.block_width*0.25)
        #计算需要画出的范围
        cdef int screen_min = -self.block_width
        cdef (int,int) screen_size = screen.get_size()
        #历遍装饰物列表里的物品
        for item in self.__decorations:
            imgToBlit = None
            thePosInMap = self.calPosInMap(item.x,item.y)
            if screen_min<=thePosInMap[0]<screen_size[0] and screen_min<=thePosInMap[1]<screen_size[1]:
                if not self.inLightArea(item):
                    keyWordTemp = True
                else:
                    keyWordTemp = False
                #篝火
                if item.type == "campfire":
                    #查看篝火的状态是否正在变化，并调整对应的alpha值
                    if item.triggered == True and item.alpha < 255:
                        item.alpha += 15
                    elif item.triggered == False and item.alpha > 0:
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
                if imgToBlit != None:
                    imgToBlit.set_pos(thePosInMap[0]+offSetX,thePosInMap[1]-offSetY)
                    imgToBlit.draw(screen)
    #更新方块
    def update_block(self,pos,name):
        self.__MapData[pos["y"]][pos["x"]].update(name,_BLOCKS_DATABASE[name]["canPassThrough"])
        self.__needUpdateMapSurface = True
    #是否角色能通过该方块
    def ifBlockCanPassThrough(self,pos):
        return self.__MapData[pos["y"]][pos["x"]].canPassThrough
    #计算在地图中的方块
    def calBlockInMap(self,int mouse_x,int mouse_y):
        cdef int guess_x = int(((mouse_x-self.__local_x-self.row*self.block_width*0.43)/0.43+(mouse_y-self.__local_y-self.block_width*0.4)/0.22)/2/self.block_width)
        cdef int guess_y = int((mouse_y-self.__local_y-self.block_width*0.4)/self.block_width/0.22) - guess_x
        cdef int x,y
        cdef (int, int) posTupleTemp
        cdef float lenUnitW = self.block_width/5
        cdef float lenUnitH = self.block_width*0.8/393*214
        block_get_click = None
        for y in range(guess_y-1,guess_y+4):
            for x in range(guess_x-1,guess_x+4):
                posTupleTemp = self.calPosInMap(x,y)
                if lenUnitW<mouse_x-posTupleTemp[0]-self.block_width*0.05<lenUnitW*3 and 0<mouse_y-posTupleTemp[1]<lenUnitH:
                    block_get_click = {"x":x,"y":y}
                    break
        return block_get_click
    #计算方块被画出的位置
    def getBlockExactLocation(self,int x,int y):
        xStart,yStart = self.calPosInMap(x,y)
        return {
        "xStart": xStart,
        "xEnd": xStart + self.block_width,
        "yStart": yStart,
        "yEnd": yStart + self.block_width*0.5
        }
    #计算光亮区域
    def calculate_darkness(self,alliances_data):
        cpdef list lightArea = []
        cdef int x,y
        for each_chara in alliances_data:
            the_character_effective_range = 2
            if alliances_data[each_chara].current_hp > 0 :
                if alliances_data[each_chara].effective_range["far"] != None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["far"][1]+1
                elif alliances_data[each_chara].effective_range["middle"] != None:
                    the_character_effective_range = alliances_data[each_chara].effective_range["middle"][1]+1
                elif alliances_data[each_chara].effective_range["near"] != None:
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
            if item.type == "campfire" and item.triggered == True:
                for y in range(int(item.y-item.range),int(item.y+item.range)):
                    if y < item.y:
                        for x in range(int(item.x-item.range-(y-item.y)+1),int(item.x+item.range+(y-item.y))):
                            if [x,y] not in lightArea:
                                lightArea.append([x,y])
                    else:
                        for x in range(int(item.x-item.range+(y-item.y)+1),int(item.x+item.range-(y-item.y))):
                            if [x,y] not in lightArea:
                                lightArea.append([x,y])
        self.__LightArea = numpy.asarray(lightArea,dtype=numpy.int8)
        self.__needUpdateMapSurface = True
        self.__block_on_surface = None
    #计算在地图中的位置
    def calPosInMap(self,float x,float y):
        cdef float widthTmp = self.block_width*0.43
        return round((x-y)*widthTmp+self.__local_x+self.row*widthTmp),round((y+x)*self.block_width*0.22+self.__local_y+self.block_width*0.4)
    #查看角色是否在光亮范围内
    def inLightArea(self,doll):
        return self.isPosInLightArea(doll.x,doll.y)
    def isPosInLightArea(self,int x,int y):
        if not self.__darkMode:
            return True
        else:
            return numpy.any(numpy.equal(self.__LightArea,[x,y]).all(1))
    #以下是A星寻路功能
    def findPath(self,startPosition,endPosition,friend_data_dict,enemies_data_dict,routeLen=None,ignoreEnemyCharacters=[]):
        #检测起点
        cdef (int,int) start_pos = convert_pos(startPosition)
        #检测终点
        cdef (int,int) end_pos = convert_pos(endPosition)
        #建立寻路地图
        self.map2d = numpy.zeros((self.column,self.row), dtype=numpy.int8)
        # 可行走标记
        self.passTag = 0
        #历遍地图，设置障碍方块
        """
        for y in range(theMap.row):
            for x in range(theMap.column):
                if theMap.mapData[y][x].canPassThrough == False:
                    self.map2d[x][y]=1
        """
        #历遍设施，设置障碍方块
        for item in self.__decorations:
            if item.type == "obstacle" or item.type == "campfire":
                self.map2d[item.x][item.y] = 1
        #如果终点有我方角色，则不允许
        for key,value in friend_data_dict.items():
            if value.x == end_pos[0] and value.y == end_pos[1]:
                return []
        #历遍所有角色，将角色的坐标点设置为障碍方块
        for key,value in enemies_data_dict.items():
            if key != ignoreEnemyCharacters:
                self.map2d[value.x][value.y] = 1
        #如果终点是障碍物
        if self.map2d[end_pos[0]][end_pos[1]] != self.passTag:
            return []
        # 起点终点
        self.startPoint = Point(start_pos[0],start_pos[1])
        self.endPoint = Point(end_pos[0],end_pos[1])
        #开始寻路
        cdef list pathList = self.__startFindingPath()
        #遍历路径点,讲指定数量的点放到路径列表中
        if len(pathList) > 0:
            if routeLen != None and len(pathList) < routeLen or routeLen == None:
                routeLen = len(pathList)
            the_route = [pathList[i].get_pos() for i in range(routeLen)]
            return the_route
        else:
            return []
    def __getMinNode(self):
        """
        获得OpenList中F值最小的节点
        :return: Node
        """
        currentNode = self.openList[0]
        for node in self.openList:
            if node.g + node.h < currentNode.g + currentNode.h:
                currentNode = node
        return currentNode
    def __pointInCloseList(self, point):
        for node in self.closeList:
            if node.point == point:
                return True
        return False
    def __pointInOpenList(self, point):
        for node in self.openList:
            if node.point == point:
                return node
        return None
    def __endPointInCloseList(self):
        for node in self.openList:
            if node.point == self.endPoint:
                return node
        return None
    def __searchNear(self, minF, offSetX, offSetY):
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
            return
        # 如果在openList中，判断minF到当前点的G是否更小
        if minF.g + step < currentNode.g:  # 如果更小，就重新计算g值，并且改变father
            currentNode.g = minF.g + step
            currentNode.father = minF
    def __startFindingPath(self):
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
                # print("关闭表中")
                cPoint = point
                pathList = []
                while True:
                    if cPoint.father:
                        pathList.append(cPoint.point)
                        cPoint = cPoint.father
                    else:
                        return list(reversed(pathList))
            if len(self.openList) == 0:
                return []
# cython: language_level=3
from .surface import *

#用于储存游戏对象的容器，类似html的div
class GameObjectContainer(GameObject):
    def __init__(self, x:Union[int,float], y:Union[int,float]):
        super().__init__(x,y)
        self.hidden = False
        self.items = []
    #新增一个物品
    def append(self, new_item:GameObject) -> None: self.items.append(new_item)
    #移除一个物品
    def pop(self, index:int) -> None: self.items.pop(index)
    #清空物品栏
    def clear(self) -> None: self.items.clear()
    #把物品画到surface上
    def draw(self, surface:pygame.Surface) -> None:
        if not self.hidden:
            for item in self.items:
                item.display(surface,self.pos)

#带有滚动条的Surface容器
class SurfaceContainerWithScrollbar(AbstractImage):
    def __init__(self, img:Union[str,pygame.Surface,None], x:Union[int,float], y:Union[int,float], width:Union[int,float], height:Union[int,float],
    mode:str="horizontal"):
        if img is not None: img = loadImg(img,(width,height))
        super().__init__(img,x,y,width,height)
        self.__local_x:int = 0
        self.__local_y:int = 0
        self.panding:int = 0
        self.__items_dict:dict = {}
        self.hidden:bool = False
        self.distance_between_item:int = 20
        self.move_speed:int = 20
        self.button_tickness = 20
        self.__total_width:int = 0
        self.__total_height:int = 0
        self.__is_holding_scroll_button:bool = False
        self.__mouse_x_last = 0
        self.__mouse_y_last = 0
        self.__mode:bool = False
        self.set_mode(mode)
        self.__scroll_bar_pos:bool = True
        self.__current_hovered_item:any = None
        self.__item_per_line:int = 1
    #获取本地坐标
    def get_local_pos(self) -> tuple: return self.__local_x,self.__local_y
    #模式
    @property
    def mode(self) -> str: return self.get_mode()
    def get_mode(self) -> str: return "vertical" if not self.__mode else "horizontal"
    def set_mode(self, mode:str) -> None:
        if mode == "horizontal":
            self.__mode = True
        elif mode == "vertical":
            self.__mode = False
        else:
            throwException("error","Mode '{}' is not supported!".format(mode))
    def switch_mode(self) -> None:
        self.__mode = not self.__mode
        self.__local_x = 0
        self.__local_y = 0
        self.clear()
    #滚动条位置
    @property
    def scroll_bar_pos(self)  -> str: return self.get_scroll_bar_pos()
    def get_scroll_bar_pos(self) -> str:
        if not self.__mode:
            return "right" if not self.__scroll_bar_pos else "left"
        else:
            return "bottom" if not self.__scroll_bar_pos else "top"
    def set_scroll_bar_pos(self, pos:str) -> None:
        if pos == "left":
            if not self.__mode:
                self.__scroll_bar_pos = True
            else:
                throwException("error","You cannot put the scroll bar on the left during horizontal mode!")
        elif pos == "right":
            if not self.__mode:
                self.__scroll_bar_pos = False
            else:
                throwException("error","You cannot put the scroll bar on the right during horizontal mode!")
        elif pos == "top":
            if self.__mode is True:
                self.__scroll_bar_pos = True
            else:
                throwException("error","You cannot put the scroll bar on the top during vertical mode!")
        elif pos == "bottom":
            if self.__mode is True:
                self.__scroll_bar_pos = False
            else:
                throwException("error","You cannot put the scroll bar on the bottom during vertical mode!")
        else:
            throwException("error",'Scroll bar position "{}" is not supported! Try sth like "right" or "bottom" instead.'.format(pos))
    #添加一个物品
    def set(self, key:Union[str,int], value:Union[AbstractImage,pygame.Surface,None]) -> None: self.__items_dict[key] = value
    #获取一个物品
    def get(self, key:Union[str,int]) -> Union[AbstractImage,pygame.Surface,None]: return self.__items_dict[key]
    #移除一个物品
    def remove(self, key:Union[str,int]) -> None: del self.__items_dict[key]
    #交换2个key名下的图片
    def swap(self, key1:Union[str,int], key2:Union[str,int]) -> None:
        temp_reference = self.__items_dict[key1]
        self.__items_dict[key1] = self.__items_dict[key2]
        self.__items_dict[key2] = temp_reference
    #清除所有物品
    def clear(self) -> None:
        self.__items_dict.clear()
    #正在被触碰的物品
    @property
    def current_hovered_item(self) -> Union[str,int,None]: return self.__current_hovered_item
    #获取滚动条按钮的Rect
    def __get_scroll_button_rect(self, off_set_x:Union[int,float], off_set_y:Union[int,float]) -> Union[pygame.Rect,None]:
        if not self.__mode:
            if self.__total_height > self._height:
                return pygame.Rect(
                    int(self.x+self.__local_x+off_set_x),
                    int(self.y-self._height*self.__local_y/self.__total_height+off_set_y),
                    self.button_tickness,
                    int(self._height*self._height/self.__total_height)
                    ) if self.__scroll_bar_pos is True else pygame.Rect(
                        int(self.x+self.__local_x+self._width-self.button_tickness+off_set_x),
                        int(self.y-self._height*self.__local_y/self.__total_height+off_set_y),
                        self.button_tickness,
                        int(self._height*self._height/self.__total_height)
                        )
        else:
            if self.__total_width > self._width:
                return pygame.Rect(
                    int(self.x-self._width*self.__local_x/self.__total_width+off_set_x),
                    int(self.y+self.__local_y+off_set_y),
                    int(self._width*self._width/self.__total_width),
                    self.button_tickness
                    ) if self.__scroll_bar_pos is True else pygame.Rect(
                        int(self.x-self._width*self.__local_x/self.__total_width+off_set_x),
                        int(self.y+self.__local_y+self._height-self.button_tickness+off_set_y),
                        int(self._width*self._width/self.__total_width),
                        self.button_tickness
                        )
        return None
    #获取滚动条的Rect
    def __get_scroll_bar_rect(self, off_set_x:Union[int,float], off_set_y:Union[int,float]) -> Union[pygame.Rect,None]:
        if not self.__mode:
            if self.__total_height > self._height:
                return pygame.Rect(
                    int(self.x+self.__local_x+off_set_x), int(self.y+off_set_y), self.button_tickness, self._height
                    ) if self.__scroll_bar_pos is True else pygame.Rect(
                        int(self.x+self.__local_x+self._width-self.button_tickness+off_set_x), int(self.y+off_set_y),
                        self.button_tickness, self._height
                        )
        else:
            if self.__total_width > self._width:
                return pygame.Rect(
                    int(self.x+off_set_x), int(self.y+self.__local_y+off_set_y), self._width, self.button_tickness
                    ) if self.__scroll_bar_pos is True else pygame.Rect(
                        int(self.x+off_set_x), int(self.y+self.__local_y+self._height-self.button_tickness+off_set_y),
                        self._width, self.button_tickness
                        )
        return None
    #每一行放多少个物品
    @property
    def item_per_line(self) -> int: return self.__item_per_line
    def get_item_per_line(self) -> int: return self.__item_per_line
    def set_item_per_line(self, value:int) -> None: self.__item_per_line = int(value)
    #把素材画到屏幕上
    def display(self, surface:pygame.Surface, off_set:tuple=(0,0), pygame_events:any=None) -> None:
        self.__current_hovered_item = None
        if not self.hidden:
            """画出"""
            #如果有背景图片，则画出
            if self.img is not None: surface.blit(self.img,add_pos(self.pos,off_set))
            #计算出基础坐标
            current_x:int = int(self.x+self.__local_x+off_set[0])
            current_y:int = int(self.y+self.__local_y+off_set[1])
            if not self.__mode:
                current_x += self.panding
            else:
                current_y += self.panding
            #定义部分用到的变量
            abs_local_y:int; crop_height:int; new_height:int
            abs_local_x:int; crop_width:int; new_width:int
            subsurface_rect:pygame.Rect
            item_has_been_dawn_on_this_line:int = 0
            #画出物品栏里的图片
            for key,item in self.__items_dict.items():
                if item is not None:
                    if not self.__mode:
                        abs_local_y = int(current_y-self.y)
                        if 0 <= abs_local_y < self._height:
                            new_height = self._height-abs_local_y
                            if new_height > item.get_height():
                                new_height = item.get_height()
                            new_width = item.get_width()
                            if new_width > self._width:
                                new_width = self._width
                            subsurface_rect = pygame.Rect(0,0,new_width,new_height)
                            surface.blit(item.subsurface(subsurface_rect),(current_x,current_y))
                            if isHoverPygameObject(subsurface_rect,off_set_x=current_x,off_set_y=current_y):
                                self.__current_hovered_item = key
                        elif -(item.get_height()) <= abs_local_y < 0:
                            crop_height = -abs_local_y
                            new_height = item.get_height()-crop_height
                            if new_height > self._height:
                                new_height = self._height
                            new_width = item.get_width()
                            if new_width > self._width:
                                new_width = self._width
                            subsurface_rect = pygame.Rect(0,crop_height,new_width,new_height)
                            surface.blit(item.subsurface(subsurface_rect),(current_x,current_y+crop_height))
                            if isHoverPygameObject(subsurface_rect,off_set_x=current_x,off_set_y=current_y+crop_height):
                                self.__current_hovered_item = key
                        #换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line-1:
                            current_y += self.distance_between_item + item.get_height()
                            current_x = int(self.x+self.__local_x+off_set[0]+self.panding)
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_x += self.distance_between_item + item.get_width()
                            item_has_been_dawn_on_this_line += 1
                    else:
                        abs_local_x = int(current_x-self.x)
                        if 0 <= abs_local_x < self._width:
                            new_width = self._width-abs_local_x
                            if new_width > item.get_width():
                                new_width = item.get_width()
                            new_height = item.get_height()
                            if new_height > self._height:
                                new_height = self._height
                            subsurface_rect = pygame.Rect(0,0,new_width,new_height)
                            surface.blit(item.subsurface(subsurface_rect),(current_x,current_y))
                            if isHoverPygameObject(subsurface_rect,off_set_x=current_x,off_set_y=current_y):
                                self.__current_hovered_item = key
                        elif -(item.get_width()) <= abs_local_x < 0:
                            crop_width = -abs_local_x
                            new_width = item.get_width()-crop_width
                            if new_width > self._width:
                                new_width = self._width
                            new_height = item.get_height()
                            if new_height > self._height:
                                new_height = self._height
                            subsurface_rect = pygame.Rect(crop_width,0,new_width,new_height)
                            surface.blit(item.subsurface(subsurface_rect),(current_x+crop_width,current_y))
                            if isHoverPygameObject(subsurface_rect,off_set_x=current_x+crop_width,off_set_y=current_y):
                                self.__current_hovered_item = key
                        #换行
                        if item_has_been_dawn_on_this_line >= self.__item_per_line-1:
                            current_x += self.distance_between_item + item.get_width()
                            current_y = int(self.y+self.__local_y+off_set[1]+self.panding)
                            item_has_been_dawn_on_this_line = 0
                        else:
                            current_y += self.distance_between_item + item.get_height()
                            item_has_been_dawn_on_this_line += 1
            #处理总长宽
            if not self.__mode:
                self.__total_height = int(current_y-self.y-self.__local_y-off_set[1])
                if item_has_been_dawn_on_this_line > 0: self.__total_height += item.get_height()
                self.__total_width = self._width
            else:
                self.__total_width = int(current_x-self.x-self.__local_x-off_set[0])
                if item_has_been_dawn_on_this_line > 0: self.__total_width += item.get_width()
                self.__total_height = self._height
            """处理事件"""
            #获取鼠标坐标
            mouse_pos:tuple = pygame.mouse.get_pos()
            if self.is_hover(subtract_pos(mouse_pos,off_set)):
                if not self.__mode and self.__total_height > self._height or self.__mode is True and self.__total_width > self._width:
                    #获取pygame事件
                    if pygame_events is None: pygame_events = pygame.event.get()
                    #查看与鼠标有关的事件
                    for event in pygame_events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                scroll_bar_rect = self.__get_scroll_bar_rect(off_set[0],off_set[1])
                                if scroll_bar_rect is not None and isHoverPygameObject(scroll_bar_rect):
                                    scroll_button_rect = self.__get_scroll_button_rect(off_set[0],off_set[1])
                                    if isHoverPygameObject(scroll_button_rect):
                                        if not self.__is_holding_scroll_button:
                                            self.__is_holding_scroll_button = True
                                            self.__mouse_x_last,self.__mouse_y_last = pygame.mouse.get_pos()
                                    else:
                                        self.__is_holding_scroll_button = True
                                        self.__mouse_x_last,self.__mouse_y_last = pygame.mouse.get_pos()
                                        if not self.__mode:
                                            self.__local_y = int(
                                                (self.y-mouse_pos[1]+scroll_button_rect.height/2)/scroll_bar_rect.height*self.__total_height
                                            )
                                        else:
                                            self.__local_x = int(
                                                (self.x-mouse_pos[0]+scroll_button_rect.width/2)/scroll_bar_rect.width*self.__total_width
                                            )
                            elif event.button == 4:
                                if not self.__mode:
                                    self.__local_y += self.move_speed
                                else:
                                    self.__local_x -= self.move_speed
                            elif event.button == 5:
                                if not self.__mode:
                                    self.__local_y -= self.move_speed
                                else:
                                    self.__local_x += self.move_speed
                        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                            self.__is_holding_scroll_button = False
                else:
                    self.__is_holding_scroll_button = False
            else:
                self.__is_holding_scroll_button = False
            #调整本地坐标
            if self.__is_holding_scroll_button is True:
                mouse_x,mouse_y = pygame.mouse.get_pos()
                if not self.__mode:
                    self.__local_y += (self.__mouse_y_last-mouse_y)*(self.__total_height/self.height)
                    self.__mouse_y_last = mouse_y
                else:
                    self.__local_x += (self.__mouse_x_last-mouse_x)*(self.__total_width/self.width)
                    self.__mouse_x_last = mouse_x
            #防止local坐标越界
            if not self.__mode:
                if self.__local_y > 0:
                    self.__local_y = 0
                elif self.__total_height > self._height:
                    local_y_max = self._height-self.__total_height
                    if self.__local_y < local_y_max: self.__local_y = local_y_max
            else:
                if self.__local_x > 0:
                    self.__local_x = 0
                elif self.__total_width > self._width:
                    local_x_max = self._width-self.__total_width
                    if self.__local_x < local_x_max: self.__local_x = local_x_max
            
            #画出滚动条
            scroll_button_rect = self.__get_scroll_button_rect(off_set[0],off_set[1])
            if scroll_button_rect is not None: pygame.draw.rect(surface,findColorRGBA("white"),scroll_button_rect)
            scroll_bar_rect = self.__get_scroll_bar_rect(off_set[0],off_set[1])
            if scroll_bar_rect is not None: pygame.draw.rect(surface,findColorRGBA("white"),scroll_bar_rect,2)

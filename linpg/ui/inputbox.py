# cython: language_level=3
import time
from .menu import *

#输入框Abstract，请勿实体化
class AbstractInputBox(GameObject2d):
    def __init__(self, x:Union[int,float], y:Union[int,float], font_size:int, txt_color:Union[tuple,list,str], default_width:int):
        super().__init__(x,y)
        self.FONTSIZE:int = int(font_size)
        self.FONT = create_font(self.FONTSIZE)
        self.default_width = default_width
        self.deafult_height = int(self.FONTSIZE*1.5)
        self.input_box = Rect(x, y, default_width, self.deafult_height)
        self.color = get_color_rbga('lightskyblue3')
        self.txt_color = get_color_rbga(txt_color)
        self.active:bool = False
        self._text = None
        self._holder = self.FONT.render("|",get_antialias(),self.txt_color)
        self.holderIndex = 0
        self.needSave = False
    def get_width(self) -> int: return self.input_box.width
    def get_height(self) -> int: return self.input_box.height
    def get_fontsize(self) -> int: return self.FONTSIZE
    def set_fontsize(self, font_size:int) -> None:
        self.FONTSIZE = int(font_size)
        self.FONT = create_font(self.FONTSIZE)
    def set_pos(self, x:Union[int,float], y:Union[int,float]) -> None:
        super().set_pos(x,y)
        self.input_box = Rect(x, y, self.default_width, self.FONTSIZE*1.5)

#单行输入框
class SingleLineInputBox(AbstractInputBox):
    def __init__(self, x:Union[int,float], y:Union[int,float], font_size:int, txt_color:Union[tuple,list,str], default_width:int=150):
        super().__init__(x,y,font_size,txt_color,default_width)
        self._text:str = ""
        self._left_ctrl_pressing:bool = False
    def get_text(self) -> str:
        self.needSave = False
        if self._text == "":
            return None
        else:
            return self._text
    def set_text(self, new_txt:str=None) -> None:
        if new_txt is not None and len(new_txt)>0:
            self._text = new_txt
            self.holderIndex = len(new_txt)-1
        else:
            self._text = ""
            self.holderIndex = 0
        self._reset_inputbox_width()
    def _add_char(self, char:str) -> None:
        if len(char) > 0:
            self._text = self._text[:self.holderIndex]+char+self._text[self.holderIndex:]
            self.holderIndex += len(char)
            self._reset_inputbox_width()
        else:
            throw_exception("warning","The value of event.unicode is empty!")
    def _remove_char(self, action:str) -> None:
        if action == "ahead":
            if self.holderIndex > 0:
                self._text = self._text[:self.holderIndex-1]+self._text[self.holderIndex:]
                self.holderIndex -= 1
        elif action == "behind":
            if self.holderIndex < len(self._text):
                self._text = self._text[:self.holderIndex]+self._text[self.holderIndex+1:]
        else:
            throw_exception("error","Action has to be either 'ahead' or 'behind'!")
        self._reset_inputbox_width()
    def _reset_holderIndex(self, mouse_x:int) -> None:
        last_width = 0
        local_x = mouse_x-self.x
        new_width = 0
        i = 0
        for i in range(len(self._text)):
            new_width = self.FONT.size(self._text[:i])[0]+self.FONTSIZE*0.25
            if new_width>local_x:
                break
            else:
                last_width = new_width
        if (new_width-local_x) < (local_x-last_width):
            self.holderIndex = i
        else:
            self.holderIndex = i-1
    def _reset_inputbox_width(self)  -> None:
        if self._text is not None and len(self._text)>0:
            self.input_box.set_width(max(self.default_width, self.FONT.size(self._text)[0]+self.FONTSIZE*0.6))
        else:
            self.input_box.set_width(self.default_width)
    def _check_key_down(self, event:object) -> bool:
        if event.key == KEY.BACKSPACE:
            self._remove_char("ahead")
            return True
        elif event.key == KEY.DELETE:
            self._remove_char("behind")
            return True
        elif event.key == KEY.ARROW_LEFT and self.holderIndex > 0:
            self.holderIndex -= 1
            return True
        elif event.key == KEY.ARROW_RIGHT and self.holderIndex < len(self._text):
            self.holderIndex += 1
            return True
        elif event.unicode == "v" and KEY.get_pressed("v") and KEY.get_pressed(KEY.LEFT_CTRL) or \
            event.key == KEY.LEFT_CTRL and KEY.get_pressed("v") and KEY.get_pressed(KEY.LEFT_CTRL):
            self._add_char(KEY.get_clipboard())
            return True
        return False
    def draw(self, screen:ImageSurface) -> None:
        mouse_x,mouse_y = controller.get_mouse_pos()
        for event in controller.events:
            if event.type == KEY.DOWN and self.active is True:
                if self._check_key_down(event):
                    pass
                elif event.key == KEY.ESCAPE:
                    self.active = False
                    self.needSave = True
                else:
                    self._add_char(event.unicode)
            elif event.type == MOUSE_BUTTON_DOWN and event.button == 1 and self.active is True:
                if self.x<=mouse_x<=self.x+self.input_box.width and self.y<=mouse_y<=self.y+self.input_box.height:
                    self._reset_holderIndex(mouse_x)
                else:
                    self.active = False
                    self.needSave = True
            elif event.type == MOUSE_BUTTON_DOWN and event.button == 1 and 0<=mouse_x-self.x<=self.input_box.width and 0<=mouse_y-self.y<=self.input_box.height:
                self.active = True
                self._reset_holderIndex(mouse_x)
        # 画出文字
        if self._text is not None and len(self._text) > 0:
            screen.blit(self.FONT.render(self._text,get_antialias(),get_color_rbga(self.txt_color)), (self.x+self.FONTSIZE*0.25,self.y))
        #画出输入框
        if self.active:
            draw_rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(controller.events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.25+self.FONT.size(self._text[:self.holderIndex])[0], self.y))

#多行输入框
class MultipleLinesInputBox(AbstractInputBox):
    def __init__(self, x:Union[int,float], y:Union[int,float], font_size:int, txt_color:Union[tuple,list,str], default_width:int=150):
        super().__init__(x,y,font_size,txt_color,default_width)
        self._text = [""]
        self.lineId = 0
    def get_text(self) -> list:
        self.needSave = False
        if len(self._text) == 0 or self._text == [""]:
            return None
        else:
            return self._text
    def set_text(self, new_txt:Union[tuple,list]=None) -> None:
        if new_txt is None or len(self._text) == 0:
            self._text = [""]
        elif isinstance(new_txt,list):
            self._text = new_txt
            self._reset_inputbox_size()
        else:
            throw_exception("error","The new_txt for MultipleLinesInputBox.set_text() must be a list!")
    def set_fontsize(self, font_size:int) -> None:
        super().set_fontsize(font_size)
        self._reset_inputbox_size()
    def _reset_inputbox_width(self) -> None:
        if self._text is not None and len(self._text) > 0:
            width = self.default_width
            for txtTmp in self._text:
                new_width = self.FONT.size(txtTmp)[0]+self.FONTSIZE/2
                if new_width > width:
                    width = new_width
        else:
            width = self.default_width
        self.input_box.set_width(width)
    def _reset_inputbox_height(self) -> None: self.input_box.set_height(self.deafult_height*len(self._text))
    def _reset_inputbox_size(self) -> None:
        self._reset_inputbox_width()
        self._reset_inputbox_height()
    def _add_char(self, char:str) -> None:
        if len(char) > 0:
            if "\n" not in char:
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]+char+self._text[self.lineId][self.holderIndex:]
                self.holderIndex += len(char)
                self._reset_inputbox_width()
            else:
                theStringAfterHolderIndex = self._text[self.lineId][self.holderIndex:]
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]
                for i in range(len(char)-1):
                    if char[i] != '\n':
                        self._text[self.lineId] += char[i]
                        self.holderIndex += 1
                    else:
                        self.lineId += 1
                        self._text.insert(self.lineId,"")
                        self.holderIndex = 0
                self._text[self.lineId] += theStringAfterHolderIndex
                self._reset_inputbox_size()
        else:
            throw_exception("warning","The value of event.unicode is empty!")
    #删除对应字符
    def _remove_char(self, action:str) -> None:
        if action == "ahead":
            if self.holderIndex > 0:
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex-1]+self._text[self.lineId][self.holderIndex:]
                self.holderIndex -= 1
            elif self.lineId > 0:
                #如果当前行有内容
                if len(self._text[self.lineId]) > 0:
                    self.holderIndex = len(self._text[self.lineId-1])
                    self._text[self.lineId-1] += self._text[self.lineId]
                    self._text.pop(self.lineId)
                    self.lineId -= 1
                else:
                    self._text.pop(self.lineId)
                    self.lineId -= 1
                    self.holderIndex = len(self._text[self.lineId])
        elif action == "behind":
            if self.holderIndex < len(self._text[self.lineId]):
                self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]+self._text[self.lineId][self.holderIndex+1:]
            elif self.lineId < len(self._text)-1:
                #如果下一行有内容
                if len(self._text[self.lineId+1]) > 0:
                    self._text[self.lineId] += self._text[self.lineId+1]
                self._text.pop(self.lineId+1)
        else:
            throw_exception("error", "Action has to be either 'ahead' or 'behind'!")
        self._reset_inputbox_size()
    def _reset_holderIndex(self, mouse_x:int, mouse_y:int) -> None:
        self.lineId = round((mouse_y-self.y)/self.FONTSIZE)-1
        if self.lineId < 0:
            self.lineId = 0
        elif self.lineId >= len(self._text):
            self.lineId = len(self._text)-1
        last_width = 0
        local_x = mouse_x-self.x
        new_width = 0
        i = 0
        for i in range(len(self._text[self.lineId])):
            new_width = self.FONT.size(self._text[self.lineId][:i])[0]+self.FONTSIZE*0.25
            if new_width>local_x:
                break
            else:
                last_width = new_width
        if (new_width-local_x) < (local_x-last_width):
            self.holderIndex = i
        else:
            self.holderIndex = i-1
    def draw(self, screen:ImageSurface) -> bool:
        mouse_x,mouse_y = controller.get_mouse_pos()
        for event in controller.events:
            if self.active:
                if event.type == KEY.DOWN:
                    if event.key == KEY.BACKSPACE:
                        self._remove_char("ahead")
                    elif event.key == KEY.DELETE:
                        self._remove_char("behind")
                    elif event.key == KEY.ARROW_LEFT and self.holderIndex > 0:
                        self.holderIndex -= 1
                    elif event.key == KEY.ARROW_RIGHT and self.holderIndex < len(self._text[self.lineId]):
                        self.holderIndex += 1
                    elif event.key == KEY.ARROW_UP and self.lineId>0:
                        self.lineId -= 1
                        if self.holderIndex > len(self._text[self.lineId])-1:
                            self.holderIndex = len(self._text[self.lineId])-1
                    elif event.key == KEY.ARROW_DOWN and self.lineId<len(self._text)-1:
                        self.lineId += 1
                        if self.holderIndex > len(self._text[self.lineId])-1:
                            self.holderIndex = len(self._text[self.lineId])-1
                    elif event.unicode == "v" and KEY.get_pressed("v") and KEY.get_pressed(KEY.LEFT_CTRL) or \
                        event.key == KEY.LEFT_CTRL and KEY.get_pressed("v") and KEY.get_pressed(KEY.LEFT_CTRL):
                        self._add_char(KEY.get_clipboard())
                    #ESC，关闭
                    elif event.key == KEY.ESCAPE:
                        self.active = False
                        self.needSave = True
                    elif event.key == KEY.RETURN:
                        #如果“|”位于最后
                        if self.holderIndex == len(self._text[self.lineId]):
                            self._text.insert(self.lineId+1,"")
                        else:
                            self._text.insert(self.lineId+1,self._text[self.lineId][self.holderIndex:])
                            self._text[self.lineId] = self._text[self.lineId][:self.holderIndex]
                        self.lineId+=1
                        self.holderIndex=0
                        self._reset_inputbox_size()
                    else:
                        self._add_char(event.unicode)
                elif event.type == MOUSE_BUTTON_DOWN and event.button == 1:
                    if self.x<=mouse_x<=self.x+self.input_box.width and self.y<=mouse_y<=self.y+self.input_box.height:
                        self._reset_holderIndex(mouse_x,mouse_y)
                    else:
                        self.active = False
                        self.needSave = True
            elif event.type == MOUSE_BUTTON_DOWN and event.button == 1 and self.x<=mouse_x<=self.x+self.input_box.width and self.y<=mouse_y<=self.y+self.input_box.height:
                self.active = True
                self._reset_holderIndex(mouse_x,mouse_y)
        if self._text is not None:
            for i in range(len(self._text)): 
                # 画出文字
                screen.blit(self.FONT.render(self._text[i],get_antialias(),get_color_rbga(self.txt_color)),(self.x+self.FONTSIZE*0.25,self.y+i*self.deafult_height))
        if self.active:
            # 画出输入框
            draw_rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(controller.events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.1+self.FONT.size(self._text[self.lineId][:self.holderIndex])[0], self.y+self.lineId*self.deafult_height))

#控制台
class Console(SingleLineInputBox):
    def __init__(self, x:Union[int,float], y:Union[int,float], font_size:int=32, default_width:int=150):
        self.color_inactive = get_color_rbga('lightskyblue3')
        self.color_active = get_color_rbga('dodgerblue2')
        super().__init__(x,y,font_size,self.color_active,default_width)
        self.color = self.color_active
        self.active:bool = True
        self.hidden:bool = True
        self.textHistory:list = []
        self.__backward_id:int = 1
        self.__events:dict = {"cheat": False}
        self.txtOutput:list = []
    def get_events(self, key:Union[int,str]) -> any:
        try:
            return self.__events[key]
        except KeyError:
            throw_exception("error",'Console cannot find key "{}"!'.format(key))
    def _check_key_down(self, event:object) -> bool:
        if super()._check_key_down(event):
            return True
        #向上-过去历史
        elif event.key == KEY.ARROW_UP and self.__backward_id<len(self.textHistory):
            self.__backward_id += 1
            self.set_text(self.textHistory[len(self.textHistory)-self.__backward_id])
            return True
        #向下-过去历史，最近的一个
        elif event.key == KEY.ARROW_DOWN and self.__backward_id>1:
            self.__backward_id -= 1
            self.set_text(self.textHistory[len(self.textHistory)-self.__backward_id])
            return True
        #回车
        elif event.key == KEY.RETURN:
            if len(self._text)>0:
                if self._text.startswith('/'):
                    self._check_command(self._text[1:].split())
                else:
                    self.txtOutput.append(self._text)
                self.textHistory.append(self._text) 
                self.set_text()
                self.__backward_id = 1
            else:
                throw_exception("warning","The input box is empty!")
            return True
        #ESC，关闭
        elif event.key == KEY.ESCAPE:
            self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
            return True
        return False
    def _check_command(self, conditions:list) -> None:
        if conditions[0] == "cheat":
            if conditions[1] == "on":
                if "cheat" in self.__events and self.__events["cheat"] is True:
                    self.txtOutput.append("Cheat mode has already been activated!")
                else:
                    self.__events["cheat"] = True
                    self.txtOutput.append("Cheat mode is activated.")
            elif conditions[1] == "off":
                if "cheat" in self.__events and not self.__events["cheat"]:
                    self.txtOutput.append("Cheat mode has already been deactivated!")
                else:
                    self.__events["cheat"] = False
                    self.txtOutput.append("Cheat mode is deactivated.")
            else:
                self.txtOutput.append("Unknown status for cheat command.")
        elif conditions[0] == "say":
            self.txtOutput.append(self._text.replace("/say"))
        elif conditions[0] == "dev":
            if conditions[1] == "on":
                if get_setting("DeveloperMode") is True:
                    self.txtOutput.append("Developer mode has been activated!")
                else:
                    set_setting("DeveloperMode", value=True)
                    self.txtOutput.append("Developer mode is activated.")
            elif conditions[1] == "off":
                if not get_setting("DeveloperMode"):
                    self.txtOutput.append("Developer mode has been deactivated!")
                else:
                    set_setting("DeveloperMode", value=False)
                    self.txtOutput.append("Developer mode is deactivated.")
            else:
                self.txtOutput.append("Unknown status for dev command.")
        elif conditions[0] == "linpg" and conditions[1] == "info":
            self.txtOutput.append("Linpg Version: {}".format(get_current_version()))
        else:
            self.txtOutput.append("The command is unknown!")
    def draw(self, screen:ImageSurface) -> None:
        if self.hidden is True:
            for event in controller.events:
                if event.type == KEY.DOWN and event.key == KEY.BACKQUOTE:
                    self.hidden = False
                    break
        elif not self.hidden:
            for event in controller.events:
                if event.type == MOUSE_BUTTON_DOWN:
                    mouse_x,mouse_y = controller.get_mouse_pos()
                    if self.x <= mouse_x <= self.x+self.input_box.width and self.y <= mouse_y <= self.y+self.input_box.height:
                        self.active = not self.active
                        # Change the current color of the input box.
                        self.color = self.color_active if self.active else self.color_inactive
                    else:
                        self.active = False
                        self.color = self.color_inactive
                elif event.type == KEY.DOWN:
                    if self.active is True:
                        if self._check_key_down(event):
                            pass
                        else:
                            self._add_char(event.unicode)
                    else:
                        if event.key == KEY.BACKQUOTE or event.key == KEY.ESCAPE:
                            self.hidden = True
                            self.set_text()
            #画出输出信息
            for i in range(len(self.txtOutput)):
                screen.blit(self.FONT.render(self.txtOutput[i],get_antialias(),self.color),(self.x+self.FONTSIZE*0.25, self.y-(len(self.txtOutput)-i)*self.FONTSIZE*1.5))
            # 画出文字
            if self._text is not None and len(self._text) > 0:
                screen.blit(self.FONT.render(self._text,get_antialias(),self.color),(self.x+self.FONTSIZE*0.25, self.y))
            #画出输入框
            draw_rect(screen, self.color, self.input_box, 2)
            #画出 “|” 符号
            if int(time.time()%2)==0 or len(controller.events)>0:
                screen.blit(self._holder, (self.x+self.FONTSIZE*0.25+self.FONT.size(self._text[:self.holderIndex])[0], self.y))

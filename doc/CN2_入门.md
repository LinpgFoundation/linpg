# 图形

让我们从最简单的图形（Image）讲起。

对于大部分pygame开发者来讲，image（又或是Surface）是最常用的功能之一：

`pygame.image.load(filename) -> Surface`

而Linpg引擎也提供了非常类似的功能：

`linpg.quickly_load_img(path:Union[str,ImageSurface], ifConvertAlpha:bool=True) -> ImageSurface`

值得注意的是，使用`quickly_load_img()`将会自动转换路径，所以你不需要使用`os.path.join(path)`来提前转换路径，同时该指令会默认返回一个转换透明度的ImageSurface（pygame可通过ifConvertAlpha参数进行改动，使用pyglet时该参数无效）。

那么，什么是ImageSurface呢？

ImageSurface是一个用于同时兼容pygame.Surface和pyglet.image的typing。如果你使用pygame作为你的基础图形库，你可以将ImageSurface视为pygame.Surface，如果你是pyglet开发者，则可以将其视为pyglet.image。对于Linpg引擎，它被认为是raw image，即不建议直接进行操作。

Linpg引擎则提供了多个适用于不同场景的图形类，其中以下2个尤为重要：

`linpg.DynamicImage(img: Union[str,ImageSurface], x: Union[int, float], y: Union[int, float], width: int_f=-1, height: int_f=-1, tag: str="")`

和

`linpg.StaticImage(img:Union[str,ImageSurface], x:Union[int,float], y:Union[int,float], width:int_f=-1, height:int_f=-1, tag:str="default")`

> 注意：int_f类型表示该参数虽然推荐int数值，但也接受float（即浮点数），不过最终给与的数值最后还是会通常以向下取整的方式转为int，如果想要向上取整或四舍五入则请提前自行转换！

DynamicImage适用于尺寸需要经常改动的图片，相比StaticImage，它占用的内存更低。不建议用于尺寸比较恒一的图形上。

StaticImage适用于尺寸不需要经常改动的图片，相比DynamicImage，它的内存占用略大一些，但blit的速度会比raw image（即ImageSurface）还快很多。

最后，Linpg支持了gif图片：

`linpg.GifImage(imgList: numpy.ndarray, x: Union[int, float], y: Union[int, float], width: int_f, height: int_f, updateGap: int_f, tag: str = "default")`

`linpg.load.gif(gif_path_or_img_list: Union[str, tuple, list], position: tuple, size: tuple, updateGap: int = 1) -> linpg.GifImage`

> 注意：你应该永远避免直接调用linpg.GifImage而是使用linpg.load.gif来获取linpg.GifImage类



# 视频（实验性功能）

Linpg提供了2个视频类：VideoSurface和VideoPlayer。

`linpg.VideoSurface(path: str, width: int, height: int, loop: bool = True, with_music: bool = False, play_range: tuple = None, volume: float = 1.0, tag: str = "")`

类似Wallpaper Engine，将视频加载为动态背景，比VideoPlayer更灵活，但缺点是不能保证视频和音效同步。

`linpg.VideoPlayer(path:str, width:int, height:int, tag:str="")`

与VideoSurface相比，VideoPlayer少了很多功能。但VideoPlayer可以确保视频和音效同步，建议用于播放过场动画。
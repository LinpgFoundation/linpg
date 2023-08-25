# :speech_balloon: Preamble / 前言

###### *"Just because c++ is the greatest language ever invented doesn't mean that writing games in c++ is easy and fun, and the same goes for pygame."*

###### *"c++是有史以来最伟大的语言，但这并不代表用c++写游戏是一件轻松而又有趣的事情，pygame也是如此。"*



# :sparkles: About Linpg Engine / 关于Linpg引擎

Linpg (Lin's python game) Engine is a game engine developed by Linpg Foundation, which aims to standardize the development of Pygame games and make the codes easier to read, expand and maintain.

Linpg Engine is developed with a modular concept. It implements many features which are commonly used in game development. Simultaneously, the Linpg Engine also maintains a high level of compatibility with Pygame, making it easy for developers to migrate existing Pygame projects to Linpg Engine or use the features which Linpg Engine provides on their own Pygame projects.

We always need your help to make Linpg the best it can be! No matter who you are, any contributors are welcome!

Linpg引擎是Linpg基金会基于pygame库自主研发的游戏引擎，目的是为了规范化pygame游戏的开发，使得游戏代码更加整洁，易读，易扩展，易维护。

Linpg引擎的开发使用了模块化的理念，并在底层实现了很多游戏开发过程中常用到的功能。Linpg引擎一直保持着与pygame高度的兼容性，使得开发者可以很容易将现有的pygame项目迁移到Linpg引擎上，或者在自己的pygame项目中使用Linpg引擎提供的功能或者工具。

世上无完人，我们需要你的帮助让Linpg引擎变得更好。欢迎任何能帮助我们改进Linpg引擎的开发者！



# :crystal_ball:Some awesome games developed using Linpg

![](https://github.com/LinpgFoundation/A-story-of-us/raw/master/Assets/image/screenshot/dialog.png)

#### [A-story-of-us](https://github.com/LinpgFoundation/A-story-of-us), a visual novel game only contains around 100 lines of code. A great starting point for anyone who is interested in Linpg.

![](https://github.com/TigeiaWorkshop/GFL-LastWish/raw/master/Assets/image/screenshot/battle.png)

#### [GFL-Last](https://github.com/TigeiaWorkshop/GFL-LastWish ), a turn-based strategy game that demonstrates some advanced features and the unlimited potential of the Linpg engine.



# :hammer_and_wrench: Dependencies / 运行库 

| Required / 必需安装 |
| :---------- |
| pygame-ce   |
| pyvns       |
| numpy       |
| PySimpleGUI |

| Recommended* / 建议安装* |
| ------------------------ |
| pyyaml                   |
| opencv                   |

\* All these libraries will be installed by default as some common features cannot be enabled without these libraries.

##### Special shout out to the developers of these libraries. They make game development using python no longer unthinkable.

##### 感谢这些第三方库的开发者，他（她）们让使用python开发游戏不再遥远。



# :computer:Installation / 安装

### Recommend:

```
pip install linpg
```

We also highly suggest you download and use [A-story-of-us](https://github.com/LinpgFoundation/A-story-of-us) as your starting point.

### Building From Source:

First, clone this repo:

```
git clone https://github.com/LinpgFoundation/linpg
```

(Optional) If you are interested in trying out the latest build, then you should switch to `dev` branch:

```
git checkout dev
```

If you have not install linpg-toolbox yet, please do so by using command:

```
pip install --upgrade linpgtoolbox
```

Run `builder.py`:

```
python builder.py
```

That's it, enjoy!


# :world_map: Branches / 分支​

### master:

The current stable version. 

该分支提供了当前的稳定版本

### dev:

The latest version that is available to the public. While this version may contain patches that fix identified problems, it may also have unknown or known new bugs that can cause harm to your system or projects. This version is typically recommended for experienced developers.

目前可以运行的最新版本，相对稳定，但可能包含未被发现的问题或未完善的功能。 推荐有经验的开发人员使用。



# :books: How to contribute / 如何贡献代码

- It would be best if you can fork the "dev" branch as your starting point. If the "dev" branch does not exist, then fork the "master" branch.

  你应该fork "dev"分支作为作为你的起始点。如果"dev"分支不存在，则fork "master"分支。

- After you have finished your work, you should request to merge to the "dev" branch instead of the "master" branch.

  所有PR应该请求merge到"dev"分支中。如果"dev"不存在，则请求merge到"master"分支。

- We are looking forward to seeing a pull request that contains a detailed explanation about any changes that were made.

  所有PR应该详细地阐明其做出的改动。



# :video_game: ​Discord

https://discord.gg/3wz6bs5jvu



# :open_book: ​Wiki / 维基百科

https://github.com/LinpgFoundation/linpg/wiki



# :construction: Changes in Linpg Engine through the generations            Linpg引擎历代的变化

| Linpg 1                                                      | ( Obsolete / 过时，不再维护 ) |                    |
| :----------------------------------------------------------- | ----------------------------- | ------------------ |
| (Hard coded) Basic implementation of the visual novel system | 视觉小说系统的基本实现        | :white_check_mark: |
| A extremely simple main menu                                 | 简易的主菜单页面              | :white_check_mark: |

------

| Linpg 2|( Obsolete / 过时，不再维护 )||
| ------------------------------------------------------------ | -------------------------------------- | ------------------ |
| Non-hard coded and easy-to-edit visual novel system          | 非hard coded，容易编辑的视觉小说系统   | :white_check_mark: |
| A more dynamic main menu                                     | 更加动态化的主菜单页面                 | :white_check_mark: |
| Basic implementation of the combat system                    | 战斗系统的基本实现                     | :white_check_mark: |
| Basic Support for video files                                | 对视频文件的支持                       | :white_check_mark: |
| The visual novel system maintains 55 fps and the combat system reaches 45 fps | 视觉小说系统保持55帧，战斗系统达到45帧 | :white_check_mark: |

------

| Linpg 3|( Current Version / 当前版本 )||
| ----------------------------------------------------------- | ------------------------------------ | ------------------ |
| A more modular and aesthetically modern visual novel system | 更加模块化和美观现代化的视觉小说系统 | :white_check_mark: |
| Options menu                                                | 选项菜单模块                         | :white_check_mark: |
| Better and more complex combat system                       | 更加完善复杂的战斗系统               | :white_check_mark: |
| Map Editor                                                  | 可用的地图编辑器                     | :white_check_mark: |
| Dialogue Editor                                             | 可用的对话编辑器                     | :white_check_mark: |
| Most functions work when correct input is accepted          | 大部分功能能在接受正确的输入后工作   | :hammer:         |
| Visual novel system and combat system can maintain 60 fps   | 视觉小说系统和战斗系统达到144帧       | :white_check_mark: |
| Video can be played at a stable 60 fps                      | 视频能稳定地以60帧播放               | :white_check_mark: |
| Pygame native input box (English only)                      | 可用的pygame原生输入框（仅支持英文） | :white_check_mark: |

------

| Linpg 4 |( On Schedule / 未来-计划中 )||
| ------------------------------------------------------------ | -------------------------------------------------------- | ---- |
| support pyglet (two libraries, one standard)                | pyglet支持（两个库，一个标准）                           |      |
| Rewrite using a combination of c++ and cython for better performance | 底层采用c++和cython结合的方式重写以获取更高效的性能      |      |
| Better options menu                                          | 更好的选项菜单模块                                       |      |
| Enemy AI systems will be partially affected by machine learning. | 敌方AI系统将部分采用machine learning的意见               |      |
| More convenient and beautiful map editor and dialogue editor | 更加便捷美观的地图编辑器和对话编辑器                     |      |
| More readable and standardized code                          | 更加易读规范化的代码                                     |      |
| Most functions are able to report errors and take the most appropriate approach after accepting incorrect input | 大部分功能能在接受错误的输入后报错并采取最合适的方案运行 |      |
| The combat system can have more varieties.                   | 战斗系统能有更多的玩法                                   |      |
| The input box will support Chinese, Japanese, and more       | 输入框支持中文，日文，以及更多                           |      |




# :memo: License / 版权说明

Please check **LICENSE**.

版权信息请查看**LICENSE**文件。
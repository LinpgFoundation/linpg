#### English | [简体中文](https://github.com/LinpgFoundation/linpg/blob/master/README_SimplifiedChinese.md) | [繁體中文](https://github.com/LinpgFoundation/linpg/blob/master/README_TraditionalChinese.md)

# :speech_balloon: Preamble

###### *"Just because c++ is the greatest language ever invented doesn't mean that writing games in c++ is easy and fun, and the same goes for pygame."*



# :sparkles: About Linpg Engine

![PyPI](https://img.shields.io/pypi/pyversions/linpg?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/v/linpg?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/dm/linpg?style=for-the-badge&logo=pypi)

Linpg (Lin's python game) Engine is a game engine developed by Linpg Foundation, which aims to standardize the development of Pygame games and make the codes easier to read, expand and maintain.

Linpg Engine is developed with a modular concept. It implements many features which are commonly used in game development. Simultaneously, the Linpg Engine also maintains a high level of compatibility with Pygame, making it easy for developers to migrate existing Pygame projects to Linpg Engine or use the features which Linpg Engine provides on their own Pygame projects.

We always need your help to make Linpg the best it can be! No matter who you are, any contributors are welcome!

##### Join our Discord: https://discord.gg/3wz6bs5jvu



# :crystal_ball:Some awesome games developed using Linpg

![](https://github.com/LinpgFoundation/A-story-of-us/raw/master/Assets/image/screenshot/dialog.png)

#### [A-story-of-us](https://github.com/LinpgFoundation/A-story-of-us), a visual novel game only contains around 100 lines of code. A great starting point for anyone who is interested in Linpg.

![](https://github.com/TigeiaWorkshop/GFL-LastWish/raw/master/Assets/image/screenshot/battle.png)

#### [GFL-Last Wish](https://github.com/TigeiaWorkshop/GFL-LastWish ), a turn-based strategy game that demonstrates some advanced features and the unlimited potential of the Linpg engine.



# :hammer_and_wrench: Dependencies

| Required |
| :---------- |
| pygame-ce   |
| pyvns       |
| numpy       |

| Recommended*       |
| ------------------ |
| pyyaml             |
| opencv             |
| speech_recognition |

\* All these libraries will be installed by default as some common features cannot be enabled without these libraries.

##### Special shout out to the developers of these libraries. They make game development using python no longer unthinkable.



# :computer:Installation

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


# :world_map: Branches

### master:

The current stable version. 

### dev:

The latest version that is available to the public. While this version may contain patches that fix identified problems, it may also have unknown or known new bugs that can cause harm to your system or projects. This version is typically recommended for experienced developers.



# :books: How to contribute

- It would be best if you can fork the "dev" branch as your starting point. If the "dev" branch does not exist, then fork the "master" branch.

- After you have finished your work, you should request to merge to the "dev" branch instead of the "master" branch.

- We are looking forward to seeing a pull request that contains a detailed explanation about any changes that were made.




# :construction: Changes in Linpg Engine through the generations

| Linpg 1 (Obsolete)                                           | Status             |
| :----------------------------------------------------------- | ------------------ |
| (Hard coded) Basic implementation of the visual novel system | :white_check_mark: |
| A extremely simple main menu                                 | :white_check_mark: |

------

| Linpg 2 (Obsolete) |Status|
| ------------------------------------------------------------ | ------------------ |
| Non-hard coded and easy-to-edit visual novel system          | :white_check_mark: |
| A more dynamic main menu                                     | :white_check_mark: |
| Basic implementation of the combat system                    | :white_check_mark: |
| Basic Support for video files                                | :white_check_mark: |
| The visual novel system maintains 55 fps and the combat system reaches 45 fps | :white_check_mark: |

------

| Linpg 3 (Current Version) |Status|
| ----------------------------------------------------------- | ------------------ |
| A more modular and aesthetically modern visual novel system | :white_check_mark: |
| Options menu                                                | :white_check_mark: |
| Better and more complex combat system                       | :white_check_mark: |
| Map Editor                                                  | :white_check_mark: |
| Dialogue Editor                                             | :white_check_mark: |
| Most functions work when correct input is accepted          | :hammer:         |
| Visual novel system and combat system can maintain 60 fps   | :white_check_mark: |
| Video can be played at a stable 60 fps                      | :white_check_mark: |
| Pygame native input box (English only)                      | :white_check_mark: |

------

| Linpg 4 (On Schedule) |
| ------------------------------------------------------------ |
| support pyglet (two libraries, one standard)                |
| Rewrite using a combination of c++ and cython for better performance |
| Better options menu                                          |
| Enemy AI systems will be partially affected by machine learning. |
| More convenient and beautiful map editor and dialogue editor |
| More readable and standardized code                          |
| Most functions are able to report errors and take the most appropriate approach after accepting incorrect input |
| The combat system can have more varieties.                   |
| The input box will support Chinese, Japanese, and more       |




# :memo: License

Linpg is licensed under **LGPL(GNU Lesser General Public License)-2.1-or-later**.

See **[LICENSE](https://github.com/LinpgFoundation/linpg/blob/master/LICENSE)**.

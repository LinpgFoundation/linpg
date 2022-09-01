import zipfile

from .organizer import *


# 压缩包处理模块
class Zipper:
    # 根据脚本打包所有文件
    @classmethod
    def excute(cls) -> None:
        for _path in glob("*.linpg.zipscript"):
            # 获取路径pattern
            with open(_path, "r", encoding="utf-8") as f:
                filesAndFoldersToZip: list[str] = f.readlines()
            # 获取文件名称
            fileName: str = os.path.basename(_path)
            # 获取zip文件的名称
            zipName: str = fileName[: fileName.index(".") + 1] + "zip"
            # 如果同名zip文件已经存在，则删除
            if os.path.exists(zipName):
                os.remove(zipName)
            # 开始打包文件
            theZipFile: zipfile.ZipFile = zipfile.ZipFile(zipName, "w")
            for i in range(len(filesAndFoldersToZip) - 1, -1, -1):
                if len(_pathTmp := filesAndFoldersToZip[i].removesuffix("\n")) > 0:
                    cls.__zip(theZipFile, _pathTmp)
                else:
                    filesAndFoldersToZip.pop(i)
            # 关闭压缩包访问
            theZipFile.close()
            # 将排序好的列表写回到脚本文件中
            with open(_path, "w+", encoding="utf-8") as f:
                f.writelines(Organizer.natural_sort(filesAndFoldersToZip))

    # 将对应路径的文件添加到压缩包中
    @classmethod
    def __zip(cls, theZipFile: zipfile.ZipFile, _path: str) -> None:
        # 如果路径中不带星号，则不是路径pattern，可以开始处理
        if "*" not in _path:
            # 如果是文件夹，则需要依次添加文件
            if os.path.isdir(_path):
                for dirname, subdirs, files in os.walk(_path):
                    theZipFile.write(dirname)
                    for filename in files:
                        theZipFile.write(os.path.join(dirname, filename))
            # 如果是文件，则可以之间写入
            else:
                theZipFile.write(_path)
        # 处理带星号的路径pattern
        else:
            for _match_path in glob(_path):
                cls.__zip(theZipFile, _match_path)

    # 打开一个压缩包
    @classmethod
    def open(cls, _path: str) -> zipfile.ZipFile:
        return zipfile.ZipFile(_path, "r")

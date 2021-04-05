import os
import linpg

LINPG_PATH = linpg.__path__[0]

datas = [
    (os.path.join(LINPG_PATH,'api/*'),"linpg/api"),
    (os.path.join(LINPG_PATH,'battle/*'),"linpg/battle"),
    (os.path.join(LINPG_PATH,'core/*'),"linpg/core"),
    (os.path.join(LINPG_PATH,'dialog/*'),"linpg/dialog"),
    (os.path.join(LINPG_PATH,'lang/*'),"linpg/lang"),
    (os.path.join(LINPG_PATH,'info.json'),'linpg'),
    (os.path.join(LINPG_PATH,'__init__.py'),'linpg'),
    ]
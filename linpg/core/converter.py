from .function import *

data_in = {
    "x" : 0,
    "y" : 0,

    "width" : 0,
    "height" : 0,
    "img_src": "Assest/?",
    "items" : [
        {
            "type": "text",
            "src": "bbb",
            "pos": (0,0)
        },
        {
            "type": "image",
            "src": "Assest/?",
            "pos": (0,0)
        },
    ]


}

def generate_container_from(data:dict) -> GameObjectContainer:
    container = GameObjectContainer(data["img_src"],data["x"],data["y"],data["width"],data["height"])
    for item in data["items"]:
        if "pos" not in item:
            item["pos"] = (0,0)
        
        container.append()
    return container
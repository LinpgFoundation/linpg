from .sprite import *


# managing all the in-game assets
class AssetsManager:
    __SHEETS: dict[str, SpriteImage] = {}

    @classmethod
    def get_sprite(cls, p: str) -> SpriteImage:
        sheet: SpriteImage | None = cls.__SHEETS.get(p)
        # load the sheet if it is not already load
        if sheet is None:
            sheet = SpriteImage(p)
            cls.__SHEETS[p] = sheet
        return sheet

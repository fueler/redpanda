
class EntityTemplate():
    def __init__(self) -> None:
        self._name: str = ''
        self._spritesheet: str = ''
        self._width: int = 0
        self._height: int = 0

    def __repr__(self) -> str:
        return f'{self._name}: sprite:{self._spritesheet}'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def spritesheet(self) -> str:
        return self._spritesheet

    @spritesheet.setter
    def spritesheet(self, new_spritesheet: str) -> None:
        self._spritesheet = new_spritesheet

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_width: int) -> None:
        self._width = new_width

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_height: int) -> None:
        self._height = new_height

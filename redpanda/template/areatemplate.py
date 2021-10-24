class AreaTemplate:
    def __init__(self) -> None:
        self._name: str = ''
        self._filename: str = ''

    def __repr__(self) -> str:
        return f'{self._name}: {self._filename}'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, new_filename: str) -> None:
        self._filename = new_filename

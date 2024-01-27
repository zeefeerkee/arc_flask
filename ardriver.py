import json
import re


class ArduinoDriver:
    def __init__(self, filename: str = "commands.json") -> None:
        """
        Инициализатор, принимает расположение файла с командами относительно
        родительской директории в формате JSON.
        """
        if re.match(r".*\.json$", filename):
            self._commands = self._set_commands(filename)
            return None
        raise TypeError("Файл должен быть в формате JSON")

    @property
    def commands(self) -> dict:
        """
        Свойство доступных команд. Только чтение.
        """

        return self._commands

    def _set_commands(self, filename: str) -> dict:
        """
        Приватный метод извлечения команд из заданных.
        """
        with open(filename, encoding="utf-8") as file:
            return {key: value for key, value in json.load(file).items()}

    def push(self, direction: str, velocity: int) -> str:
        """
        Метод, позволяющий представить текущую команду в двочином коде.
        """
        # Проверка входных данных на валидность
        if direction not in self.commands:
            raise KeyError("Incrorrect command.")
        if velocity not in range(0, 110):
            raise ValueError("Incrorrect velocity.")

        # Представляем значения направления и скорости в битах
        direction = format(self.commands[direction], '04b')
        velocity = format(velocity // 10, '04b')
        return direction + velocity

    def pull(self):
        """
        Метод, позволяющий вытянуть информацию из ардуино.
        В разработке...
        """
        pass

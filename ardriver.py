import json
import re
import serial


class ArduinoDriver:
    def __init__(self, filename: str = "commands.json") -> None:
        """
        Инициализатор, принимает расположение файла с командами относительно
        родительской директории в формате JSON.
        """

        self._commands = self._set_commands(filename)

        try:
            self.serial_port = serial.Serial(
                "/dev/ttyAMA0", baudrate=4800, timeout=1
                )
        except serial.serialutil.SerialException:
            self.serial_port = None
            print(
                """Открыть последовательный порт не удалось.\nПопробуйте установить последовательный порт вручную"""  # noqa: E501
                )

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

        if re.match(r".*\.json$", filename):
            with open(filename, encoding="utf-8") as file:
                return {key: value for key, value in json.load(file).items()}
        raise TypeError("Файл должен быть в формате JSON")

    @property
    def serial_port(self):
        return self._serial_port

    @serial_port.setter
    def serial_port(self, serial_port: serial.Serial):
        self._serial_port = serial_port

    def push(self, direction: str, velocity: int) -> None:
        """
        Метод, отправляющий на последовательный порт команду в виде байта.
        """

        # Проверка входных данных на валидность
        if direction not in self.commands:
            raise KeyError("Incrorrect command.")
        if velocity not in range(0, 110):
            raise ValueError("Incrorrect velocity.")

        # Представляем значения направления и скорости в битах
        direction = format(self.commands[direction], '04b')
        velocity = format(velocity // 10, '04b')
        bin_command = int(direction + velocity, 2)

        # Отправляем на последовательный порт
        self._serial_port.write(
            bin_command.to_bytes(1, byteorder='big')
            )

    def pull(self):
        """
        Метод, позволяющий вытянуть информацию из ардуино.
        В разработке...
        """
        pass

from typing import Self
import serial
import struct


class Driver:
    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600) -> None:  # noqa: E501
        if "/dev/tty" not in port:
            raise TypeError("Неверное имя последовательного порта")

        self.serial_port = serial.Serial(port=port, baudrate=baudrate, timeout=1)  # noqa: E501
        self.read  # Просёр
        self.read  # Просёр

    def __del__(self):
        if not self.serial_port.closed:
            self.serial_port.close()

    def __repr_(self):
        return f"Driver(port={self.serial_port}, baudrate={self.serial_port.baudrate})"  # noqa: E501

    def write(self, message: bytes) -> None:
        self.serial_port.write(message)

    @property
    def read(self) -> bytes:
        return self.serial_port.readline()


def combine_bytes(*args: int) -> bytes:
    return struct.pack(f">{len(args)}B", *args)

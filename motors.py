class Motor:
    def __init__(self, address, direction=0, velocity=0):
        self.address = int(address)
        self.direction = int(bool(direction))
        self.velocity = int(velocity)

    def __repr__(self):
        return ("Motor(address={0}, direction={1}, velocity={2})".format(*self.__fields))  # noqa: E501

    def __hash__(self) -> int:
        return self.address << 6 | self.direction << 5 | self.velocity

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity: int):
        self._velocity = velocity

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction):
        self._direction = int(bool(direction))

    @property
    def __fields(self):
        return self.address, self.direction, self.velocity

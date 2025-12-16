from dataclasses import dataclass
from collections import UserList

from .material import Material


@dataclass(slots=True)
class Section:
    pass


@dataclass(slots=True)
class Medium(Section):
    material: Material


class Substrate(Medium):
    pass


@dataclass(slots=True)
class Layer(Medium):
    thickness: float  # in nm


@dataclass(slots=True)
class MultiLayer(UserList[Section]):
    def items(self) -> list[Section]:
        return self.data

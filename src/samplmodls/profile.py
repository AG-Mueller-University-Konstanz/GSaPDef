from dataclasses import dataclass
from collections import UserList

from material import Section


@dataclass(slots=True)
class Profile(UserList[Section]):
    def items(self) -> list[Section]:
        return self.data

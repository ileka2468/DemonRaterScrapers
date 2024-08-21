from enum import Enum


class MemberLevel(Enum):
    ALL_MEMBERS = "ALL"
    FOREIGN_MEMBERS = "FOREIGN"
    MEMBERS = "MEMBERS"

    def __eq__(self, other):
        return self.name == other.name

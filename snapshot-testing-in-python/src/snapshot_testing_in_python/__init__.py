from dataclasses import dataclass
from typing import Any


def hello() -> str:
    return "Hello from snapshot-testing-in-python!"


@dataclass
class User:
    name: str
    timestamp: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__

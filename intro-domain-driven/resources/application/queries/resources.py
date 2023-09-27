import abc
from dataclasses import dataclass


@dataclass
class ResourceDto:
    id: str
    name: str
    type: str


class ListResources(abc.ABC):
    @abc.abstractmethod
    def query(self) -> list[ResourceDto]:
        ...

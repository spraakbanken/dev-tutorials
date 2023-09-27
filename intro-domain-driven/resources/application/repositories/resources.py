import abc
from uuid import UUID

from resources.domain.entites.resource import Resource


class ResourceRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id: UUID) -> Resource:
        ...

    @abc.abstractmethod
    def save(self, resource: Resource) -> None:
        ...

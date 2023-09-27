import copy
from uuid import UUID

from resources.application.repositories.resources import ResourceRepository
from resources.domain.entites.resource import Resource


class InMemoryResourceRepository(ResourceRepository):
    def __init__(self) -> None:
        self._resources = {}

    def save(self, resource: Resource) -> None:
        self._resources[resource.id] = copy.deepcopy(resource)

    def get(self, id: UUID) -> Resource:
        return copy.deepcopy(self._resources[id])

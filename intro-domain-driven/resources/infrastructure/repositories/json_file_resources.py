import copy
from pathlib import Path
import json
from typing import Optional
from uuid import UUID

from resources.application.repositories.resources import ResourceRepository
from resources.domain.entites.resource import Resource, ResourceType


class JsonFileResourceRepository(ResourceRepository):
    def __init__(self, path: Path) -> None:
        self._path = path
        self._resources: dict[UUID, Resource] = {}
        self.load_from_path(self._path)

    def load_from_path(self, path: Path) -> None:
        for id, data in json.loads(self._path.read_text()).items():
            uuid = UUID(id)
            resource = Resource(
                id=uuid, name=data["name"], type=ResourceType(data["type"])
            )
            self._resources[uuid] = resource

    def get(self, id: UUID) -> Resource:
        return copy.deepcopy(self._resources[id])

    def save(self, resource: Resource) -> None:
        self._resources[resource.id] = copy.deepcopy(resource)

    def write_to_path(self, path: Optional[Path] = None):
        to_disk = {
            str(res.id): {"name": res.name, "type": str(res.type.value)}
            for res in self._resources.values()
        }
        if path:
            self._path = path
        self._path.write_text(json.dumps(to_disk))

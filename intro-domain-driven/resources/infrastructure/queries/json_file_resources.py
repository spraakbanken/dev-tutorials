import json
from pathlib import Path

from resources.application.queries.resources import ListResources, ResourceDto


class JsonFileListResources(ListResources):
    def __init__(self, path: Path) -> None:
        self._path = path

    def query(self) -> list[ResourceDto]:
        return [
            ResourceDto(id=id, name=res["name"], type=res["type"])
            for id, res in json.loads(self._path.read_text()).items()
        ]

import json
from pathlib import Path

from resources.application.queries.resources import ListResources


class JsonFileListResources(ListResources):
    def __init__(self, path: Path) -> None:
        self._path = path

    def query(self) -> list[dict[str, str]]:
        return [
            res | {"id": id} for id, res in json.loads(self._path.read_text()).items()
        ]

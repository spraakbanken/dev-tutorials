from pathlib import Path

from resources.infrastructure.queries.json_file_resources import JsonFileListResources

from resources.application.queries.resources import ListResources

from resources.application.use_cases import UpdateName, UpdatingName

from resources.infrastructure.repositories import JsonFileResourceRepository


class CommandBus:
    def __init__(self) -> None:
        self._cmp_map = {}

    def register(self, cmd_type, cmd_handler) -> None:
        self._cmp_map[cmd_type] = cmd_handler

    def dispatch(self, cmd) -> None:
        handler = self._cmp_map[type(cmd)]
        handler.execute(cmd)


class AppContext:
    def __init__(self, command_bus: CommandBus, list_resources: ListResources) -> None:
        self.command_bus = command_bus
        self.list_resources = list_resources


def bootstrap_app(json_path: Path | str) -> AppContext:
    if not isinstance(json_path, Path):
        json_path = Path(json_path)

    command_bus = CommandBus()
    resource_repo = JsonFileResourceRepository(json_path)

    update_name_handler = UpdatingName(repo=resource_repo)
    command_bus.register(UpdateName, update_name_handler)
    return AppContext(
        command_bus=command_bus, list_resources=JsonFileListResources(json_path)
    )

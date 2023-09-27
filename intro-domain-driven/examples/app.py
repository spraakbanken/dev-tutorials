from pathlib import Path
import sys

from resources.application.use_cases.updating_name import UpdateName, UpdatingName

from resources.infrastructure.repositories.json_file_resources import JsonFileResourceRepository

from resources.infrastructure.queries.json_file_resources import JsonFileListResources


def main() -> None:
    json_path, cmd, *rest = sys.argv[1:]
    json_path = Path(json_path)
    if cmd == "list":
        list_all_resources(json_path)
    elif cmd == "update-name":
        update_name(rest, json_path)


def list_all_resources(json_path: Path) -> None:
    list_resources = JsonFileListResources(json_path)
    print(f"{'id': ^38}{'type': ^8}name")
    print(f"{'':-<38}{'':-<8}{'':-<20}")
    for res in list_resources.query():
        print(f"{res.id: <38}{res.type: <8}{res.name}")


def update_name(rest: list[str], json_path: Path) -> None:
    resource_id, name = rest[:1]
    if not resource_id or not name:
        print("You must give resource_id and name")
        sys.exit(1)
    resource_repo = JsonFileResourceRepository(json_path)
    uc = UpdatingName(repo=resource_repo)
    input_dto = UpdateName(id=resource_id,name=name)
    uc.execute(input_dto)
    print(f"resource '{resource_id}' updated")


if __name__ == "__main__":
    main()

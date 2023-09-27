from pathlib import Path
import sys

from resources.main import AppContext, bootstrap_app

from resources.application.use_cases.updating_name import UpdateName



def main() -> None:
    json_path, cmd, *rest = sys.argv[1:]
    app_context = bootstrap_app(json_path)
    if cmd == "list":
        list_all_resources(app_context)
    elif cmd == "update-name":
        update_name(rest, app_context)


def list_all_resources(app_context: AppContext) -> None:
    print(f"{'id': ^38}{'type': ^8}name")
    print(f"{'':-<38}{'':-<8}{'':-<20}")
    for res in app_context.list_resources.query():
        print(f"{res.id: <38}{res.type: <8}{res.name}")


def update_name(rest: list[str], app_context: AppContext) -> None:
    resource_id, name, *_ = rest
    if not resource_id or not name:
        print("You must give resource_id and name")
        sys.exit(1)
    input_dto = UpdateName(id=resource_id,name=name)
    app_context.command_bus.dispatch(input_dto)
    print(f"resource '{resource_id}' updated")


if __name__ == "__main__":
    main()

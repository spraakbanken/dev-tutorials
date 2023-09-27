# Introduction to Domain-Driven Development

The idea is to model the domain based on the domain language, so that developers and non-developers can talk about the model.
E.g. if the software handles auctions, the model should contain a class `Auction`.

Another point is to keep the domain clean without dependencies of the system.

We are going to implement a system talking about resources, so our first code is a tests for how we represent a resource:

```python
# tests/unit/domain/test_resource.py
import uuid

from resources.domain.entites.resource import Resource, ResourceType


def test_can_create_resource():
    resource = Resource(id=uuid.uuid4(), name="Lexicon Rex", type_="lexicon")

    assert resource.type == ResourceType.Lexicon
    assert resource.name == "Lexicon Rex"


def test_can_create_resource_with_comment():
    resource = Resource(
        id=uuid.uuid4(), name="Lexicon Rex", type_="lexicon", comment="Comment"
    )

    assert resource.comment == "Comment"
```

and here is some code that makes the test pass:

```python
# file: resources/domain/entities/resource.py
import enum
from uuid import UUID


class ResourceType(str, enum.Enum):
    Corpus = "corpus"
    Lexicon = "lexicon"


class Resource:
    def __init__(
        self,
        *,
        id: UUID,
        name: str,
        type_: ResourceType | str,
        comment: str | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._type = ResourceType(type_) if isinstance(type_, str) else type_
        self._comment = comment

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> ResourceType:
        return self._type

    @property
    def comment(self) -> str | None:
        return self._comment

```

We allow to pass a Resource's type as `ResourceType` or `str` and added a optional `comment` field.


## Use case 1: Update name

We can now imagine that a user wants to update the name of a resource.

So what does our program needs to do?

1. Fetch existing resource from a repository.
2. Update the name.
3. Write back to the repository.

Point 2 clearly belongs in the domain, but point 1 & 3 belong somewhere else let us call
that layer `application`.

So we can write a test for our use case `UpdatingName` like this:

```python
# tests/unit/application/test_updating_name.py
import pytest

from resources.application.use_cases.updating_name import UpdateName, UpdatingName


@pytest.fixture()
def repo():
    raise NotImplementedError("?")


@pytest.fixture()
def resource_id() -> UUID:
    raise NotImplementedError("?")


def test_updating_name_succeeds(repo, resource_id: UUID):
    uc = UpdatingName(repo)

    input_dto = UpdateName(
        id=resource_id,
        name="Lexicon Royale",
    )
    uc.execute(input_dto)

    resource = repo.get(resource_id)

    assert resource.name == "Lexicon Royale"
```

Ok, looks simple, but we don't know what repo is and how are we going to get correct resource_id?

We can write the code for what we know about the use case:

```python
# resources/application/use_cases/updating_name.py
from pydantic import UUID4, BaseModel


class UpdateName(BaseModel):
    id: UUID4
    name: str


class UpdatingName:
    def __init__(self, repo=?) -> None:
        self.repo = repo

    def execute(self, input_dto: UpdateName) -> None:
        resource = self.repo.get(input_dto.id)

        resource.set_name(input_dto.name)

        self.repo.save(resource)
```

First, we can add this method to our `Resource`:
```python
class Resource:
    ...
    def set_name(self, name: str) -> None:
        # TODO validate name
        self._name = name
```

We want all changes to our domain entities to happen through methods on the class, to concentrate all business logic here.

We don't know yet what kind of repository we will use, so let's write an interface for one:

```python
# resources/application/repositories/resources.py
import abc


class ResourceRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id: UUID) -> Resource:
        ...

    @abc.abstractmethod
    def save(self, resource: Resource) -> None:
        ...
```

So with this definition we can go back to `UpdatingName`.

```python
...

from resources.application.repositories.resources import ResourceRepository

...

class UpdatingName:
    def __init__(self, repo: ResourceRepository) -> None:
        self.repo = repo

    ...
```

Good, now we need an implementation of `ResourceRepository`, lets call it `InMemoryResourceRepository`.


```python
# resources/application/repositories/mem/mem_resources.py
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
```

> [!NOTE]
> We make a copy of the resource both when we save and return a resource, so that mutating the resource outside of the repository don't change the resource in the repository.

With this we can update our test.

```python
from uuid import UUID

import pytest

from resources.application.repositories.mem.mem_resources import (
    InMemoryResourceRepository,
)
from resources.application.repositories.resources import ResourceRepository
from resources.application.use_cases.updating_name import UpdateName, UpdatingName
from resources.domain.entites.resource import ResourceType, Resource


@pytest.fixture()
def repo():
    return InMemoryResourceRepository()


@pytest.fixture()
def resource_id():
    return UUID("18cc403e-a0a4-4a93-9123-4720c34fe005")


@pytest.fixture()
def repo_with_resource(
    repo: ResourceRepository, resource_id: UUID
) -> ResourceRepository:
    repo.save(Resource(id=resource_id, name="RANDOM", type=ResourceType.Lexicon))
    return repo


def test_updating_name_succeeds(
    repo_with_resource: ResourceRepository, resource_id: UUID
):
    uc = UpdatingName(repo=repo_with_resource)

    input_dto = UpdateName(
        id=resource_id,
        name="Lexicon Royale",
    )
    uc.execute(input_dto)

    resource = repo_with_resource.get(resource_id)

    assert resource.name == "Lexicon Royale"
```

And run it:
```bash
❯ pytest -v tests
================================= test session starts ==========================================
platform linux -- Python 3.10.9, pytest-7.2.2, pluggy-1.0.0 --
collected 2 items

tests/unit/application/test_updating_name.py::test_updating_name_succeeds PASSED       [ 50%]
tests/unit/domain/test_resource.py::test_can_create_resource PASSED                    [100%]

================================= 2 passed in 0.04s ============================================

```

### Benefits

What have we achieved here?

We have a isolated our business logic in our domain object `Resource`.

We have a generic use case `UpdatingName` that handles updating the name for any repository.


## Infrastructure

We now have 2 layers, `domain` and `application`, but where should we put our implementations of the `ResourceRepository`?

You guessed right, we introduce a new layer `infrastructure` where we can can implement for instance a `JsonFileResourceRepository`:


```python
# resources/infrastructure/repositories/json_file_resources.py
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
                id=uuid,
                name=data["name"],
                type_=ResourceType.from_str(data["type"]),
                comment=data.get("comment"),
            )
            self._resources[uuid] = resource

    def get(self, id: UUID) -> Resource:
        return copy.deepcopy(self._resources[id])

    def save(self, resource: Resource) -> None:
        self._resources[resource.id] = copy.deepcopy(resource)

    def write_to_path(self, path: Optional[Path] = None):
        to_disk = {
            str(res.id): {
                "name": res.name,
                "type": str(res.type),
                "comment": res.comment,
            }
            for res in self._resources.values()
        }
        if path:
            self._path = path
        self._path.write_text(json.dumps(to_disk))
```

And adding a integration test for this class since this treats paths, and also test that the
serialization and deserialization of the Json files works.

```python
# tests/integration/test_json_file_resources.py
from pathlib import Path
from uuid import UUID

import pytest

from resources.infrastructure.repositories.json_file_resources import (
    JsonFileResourceRepository,
)
from resources.application.use_cases.updating_name import UpdateName, UpdatingName


@pytest.fixture()
def resource_id():
    return UUID("53dd4178-17fa-4725-a5ef-1a217e9946b9")


def test_updating_name_succeeds(resource_id: UUID):
    repo = JsonFileResourceRepository(Path("tests/assets/resources.json"))

    uc = UpdatingName(repo=repo)

    input_dto = UpdateName(
        id=resource_id,
        name="Lexicon Royale",
    )
    uc.execute(input_dto)
    repo.write_to_path(Path("tests/assets/generated/resources.json"))

    repo_copy = JsonFileResourceRepository(Path("tests/assets/generated/resources.json"))
    resource = repo_copy.get(resource_id)

    assert resource.name == "Lexicon Royale"
```

We write our repo with a updated resource to a new path (`tests/assets/generated/resources.json`) and open a repository that uses that file.

But we have a problem, to write our changes we use a method that not is included in the interface.

Let's move to writing to the `save` method:
```diff
def save(self, resource: Resource) -> None:
    self._resources[resource.id] = copy.deepcopy(resource)
+    self.write_to_path()
```

and then we must rewrite the test:
```diff
+import json
from pathlib import Path
from uuid import UUID

@pytest.fixture()
def resource_id():
    return UUID("53dd4178-17fa-4725-a5ef-1a217e9946b9")

+@pytest.fixture()
+def json_path(resource_id: UUID) -> Path:
+    path = Path("tests/assets/generated/resources.json")
+    data = {str(resource_id): {"name": "NOT SET", "type": "lexicon"}}
+    path.write_text(json.dumps(data))
+    return path


-def test_updating_name_succeeds(resource_id: UUID):
-    repo = JsonFileResourceRepository(Path("tests/assets/resources.json"))
+def test_updating_name_succeeds(resource_id: UUID, json_path: Path):
+    repo = JsonFileResourceRepository(json_path)

    uc = UpdatingName(repo=repo)

    input_dto = UpdateName(
        id=resource_id,
        name="Lexicon Royale",
    )
    uc.execute(input_dto)
-    repo.write_to_path(Path("tests/assets/generated/resources.json"))

-    repo_copy = JsonFileResourceRepository(
-        Path("tests/assets/generated/resources.json")
-    )
+    repo_copy = JsonFileResourceRepository(json_path)
    resource = repo_copy.get(resource_id)

    assert resource.name == "Lexicon Royale"
```

Much better!

We could also use `sqlalchemy` for using a SQL repo.

### Queries

Sometimes the domain objects are big and need a lot of validation when working with, but for reading that validation is not needed. So we can define an interface for a specific query:

```python
# resources/application/queries/resources.py

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
```

We create a `dataclass` named `ResourceDto` (where `DTO` stands for `D`ata `T`ransfer `O`bject) to show that this query only is interested in this fields.

And implement it for our Json file:

```python
# resources/infrastructure/queries/json_file_resources.py
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
```

Here we build a `ResourceDto` for every resource.

### Example

How shall we use this in an app?

```python
# examples/app.py
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


def list_all_resources(json_path) -> None:
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

```

So we can run it with:
```bash
> poetry run python examples/app.py examples/resources.json list
                  id                    type  name
------------------------------------------------------------------
53dd4178-17fa-4725-a5ef-1a217e9946b9  lexicon NOT SET
```
and
```bash
> poetry run python examples/app.py examples/resources.json update-name 53dd4178-17fa-4725-a5ef-1a217e9946b9 'Lexicon Royale'
resource '53dd4178-17fa-4725-a5ef-1a217e9946b9' updated
```
And running list again gives us:
```bash
> poetry run python examples/app.py examples/resources.json list
                  id                    type  name
------------------------------------------------------------------
53dd4178-17fa-4725-a5ef-1a217e9946b9  lexicon Lexicon Royale
```

### Command-Query Response Separation

We can also decouple the updating of our business model to something that is called a `CommandBus`.

Currently when we want to use our repository we have to collect all moving parts.

The idea with a commandbus is to hide that complexity and expose a command_bus that handles commands.

We add the module `main` to collect the app configuration:
```python
# resources/main.py
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
        command_bus=command_bus,
        list_resources=JsonFileListResources(json_path)
    )
```

which we can use in our example

```diff
from pathlib import Path
import sys

+from resources.main import AppContext, bootstrap_app

-from resources.application.use_cases.updating_name import UpdateName, UpdatingName
+from resources.application.use_cases.updating_name import UpdateName

-from resources.infrastructure.repositories.json_file_resources import JsonFileResourceRepository

-from resources.infrastructure.queries.json_file_resources import JsonFileListResources


def main() -> None:
    json_path, cmd, *rest = sys.argv[1:]
-    json_path = Path(json_path)
+    app_context = bootstrap_app(json_path)
    if cmd == "list":
-        list_all_resources(json_path)
+        list_all_resources(app_context)
    elif cmd == "update-name":
-        update_name(rest, json_path)
+        update_name(rest, app_context)


-def list_all_resources(json_path: Path) -> None:
+def list_all_resources(app_context: AppContext) -> None:
-    list_resources = JsonFileListResources(json_path)
    print(f"{'id': ^38}{'type': ^8}name")
    print(f"{'':-<38}{'':-<8}{'':-<20}")
-    for res in list_resources.query():
+    for res in app_context.list_resources.query():
        print(f"{res.id: <38}{res.type: <8}{res.name}")


-def update_name(rest: list[str], json_path: Path) -> None:
+def update_name(rest: list[str], app_context: AppContext) -> None:
    resource_id, name = rest[:1]
    if not resource_id or not name:
        print("You must give resource_id and name")
        sys.exit(1)
-    resource_repo = JsonFileResourceRepository(json_path)
-    uc = UpdatingName(repo=resource_repo)
    input_dto = UpdateName(id=resource_id,name=name)
-    uc.execute(input_dto)
+    app_context.command_bus.dispatch(input_dto)
    print(f"resource '{resource_id}' updated")


if __name__ == "__main__":
    main()
```

The new code exists in [`examples/app_cqrs.py`](./examples/app_cqrs.py), it works the same but we have made our app code ignorant of what kind of repository we use, so the app code doesn't need to change if we decide to use a `SQL` repository instead.

But in this simplified example we always load the whole repository even if we only shall list all resources using the query. This can be solved by using some kind of *dependency injection* solution, which allow us to only load the repository when we need to interact with it.

## Next steps

### Implement more use cases

We should add use cases for adding a resource and deleting a resource.

### Events

You can define Domain Events that a domain entity emit when some has happened, for instance our method `set_name` could emit a event `ResourceNameChanged` if the name is changed.

Then other parts of the code can listen for specific event types, and act upon them. This decouples different modules in the code.

In our code above the query `ListResources` can listen to any changes to any `Resource` to update a read-view of our database.

# References

- [Fowler, Martin; DomainDrivenDesign](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Miteva, Sara; The conepts of domain driven design explained](https://dev.to/microtica/the-concept-of-domain-driven-design-explained-1ccn)
- [Graca, Herberto; Explicit architecture](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/#more-14874)






# Introduction to Domain-Driven Development

The idea is to model the domain based on the domain language, so that developers and non-developers can talk about the model.
E.g. if the software handles auctions, the model should contain a class `Auction`.

Another point is to keep the domain clean without dependencies of the system.

We are going to implement a system talking about resources, so our first code is a test for how we represent a resource:

```python
# tests/unit/domain/test_resource.py
import uuid

from resources.domain.entites.resource import Resource, ResourceType


def test_can_create_resource():
    resource = Resource(id=uuid.uuid4(), name="Lexicon Rex", type="lexicon")

    assert resource.type == ResourceType.Lexicon
    assert resource.name == "Lexicon Rex"
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
        type: ResourceType,
    ) -> None:
        self._id = id
        self._name = name
        self._type = type

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> ResourceType:
        return self._type

```



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
We don't know yet what kind of repository we will use, so let's write an interface for one:

```python
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
                id=uuid, name=data["name"], type=ResourceType.from_str(data["type"])
            )
            self._resources[uuid] = resource

    def get(self, id: UUID) -> Resource:
        return copy.deepcopy(self._resources[id])

    def save(self, resource: Resource) -> None:
        self._resources[resource.id] = copy.deepcopy(resource)

    def write_to_path(self, path: Optional[Path] = None):
        to_disk = {
            str(res.id): {"name": res.name, "type": str(res.type)}
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

We could also use `sqlalchemy` for using a SQL repo.

## Next steps

### Queries

Sometimes the domain objects are big and need a lot of validation when working with, but for reading that validation is not needed. So we can define an interface for a specific query:

```python
# resources/application/queries/resources.py

import abc

class ListResources(abc.ABC):
    @abc.abstractmethod
    def query(self) -> list[dict[str, str]]:
        ...
```

and implement it for our Json file:

```python
# resources/infrastructure/queries/json_file_resources.py
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
```

### Events

You can define Domain Events that a domain entity emit when some has happened, for instance our method `set_name` could emit a event `ResourceNameChanged` if the name is changed.

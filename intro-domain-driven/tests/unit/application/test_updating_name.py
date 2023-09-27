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
def resource_id() -> UUID:
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

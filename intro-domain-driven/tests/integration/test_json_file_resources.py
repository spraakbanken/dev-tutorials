import json
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


@pytest.fixture()
def json_path(resource_id: UUID) -> Path:
    path = Path("tests/assets/generated/resources.json")
    data = {str(resource_id): {"name": "NOT SET", "type": "lexicon"}}
    path.write_text(json.dumps(data))
    return path


def test_updating_name_succeeds(resource_id: UUID, json_path: Path):
    repo = JsonFileResourceRepository(json_path)

    uc = UpdatingName(repo=repo)

    input_dto = UpdateName(
        id=resource_id,
        name="Lexicon Royale",
    )
    uc.execute(input_dto)

    repo_copy = JsonFileResourceRepository(json_path)
    resource = repo_copy.get(resource_id)

    assert resource.name == "Lexicon Royale"

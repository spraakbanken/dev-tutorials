import random

import pytest
from snapshot_testing_in_python import User, hello
from syrupy.extensions.json import JSONSnapshotExtension
from syrupy.matchers import path_type


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


def test_hello(snapshot) -> None:
    assert hello() == snapshot


def random_user() -> User:
    return User(name="Mormor Karl", timestamp=random.randint(100000, 200000))


def test_user(snapshot_json) -> None:
    user = random_user()

    assert user.to_dict() == snapshot_json(matcher=path_type({"timestamp": (int,)}))

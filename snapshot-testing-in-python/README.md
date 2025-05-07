# Snapshot testing in python

This tutorial contains an example project that showcases the using of [`syrupy`](https://github.com/syrupy-project/syrupy) in Python.

Snapshot testing a data-driven method for testing.

## Project setup

Do either:

```shell
uv init --lib snapshot-testing-in-python
```

or:

```shell
mkdir snapshot-testing-in-python
cd snapshot-testing-in-python
uv init --lib
```

## Add Pytest and Syrupy

```shell
uv add --dev pytest syrupy
```

## Write Tests

```python
# file: tests/test_all.py
from snapshot_testing_in_python import hello


def test_hello():
    assert hello() == snapshot
```

If we run this with `uv run pytest` we will get this result:

```shell
    def test_hello(snapshot) -> None:
>       assert hello() == snapshot
E       AssertionError: assert [+ received] == [- snapshot]
E         Snapshot 'test_hello' does not exist!
E         + 'Hello from shapshot-testing-in-python!'

tests/test_all.py:13: AssertionError
```

We can see that the snapshot `test_hello` does not exist, so lets generate that!

```shell
uv run pytest --snapshot-update
```

After that we can run our tests and they should pass.

```shell
uv run pytest -vv
```

gives this output:

```shell
tests/test_all.py::test_hello PASSED                                                 [ 100%]

--------------------------------- snapshot report summary ----------------------------------
1 snapshots passed.
==================================== 1 passed in 0.02s =====================================
```

## Generate snapshots as Json

Lets add a class that we want to test.

```python
# file: src/snapshot_testing_in_python/__init__.py
from dataclasses import dataclass
from typing import Any

# ...

@dataclass
class User:
    name: str
    timestamp: int
    
    def to_dict(self) -> dict[str, Any]:
        return self.__dict__
```

How should we test this? Lets write a test for this.

```python
import random

from snapshot_testing_in_python import User, hello

...

def random_user() -> User:
    return User(name="Mormor Karl", timestamp=random.randint(100000,200000))


def test_user(snapshot):
    user = random_user()
    
    assert user.to_dict() == snapshot
```

If we test this with `uv run pytest -vv` we get:

```shell
    def test_user2(snapshot) -> None:
        user = random_user()
>       assert user == snapshot
E       AssertionError: assert [+ received] == [- snapshot]
E         Snapshot 'test_user' does not exist!
E         + User(name='Mormor Karl', timestamp=173001)

tests/test_all.py:31: AssertionError
```

Great, so now we can update the snapshots and we are done. But we want to see it as json.

First we need to add a fixture for that.

```python
import pytest
from syrupy.extensions.json import JSONSnapshotExtension


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)
```

So now we can use that in our test.

```python
def test_user(snapshot_json) -> None:
    user = random_user()

    assert user.to_dict() == snapshot_json
```

If we now run this example we get the following output:

```shell
    def test_user(snapshot_json) -> None:
        user = random_user()

>       assert user.to_dict() == snapshot_json
E       assert [+ received] == [- snapshot]
E         Snapshot 'test_user' does not exist!
E         + {
E         +   "name": "Mormor Karl",
E         +   "timestamp": 143329
E         + }

tests/test_all.py:24: AssertionError
```

That is easier to look at. We generate a snapshot for this.

Lets run the test again:

```python
def test_user(snapshot_json) -> None:
    user = random_user()

>       assert user.to_dict() == snapshot_json
E       assert [+ received] == [- snapshot]
E           {
E             "name": "Mormor Karl",
E         -   "timestamp": 138134
E         +   "timestamp": 171993
E           }

tests/test_all.py:24: AssertionError
``` 

Our `timestamp` field is random, so our snapshot will fail.

But we know that `timestamp` has the type `int`, we can add a `matcher` for that.

```python
from syrupy.matchers import path_type

...

def test_user(snapshot_json) -> None:
    user = random_user()

    assert user.to_dict() == snapshot_json(matcher=path_type({"timestamp": (int,)}))
```

If we run `uv run pytest -vv` now we get.

```shell
    def test_user(snapshot_json) -> None:
        user = random_user()

>       assert user.to_dict() == snapshot_json(matcher=path_type({"timestamp": (int,)}))
E       assert [+ received] == [- snapshot]
E           {
E             "name": "Mormor Karl",
E         -   "timestamp": 138134
E         +   "timestamp": "int"
E           }

tests/test_all.py:25: AssertionError
```

Here we can see that `timestamp` is `"int"` instead of an actual `int`.

So if we now update our snapshots with `uv run pytest --snapshot-update` and run our test again.

```shell
tests/test_all.py::test_hello PASSED                                                 [ 50%]
tests/test_all.py::test_user PASSED                                                  [100%]

--------------------------------- snapshot report summary ----------------------------------
2 snapshots passed.
==================================== 2 passed in 0.03s =====================================
```

With this matcher our test will pass every time.

## Update tests

Sometimes later, when we run our test we get an error:

```shell
    def test_hello(snapshot) -> None:
>       assert hello() == snapshot
E       AssertionError: assert [+ received] == [- snapshot]
E         - 'Hello from shapshot-testing-in-python!'
E         + 'Hello from snapshot-testing-in-python!'

tests/test_all.py:15: AssertionError
```

We can now inspect the error and see if:
- this is a bug and fix it
- this is the new expected answer and update snapshots.

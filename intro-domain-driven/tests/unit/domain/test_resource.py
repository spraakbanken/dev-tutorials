import uuid

from resources.domain.entites.resource import Resource, ResourceType


def test_can_create_resource():
    resource = Resource(id=uuid.uuid4(), name="Lexicon Rex", type="lexicon")

    assert resource.type == ResourceType.Lexicon
    assert resource.name == "Lexicon Rex"

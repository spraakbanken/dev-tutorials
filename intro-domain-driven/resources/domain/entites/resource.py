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
    def comment(self) -> str | None:
        return self._comment

    @property
    def type(self) -> ResourceType:
        return self._type

    def set_name(self, name: str) -> None:
        # TODO validate name
        self._name = name

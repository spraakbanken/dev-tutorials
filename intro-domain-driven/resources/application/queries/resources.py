import abc


class ListResources(abc.ABC):
    @abc.abstractmethod
    def query(self) -> list[dict[str, str]]:
        ...

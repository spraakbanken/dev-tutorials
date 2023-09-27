from pydantic import UUID4, BaseModel

from resources.application.repositories.resources import ResourceRepository


class UpdateName(BaseModel):
    id: UUID4
    name: str


class UpdatingName:
    def __init__(self, repo: ResourceRepository) -> None:
        self.repo = repo

    def execute(self, input_dto: UpdateName) -> None:
        resource = self.repo.get(input_dto.id)

        resource.set_name(input_dto.name)

        self.repo.save(resource)

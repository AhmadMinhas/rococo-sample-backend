from uuid import UUID

from common.repositories.factory import RepositoryFactory, RepoType
from common.models.todo import Todo


class TodoService:
    def __init__(self, config):
        self.config = config
        self.repository_factory = RepositoryFactory(config)
        self.todo_repo = self.repository_factory.get_repository(RepoType.TODO)

    def get_todo_by_id(self, entity_id: str) -> Todo:
        return self.todo_repo.get_one({"entity_id": entity_id})

    def update_todo(self, entity_id: str, updates: dict, changed_by_id: UUID) -> Todo:
        existing_todo = self.get_todo_by_id(entity_id)
        for key, value in updates.items():
            setattr(existing_todo, key, value)
        existing_todo.prepare_for_save(changed_by_id=changed_by_id)
        self.todo_repo.save(existing_todo)
        return existing_todo

    def delete_todo(self, entity_id: str, changed_by_id: UUID) -> Todo:
        todo = self.get_todo_by_id(entity_id)
        todo.active = False
        todo.prepare_for_save(changed_by_id)
        self.todo_repo.save(todo)
        return todo

    def list_todos(self, filters: dict = None) -> list[Todo]:
        return self.todo_repo.list(filters or {})

    def list(self, person_id: str, status: str = None):
        query = {'person_id': person_id, 'active': True}
        if status == "active":
            query['is_completed'] = True
        elif status == "inactive":
            query['is_completed'] = False
        return self.todo_repo.get_many(query, sort=[("changed_on", 'asc')])

    def create(self, person_id: str, title: str):
        todo = Todo(person_id=person_id, title=title)
        todo.prepare_for_save(changed_by_id=UUID(person_id))
        return self.todo_repo.save(todo)

    def update_status_bulk(self, person_id: str, active: bool = None, is_deleted: bool = None):
        todos = self.todo_repo.get_many({"person_id": person_id, "active": True})
        updated = []
        for todo in todos:
            if active is not None:
                todo.is_completed = active
            if is_deleted is not None:
                todo.active = not is_deleted
            # TODO: implement bulk update method in Base Repository
            todo.prepare_for_save(changed_by_id=UUID(person_id))
            self.todo_repo.save(todo)
            updated.append(todo)
        return updated

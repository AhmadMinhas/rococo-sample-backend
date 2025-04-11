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

    def filter_todo(self, person_id: str, status: str = None):
        filters = {'person_id': person_id, 'active': True}
        if status == "completed":
            filters['is_completed'] = True
        elif status == "pending":
            filters['is_completed'] = False
        return self.todo_repo.get_many(filters, sort=[("changed_on", 'asc')])

    def create(self, person_id: str, title: str):
        todo = Todo(person_id=person_id, title=title)
        todo.prepare_for_save(changed_by_id=UUID(person_id))
        return self.todo_repo.save(todo)

    def get_pending_todos(self, person_id: str = None) -> list[Todo]:
        filters = {"is_completed": False, "active": True}
        if person_id:
            filters["person_id"] = person_id
        return self.todo_repo.get_many(filters)

    def get_completed_todos(self, person_id: str = None) -> list[Todo]:
        filters = {"is_completed": True, "active": True}
        if person_id:
            filters["person_id"] = person_id
        return self.todo_repo.get_many(filters)

    def mark_all_as_completed(self, person_id: str):
        active_todos = self.get_pending_todos(person_id)
        updated = list()
        for todo in active_todos:
            todo.is_completed = True
            self.todo_repo.save(todo)
            updated.append(todo)
        return len(updated)

    def mark_all_as_pending(self, person_id: str):
        active_todos = self.get_completed_todos(person_id)
        updated = list()
        for todo in active_todos:
            todo.is_completed = False
            self.todo_repo.save(todo)
            updated.append(todo)
        return len(updated)

    def clear_completed(self, person_id: str):
        active_todos = self.get_completed_todos(person_id)
        updated = list()
        for todo in active_todos:
            todo.active = False
            self.todo_repo.save(todo)
            updated.append(todo)
        return len(updated)

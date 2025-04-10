from flask_restx import Namespace, Resource, fields, reqparse
from app.helpers.response import get_success_response, get_failure_response
from app.helpers.decorators import login_required

from common.services import TodoService
from common.app_config import config

todo_api = Namespace('todo', description="Todo-tasks related APIs")
todo_service = TodoService(config)

todo_model = todo_api.model('Todo', {
    'title': fields.String(required=True),
})

todo_filter_model = reqparse.RequestParser()
todo_filter_model.add_argument('status', choices=('active', 'inactive', 'all'), default='all')

todo_update_model = todo_api.model('TodoUpdate', {
    'is_deleted': fields.Boolean(description='Delete status of the todo task'),
    'is_completed': fields.Boolean(description='Completion status of the todo task'),
    'title': fields.Boolean(description='Title of the todo task')
})


@todo_api.route('/')
class TodoList(Resource):
    @login_required()
    @todo_api.expect(todo_filter_model)
    def get(self, person):
        # Retrieve query parameters
        args = todo_filter_model.parse_args()
        # Call the service to list todos by person and status
        todos = todo_service.list(person_id=person.entity_id, status=args['status'])
        return get_success_response(todos=[todo.as_dict() for todo in todos])

    @login_required()
    @todo_api.expect(todo_model)
    def post(self, person):
        # Retrieve the data from the request payload
        data = todo_api.payload
        if 'title' not in data:
            return get_failure_response(message="title is required", status_code=400)
        # Call the service to create a new todo
        todo = todo_service.create(person_id=person.entity_id, title=data['title'])
        return get_success_response(todo=todo.as_dict())


@todo_api.route('/<string:entity_id>')
class TodoItem(Resource):
    @login_required()
    @todo_api.expect(todo_update_model)  # Expect the model for updates
    def patch(self, person, entity_id):
        # Retrieve the update data from the request payload
        data = todo_api.payload

        # Fetch the todo task by entity_id
        todo = todo_service.get_todo_by_id(entity_id)

        if not todo:
            return get_failure_response(message="Details Not Found", status_code=400)

        # Ensure the required fields (active or is_deleted) are passed in the request and apply updates
        update_data = {}
        if 'is_deleted' in data:
            update_data['active'] = data['is_deleted']
        if 'is_completed' in data:
            update_data['is_completed'] = data['is_completed']
        if 'title' in data and data['title']:
            update_data['title'] = data['title']

        # Update the task using the service
        updated_todo = todo_service.update_todo(
            entity_id=entity_id,
            updates=update_data,
            changed_by_id=person.entity_id
        )

        return get_success_response(todo=updated_todo.as_dict())


@todo_api.route('/bulk/activate')
class MarkAllActive(Resource):
    @login_required()
    def post(self, person):
        # Call the service to update the status of all todos to active
        todos = todo_service.update_status_bulk(person.entity_id, active=True)
        return get_success_response(updated=len(todos))


@todo_api.route('/bulk/deactivate')
class MarkAllInactive(Resource):
    @login_required()
    def post(self, person):
        # Call the service to update the status of all todos to inactive
        todos = todo_service.update_status_bulk(person.entity_id, active=False)
        return get_success_response(updated=len(todos))


@todo_api.route('/bulk/delete')
class MarkAllDeleted(Resource):
    @login_required()
    def post(self, person):
        # Call the service to mark all todos as deleted
        todos = todo_service.update_status_bulk(person.entity_id, is_deleted=True)
        return get_success_response(updated=len(todos))

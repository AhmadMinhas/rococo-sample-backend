from flask_restx import Namespace, Resource, fields
from app.helpers.response import get_success_response
from app.helpers.decorators import login_required

from common.app_config import config
from common.services import PersonService

todo_service = PersonService(config)

# Create the organization blueprint
person_api = Namespace('person', description="Person-related APIs")
person_modal = person_api.model('Person Update', {
    'first_name': fields.String(),
    'last_name': fields.String(),
})


@person_api.route('/me')
class Me(Resource):
    
    @login_required()
    def get(self, person):
        return get_success_response(person=person)

    @login_required()
    @person_api.expect(person_modal)
    def patch(self, person):
        data = person_api.payload

        if 'first_name' in data and data['first_name']:
            person.first_name = data['first_name']
        if 'last_name' in data and data['last_name']:
            person.last_name = data['last_name']

        todo_service.save_person(person)
        return get_success_response(person=person)

from microservice_template_core.tools.flask_restplus import api
from flask_restx import Resource
import traceback
from microservice_template_core.tools.logger import get_logger
from harp_licenses.models.licenses import Licenses, LicensesSchema
from flask import request
from microservice_template_core.decorators.auth_decorator import token_required

logger = get_logger()
ns = api.namespace('api/v1/licenses', description='Harp Licenses endpoint')
licenses = LicensesSchema()


@ns.route('/verify/<notification_id>')
class UpdateLicenses(Resource):
    @staticmethod
    @api.response(200, 'Licenses is good')
    @api.response(600, 'License limit was reached')
    @api.response(601, 'Notification ID not found in DB')
    def get(notification_id):
        """
            Verify and update licenses for each notification type
        """
        event_id = request.headers['Event-Id']

        if not notification_id:
            return {'msg': 'notification_id should be specified'}, 404

        if not event_id:
            return {'msg': 'event_id should be specified'}, 404

        obj = Licenses.obj_exist(notification_id)

        try:
            result = licenses.dump(obj.dict())
        except AttributeError:
            logger.error(
                msg=f"Notification ID: {notification_id} not found in DB",
                extra={'tags': {
                    'event_id': event_id
                }}
            )
            return 'Notification ID not found in DB', 601

        if result['current_usage'] >= result['limit']:
            logger.error(
                msg=f"License limit was reached for {result['notification_name']}",
                extra={'tags': {
                    'event_id': event_id
                }}
            )
            new_status = {
                'status': 'limit_reached'
            }
            obj.update_obj(new_status, notification_id=notification_id)
            return 'license limit was reached', 600
        else:
            logger.info(
                msg=f"License is OK for {result['notification_name']}",
                extra={'tags': {
                    'event_id': event_id
                }}
            )
            new_usage = {
                'current_usage': result['current_usage'] + 1,
                'status': 'active'
            }
            obj.update_obj(new_usage, notification_id=notification_id)
            return 'license ok', 200


@ns.route('/all')
class LicenseStatus(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    @token_required()
    def get():
        """
        Return All exist Licenses
        """
        new_obj = Licenses.get_all_licenses()

        result = {'licenses': new_obj}

        return result, 200

import traceback
from microservice_template_core import db
from microservice_template_core.tools.logger import get_logger
from marshmallow import Schema, fields

logger = get_logger()


class Licenses(db.Model):
    __tablename__ = 'licenses'

    notification_id = db.Column(db.Integer, primary_key=True)
    notification_name = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    current_usage = db.Column(db.Integer)
    limit = db.Column(db.Integer)
    status = db.Column(db.VARCHAR(70), nullable=False, unique=False)

    def __repr__(self):
        return f"{self.notification_id}_{self.notification_name}"

    def dict(self):
        return {
            'notification_id': self.notification_id,
            'notification_name': self.notification_name,
            'current_usage': self.current_usage,
            'limit': self.limit,
            'status': self.status
        }

    @classmethod
    def obj_exist(cls, notification_id):
        return cls.query.filter_by(notification_id=notification_id).one_or_none()

    @classmethod
    def get_all_licenses(cls):
        get_all_licenses = cls.query.filter_by().all()
        all_licenses = [single_event.dict() for single_event in get_all_licenses]

        return all_licenses

    def update_obj(self, data, notification_id):

        self.query.filter_by(notification_id=notification_id).update(data)

        db.session.commit()

    def save(self):
        try:
            db.session.add(self)
            db.session.flush()
            db.session.commit()

            return self
        except Exception as exc:
            logger.critical(
                msg=f"Can't commit changes to DB \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            db.session.rollback()

    def delete_obj(self):
        db.session.delete(self)
        db.session.commit()


class LicensesSchema(Schema):
    notification_id = fields.Int(dump_only=True)
    notification_name = fields.Str(required=True)
    current_usage = fields.Int(required=True)
    limit = fields.Int(required=True)
    status = fields.Str(required=True)

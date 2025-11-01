from app.extensions import ma
from models.payment import Payment
from marshmallow import fields

class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    status = fields.Str(dump_only=True)
    reference = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

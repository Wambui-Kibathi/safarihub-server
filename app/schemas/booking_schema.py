from marshmallow import Schema, fields
from app.schemas.user_schema import UserSchema
from app.schemas.destination_schema import DestinationSchema

class BookingSchema(Schema):
    id = fields.Int(dump_only=True)
    traveler_id = fields.Int(required=True)
    destination_id = fields.Int(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    total_cost = fields.Float(required=True)
    is_paid = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    traveler = fields.Nested(UserSchema, dump_only=True)
    destination = fields.Nested(DestinationSchema, dump_only=True)

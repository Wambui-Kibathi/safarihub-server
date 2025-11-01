from flask import Blueprint, request, jsonify
from app.extensions import db
from models.payment import Payment
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.payment_schema import PaymentSchema
from app.utils.role_required import role_required
from app.utils.paystack_service import initialize_payment, verify_payment

payment_bp = Blueprint("payment_bp", __name__)
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)

# GET all payments (admin only)
@payment_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_payments():
    payments = Payment.query.all()
    return payments_schema.jsonify(payments), 200

# GET single payment
@payment_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_payment(id):
    payment = Payment.query.get_or_404(id)
    current_user = get_jwt_identity()
    if payment.user_id != current_user["id"] and current_user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    return payment_schema.jsonify(payment), 200

# POST a new payment (initialize)
@payment_bp.route("/", methods=["POST"])
@jwt_required()
def create_payment():
    data = request.get_json()
    errors = payment_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    current_user = get_jwt_identity()
    payment_response = initialize_payment(
        email=current_user["email"], 
        amount=data["amount"]  # amount in kobo if Paystack
    )
    if payment_response.get("status") != True:
        return jsonify({"error": "Payment initialization failed"}), 400

    new_payment = Payment(
        user_id=current_user["id"],
        amount=data["amount"],
        status="pending",
        reference=payment_response["data"]["reference"]
    )
    db.session.add(new_payment)
    db.session.commit()
    return payment_schema.jsonify(new_payment), 201

# PATCH (update payment status via webhook)
@payment_bp.route("/verify/<string:reference>", methods=["PATCH"])
def verify_payment_route(reference):
    payment = Payment.query.filter_by(reference=reference).first_or_404()
    verified = verify_payment(reference)
    if verified:
        payment.status = "success"
    else:
        payment.status = "failed"
    db.session.commit()
    return payment_schema.jsonify(payment), 200

# DELETE a payment (admin only)
@payment_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({"message": "Payment deleted"}), 200

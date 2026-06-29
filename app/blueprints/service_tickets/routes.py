from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, Customer, Service_Ticket, db
from . import service_tickets_bp

# CREATE NEW SERVICE TICKET
@service_tickets_bp.route("/", methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer_id = service_ticket_data.get("customer_id")
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found. Please try again or create a customer account."}), 404

    new_service_ticket = Service_Ticket(**service_ticket_data)

    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201

# GET/READ ALL EXISTING SERVICE TICKETS

@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(Service_Ticket)
    service_tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(service_tickets), 200

# ASSIGN MECHANICS TO SERVICE TICKETS

@service_tickets_bp.route("/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
def assign_mechanic(service_ticket_id, mechanic_id):
    ticket = db.session.get(Service_Ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
    else:
        return jsonify({"error": "Mechanic is already assigned to this service ticket"}), 400
        
    return jsonify({"message": 
        f"Mechanic {mechanic.id} assigned to service ticket {ticket.id} successfully.",
        "current_assigned_mechanics": [m.id for m in ticket.mechanics]}), 200

# UNASSIGN MECHANICS FROM SERVICE TICKETS
@service_tickets_bp.route("/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(service_ticket_id, mechanic_id):
    ticket = db.session.get(Service_Ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
    else:
        return jsonify({"error": "Mechanic is not assigned to this service ticket"}), 400
        
    return jsonify ({"message": 
        f"Mechanic {mechanic.id} removed from service ticket {ticket.id} successfully.",
        "current_assigned_mechanics": [m.id for m in ticket.mechanics]}), 200 
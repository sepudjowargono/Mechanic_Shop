from typing import Any, cast

from .schemas import service_ticket_schema, service_tickets_schema, edit_ticket_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, Mechanic, Customer, Service_Ticket, db
from . import service_tickets_bp
from app.extensions import limiter, cache
from app.utils.util import mechanic_token_required

# CREATE NEW SERVICE TICKET
@service_tickets_bp.route("/", methods=['POST'])
@mechanic_token_required
@limiter.limit("10 per minute") # Rate limiting is applied because creating new service ticket records is a sensitive operation. Limiting requests helps prevent abuse, spam, accidental duplicate submissions, and excessive traffic that could overwhelm the server or database.
def create_service_ticket(token_mechanic_id):
    try:
        new_service_ticket = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer = db.session.get(Customer, new_service_ticket.customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    db.session.add(new_service_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_service_ticket), 201

# GET/READ ALL EXISTING SERVICE TICKETS

@service_tickets_bp.route("/", methods=['GET'])
@mechanic_token_required
@cache.cached(timeout=60) # Caching is applied because service tickets may be viewed multiple times within a short period. Caching helps reduce unnecessary database queries, improving response times and overall API efficiency.
def get_service_tickets(token_mechanic_id):
    query = select(Service_Ticket)
    service_tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(service_tickets), 200

# ASSIGN MECHANICS TO SERVICE TICKETS

@service_tickets_bp.route("/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
@mechanic_token_required
@limiter.limit("10 per minute") # Rate limiting is applied because this route modifies existing service ticket records by assigning mechanics. Limiting requests helps prevent accidental duplicate tickets, spam requests and excessive database activity that could affect system performance and data integrity.
def assign_mechanic(token_mechanic_id, service_ticket_id, mechanic_id):
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
@mechanic_token_required
@limiter.limit("5 per minute") # Rate limiting is applied because this route modifies existing service ticket records by unassigning mechanics. Limiting requests helps prevent accidental duplicate tickets, spam requests and excessive database activity that could affect system performance and data integrity.
def remove_mechanic(token_mechanic_id, service_ticket_id, mechanic_id):
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
    
#ADVANCED ENDPOINT THAT ALLOWS ADDING AND REMOVING MULTIPLE MECHANICS FROM A SERVICE TICKET IN ONE REQUEST
@service_tickets_bp.route("/<int:service_ticket_id>/edit-mechanics", methods=["PUT"])
@mechanic_token_required
def edit_ticket_mechanics(token_mechanic_id, service_ticket_id):
    try:
        edit_mechanics = cast(dict[str, Any], edit_ticket_schema.load(request.json))
        
    except ValidationError as e:
        return jsonify(e.messages), 400

    ticket = db.session.get(Service_Ticket, service_ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    add_mechanic_ids = edit_mechanics.get("add_mechanic_ids", [])
    remove_mechanic_ids = edit_mechanics.get("remove_mechanic_ids", [])

    for mechanic_id in add_mechanic_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)

        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in remove_mechanic_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)

        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()

    return jsonify({
        "message": "Service ticket mechanics updated successfully.",
        "current_assigned_mechanics": [m.id for m in ticket.mechanics]
    }), 200
    
# ADD PART TO SERVICE TICKETS

@service_tickets_bp.route("/<int:service_ticket_id>/add-part/<int:inventory_item_id>", methods=["PUT"])
@mechanic_token_required
@limiter.limit("10 per minute") 
def add_part_to_service_ticket(token_mechanic_id, service_ticket_id, inventory_item_id):
    ticket = db.session.get(Service_Ticket, service_ticket_id)
    inventory_item = db.session.get(Inventory, inventory_item_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404
    
    if inventory_item not in ticket.inventory:
        ticket.inventory.append(inventory_item)
    else:
        return jsonify({"message": "Inventory item is already assigned to this service ticket.", "current_assigned_parts": [p.id for p in ticket.inventory]}), 409

    db.session.commit()

    return jsonify({
        "message": f"Part {inventory_item.id} added to service ticket {ticket.id} successfully.",
        "current_assigned_parts": [p.id for p in ticket.inventory]
    }), 200
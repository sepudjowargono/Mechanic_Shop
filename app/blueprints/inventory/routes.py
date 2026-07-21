from .schemas import inventory_schema, inventories_schema, inventory_update_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, db
from . import inventory_bp
from app.extensions import limiter, cache
from app.utils.util import mechanic_token_required

# CREATE NEW INVENTORY ITEM

@inventory_bp.route("/", methods=['POST'])
@mechanic_token_required
@limiter.limit("5 per minute") # Rate limiting is applied because creating new inventory records is a sensitive operation. Limiting requests helps prevent abuse, spam, accidental duplicate submissions, and excessive traffic that could overwhelm the server or database.
def create_inventory(token_mechanic_id):
    try:
        new_inventory = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Inventory).where(Inventory.part_name == new_inventory.part_name)
    
    existing_inventory = db.session.execute(query).scalars().all()
    
    if existing_inventory:
        return jsonify({"error": "Inventory item already exists."}), 400
    
    db.session.add(new_inventory)
    db.session.commit()
    
    return inventory_schema.jsonify(new_inventory), 201

# GET/READ EXISTING INVENTORY

@inventory_bp.route("/", methods=['GET'])
@mechanic_token_required
@cache.cached(timeout=30)
def get_inventory(token_mechanic_id):
    query = select(Inventory)
    inventory = db.session.execute(query).scalars().all()
    
    return inventories_schema.jsonify(inventory), 200

# UPDATE SPECIFIC EXISTING INVENTORY ITEM

@inventory_bp.route("/<int:inventory_id>", methods=['PUT'])
@mechanic_token_required
@limiter.limit("5 per minute") # Rate limiting is applied because updating inventory records is a sensitive operation. Limiting requests helps prevent abuse, spam, accidental duplicate submissions, and excessive traffic that could overwhelm the server or database.
def update_inventory(token_mechanic_id, inventory_id):
    inventory_item = db.session.get(Inventory, inventory_id)
    
    if not inventory_item:
        return jsonify({"error": "Inventory item not found."}), 404
    
    try:
        inventory_data = inventory_update_schema.load(
            request.json, 
            partial=True) # Allow partial updates
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in inventory_data.items():
        setattr(inventory_item, key, value)
        
    db.session.commit()
    
    return inventory_schema.jsonify(inventory_item), 200

# DELETE EXISTING INVENTORY ITEM

@inventory_bp.route("/<int:inventory_id>", methods=['DELETE'])
@mechanic_token_required
@limiter.limit("5 per minute") # Rate limiting is applied because deleting inventory records is a sensitive operation. Limiting requests helps prevent abuse, spam, accidental duplicate submissions, and excessive traffic that could overwhelm the server or database.
def delete_inventory(token_mechanic_id, inventory_id):
    inventory_item = db.session.get(Inventory, inventory_id)
    
    if not inventory_item: 
        return jsonify({"error": "Inventory item not found."}), 404
    
    db.session.delete(inventory_item)
    db.session.commit()
    
    return jsonify({
        "message": f'Inventory item {inventory_item.part_name} has been deleted successfully',
        "status": "success"
    }), 200
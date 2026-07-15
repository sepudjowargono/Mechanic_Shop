from .schemas import mechanic_schema, mechanics_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp
from app.extensions import limiter, cache
from app.utils.util import encode_mechanic_token

# LOGIN MECHANIC

@mechanics_bp.route("/login", methods=['POST'])
def login():
    
    try:
        credentials = login_schema.load(request.json)
        
        email = credentials.email
        password = credentials.password
    
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and mechanic.password == password:
        token = encode_mechanic_token(mechanic.id)
        
        response = {
            "status": "success",
            "message": "Login successful",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
# CREATE NEW MECHANIC

@mechanics_bp.route("/", methods=['POST'])
@limiter.limit("5 per minute") # Rate limiting is applied because creating new mechanic records is a sensitive operation. Limiting requests helps prevent abuse, spam, accidental duplicate submissions, and excessive traffic that could overwhelm the server or database.
def create_mechanic():
    try:
        new_mechanic = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(
        Mechanic.email == new_mechanic.email
    )
    existing_mechanic = db.session.execute(query).scalars().first()

    if existing_mechanic:
        return jsonify({
            "error": "Email already associated with a mechanic employee."
        }), 400

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

# GET/READ EXISTING MECHANIC

@mechanics_bp.route("/", methods=['GET'])
@cache.cached(timeout=30) # Caching is applied because the list of mechanics is requested frequently and changes infrequently. Caching the response reduces database load and allows the API to respond more quickly to repeated requests for the same data, improving performance and user experience.
def get_mechanics():
    page = (request.args.get('page', type=int, default=1))
    per_page = (request.args.get('per_page', type=int, default=5))
    
    query = select(Mechanic)
    mechanics = db.paginate(query, page=page, per_page=per_page)
    
    return mechanics_schema.jsonify(mechanics), 200

# UPDATE SPECIFIC EXISTING MECHANIC

@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
@limiter.limit("5 per minute")
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        updated_mechanic_data = mechanic_schema.load(
            request.json,
            partial=True
        )
    except ValidationError as e:
        return jsonify(e.messages), 400

    for field in request.json.keys():
        setattr(
            mechanic,
            field,
            getattr(updated_mechanic_data, field)
        )

    db.session.commit()

    return mechanic_schema.jsonify(mechanic), 200

# DELETE EXISTING MECHANIC

@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
@limiter.limit("5 per minute") # Rate limiting is applied because deleting mechanic records is a sensitive operation. Limiting delete requests helps prevent accidental mass deletions, malicious abuse, and excessive requests that could compromise data integrity.
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic: 
        return jsonify({"error": "Mechanic not found."}), 400
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'Mechanic Id: {mechanic_id} has been deleted successfully'})

# LIST OF MECHANICS IN ORDER OF WHO HAS WORKED ON THE MOST TICKETS
@mechanics_bp.route("/most-tickets", methods=['GET'])
@cache.cached(timeout=60)
def most_tickets_worked():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    # Sort mechanics by the number of service tickets they are assigned to. "Reverse=True" ensures that the mechanic with the most tickets appears first in the list.
    mechanics = sorted(mechanics, key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    
    return mechanics_schema.jsonify(mechanics), 200
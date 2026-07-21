from .schemas import customer_schema, customers_schema, login_schema
from app.blueprints.service_tickets.schemas import service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, Service_Ticket, db
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

# LOGIN CUSTOMER

@customers_bp.route("/login", methods=['POST'])
def login():
    
    try:
        credentials = login_schema.load(request.json)
        
        email = credentials.email
        password = credentials.password
    
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()
    
    if customer and customer.password == password:
        token = encode_token(customer.id)
        
        response = {
            "status": "success",
            "message": "Login successful",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# CREATE NEW CUSTOMER

@customers_bp.route("/", methods=['POST'])
@limiter.limit("5 per minute") # This route is rate limited because it creates new records in the database. Limiting requests helps prevent abuse, spam, accidental duplicate submissions, and excessive traffic that could overwhelm the server or database.
def create_customer():
    try:
        new_customer = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == new_customer.email)
    
    existing_customer = db.session.execute(query).scalars().first()
    
    if existing_customer:
        return jsonify({"error": "Email already associated with an existing customer account."}), 400
    
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

# GET/READ EXISTING CUSTOMER

@customers_bp.route("/", methods=['GET'])
@cache.cached(timeout=30)
def get_customers():
    page = (request.args.get('page', type=int, default=1))
    per_page = (request.args.get('per_page', type=int, default=5))
        
    query = select(Customer)
    customers = db.paginate(query, page=page, per_page=per_page)
        
    return customers_schema.jsonify(customers.items), 200

# GET/READ SPECIFIC CUSTOMER

@customers_bp.route("/<int:customer_id>", methods=['GET'])
@cache.cached(timeout=30) # Caching is applied because customer information is read frequently but does not change with every request. Storing the response for 60 seconds reduces repeated database queries and improves API performance.
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found"}), 404

# UPDATE SPECIFIC EXISTING CUSTOMER

@customers_bp.route("/<int:customer_id>/update-account", methods=['PUT'])
@token_required
def update_customer(token_customer_id, customer_id):
    if token_customer_id != customer_id:
        return jsonify({"error": "You are not authorized to update this account."}), 403
    
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    try:
        update_customer_data = customer_schema.load(
            request.json, 
            partial=True
        )
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field in request.json.keys():
        setattr(
            customer, 
            field, 
            getattr(update_customer_data, field)
        )
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE EXISTING CUSTOMER 

@customers_bp.route("/<int:customer_id>/delete-account", methods=['DELETE'])
@token_required
def delete_customer(token_customer_id, customer_id):
    if token_customer_id != customer_id:
        return jsonify({"error": "You are not authorized to delete this account."}), 403
    
    customer = db.session.get(Customer, customer_id)
    
    if not customer: 
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer Id: {customer_id} has been deleted successfully'}), 200

# GET SERVICE TICKETS ASSOCIATED WITH A SPECIFIC CUSTOMER
@customers_bp.route("/<int:customer_id>/my-service-tickets", methods=['GET'])
@token_required
def get_service_tickets(token_customer_id, customer_id):
    if token_customer_id != customer_id:
        return jsonify({"error": "You are not authorized to view these service tickets."}), 403
    
    query = select(Service_Ticket).where(Service_Ticket.customer_id == customer_id)
    service_tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(service_tickets), 200
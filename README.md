# 🔧 Mechanic Shop API

A RESTful API built with **Flask**, **SQLAlchemy**, **Marshmallow**, **MySQL**, **JWT Authentication**, **Swagger/OpenAPI Documentation**, **Flask-Caching**, **Flask-Limiter**, and **unittest** using the **Application Factory Pattern**.

This project simulates a mechanic shop management system by allowing users to manage customers, mechanics, inventory, and service tickets while demonstrating secure authentication, authorization, API documentation, automated testing, caching, and rate limiting.

---

## ⭐ Project Highlights

- RESTful API design
- Application Factory Pattern
- Blueprint architecture
- JWT Authentication
- Role-based authorization
- Swagger/OpenAPI documentation
- Automated unit testing
- Flask-Caching
- Flask-Limiter
- SQLAlchemy ORM
- Marshmallow validation
- MySQL database

---

## 📚 Features

### 👤 Customer Management
- Customer login with JWT authentication
- Create a customer
- Retrieve all customers (pagination supported)
- Retrieve a single customer
- Update customer information (protected)
- Delete a customer account (protected)
- View all service tickets associated with a customer (protected)

### 🔧 Mechanic Management
- Mechanic login with JWT authentication
- Create a mechanic
- Retrieve all mechanics (pagination supported)
- Update mechanic information
- Delete mechanic information
- View mechanic ranked by number of service tickets completed

### 🚗 Service Ticket Management
- Create a service ticket (protected)
- Retrieve all service tickets (protected)
- Assign a mechanic to a service ticket (protected)
- Remove a mechanic from a service ticket (protected)
- Edit multiple mechanic assignments in a single request (protected)
- Add inventory part to a service ticket (protected)

### 📦 Inventory Management
- Create inventory items (protected)
- Retrieve inventory items (protected)
- Update inventory items (protected)
- Delete Inventory items (protected)

---

## 🛠 Technologies Used

- Python
- Flask
- SQLAlchemy
- Marshmallow
- MySQL
- Flask-SQLAlchemy
- Flask-Marshmallow
- Flask-JWT
- Flask-Caching
- Flask-Limiter
- MySQL Connector
- Postman
- Flasgger (Swagger/OpenAPI)
- unittest

---

## 📂 Project Structure

```
app/
│
├── blueprints/
│   ├── customers/
│     ├── __init__.py/
│     ├── routes.py/
│     └── schemas.py/
│   ├── mechanics/
│     ├── __init__.py/
│     ├── routes.py/
│     └── schemas.py/
│   └── service_tickets/
│     ├── __init__.py/
│     ├── routes.py/
│     └── schemas.py/
│   └── inventory/
│     ├── __init__.py/
│     ├── routes.py/
│     └── schemas.py/
│
├── utils/
│   └── util.py/
│
├── __init__.py
├── extensions.py
└── models.py
│
├── app.py
└── config.py
```

The application follows the **Application Factory Pattern**, providing a clean, modular, and scalable structure through the use of Blueprints. 

---

## 📋 API Endpoints

### Customers

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /customers/login | Customer login |
| POST | /customers | Create a customer |
| GET | /customers | Retrieve all customers (pagination supported) |
| GET | /customers/<customer_id> | Retrieve one customer |
| PUT | /customers/<customer_id>update-account | Update customer account (JWT Protected) |
| DELETE | /customers/<customer_id> | Delete customer account (JWT Protected) |
| GET | /customers/<customer_id>/my-service-tickets | Retrieve customer's service tickets (JWT Protected) |

### Mechanics

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /mechanics | Mechanic login |
| POST | /mechanics | Create mechanic |
| GET | /mechanics | Retrieve all mechanics |
| PUT | /mechanics/<mechanic_id> | Update mechanic |
| DELETE | /mechanics/<mechanic_id> | Delete mechanic |
| GET | /mechanics/most-tickets | Mechanics ranked by completed service tickets|

### Service Tickets

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /service-tickets | Create service ticket (JWT Protected) |
| GET | /service-tickets | Retrieve all service tickets (JWT Protected) |
| PUT | /service-tickets/<service_ticket_id>/assign-mechanic/<mechanic_id> | Assign mechanic (JWT Protected) |
| PUT | /service-tickets/<service_ticket_id>/remove-mechanic/<mechanic_id> | Remove mechanic (JWT Protected) |
| PUT | /service-tickets/<service_ticket_id>/edit-mechanics | Add and remove multiple mechanics (JWT Protected) |
| PUT | /service-tickets/<service_ticket_id>/add-part/<inventory_item_id> | Add inventory part to service ticket (JWT Protected) |

### Inventory

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /inventory | Create inventory item (JWT Protected) |
| GET | /inventory | Retrieve all inventory items (JWT Protected) |
| PUT | /inventory/<inventory_item_id> | Update inventory item (JWT Protected) |
| DELETE | /inventory/<inventory_item_id> | Delete inventory item (JWT Protected) |

---

## 🔐 Authentication

JWT authentication is used to secure protected endpoints. 

After logging in as either a customer or mechanic, a JWT token is returned. This token must be included in the Authorization header when accessing protected routes. 

Example:

`Authorization: Bearer <your_token_here>`

Protected customer endpoints allow customers to update or delete only their own accounts and to view only their own service tickets.

Protected mechanic endpoints require a valid mechanic token before allowing modifications to service tickets or inventory.

---

## 📖 API Documentation

Interactive API documentation is provided using **Swagger (OpenAPI)**.

Swagger documentation includes:

- Endpoint descriptions
- Request parameters
- Request body schemas
- Response examples
- Authentication requirements
- Error responses

After running the application, the documentation can be viewed by navigating to:

```http://localhost:5000/api/docs/```

---

## ✅ Error Handling

The API includes validation and error handling for:

- Invalid request data
- Missing resources (404)
- Validation errors (400)
- Authentication failures (403)
- Resource not found (404)
- Duplicate mechanic assignments
- Duplicate inventory assignments
- Invalid customer IDs
- Duplicate customer and mechanic email addresses

---

## 🧪 Testing

This project includes both **manual** and **automated** testing.

### Manual Testing

API endpoints were tested using **Postman** to verify:

- Customer authentication
- Mechanic authentication
- Customer CRUD operations
- Mechanic CRUD operations
- Inventory CRUD operations
- Service ticket operations
- Protected endpoints
- Pagination
- Error handling

### Automated Testing

Automated unit tests were written using Python's **unittest** framework.

The test suite covers:

- Customer routes
- Mechanic routes
- Inventory routes
- Service Ticket routes
- Successful requests
- Validation errors
- Authentication failures
- Authorization checks
- Resource not found responses
- Advanced endpoints
- Inventory assignment
- Mechanic assignment

Run the test suite with:

```bash
python -m unittest discover tests
```

---

## ⚡ Performance & Security

This API includes several features to improve security and performance:

- JWT Authentication
- Customer and Mechanic authorization
- Flask-Limiter rate limiting
- Flask-Caching for frequently accessed GET endpoints
- Input validation with Marshmallow
- SQLAlchemy ORM relationships

---

## ▶️ Running the Project

Clone the repository:

```bash
git clone [https://github.com/sepudjowargono/Mechanic_Shop.git]
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
flask run
```

---

## 👨‍💻 Author

Stephana Pudjowargono

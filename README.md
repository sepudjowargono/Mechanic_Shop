# 🔧 Mechanic Shop API

A RESTful API built with **Flask**, **SQLAlchemy**, **Marshmallow**, and **MySQL** using the **Application Factory Pattern**. This project simulates a mechanic shop management system by allowing users to manage customers, mechanics, service tickets, and the relationships between mechanics and service tickets.

---

## 📚 Features

### 👤 Customer Management
- Create a customer
- Retrieve all customers
- Retrieve a single customer
- Update customer information
- Delete a customer

### 🔧 Mechanic Management
- Create a mechanic
- Retrieve all mechanics
- Update mechanic information
- Delete a mechanic

### 🚗 Service Ticket Management
- Create a service ticket
- Retrieve all service tickets
- Assign mechanics to service tickets
- Remove mechanics from service tickets

---

## 🛠 Technologies Used

- Python
- Flask
- SQLAlchemy
- Marshmallow
- MySQL
- Flask-SQLAlchemy
- Flask-Marshmallow
- MySQL Connector
- Postman

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
│
├── __init__.py
├── extensions.py
└── models.py
│
├── app.py
└── config.py
```

The application follows the **Application Factory Pattern** to keep the project modular and scalable.

---

## 📋 API Endpoints

### Customers

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /customers | Create a customer |
| GET | /customers | Get all customers |
| GET | /customers/<customer_id> | Get one customer |
| PUT | /customers/<customer_id> | Update customer |
| DELETE | /customers/<customer_id> | Delete customer |

### Mechanics

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /mechanics | Create mechanic |
| GET | /mechanics | Get all mechanics |
| PUT | /mechanics/<mechanic_id> | Update mechanic |
| DELETE | /mechanics/<mechanic_id> | Delete mechanic |

### Service Tickets

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /service-tickets | Create service ticket |
| GET | /service-tickets | Retrieve all service tickets |
| PUT | /service-tickets/<service_ticket_id>/assign-mechanic/<mechanic_id> | Assign mechanic |
| PUT | /service-tickets/<service_ticket_id>/remove-mechanic/<mechanic_id> | Remove mechanic |

---

## ✅ Error Handling

The API includes validation and error handling for:

- Invalid request data
- Missing resources (404)
- Validation errors (400)
- Duplicate mechanic assignments
- Removing mechanics that are not assigned
- Invalid customer IDs when creating service tickets

---

## 🧪 Testing

All API endpoints were tested using **Postman**.

The Postman collection included with this project demonstrates:

- Customer CRUD operations
- Mechanic CRUD operations
- Service Ticket creation
- Assigning mechanics
- Removing mechanics
- Error handling

---

## ▶️ Running the Project

Clone the repository:

```bash
git clone <repository-url>
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

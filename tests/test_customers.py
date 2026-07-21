from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        
            self.customer = Customer(
                name="test_user",
                email="test@email.com",
                phone="123-456-7890",
                password="testtesttest"
            )
        
            db.session.add(self.customer)
            db.session.commit()
        
            self.customer_id = self.customer.id
            self.token = encode_token(self.customer.id)
    
    def test_create_customer(self):
        customer_payload = {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "987-654-3210",
            "password": "anothersecurepassword"
        }
        
        response = self.client.post(
            "/customers/", 
            json=customer_payload
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["name"], "John Smith")
        self.assertEqual(data["email"], "john.smith@example.com")
        self.assertEqual(data["phone"], "987-654-3210")
        
    def test_invalid_customer_creation(self):
        customer_payload = {
            "name": "John Smith",
            "phone": "987-654-3210",
            "password": "anothersecurepassword"
        }

        response = self.client.post(
            "/customers/", 
            json=customer_payload
        )
        
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["email"], ["Missing data for required field."])
        
    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "testtesttest"
        }

        response = self.client.post(
            "/customers/login",
            json=credentials
        )

        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["message"], "Login successful")
        self.assertIn("token", data)
        self.assertIsInstance(data["token"], str)
    
    def test_invalid_login(self):
        credentials = {
            "email": "wrong@email.com",
            "password": "wrongpassword"
        }
        
        response = self.client.post(
            "/customers/login",
            json=credentials
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["error"], "Invalid email or password")
        
    def test_get_all_customers(self):
        response = self.client.get(
            "/customers/",
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
    
    def test_get_customer_by_id(self):
        response = self.client.get(
            f"/customers/{self.customer_id}",
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], "test_user")
        
    def test_get_customer_not_found(self):
        response = self.client.get(
            "/customers/9999",
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Customer not found")
    
    def test_update_customer(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        update_payload = {
            "name": "Updated Name",
            "email": "updated@email.com"
        }

        response = self.client.put(
            f"/customers/{self.customer_id}/update-account",
            headers=headers,
            json=update_payload
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], "Updated Name")
        self.assertEqual(data["email"], "updated@email.com")
        
    def test_update_customer_unauthorized(self):
        response = self.client.put(
            f"/customers/{self.customer_id}/update-account",
            json={"name": "Updated Name"}
        )
        
        self.assertIn(response.status_code, [401, 403])
    
    def test_delete_customer(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = self.client.delete(
            f"/customers/{self.customer_id}/delete-account",
            headers=headers
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], f'Customer Id: {self.customer_id} has been deleted successfully')
        
        with self.app.app_context():
            deleted_customer = db.session.get(Customer, self.customer_id)
            self.assertIsNone(deleted_customer)
            
    def test_delete_customer_unauthorized(self):
        response = self.client.delete(
            f"/customers/{self.customer_id}/delete-account"
        )
        
        self.assertIn(response.status_code, [401, 403])
        
    def test_get_customer_service_tickets(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = self.client.get(
            f"/customers/{self.customer_id}/my-service-tickets",
            headers=headers
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
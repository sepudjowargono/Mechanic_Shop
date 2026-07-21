from app import create_app
from app.models import db, Mechanic
from app.utils.util import encode_mechanic_token
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        
            self.mechanic = Mechanic(
                name="test_mechanic",
                email="test_mechanic@email.com",
                phone="123-456-7890",
                salary=50000.00,
                password="testpassword"
            )
            
            db.session.add(self.mechanic)
            db.session.commit()
            
            self.mechanic_id = self.mechanic.id
            self.token = encode_mechanic_token(self.mechanic.id)
            
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "987-654-3210",
            "salary": "60000.00",
            "password": "securepassword"
        }
        
        response = self.client.post(
            "/mechanics/",
            json=mechanic_payload
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["email"], "john.doe@email.com")
        self.assertEqual(data["phone"], "987-654-3210")
        self.assertEqual(data["salary"], "60000.00")
        self.assertEqual(data["password"], "securepassword")
    
    def test_invalid_mechanic_creation(self):
        mechanic_payload = {
            "name": "John Doe",
            "phone": "987-654-3210",
            "salary": "60000.00",
            "password": "securepassword"
        }
        
        response = self.client.post(
            "/mechanics/",
            json=mechanic_payload
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["email"],["Missing data for required field."])
        
    def test_login_mechanic(self):
        credentials = {
            "email": "test_mechanic@email.com",
            "password": "testpassword"
        }
        
        response = self.client.post(
            "/mechanics/login",
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
            "email": "invalid@email.com",
            "password": "invalidpassword"
        }
        
        response = self.client.post(
            "/mechanics/login",
            json=credentials
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["error"], "Invalid email or password")
        
    def test_get_all_mechanics(self):
        response = self.client.get(
            "/mechanics/",
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        
    def test_update_mechanic(self):
        update_payload = {
            "name": "Updated Mechanic",
            "email": "updated.mechanic@email.com",
            "phone": "987-654-3210",
            "salary": "50000.00",
        }

        response = self.client.put(
            f"/mechanics/{self.mechanic_id}",
            json=update_payload
        )

        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], "Updated Mechanic")
        self.assertEqual(data["email"], "updated.mechanic@email.com")
        
    def test_update_mechanic_invalid(self):
        response = self.client.put(
            "/mechanics/9999",
            json={"name": "Non-existent Mechanic"}
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Mechanic not found.")
        
    def test_delete_mechanic(self):
        response = self.client.delete(
            f"/mechanics/{self.mechanic_id}"
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], f"Mechanic Id: {self.mechanic_id} has been deleted successfully")
        self.assertEqual(data["status"], "success")
    
    def test_delete_mechanic_not_found(self):
        response = self.client.delete(
            "/mechanics/9999"
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Mechanic not found.")
        
    def test_most_tickets_worded(self):
        response = self.client.get(
            "/mechanics/most-tickets"
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
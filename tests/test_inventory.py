from app import create_app
from app.models import db, Inventory, Mechanic
from app.utils.util import encode_mechanic_token
import unittest

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        
            self.mechanic = Mechanic(
                name="John Doe",
                email="john@example.com",
                phone="123-456-7890",
                salary="50000",
                password="password"
            )
            
            self.inventory = Inventory(
                part_name="Brake Pad",
                price="50.00"
            )
            
            db.session.add(self.mechanic)
            db.session.add(self.inventory)
            db.session.commit()
            
            self.inventory_id = self.inventory.id
            self.token = encode_mechanic_token(self.mechanic.id)
            
    def test_create_inventory(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        inventory_payload = {
            "part_name": "Oil Filter",
            "price": "15.00"
        }
        
        response = self.client.post(
            "/inventory/", 
            json=inventory_payload,
            headers=headers
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["part_name"], "Oil Filter")
        self.assertEqual(data["price"], "15.00")
        
    def test_existing_inventory_creation(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        inventory_payload = {
            "part_name": "Brake Pad",
            "price": "50.00"
        }
        
        response = self.client.post(
            "/inventory/", 
            json=inventory_payload,
            headers=headers
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Inventory item already exists.")
        
    def test_get_all_inventory(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = self.client.get(
            "/inventory/",
            headers=headers
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        
    def test_update_inventory(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        inventory_payload = {
            "part_name": "Updated Inventory Name",
            "price": "75.00"
        }

        response = self.client.put(
            f"/inventory/{self.inventory_id}",
            json=inventory_payload,
            headers=headers
        )

        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data)
        self.assertEqual(data["part_name"], "Updated Inventory Name")
        self.assertEqual(data["price"], "75.00")
        
    def test_update_inventory_not_found(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = self.client.put(
            "/inventory/9999",  # Assuming 9999 is a non-existent ID
            json={
                "part_name": "Non-existent Inventory",
                "price": "100.00"
            },
            headers=headers
        )

        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Inventory item not found.")
        
    def test_delete_inventory(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = self.client.delete(
            f"/inventory/{self.inventory_id}",
            headers=headers
        )

        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], f'Inventory item {self.inventory.part_name} has been deleted successfully')
        self.assertEqual(data["status"], "success")
        
    def test_delete_inventory_not_found(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = self.client.delete(
            "/inventory/9999",  # Assuming 9999 is a non-existent ID
            headers=headers
        )

        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Inventory item not found.")
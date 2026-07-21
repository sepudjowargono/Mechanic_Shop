from app import create_app
from app.models import (
    db,
    Customer,
    Mechanic,
    Service_Ticket,
    Inventory
)
from app.utils.util import encode_mechanic_token
from datetime import date
from decimal import Decimal
import unittest

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.customer = Customer(
                name="Test Customer",
                email="test.customer@email.com",
                phone="123-456-7890",
                password="passwordtestest"
            )
            
            self.mechanic = Mechanic(
                name="Test Mechanic",
                email="test.mechanic@email.com",
                phone="098-765-4321",
                salary=Decimal("50000.00"),
                password="testpassword"
            )
            
            self.second_mechanic = Mechanic(
                name="Second Mechanic",
                email="second.mechanic@email.com",
                phone="111-222-3333",
                salary=Decimal("60000.00"),
                password="secondpassword"
            )
            
            self.inventory_item = Inventory(
                part_name="Test Part",
                price=Decimal("100.00")
            )
            
            db.session.add(self.customer)
            db.session.add(self.mechanic)
            db.session.add(self.second_mechanic)
            db.session.add(self.inventory_item)
            db.session.commit()
            
            self.service_ticket = Service_Ticket(
                vin="1HGCM82633A123456",
                service_date=date(2026, 7, 20),
                service_desc="Test service description",
                customer_id=self.customer.id
            )
            
            db.session.add(self.service_ticket)
            db.session.commit()
            
            self.customer_id = self.customer.id
            self.mechanic_id = self.mechanic.id
            self.second_mechanic_id = self.second_mechanic.id
            self.inventory_item_id = self.inventory_item.id
            self.service_ticket_id = self.service_ticket.id
            
            self.token = encode_mechanic_token(self.mechanic_id)
            
    def test_create_service_ticket(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        service_ticket_payload = {
            "vin": "1HGCM82633A654321",
            "service_date": "2026-07-21",
            "service_desc": "Oil change and tire rotation",
            "customer_id": self.customer_id
        }
        
        response = self.client.post(
            "/service_tickets/",
            json=service_ticket_payload,
            headers=header
        )
            
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(data)
        self.assertEqual(data["vin"], "1HGCM82633A654321")
        self.assertEqual(data["service_date"], "2026-07-21")
        self.assertEqual(data["service_desc"], "Oil change and tire rotation")
        self.assertEqual(data["customer_id"], self.customer_id)
            
    def test_invalid_create_service_ticket(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        service_ticket_payload = {
            "service_date": "2026-07-21",
            "service_desc": "Oil change and tire rotation",
            "customer_id": self.customer_id
        }
        
        response = self.client.post(
            "/service_tickets/",
            json=service_ticket_payload,
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("vin", data)
        
    def test_customer_not_found_create_service_ticket(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        service_ticket_payload = {
            "vin": "1HGCM82633A654321",
            "service_date": "2026-07-21",
            "service_desc": "Oil change and tire rotation",
            "customer_id": 9999
        }
        
        response = self.client.post(
            "/service_tickets/",
            json=service_ticket_payload,
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Customer not found")
        
    def test_get_all_service_tickets(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.get(
            "/service_tickets/",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        
    def test_assign_mechanic_to_service_ticket(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{self.second_mechanic_id}",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", data)
        self.assertIn("current_assigned_mechanics", data)
        self.assertIn(self.second_mechanic_id, data["current_assigned_mechanics"])
        
    def test_assign_mechanic_service_ticket_not_found(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.put(
            f"/service_tickets/9999/assign-mechanic/{self.second_mechanic_id}",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Service ticket not found")
        
    def test_remove_mechanic_from_service_ticket(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        assign_response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{self.second_mechanic_id}",
            headers=header
        )
        
        self.assertEqual(assign_response.status_code, 200)
        
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/remove-mechanic/{self.second_mechanic_id}",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", data)
        self.assertIn("current_assigned_mechanics", data)
        self.assertNotIn(self.second_mechanic_id, data["current_assigned_mechanics"])
        
    def test_remove_mechanic_not_assigned(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/remove-mechanic/{self.second_mechanic_id}",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Mechanic is not assigned to this service ticket")
        
    def test_remove_mechanic_service_ticket_not_found(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.put(
            f"/service_tickets/9999/remove-mechanic/{self.second_mechanic_id}",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Service ticket not found")
        
    def test_edit_ticket_mechanics(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        assign_response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{self.second_mechanic_id}",
            headers=header
        )
        
        self.assertEqual(assign_response.status_code, 200)
        
        edit_payload = {
            "add_mechanic_ids": [self.mechanic_id],
            "remove_mechanic_ids": [self.second_mechanic_id]
        }
        
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/edit-mechanics",
            json=edit_payload,
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", data)
        self.assertIn("current_assigned_mechanics", data)
        self.assertIn(self.mechanic_id, data["current_assigned_mechanics"])
        self.assertNotIn(self.second_mechanic_id, data["current_assigned_mechanics"])
        
    def test_edit_ticket_service_ticket_not_found(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        edit_payload = {
            "add_mechanic_ids": [self.mechanic_id],
            "remove_mechanic_ids": [self.second_mechanic_id]
        }
        
        response = self.client.put(
            f"/service_tickets/9999/edit-mechanics",
            json=edit_payload,
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Service ticket not found.")
        
    def test_add_part_to_service_ticket(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/add-part/{self.inventory_item_id}",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            data["message"],
            (
                f"Part {self.inventory_item_id} added to service "
                f"ticket {self.service_ticket_id} successfully."
            )
        )
        self.assertIn(
            self.inventory_item_id,
            data["current_assigned_parts"]
        )
        
    def test_add_part_service_ticket_not_found(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.put(
            f"/service_tickets/9999/add-part/{self.inventory_item_id}",
            headers=header
        )
        
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Service ticket not found")
        
    def test_add_part_already_assigned(self):
        header = {"Authorization": f"Bearer {self.token}"}
        
        response1 = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/add-part/{self.inventory_item_id}",
            headers=header
        )
        
        self.assertEqual(response1.status_code, 200)
        
        response2 = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/add-part/{self.inventory_item_id}",
            headers=header
        )
        
        data = response2.get_json()
        
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(
            data["message"],
            (
                "Inventory item is already assigned to this "
                "service ticket."
            )
        )
        self.assertIn(
            self.inventory_item_id,
            data["current_assigned_parts"]
        )
        
    def test_create_service_ticket_without_token(self):
        service_ticket_payload = {
            "vin": "1HGCM82633A654321",
            "service_date": "2026-07-21",
            "service_desc": "Oil change and tire rotation",
            "customer_id": self.customer_id
        }
        
        response = self.client.post(
            "/service_tickets/",
            json=service_ticket_payload
        )
        
        data = response.get_json()
        
        self.assertIn(response.status_code, [401, 403])
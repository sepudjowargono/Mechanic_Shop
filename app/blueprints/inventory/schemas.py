from marshmallow import fields

from app.extensions import ma
from app.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_relationships = True
        load_instance = True 
        
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
inventory_update_schema = InventorySchema(load_instance=False) # This schema is used for updates, allowing partial updates without loading into an instance.

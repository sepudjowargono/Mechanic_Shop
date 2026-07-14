from app.extensions import ma
from app.models import Service_Ticket
from marshmallow import fields

class Service_TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Ticket
        include_fk = True
        include_relationships = True
        load_instance = True
        
    customer = fields.Nested('CustomerSchema', only=('name', 'email'))
        
class EditTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Integer(), required=False)
    remove_mechanic_ids = fields.List(fields.Integer(), required=False)
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")
                
service_ticket_schema = Service_TicketSchema()
service_tickets_schema = Service_TicketSchema(many=True)
edit_ticket_schema = EditTicketSchema()
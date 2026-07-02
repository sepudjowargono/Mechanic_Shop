from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date
from typing import List
from decimal import Decimal

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class= Base)

service_mechanic = db.Table(
    'service_mechanics',
    Base.metadata,
    db.Column('service_ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    password: Mapped[str] = mapped_column(db.String(200), nullable=False)
    
    service_tickets: Mapped[List['Service_Ticket']] = relationship(back_populates='customer')
    
class Service_Ticket(Base):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(800), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))
    
    customer: Mapped['Customer'] = relationship(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanic']] = relationship(secondary='service_mechanics', back_populates='service_tickets')

class Mechanic(Base):
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    salary: Mapped[Decimal] = mapped_column(db.Numeric(10,2), nullable=False)
    
    service_tickets: Mapped[List['Service_Ticket']] = relationship(secondary='service_mechanics', back_populates='mechanics')
    
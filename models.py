
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

'modelos de la base de datos: Company y Email'
class Company(Base):
    __tablename__ = "companies"
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    client_id = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación: Una empresa tiene muchos emails
    emails = relationship("Email", back_populates="company")
    
    def __repr__(self):
        return f"<Company(name={self.name}, client_id={self.client_id})>"

'Modelo para la tabla de Emails'
class Email(Base):
    __tablename__ = "emails"
    
    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String(200), nullable=False, index=True)
    sender = Column(String(200), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Llave foránea: Relaciona el email con una empresa
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Código único del proveedor SMTP
    smtp_code = Column(String(200), unique=True, nullable=False, index=True)
    
    # Contenido del correo (puede ser muy largo)
    content = Column(Text, nullable=False)
    
    # Fecha de creación del registro
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación: Un email pertenece a una empresa
    company = relationship("Company", back_populates="emails")
    
    def __repr__(self):
        return f"<Email(smtp_code={self.smtp_code}, sender={self.sender})>"
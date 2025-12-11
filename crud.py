
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import models
import schemas
from typing import List, Optional
from datetime import datetime
import math


# ============== lOGICA DE NEGOCIO ===============
'crear empresa ,datos de empresa y empresq creada'
def create_company(db: Session, company: schemas.CompanyCreate):
    db_company = models.Company(
        name=company.name,
        client_id=company.client_id
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

'buscar empresa por nombre, retorna empresa o None'
def get_company_by_name(db: Session, name: str):
    return db.query(models.Company).filter(models.Company.name == name).first()

'listar todas las empresas con paginacion'
def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Company).offset(skip).limit(limit).all()


# ============== OPERACIONES DE EMAILS ==============
'crear email , datos de email y id de empresa emisora'
def create_email(db: Session, email: schemas.EmailCreate, company_id: int):
    db_email = models.Email(
        recipient=email.recipient,
        sender=email.sender,
        date=email.date,
        company_id=company_id,
        smtp_code=email.smtp_code,
        content=email.content
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

'buscar email por codigo smtp, retorna email o None'
def get_email_by_smtp_code(db: Session, smtp_code: str):
    return db.query(models.Email).filter(models.Email.smtp_code == smtp_code).first()


def search_emails(
    db: Session,
    content: str,
    recipient: Optional[str] = None,
    sender: Optional[str] = None,
    company_name: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 10
):
    """Busca emails con filtros múltiples y paginación"""
    # Query base: unir emails con companies
    query = db.query(models.Email).join(models.Company)
    
    # FILTRO OBLIGATORIO: Contenido
    # Busca el texto en cualquier parte del contenido
    query = query.filter(models.Email.content.contains(content))
    
    # FILTROS OPCIONALES
    if recipient:
        query = query.filter(models.Email.recipient.contains(recipient))
    
    if sender:
        query = query.filter(models.Email.sender.contains(sender))
    
    if company_name:
        query = query.filter(models.Company.name.contains(company_name))
    
    if date_from:
        query = query.filter(models.Email.date >= date_from)
    
    if date_to:
        query = query.filter(models.Email.date <= date_to)
    
    # Contar total de resultados
    total = query.count()
    
    # Calcular paginación
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size
    
    # Obtener emails de la página actual
    emails = query.offset(skip).limit(page_size).all()
    
    # Convertir a formato de respuesta con nombre de empresa
    email_responses = []
    for email in emails:
        email_dict = {
            "id": email.id,
            "recipient": email.recipient,
            "sender": email.sender,
            "date": email.date,
            "company_name": email.company.name,  
            "smtp_code": email.smtp_code,
            "content": email.content,
            "created_at": email.created_at
        }
        email_responses.append(schemas.EmailResponse(**email_dict))
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "emails": email_responses
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, models
from database import get_db
import math

router = APIRouter()

@router.post("/api/emails/bulk", response_model=schemas.EmailBulkResponse, status_code=201)
def create_bulk_emails(bulk_data: schemas.EmailBulkCreate, db: Session = Depends(get_db)):
    """Registra múltiples emails de forma masiva"""
    success = 0
    failed = 0
    errors = []
    
    for i, email_data in enumerate(bulk_data.emails):
        try:
            # 1. Buscar empresa por nombre
            empresa = db.query(models.Company).filter(
                models.Company.name == email_data.company_name
            ).first()
            
            if not empresa:
                errors.append({
                    "indice": i,
                    "smtp_code": email_data.smtp_code,
                    "error": f"Empresa no parametrizada: {email_data.company_name}"
                })
                failed += 1
                continue
            
            # 2. Verificar que smtp_code no exista
            existe = db.query(models.Email).filter(
                models.Email.smtp_code == email_data.smtp_code
            ).first()
            
            if existe:
                errors.append({
                    "indice": i,
                    "smtp_code": email_data.smtp_code,
                    "error": "Código SMTP duplicado"
                })
                failed += 1
                continue
            
            # 3. Crear el email
            nuevo_email = models.Email(
                recipient=email_data.recipient,
                sender=email_data.sender,
                date=email_data.date,
                company_id=empresa.id,
                smtp_code=email_data.smtp_code,
                content=email_data.content
            )
            
            db.add(nuevo_email)
            db.commit()  # ← CRÍTICO: esto guarda en la BD
            db.refresh(nuevo_email)  # Obtiene el ID generado
            success += 1
            
        except Exception as e:
            db.rollback()
            errors.append({
                "indice": i,
                "smtp_code": email_data.smtp_code,
                "error": str(e)
            })
            failed += 1
    
    return {
        "success": success,
        "failed": failed,
        "errors": errors
    }

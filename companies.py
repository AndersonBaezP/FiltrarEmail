"""
Endpoints para manejar empresas (catálogo)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, models
from database import get_db

router = APIRouter()


@router.post("/api/companies", response_model=schemas.CompanyResponse, status_code=201)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
  
    # Verificar si ya existe
    exists = db.query(models.Company).filter(models.Company.name == company.name).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"La empresa '{company.name}' ya existe")
    
    # Crear nueva empresa
    new_company = models.Company(
        name=company.name,
        client_id=company.client_id
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    return new_company


@router.get("/api/companies", response_model=List[schemas.CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    """
    Lista todas las empresas registradas en el catálogo
    """
    companies = db.query(models.Company).all()
    return companies


from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import emails
import companies
import models
import schemas
import crud
from database import engine, get_db


'Archivo principal de la aplicación FastAPI'
# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Email Filter API",
    description="API para registrar y buscar emails de forma masiva",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(companies.router)
app.include_router(emails.router)

# ============== ENDPOINTS DE COMPANIES ==============
'Registrar nueva empresa en el catálogo'
@app.post("/api/companies", response_model=schemas.CompanyResponse, status_code=201)
def create_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    # Verificar si la empresa ya existe
    db_company = crud.get_company_by_name(db, name=company.name)
    if db_company:
        raise HTTPException(
            status_code=400,
            detail=f"Company '{company.name}' already exists"
        )
    
    # Crear la empresa
    return crud.create_company(db=db, company=company)


'Listar todas las empresas con paginación'
@app.get("/api/companies", response_model=List[schemas.CompanyResponse])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    companies = crud.get_companies(db, skip=skip, limit=limit)
    return companies


# ============== ENDPOINTS DE EMAILS ==============
'Registrar múltiples emails de forma masiva'
@app.post("/api/emails/bulk", response_model=schemas.EmailBulkResponse, status_code=201)
def create_emails_bulk(
    bulk_data: schemas.EmailBulkCreate,
    db: Session = Depends(get_db)
):
    success_count = 0
    failed_count = 0
    errors = []
    
    # Procesar cada email
    for email_data in bulk_data.emails:
        try:
            # 1. Verificar que la empresa existe
            company = crud.get_company_by_name(db, name=email_data.company_name)
            if not company:
                raise ValueError(f"Company '{email_data.company_name}' not found in catalog")
            
            # 2. Verificar que el smtp_code no esté duplicado
            existing_email = crud.get_email_by_smtp_code(db, smtp_code=email_data.smtp_code)
            if existing_email:
                raise ValueError(f"Email with smtp_code '{email_data.smtp_code}' already exists")
            
            # 3. Crear el email
            crud.create_email(db=db, email=email_data, company_id=company.id)
            success_count += 1
            
        except ValueError as e:
            # Error de validación de negocio
            failed_count += 1
            errors.append({
                "smtp_code": email_data.smtp_code,
                "sender": email_data.sender,
                "error": str(e)
            })
        except Exception as e:
            # Error inesperado
            failed_count += 1
            errors.append({
                "smtp_code": email_data.smtp_code,
                "sender": email_data.sender,
                "error": f"Unexpected error: {str(e)}"
            })
    
    # Si todos fallaron, devolver error 400
    if failed_count > 0 and success_count == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "All emails failed to register",
                "success": success_count,
                "failed": failed_count,
                "errors": errors
            }
        )
    
    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors
    }

'Buscar emails con filtros múltiples y paginación'
@app.get("/api/emails/search", response_model=schemas.EmailSearchResponse)
def search_emails(
    content: str = Query(..., description="Texto a buscar en el contenido del email (OBLIGATORIO)"),
    recipient: Optional[str] = Query(None, description="Filtrar por destinatario (opcional)"),
    sender: Optional[str] = Query(None, description="Filtrar por emisor (opcional)"),
    company_name: Optional[str] = Query(None, description="Filtrar por nombre de empresa (opcional)"),
    date_from: Optional[datetime] = Query(None, description="Filtrar desde fecha (opcional, formato: 2024-12-01T10:30:00)"),
    date_to: Optional[datetime] = Query(None, description="Filtrar hasta fecha (opcional, formato: 2024-12-01T23:59:59)"),
    page: int = Query(1, ge=1, description="Número de página (mínimo 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Cantidad de emails por página (máximo 100)"),
    db: Session = Depends(get_db)
):
    
    # Validar que content no esté vacío
    if not content or content.strip() == "":
        # Según requisitos: sin filtros = lista vacía
        return {
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "emails": []
        }
    
    # Realizar búsqueda
    result = crud.search_emails(
        db=db,
        content=content,
        recipient=recipient,
        sender=sender,
        company_name=company_name,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size
    )
    
    return result


# ============== ENDPOINT DE SALUD ==============
'Verificar el estado de salud de la API'
@app.get("/")
def root():
    return {
        "message": "Email Filter API is running",
        "version": "1.0.0",
        "endpoints": {
            "companies": "/api/companies",
            "bulk_emails": "/api/emails/bulk",
            "search_emails": "/api/emails/search",
            "docs": "/docs"
        }
    }

'Verificar el estado de salud de la API'
@app.get("/health")
def health_check():
    return {"status": "healthy"}
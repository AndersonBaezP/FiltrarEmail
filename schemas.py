
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List, Optional


# ============== ESQUEMAS PARA COMPANIES ==============
'definimos los esquemas para las empresas de entrada y salida de la API'
'esquema para CREAR una nueva empresa'
class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Nombre de la empresa")
    client_id: str = Field(..., min_length=1, max_length=100, description="ID del cliente")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Google Inc",
                "client_id": "cliente_001"
            }
        }

'esquema para RESPONDER con datos de una empresa lo que la API devuelve'
class CompanyResponse(BaseModel):
    id: int
    name: str
    client_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== ESQUEMAS PARA EMAILS ==============
'Esquema para CREAR un email individual parte del registro masivo'
class EmailCreate(BaseModel):
    recipient: str = Field(..., min_length=1, max_length=200, description="Email del destinatario")
    sender: str = Field(..., min_length=1, max_length=200, description="Email del emisor")
    date: datetime = Field(..., description="Fecha del correo")
    company_name: str = Field(..., min_length=1, max_length=200, description="Nombre de la empresa emisora")
    smtp_code: str = Field(..., min_length=1, max_length=200, description="Código único SMTP")
    content: str = Field(..., min_length=1, description="Contenido del correo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipient": "juan@example.com",
                "sender": "maria@google.com",
                "date": "2024-12-01T10:30:00",
                "company_name": "Google Inc",
                "smtp_code": "SMTP-001-XYZ",
                "content": "Hola, este es un correo de prueba"
            }
        }

'Esquema para registro MASIVO de emails contiene una lista de emails'
class EmailBulkCreate(BaseModel):
    emails: List[EmailCreate] = Field(..., min_length=1, description="Lista de emails a registrar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "emails": [
                    {
                        "recipient": "juan@example.com",
                        "sender": "maria@google.com",
                        "date": "2024-12-01T10:30:00",
                        "company_name": "Google Inc",
                        "smtp_code": "SMTP-001-XYZ",
                        "content": "Correo de ejemplo"
                    }
                ]
            }
        }

'Esquema para RESPONDER con datos de un email'
class EmailResponse(BaseModel):
    id: int
    recipient: str
    sender: str
    date: datetime
    company_name: str  # Nombre de la empresa (no el ID)
    smtp_code: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

'Esquema para RESPONDER con datos de un email Indica cuántos se guardaron y cuáles fallaron'
class EmailBulkResponse(BaseModel):
    success: int = Field(..., description="Cantidad de emails guardados exitosamente")
    failed: int = Field(..., description="Cantidad de emails que fallaron")
    errors: List[dict] = Field(default=[], description="Lista de errores ocurridos")


# ============== ESQUEMAS PARA BÚSQUEDA ==============
'respuesta de la búsqueda con paginación'
class EmailSearchResponse(BaseModel):
    total: int = Field(..., description="Total de emails encontrados")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Cantidad de emails por página")
    total_pages: int = Field(..., description="Total de páginas disponibles")
    emails: List[EmailResponse] = Field(..., description="Lista de emails en esta página")
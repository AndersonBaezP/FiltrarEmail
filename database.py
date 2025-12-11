
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

'Configuración de la base de datos SQLite'
# URL de conexión a SQLite
# El archivo se creará automáticamente en la carpeta del proyecto
SQLALCHEMY_DATABASE_URL = "sqlite:///./emails.db"

# Crear el motor de la base de datos
# check_same_thread: False permite usar SQLite con FastAPI (múltiples hilos)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Crear una sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
# Todos los modelos heredarán de esta clase
Base = declarative_base()


# Función para obtener una sesión de base de datos
# Se usa en cada endpoint para conectarse a la BD
def get_db():
    db = SessionLocal()
    try:
        yield db  
    finally:
        db.close() 
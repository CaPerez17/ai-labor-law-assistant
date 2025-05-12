from typing import Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

# Crear la clase base para los modelos
Base = declarative_base()

# Añadir propiedades comunes a la clase base
class CustomBase:
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() 
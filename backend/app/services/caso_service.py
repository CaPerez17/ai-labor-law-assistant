"""
Servicio para la gestión de casos
---------------------------------
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.caso import Caso
from app.models.usuario import Usuario
from app.schemas.caso import CasoCreate, CasoUpdate
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

class CasoService:
    """Servicio para manejar operaciones CRUD de casos"""

    def __init__(self, db: Session):
        self.db = db

    def create_caso(self, caso_data: CasoCreate, current_user: Usuario) -> Caso:
        """Crea un nuevo caso"""
        db_caso = Caso(
            titulo=caso_data.titulo,
            descripcion=caso_data.descripcion,
            nivel_riesgo=caso_data.nivel_riesgo,
            cliente_id=caso_data.cliente_id,
            abogado_id=caso_data.abogado_id
        )
        
        self.db.add(db_caso)
        self.db.commit()
        self.db.refresh(db_caso)
        
        logger.info(f"Caso creado: {db_caso.id} - {db_caso.titulo}")
        return db_caso

    def get_casos(self, current_user: Usuario, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtiene lista de casos según el rol del usuario"""
        query = self.db.query(Caso)
        
        # Filtrar casos según el rol del usuario
        if current_user.rol.value == "CLIENTE":
            query = query.filter(Caso.cliente_id == current_user.id)
        elif current_user.rol.value == "ABOGADO":
            query = query.filter(Caso.abogado_id == current_user.id)
        # ADMIN puede ver todos los casos
        
        return query.offset(skip).limit(limit).all()

    def get_caso(self, caso_id: int, current_user: Usuario) -> Optional[Caso]:
        """Obtiene un caso específico"""
        query = self.db.query(Caso).filter(Caso.id == caso_id)
        
        # Verificar permisos según el rol
        if current_user.rol.value == "CLIENTE":
            query = query.filter(Caso.cliente_id == current_user.id)
        elif current_user.rol.value == "ABOGADO":
            query = query.filter(Caso.abogado_id == current_user.id)
        # ADMIN puede ver cualquier caso
        
        return query.first()

    def update_caso(self, caso_id: int, caso_data: CasoUpdate, current_user: Usuario) -> Optional[Caso]:
        """Actualiza un caso existente"""
        caso = self.get_caso(caso_id, current_user)
        if not caso:
            return None
        
        # Actualizar campos si están presentes
        if caso_data.estado is not None:
            caso.estado = caso_data.estado
        if caso_data.comentarios is not None:
            caso.comentarios = caso_data.comentarios
        if caso_data.abogado_id is not None:
            caso.abogado_id = caso_data.abogado_id
        
        self.db.commit()
        self.db.refresh(caso)
        
        logger.info(f"Caso actualizado: {caso.id}")
        return caso

    def delete_caso(self, caso_id: int, current_user: Usuario) -> bool:
        """Elimina un caso"""
        caso = self.get_caso(caso_id, current_user)
        if not caso:
            return False
        
        # Solo ADMIN puede eliminar casos
        if current_user.rol.value != "ADMIN":
            return False
        
        self.db.delete(caso)
        self.db.commit()
        
        logger.info(f"Caso eliminado: {caso_id}")
        return True 
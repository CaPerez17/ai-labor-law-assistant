"""
Servicio de Autenticación
---------------------
Implementa la lógica para la autenticación y autorización de usuarios.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging

from app.models.usuario import Usuario, RolUsuario
from app.schemas.auth import UsuarioCreate, TokenData
from app.db.session import get_db
from app.core.security import get_password_hash, verify_password, SECRET_KEY, ALGORITHM

# Configuración de seguridad
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurar logger
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class AuthService:
    """Servicio para manejar la autenticación y autorización"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña coincide con el hash"""
        return verify_password(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera el hash de la contraseña"""
        return get_password_hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> Usuario:
        """Obtiene el usuario actual basado en el token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Intentar decodificar el token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            logger.debug(f"Token decodificado: {payload}")
            
            # El token puede contener 'sub' como ID numérico o como correo electrónico
            user_id = payload.get("sub")
            
            if user_id is None:
                logger.error("Token sin 'sub' encontrado")
                raise credentials_exception
                
            # Determinar si 'sub' es un ID numérico o un correo
            if isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()):
                # Es un ID numérico
                logger.debug(f"Buscando usuario por ID: {user_id}")
                user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
            else:
                # Es un correo electrónico
                logger.debug(f"Buscando usuario por email: {user_id}")
                user = db.query(Usuario).filter(Usuario.email == user_id).first()
            
            if user is None:
                logger.error(f"Usuario no encontrado para el token: {user_id}")
                raise credentials_exception
                
            logger.debug(f"Usuario encontrado: {user.email} (ID: {user.id})")
            return user
            
        except JWTError as e:
            logger.error(f"Error al decodificar token JWT: {str(e)}")
            raise credentials_exception

    @staticmethod
    def get_current_active_user(
        current_user: Usuario = Depends(get_current_user)
    ) -> Usuario:
        """Verifica que el usuario esté activo"""
        if not current_user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        return current_user

    @staticmethod
    def get_current_admin_user(
        current_user: Usuario = Depends(get_current_active_user)
    ) -> Usuario:
        """Verifica que el usuario sea administrador y esté activo"""
        if current_user.rol != RolUsuario.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos de administrador"
            )
        return current_user

    @staticmethod
    def check_admin_role(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        """Verifica que el usuario sea administrador"""
        if current_user.rol != RolUsuario.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos de administrador"
            )
        return current_user

    @staticmethod
    def check_abogado_role(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        """Verifica que el usuario sea abogado"""
        if current_user.rol != RolUsuario.ABOGADO:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos de abogado"
            )
        return current_user

    @staticmethod
    def check_cliente_role(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        """Verifica que el usuario sea cliente"""
        if current_user.rol != RolUsuario.CLIENTE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos de cliente"
            )
        return current_user

    @staticmethod
    def register_user(user_data: UsuarioCreate, db: Session) -> Usuario:
        """Registra un nuevo usuario"""
        # Verificar si el email ya existe
        if db.query(Usuario).filter(Usuario.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario
        hashed_password = AuthService.get_password_hash(user_data.password)
        db_user = Usuario(
            nombre=user_data.nombre,
            email=user_data.email,
            password_hash=hashed_password,
            rol=user_data.rol
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> Optional[Usuario]:
        """Autentica un usuario con su correo y contraseña"""
        logger.debug(f"Intentando autenticar usuario: {email}")
        
        # Buscar al usuario por su correo
        user = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not user:
            logger.warning(f"Usuario no encontrado: {email}")
            return None
        
        logger.debug(f"Usuario encontrado: {email} (ID: {user.id}, Rol: {user.rol})")
        
        # Verificar la contraseña
        if not verify_password(password, user.password_hash):
            logger.warning(f"Contraseña incorrecta para usuario: {email}")
            return None
        
        # Verificar si la cuenta está activa
        if not user.activo:
            logger.warning(f"Usuario inactivo: {email}")
            return None
        
        logger.info(f"Autenticación exitosa para usuario: {email}")
        return user 
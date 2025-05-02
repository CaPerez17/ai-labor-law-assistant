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

from ..models.usuario import Usuario, RolUsuario
from ..schemas.auth import UsuarioCreate, TokenData
from ..db.session import get_db

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta_muy_segura"  # En producción, usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class AuthService:
    """Servicio para manejar la autenticación y autorización"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña coincide con el hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera el hash de la contraseña"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
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
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
        
        user = db.query(Usuario).filter(Usuario.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def get_current_active_user(
        current_user: Usuario = Depends(get_current_user)
    ) -> Usuario:
        """Verifica que el usuario esté activo"""
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
        """Autentica un usuario"""
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user 
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.usuario import Usuario
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Usar directamente desde settings, que ya maneja os.environ.get y el default
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# Advertir si la SECRET_KEY es la predeterminada y potencialmente insegura
if SECRET_KEY == "tu_clave_secreta_aqui":
    logger.warning("⚠️ ADVERTENCIA: Se está usando una clave secreta predeterminada. Configura una variable de entorno SECRET_KEY segura para producción.")

# Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    Logs detallados para depuración.
    """
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Verificación de contraseña: {'exitosa' if result else 'fallida'}")
        return result
    except Exception as e:
        logger.error(f"Error al verificar contraseña: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para una contraseña en texto plano
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados
    """
    to_encode = data.copy()
    
    # Log para depuración
    logger.debug(f"Creando token para datos: {to_encode}")
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verifica un token JWT y devuelve su payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token verificado con éxito")
        return payload
    except JWTError as e:
        logger.error(f"Error al verificar token: {str(e)}")
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtiene el usuario actual basado en el token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        # El token puede contener 'sub' como ID numérico o como correo electrónico
        user_id = payload.get("sub")
        if user_id is None:
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
            
    except JWTError:
        raise credentials_exception
        
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Decodifica y valida el JWT, comprueba que el usuario existe y está activo.
    Lanza HTTPException(401) si no es válido o el usuario está inactivo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        # El token puede contener 'sub' como ID numérico o como correo electrónico
        user_id = payload.get("sub")
        if user_id is None:
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
            
    except JWTError:
        raise credentials_exception
        
    if user is None or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return user

__all__ = [
    "get_current_user",
    "get_current_active_user",
    # ... otros exports si los hay ...
] 
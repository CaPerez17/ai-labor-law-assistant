from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import os
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Asegurarse de que la SECRET_KEY esté presente y sea segura
SECRET_KEY = os.environ.get("SECRET_KEY", settings.SECRET_KEY)
if not SECRET_KEY or SECRET_KEY == "tu_clave_secreta_aqui":
    logger.warning("⚠️ ADVERTENCIA: Se está usando una clave secreta predeterminada. Configura SECRET_KEY para mayor seguridad.")
    # Generar una clave aleatoria para esta sesión
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    logger.info("Se ha generado una clave secreta temporal para esta sesión")

ALGORITHM = settings.ALGORITHM

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
"""
Registry para Autenticación
-----------------------
Proporciona un registro centralizado para configuraciones de autenticación.
"""
import logging

# Configurar logger
logger = logging.getLogger(__name__)

class Registry:
    """Registro simple para configuración de autenticación y servicios"""
    def __init__(self):
        self._configured = False
        self._services = {}
        logger.info("Registry creado")
        
    def configure(self):
        """Configura el registry"""
        if self._configured:
            logger.info("Registry ya estaba configurado")
            return
            
        logger.info("Registry configurado")
        self._configured = True
        
    def register_service(self, name, service):
        """Registra un servicio en el registry"""
        self._services[name] = service
        logger.info(f"Servicio '{name}' registrado en registry")
        
    def get_service(self, name):
        """Obtiene un servicio del registry"""
        if name not in self._services:
            logger.warning(f"Servicio '{name}' no encontrado en registry")
            return None
        return self._services[name]
        
    @property
    def is_configured(self):
        return self._configured
        
    def __str__(self):
        services = ", ".join(self._services.keys())
        return f"Registry(configured={self._configured}, services=[{services}])"

# Crear instancia global
registry = Registry() 
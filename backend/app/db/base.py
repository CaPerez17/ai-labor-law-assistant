"""
Base de la base de datos
---------------------
Importa todos los modelos para asegurar que SQLAlchemy los registre correctamente.
"""

from .base_class import Base

# Importar todos los modelos aquí
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.models.caso import Caso
from app.models.notificacion import Notificacion
from app.models.feedback_usuario import FeedbackUsuario
from app.models.calificacion import Calificacion
from app.models.metrica_uso import MetricaUso
from app.models.mensaje import Mensaje
from app.models.factura import Factura 
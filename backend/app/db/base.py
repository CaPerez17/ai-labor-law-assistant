"""
Base de la base de datos
---------------------
Importa todos los modelos para asegurar que SQLAlchemy los registre correctamente.
"""

from .base_class import Base

# Importar todos los modelos aquí
from ..models.usuario import Usuario
from ..models.documento import Documento
from ..models.caso import Caso
from ..models.notificacion import Notificacion
from ..models.feedback_usuario import FeedbackUsuario
from ..models.calificacion import Calificacion
from ..models.metrica_uso import MetricaUso
from ..models.mensaje import Mensaje
from ..models.factura import Factura 
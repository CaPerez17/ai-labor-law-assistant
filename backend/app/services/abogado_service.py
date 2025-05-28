"""
Servicio de Abogados
-----------------
Implementa la lógica para la gestión de casos por abogados.
"""

import os
import json
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from app.schemas.abogado import CasoAbogado, UpdateCasoInput, CasoResponse

# Configurar logging
logger = logging.getLogger(__name__)

class AbogadoService:
    """Servicio para la gestión de casos por abogados"""
    
    def __init__(self):
        """Inicializa el servicio con la configuración necesaria"""
        self.data_dir = Path("data/casos")
        self.casos_file = self.data_dir / "casos.json"
        self._inicializar_almacenamiento()
    
    def _inicializar_almacenamiento(self):
        """Inicializa el almacenamiento de casos"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            if not self.casos_file.exists():
                with open(self.casos_file, "w") as f:
                    json.dump([], f)
        except Exception as e:
            logger.error(f"Error al inicializar almacenamiento: {str(e)}")
            raise
    
    def _cargar_casos(self) -> List[dict]:
        """Carga los casos desde el archivo JSON"""
        try:
            with open(self.casos_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar casos: {str(e)}")
            return []
    
    def _guardar_casos(self, casos: List[dict]):
        """Guarda los casos en el archivo JSON"""
        try:
            with open(self.casos_file, "w") as f:
                json.dump(casos, f, default=str)
        except Exception as e:
            logger.error(f"Error al guardar casos: {str(e)}")
            raise
    
    def obtener_casos(
        self,
        estado: Optional[str] = None,
        nivel_riesgo: Optional[str] = None
    ) -> List[CasoAbogado]:
        """
        Obtiene la lista de casos con filtros opcionales
        
        Args:
            estado: Filtrar por estado del caso
            nivel_riesgo: Filtrar por nivel de riesgo
            
        Returns:
            Lista de casos que coinciden con los filtros
        """
        casos = self._cargar_casos()
        
        # Aplicar filtros
        if estado:
            casos = [c for c in casos if c["estado"] == estado]
        if nivel_riesgo:
            casos = [c for c in casos if c["nivel_riesgo"] == nivel_riesgo]
        
        # Convertir a objetos CasoAbogado
        return [CasoAbogado(**caso) for caso in casos]
    
    def actualizar_caso(self, data: UpdateCasoInput) -> CasoResponse:
        """
        Actualiza el estado y comentarios de un caso
        
        Args:
            data: Datos para actualizar el caso
            
        Returns:
            Respuesta con el resultado de la actualización
        """
        casos = self._cargar_casos()
        
        # Buscar el caso
        caso_idx = next(
            (i for i, c in enumerate(casos) if c["id_caso"] == data.id_caso),
            None
        )
        
        if caso_idx is None:
            return CasoResponse(
                exito=False,
                mensaje=f"No se encontró el caso con ID {data.id_caso}"
            )
        
        # Actualizar caso
        caso = casos[caso_idx]
        caso["estado"] = data.nuevo_estado
        caso["comentarios_abogado"].append({
            "texto": data.comentarios,
            "fecha": datetime.now().isoformat()
        })
        caso["fecha_ultima_actualizacion"] = datetime.now().isoformat()
        
        # Guardar cambios
        self._guardar_casos(casos)
        
        return CasoResponse(
            exito=True,
            mensaje="Caso actualizado exitosamente",
            caso=CasoAbogado(**caso)
        )
    
    def obtener_caso(self, id_caso: str) -> Optional[CasoAbogado]:
        """
        Obtiene un caso específico por su ID
        
        Args:
            id_caso: ID del caso a obtener
            
        Returns:
            Caso encontrado o None si no existe
        """
        casos = self._cargar_casos()
        caso = next((c for c in casos if c["id_caso"] == id_caso), None)
        return CasoAbogado(**caso) if caso else None 
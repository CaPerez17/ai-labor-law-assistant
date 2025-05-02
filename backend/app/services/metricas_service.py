"""
Servicio de Métricas y Feedback
----------------------------
Este servicio implementa la lógica para registrar métricas de uso
y feedback de los usuarios.
"""

import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..schemas.metricas import MetricaUso, FeedbackUsuario, FeedbackResponse

class MetricasService:
    """Servicio para el manejo de métricas y feedback"""
    
    def __init__(self):
        """Inicializa el servicio con la configuración necesaria"""
        self.data_dir = Path("data/metricas")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metricas_file = self.data_dir / "metricas_uso.json"
        self.feedback_file = self.data_dir / "feedback_usuarios.json"
        
        # Inicializar archivos si no existen
        if not self.metricas_file.exists():
            with open(self.metricas_file, "w") as f:
                json.dump({"metricas": []}, f)
        
        if not self.feedback_file.exists():
            with open(self.feedback_file, "w") as f:
                json.dump({"feedback": []}, f)
    
    def registrar_metrica(self, metrica: MetricaUso) -> None:
        """
        Registra una métrica de uso
        
        Args:
            metrica: Datos de la métrica a registrar
        """
        # Leer métricas existentes
        with open(self.metricas_file, "r") as f:
            data = json.load(f)
        
        # Agregar nueva métrica
        data["metricas"].append(metrica.dict())
        
        # Guardar actualización
        with open(self.metricas_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def registrar_feedback(self, feedback: FeedbackUsuario) -> FeedbackResponse:
        """
        Registra el feedback de un usuario
        
        Args:
            feedback: Datos del feedback a registrar
            
        Returns:
            Respuesta con mensaje de confirmación
        """
        # Leer feedback existente
        with open(self.feedback_file, "r") as f:
            data = json.load(f)
        
        # Agregar nuevo feedback
        data["feedback"].append(feedback.dict())
        
        # Guardar actualización
        with open(self.feedback_file, "w") as f:
            json.dump(data, f, indent=2)
        
        return FeedbackResponse(
            mensaje="¡Gracias por tu feedback! Tu opinión nos ayuda a mejorar."
        )
    
    def exportar_metricas_csv(self, ruta_archivo: str) -> None:
        """
        Exporta las métricas a un archivo CSV
        
        Args:
            ruta_archivo: Ruta donde se guardará el archivo CSV
        """
        # Leer métricas
        with open(self.metricas_file, "r") as f:
            data = json.load(f)
        
        # Preparar datos para CSV
        metricas = data["metricas"]
        if not metricas:
            return
        
        # Obtener campos del primer registro
        campos = list(metricas[0].keys())
        
        # Escribir CSV
        with open(ruta_archivo, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(metricas)
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso y feedback
        
        Returns:
            Diccionario con estadísticas
        """
        # Leer métricas
        with open(self.metricas_file, "r") as f:
            metricas_data = json.load(f)
        
        # Leer feedback
        with open(self.feedback_file, "r") as f:
            feedback_data = json.load(f)
        
        # Calcular estadísticas de métricas
        metricas = metricas_data["metricas"]
        total_interacciones = len(metricas)
        interacciones_exitosas = sum(1 for m in metricas if m["exito"])
        
        # Calcular estadísticas de feedback
        feedback = feedback_data["feedback"]
        total_feedback = len(feedback)
        promedio_calificacion = (
            sum(f["calificacion"] for f in feedback) / total_feedback
            if total_feedback > 0 else 0
        )
        
        return {
            "total_interacciones": total_interacciones,
            "interacciones_exitosas": interacciones_exitosas,
            "tasa_exito": (interacciones_exitosas / total_interacciones * 100) if total_interacciones > 0 else 0,
            "total_feedback": total_feedback,
            "promedio_calificacion": round(promedio_calificacion, 2)
        } 
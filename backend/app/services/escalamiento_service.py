"""
Servicio de Escalamiento a Abogados
--------------------------------
Este servicio implementa la lógica para escalar casos a abogados humanos,
gestionando el registro en CRM y la preparación de mensajes para WhatsApp.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from ..schemas.escalamiento import (
    EscalamientoInput,
    EscalamientoResponse,
    EstadoEscalamiento,
    NivelRiesgo
)

class EscalamientoService:
    """Servicio para el proceso de escalamiento"""
    
    def __init__(self):
        """Inicializa el servicio con la configuración necesaria"""
        self.crm_file = Path("data/crm_casos.json")
        self.crm_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar archivo CRM si no existe
        if not self.crm_file.exists():
            with open(self.crm_file, "w") as f:
                json.dump({"casos": []}, f)
    
    def _generar_caso_id(self) -> str:
        """Genera un ID único para el caso"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"CASO-{timestamp}"
    
    def _registrar_en_crm(self, caso: Dict[str, Any]) -> str:
        """
        Registra el caso en el CRM (archivo JSON)
        
        Args:
            caso: Datos del caso a registrar
            
        Returns:
            ID del caso registrado
        """
        # Leer casos existentes
        with open(self.crm_file, "r") as f:
            data = json.load(f)
        
        # Verificar si ya existe un caso para este usuario
        for caso_existente in data["casos"]:
            if caso_existente["usuario_id"] == caso["usuario_id"]:
                # Actualizar caso existente
                caso_existente.update({
                    "estado": EstadoEscalamiento.PENDIENTE,
                    "ultima_actualizacion": datetime.now().isoformat(),
                    "detalle_consulta": caso["detalle_consulta"],
                    "nivel_riesgo": caso["nivel_riesgo"]
                })
                return caso_existente["caso_id"]
        
        # Generar nuevo ID y agregar caso
        caso_id = self._generar_caso_id()
        caso["caso_id"] = caso_id
        caso["fecha_creacion"] = datetime.now().isoformat()
        caso["estado"] = EstadoEscalamiento.PENDIENTE
        
        data["casos"].append(caso)
        
        # Guardar actualización
        with open(self.crm_file, "w") as f:
            json.dump(data, f, indent=2)
        
        return caso_id
    
    def _preparar_mensaje_whatsapp(self, caso: Dict[str, Any]) -> str:
        """
        Prepara el mensaje para WhatsApp Business
        
        Args:
            caso: Datos del caso
            
        Returns:
            Mensaje formateado para WhatsApp
        """
        return (
            f"*Nuevo Caso Requiere Atención*\n\n"
            f"ID: {caso['caso_id']}\n"
            f"Usuario: {caso['usuario_id']}\n"
            f"Flujo: {caso['flujo']}\n"
            f"Nivel de Riesgo: {caso['nivel_riesgo']}\n\n"
            f"*Detalle:*\n{caso['detalle_consulta']}\n\n"
            f"Contacto WhatsApp: {caso.get('contacto_whatsapp', 'No proporcionado')}"
        )
    
    def escalar_caso(self, input_data: EscalamientoInput) -> EscalamientoResponse:
        """
        Procesa el escalamiento de un caso
        
        Args:
            input_data: Datos del caso a escalar
            
        Returns:
            Respuesta con el resultado del escalamiento
        """
        # Preparar datos del caso
        caso = input_data.dict()
        
        # Registrar en CRM si el riesgo es alto
        caso_id = None
        if input_data.nivel_riesgo == NivelRiesgo.ALTO:
            caso_id = self._registrar_en_crm(caso)
            
            # Preparar mensaje para WhatsApp (para integración futura)
            mensaje_whatsapp = self._preparar_mensaje_whatsapp(caso)
            
            # Aquí se podría implementar la integración con WhatsApp Business API
            # Por ahora solo guardamos el mensaje en un archivo
            whatsapp_dir = Path("data/whatsapp_mensajes")
            whatsapp_dir.mkdir(parents=True, exist_ok=True)
            
            with open(whatsapp_dir / f"{caso_id}.txt", "w") as f:
                f.write(mensaje_whatsapp)
        
        # Preparar mensaje de confirmación
        if input_data.nivel_riesgo == NivelRiesgo.ALTO:
            mensaje = (
                "Tu caso ha sido registrado y será revisado por un abogado especializado. "
                "Te contactaremos pronto por WhatsApp para brindarte la atención personalizada que necesitas."
            )
        else:
            mensaje = (
                "Hemos registrado tu consulta. Un abogado la revisará y te contactará "
                "si considera necesario brindarte atención personalizada."
            )
        
        return EscalamientoResponse(
            mensaje_confirmacion=mensaje,
            estado=EstadoEscalamiento.PENDIENTE,
            caso_id=caso_id,
            timestamp=datetime.now()
        ) 
"""
Servicio de Análisis de Documentos
--------------------------------
Este servicio implementa la lógica para analizar documentos legales
y extraer información relevante.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException
import PyPDF2
import docx
import re
from datetime import datetime
from app.schemas.documento import (
    DocumentoResponse,
    Clausula,
    Riesgo,
    TipoRiesgo
)

class DocumentoService:
    """Servicio para análisis de documentos legales"""
    
    def __init__(self):
        """Inicializa el servicio con las reglas de análisis"""
        self.palabras_clave = {
            'subordinacion': ['subordinación', 'subordinado', 'jefe inmediato', 'superior'],
            'salario': ['salario', 'remuneración', 'compensación', 'pago'],
            'horario': ['horario', 'jornada', 'turno', 'horas'],
            'terminacion': ['terminación', 'despido', 'renuncia', 'finalización'],
            'confidencialidad': ['confidencialidad', 'secreto', 'reservado', 'privado'],
            'no_competencia': ['no competencia', 'competencia', 'restricción'],
            'propiedad_intelectual': ['propiedad intelectual', 'derechos de autor', 'patente']
        }
        
        self.riesgos = {
            'clausulas_abusivas': {
                'patrones': [
                    r'renuncia.*derechos',
                    r'prohibido.*demandar',
                    r'sin.*compensación',
                    r'acepta.*condiciones'
                ],
                'nivel': TipoRiesgo.ALTO
            },
            'horarios_excesivos': {
                'patrones': [
                    r'jornada.*ilimitada',
                    r'horario.*extendido',
                    r'disponibilidad.*24/7'
                ],
                'nivel': TipoRiesgo.MEDIO
            },
            'confidencialidad_excesiva': {
                'patrones': [
                    r'confidencialidad.*perpetua',
                    r'secreto.*indefinido'
                ],
                'nivel': TipoRiesgo.MEDIO
            }
        }
    
    async def analizar_documento(self, file: UploadFile) -> DocumentoResponse:
        """
        Analiza un documento legal y extrae información relevante.
        
        Args:
            file: Archivo a analizar
            
        Returns:
            Resultado del análisis
            
        Raises:
            HTTPException: Si hay un error en el análisis
        """
        # Validar tipo de archivo
        if not self._validar_tipo_archivo(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no soportado. Use PDF, DOCX o TXT."
            )
            
        # Validar tamaño
        if not self._validar_tamano(file):
            raise HTTPException(
                status_code=400,
                detail="El archivo excede el tamaño máximo permitido (5MB)."
            )
            
        # Extraer texto
        texto = await self._extraer_texto(file)
        if not texto:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer texto del documento."
            )
            
        # Analizar documento
        clausulas = self._identificar_clausulas(texto)
        riesgos = self._identificar_riesgos(texto, clausulas)
        resumen = self._generar_resumen(texto, clausulas)
        recomendaciones = self._generar_recomendaciones(riesgos)
        
        return DocumentoResponse(
            clausulas_destacadas=clausulas,
            riesgos_detectados=riesgos,
            resumen_general=resumen,
            recomendaciones=recomendaciones,
            tipo_documento=self._identificar_tipo_documento(texto),
            fecha_documento=self._extraer_fecha(texto)
        )
    
    def _validar_tipo_archivo(self, filename: str) -> bool:
        """Valida que el tipo de archivo sea soportado"""
        extensiones_validas = {'.pdf', '.docx', '.txt'}
        return os.path.splitext(filename.lower())[1] in extensiones_validas
    
    def _validar_tamano(self, file: UploadFile) -> bool:
        """Valida que el tamaño del archivo no exceda el límite"""
        TAMANO_MAXIMO = 5 * 1024 * 1024  # 5MB
        return file.size <= TAMANO_MAXIMO
    
    async def _extraer_texto(self, file: UploadFile) -> str:
        """Extrae el texto del documento según su tipo"""
        extension = os.path.splitext(file.filename.lower())[1]
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            try:
                if extension == '.pdf':
                    return self._extraer_texto_pdf(temp_file.name)
                elif extension == '.docx':
                    return self._extraer_texto_docx(temp_file.name)
                else:  # .txt
                    return self._extraer_texto_txt(temp_file.name)
            finally:
                os.unlink(temp_file.name)
    
    def _extraer_texto_pdf(self, filepath: str) -> str:
        """Extrae texto de un archivo PDF"""
        texto = []
        with open(filepath, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            for pagina in pdf.pages:
                texto.append(pagina.extract_text())
        return '\n'.join(texto)
    
    def _extraer_texto_docx(self, filepath: str) -> str:
        """Extrae texto de un archivo DOCX"""
        doc = docx.Document(filepath)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    def _extraer_texto_txt(self, filepath: str) -> str:
        """Extrae texto de un archivo TXT"""
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _identificar_clausulas(self, texto: str) -> List[Clausula]:
        """Identifica cláusulas importantes en el texto"""
        clausulas = []
        
        # Buscar patrones de cláusulas
        patrones = [
            r'(?:CLÁUSULA|ARTÍCULO)\s+[IVX]+\s*[-–]\s*([^:]+):\s*(.*?)(?=(?:CLÁUSULA|ARTÍCULO|$))',
            r'(?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SÉPTIMA|OCTAVA|NOVENA|DÉCIMA)\s*[-–]\s*([^:]+):\s*(.*?)(?=(?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SÉPTIMA|OCTAVA|NOVENA|DÉCIMA|$))'
        ]
        
        for patron in patrones:
            matches = re.finditer(patron, texto, re.IGNORECASE | re.DOTALL)
            for match in matches:
                titulo = match.group(1).strip()
                contenido = match.group(2).strip()
                
                # Evaluar riesgo de la cláusula
                riesgo = self._evaluar_riesgo_clausula(contenido)
                
                clausulas.append(Clausula(
                    titulo=titulo,
                    contenido=contenido,
                    riesgo=riesgo['nivel'] if riesgo else None,
                    razon_riesgo=riesgo['razon'] if riesgo else None
                ))
        
        return clausulas
    
    def _evaluar_riesgo_clausula(self, contenido: str) -> Dict[str, Any]:
        """Evalúa el nivel de riesgo de una cláusula"""
        contenido = contenido.lower()
        
        for tipo_riesgo, info in self.riesgos.items():
            for patron in info['patrones']:
                if re.search(patron, contenido, re.IGNORECASE):
                    return {
                        'nivel': info['nivel'],
                        'razon': f"Cláusula contiene términos potencialmente abusivos: {patron}"
                    }
        
        return None
    
    def _identificar_riesgos(self, texto: str, clausulas: List[Clausula]) -> List[Riesgo]:
        """Identifica riesgos en el documento"""
        riesgos = []
        texto = texto.lower()
        
        # Analizar cada tipo de riesgo
        for tipo_riesgo, info in self.riesgos.items():
            for patron in info['patrones']:
                if re.search(patron, texto, re.IGNORECASE):
                    # Encontrar cláusulas relacionadas
                    clausulas_relacionadas = [
                        c.titulo for c in clausulas
                        if re.search(patron, c.contenido.lower(), re.IGNORECASE)
                    ]
                    
                    riesgos.append(Riesgo(
                        descripcion=self._get_descripcion_riesgo(tipo_riesgo),
                        nivel=info['nivel'],
                        clausulas_relacionadas=clausulas_relacionadas,
                        recomendacion=self._get_recomendacion_riesgo(tipo_riesgo)
                    ))
        
        return riesgos
    
    def _get_descripcion_riesgo(self, tipo_riesgo: str) -> str:
        """Obtiene la descripción de un tipo de riesgo"""
        descripciones = {
            'clausulas_abusivas': "Se detectaron cláusulas que podrían ser consideradas abusivas o contrarias a la ley.",
            'horarios_excesivos': "Se identificaron disposiciones sobre horarios que podrían exceder los límites legales.",
            'confidencialidad_excesiva': "Las cláusulas de confidencialidad podrían ser excesivas o indefinidas."
        }
        return descripciones.get(tipo_riesgo, "Riesgo no especificado")
    
    def _get_recomendacion_riesgo(self, tipo_riesgo: str) -> str:
        """Obtiene la recomendación para un tipo de riesgo"""
        recomendaciones = {
            'clausulas_abusivas': "Revisar y modificar las cláusulas para asegurar que no vulneren derechos fundamentales.",
            'horarios_excesivos': "Ajustar las disposiciones de horario para cumplir con la jornada máxima legal.",
            'confidencialidad_excesiva': "Limitar el alcance y duración de las obligaciones de confidencialidad."
        }
        return recomendaciones.get(tipo_riesgo, "Consultar con un abogado especializado.")
    
    def _generar_resumen(self, texto: str, clausulas: List[Clausula]) -> str:
        """Genera un resumen del documento"""
        # Identificar tipo de documento
        tipo_doc = self._identificar_tipo_documento(texto)
        
        # Contar cláusulas por categoría
        categorias = {}
        for clausula in clausulas:
            for categoria, palabras in self.palabras_clave.items():
                if any(palabra in clausula.contenido.lower() for palabra in palabras):
                    categorias[categoria] = categorias.get(categoria, 0) + 1
        
        # Generar resumen
        resumen = f"El documento parece ser un {tipo_doc} que contiene {len(clausulas)} cláusulas principales. "
        resumen += "Se identificaron secciones relacionadas con: "
        resumen += ", ".join(f"{categoria.replace('_', ' ')} ({cantidad})" 
                           for categoria, cantidad in categorias.items())
        
        return resumen
    
    def _generar_recomendaciones(self, riesgos: List[Riesgo]) -> List[str]:
        """Genera recomendaciones basadas en los riesgos identificados"""
        recomendaciones = []
        
        # Recomendaciones específicas por riesgo
        for riesgo in riesgos:
            recomendaciones.append(riesgo.recomendacion)
        
        # Recomendaciones generales
        if not riesgos:
            recomendaciones.append("El documento no presenta riesgos evidentes, pero se recomienda una revisión legal completa.")
        
        recomendaciones.append("Asegúrese de que todas las cláusulas cumplan con la normativa laboral vigente.")
        recomendaciones.append("Verifique que las condiciones laborales no vulneren derechos fundamentales.")
        
        return recomendaciones
    
    def _identificar_tipo_documento(self, texto: str) -> str:
        """Identifica el tipo de documento"""
        texto = texto.lower()
        
        if "contrato" in texto and "trabajo" in texto:
            return "contrato de trabajo"
        elif "convenio" in texto:
            return "convenio"
        elif "acuerdo" in texto:
            return "acuerdo"
        else:
            return "documento legal"
    
    def _extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae la fecha del documento si está presente"""
        # Patrones comunes de fecha en documentos legales
        patrones = [
            r'(\d{1,2})\s+de\s+([a-zA-Z]+)\s+de\s+(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                try:
                    if '/' in patron:
                        return datetime.strptime(match.group(0), '%d/%m/%Y').strftime('%Y-%m-%d')
                    elif '-' in patron:
                        return match.group(0)
                    else:
                        # Convertir mes en español a número
                        meses = {
                            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                        }
                        dia = int(match.group(1))
                        mes = meses[match.group(2).lower()]
                        anio = int(match.group(3))
                        return datetime(anio, mes, dia).strftime('%Y-%m-%d')
                except (ValueError, KeyError):
                    continue
        
        return None 
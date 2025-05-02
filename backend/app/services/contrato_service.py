"""
Servicio de Generación de Contratos
--------------------------------
Este servicio implementa la lógica para generar contratos laborales
a partir de plantillas predefinidas.
"""

import os
from datetime import datetime
from typing import Dict, Optional
from app.schemas.contrato import ContratoInput, ContratoResponse, TipoContrato

class ContratoService:
    """Servicio para generación de contratos laborales"""
    
    def __init__(self):
        """Inicializa el servicio con las plantillas de contratos"""
        self.plantillas = {
            TipoContrato.TERMINO_FIJO: self._get_plantilla_fijo(),
            TipoContrato.TERMINO_INDEFINIDO: self._get_plantilla_indefinido(),
            TipoContrato.OBRA_LABOR: self._get_plantilla_obra_labor(),
            TipoContrato.DOMESTICO: self._get_plantilla_domestico()
        }
        
    def generar_contrato(self, data: ContratoInput) -> ContratoResponse:
        """
        Genera un contrato laboral basado en los datos proporcionados.
        
        Args:
            data: Datos para la generación del contrato
            
        Returns:
            Contrato generado y metadatos
        """
        # 1. Obtener la plantilla correspondiente
        plantilla = self.plantillas[data.tipo_contrato]
        
        # 2. Preparar los datos para el reemplazo
        valores = self._preparar_valores_reemplazo(data)
        
        # 3. Generar el contrato reemplazando los placeholders
        contrato_generado = self._aplicar_reemplazos(plantilla, valores)
        
        # 4. Generar nombre de archivo sugerido
        nombre_archivo = self._generar_nombre_archivo(data)
        
        # 5. Generar advertencia si es necesario
        advertencia = self._generar_advertencia(data)
        
        return ContratoResponse(
            contrato_generado=contrato_generado,
            tipo_contrato=data.tipo_contrato,
            nombre_archivo=nombre_archivo,
            advertencia=advertencia
        )
    
    def _preparar_valores_reemplazo(self, data: ContratoInput) -> Dict[str, str]:
        """Prepara el diccionario de valores para reemplazar en la plantilla"""
        valores = {
            "{{TIPO_CONTRATO}}": self._get_tipo_contrato_texto(data.tipo_contrato),
            "{{NOMBRE_EMPLEADOR}}": data.nombre_empleador.upper(),
            "{{NIT_EMPLEADOR}}": data.nit_empleador,
            "{{DIRECCION_EMPLEADOR}}": data.direccion_empleador,
            "{{NOMBRE_EMPLEADO}}": data.nombre_empleado.upper(),
            "{{DOCUMENTO_EMPLEADO}}": data.documento_empleado,
            "{{CARGO}}": data.cargo.upper(),
            "{{SALARIO_NUMERO}}": f"{data.salario:,.0f}",
            "{{SALARIO_LETRAS}}": self._numero_a_letras(data.salario),
            "{{FECHA_INICIO}}": data.fecha_inicio.strftime("%d de %B de %Y"),
            "{{MODALIDAD_TRABAJO}}": data.modalidad_trabajo.value.upper(),
            "{{LUGAR_TRABAJO}}": data.lugar_trabajo or "N/A",
            "{{FECHA_GENERACION}}": datetime.now().strftime("%d de %B de %Y"),
            "{{HORARIO_TRABAJO}}": data.horario_trabajo or "según lo establecido en el reglamento interno de trabajo",
        }
        
        if data.funciones_principales:
            valores["{{FUNCIONES}}"] = data.funciones_principales
        else:
            valores["{{FUNCIONES}}"] = "Las inherentes al cargo y las demás que le sean asignadas por su jefe inmediato."
            
        if data.tipo_contrato == TipoContrato.TERMINO_FIJO:
            valores["{{DURACION}}"] = f"{data.duracion_meses} meses"
            valores["{{FECHA_FIN}}"] = (data.fecha_inicio.replace(month=data.fecha_inicio.month + data.duracion_meses)).strftime("%d de %B de %Y")
            
        return valores
    
    def _aplicar_reemplazos(self, plantilla: str, valores: Dict[str, str]) -> str:
        """Aplica los reemplazos de valores en la plantilla"""
        texto = plantilla
        for key, value in valores.items():
            texto = texto.replace(key, str(value))
        return texto
    
    def _generar_nombre_archivo(self, data: ContratoInput) -> str:
        """Genera un nombre de archivo sugerido para el contrato"""
        tipo = data.tipo_contrato.value.replace("_", "-")
        fecha = datetime.now().strftime("%Y%m%d")
        empleado = data.nombre_empleado.lower().replace(" ", "-")
        return f"contrato-{tipo}-{empleado}-{fecha}.txt"
    
    def _generar_advertencia(self, data: ContratoInput) -> Optional[str]:
        """Genera advertencias específicas según el tipo de contrato y datos"""
        if data.tipo_contrato == TipoContrato.TERMINO_FIJO and data.duracion_meses > 12:
            return "Recuerde que los contratos a término fijo superiores a un año requieren justa causa para su terminación."
        elif data.tipo_contrato == TipoContrato.DOMESTICO:
            return "Este contrato debe ser registrado en el Sistema del Servicio Doméstico de la Seguridad Social."
        return None
    
    def _get_tipo_contrato_texto(self, tipo: TipoContrato) -> str:
        """Obtiene el texto formal para el tipo de contrato"""
        mapping = {
            TipoContrato.TERMINO_FIJO: "CONTRATO INDIVIDUAL DE TRABAJO A TÉRMINO FIJO",
            TipoContrato.TERMINO_INDEFINIDO: "CONTRATO INDIVIDUAL DE TRABAJO A TÉRMINO INDEFINIDO",
            TipoContrato.OBRA_LABOR: "CONTRATO INDIVIDUAL DE TRABAJO POR OBRA O LABOR",
            TipoContrato.DOMESTICO: "CONTRATO DE TRABAJO PARA EL SERVICIO DOMÉSTICO"
        }
        return mapping[tipo]
    
    def _numero_a_letras(self, numero: float) -> str:
        """Convierte un número a su representación en letras"""
        # Esta es una implementación simplificada
        # En un caso real, se usaría una biblioteca como num2words
        return f"{numero:,.0f} PESOS M/CTE"
    
    def _get_plantilla_fijo(self) -> str:
        """Retorna la plantilla para contrato a término fijo"""
        return """
{{TIPO_CONTRATO}}

Entre los suscritos, {{NOMBRE_EMPLEADOR}}, identificado con NIT {{NIT_EMPLEADOR}}, domiciliado en {{DIRECCION_EMPLEADOR}}, quien para efectos de este contrato se denominará EL EMPLEADOR, y {{NOMBRE_EMPLEADO}}, identificado con cédula de ciudadanía No. {{DOCUMENTO_EMPLEADO}}, quien para efectos de este contrato se denominará EL TRABAJADOR, se ha celebrado el presente Contrato Individual de Trabajo, regido por las siguientes cláusulas:

PRIMERA - OBJETO: EL EMPLEADOR contrata los servicios personales de EL TRABAJADOR para desempeñar el cargo de {{CARGO}}, y las funciones inherentes al mismo que se describen a continuación: {{FUNCIONES}}

SEGUNDA - DURACIÓN: El presente contrato tendrá una duración de {{DURACION}} contados a partir del {{FECHA_INICIO}} hasta el {{FECHA_FIN}}.

TERCERA - JORNADA: EL TRABAJADOR se obliga a laborar la jornada ordinaria en los turnos y dentro de las horas señaladas por EL EMPLEADOR, {{HORARIO_TRABAJO}}.

CUARTA - MODALIDAD: El trabajo se desarrollará bajo la modalidad {{MODALIDAD_TRABAJO}} en {{LUGAR_TRABAJO}}.

QUINTA - SALARIO: EL EMPLEADOR pagará al TRABAJADOR por la prestación de sus servicios el salario mensual de {{SALARIO_NUMERO}} ({{SALARIO_LETRAS}}).

SEXTA - OBLIGACIONES: EL TRABAJADOR se obliga a prestar sus servicios de manera exclusiva a EL EMPLEADOR, a cumplir con las funciones propias del cargo y con todas las órdenes e instrucciones que le sean impartidas.

SÉPTIMA - MODIFICACIÓN: Cualquier modificación al presente contrato debe efectuarse por escrito y anexarse a este documento.

OCTAVA - LEGISLACIÓN: En todo lo no previsto en el presente contrato, las partes se regirán por las normas del Código Sustantivo del Trabajo.

Para constancia se firma en dos ejemplares del mismo tenor, en la ciudad de {{LUGAR_TRABAJO}}, el {{FECHA_GENERACION}}.


_______________________                    _______________________
EL EMPLEADOR                               EL TRABAJADOR
{{NOMBRE_EMPLEADOR}}                       {{NOMBRE_EMPLEADO}}
NIT: {{NIT_EMPLEADOR}}                     C.C.: {{DOCUMENTO_EMPLEADO}}
"""
    
    def _get_plantilla_indefinido(self) -> str:
        """Retorna la plantilla para contrato a término indefinido"""
        return """
{{TIPO_CONTRATO}}

Entre los suscritos, {{NOMBRE_EMPLEADOR}}, identificado con NIT {{NIT_EMPLEADOR}}, domiciliado en {{DIRECCION_EMPLEADOR}}, quien para efectos de este contrato se denominará EL EMPLEADOR, y {{NOMBRE_EMPLEADO}}, identificado con cédula de ciudadanía No. {{DOCUMENTO_EMPLEADO}}, quien para efectos de este contrato se denominará EL TRABAJADOR, se ha celebrado el presente Contrato Individual de Trabajo, regido por las siguientes cláusulas:

PRIMERA - OBJETO: EL EMPLEADOR contrata los servicios personales de EL TRABAJADOR para desempeñar el cargo de {{CARGO}}, y las funciones inherentes al mismo que se describen a continuación: {{FUNCIONES}}

SEGUNDA - DURACIÓN: El presente contrato es a término indefinido, iniciando el día {{FECHA_INICIO}}.

TERCERA - JORNADA: EL TRABAJADOR se obliga a laborar la jornada ordinaria en los turnos y dentro de las horas señaladas por EL EMPLEADOR, {{HORARIO_TRABAJO}}.

CUARTA - MODALIDAD: El trabajo se desarrollará bajo la modalidad {{MODALIDAD_TRABAJO}} en {{LUGAR_TRABAJO}}.

QUINTA - SALARIO: EL EMPLEADOR pagará al TRABAJADOR por la prestación de sus servicios el salario mensual de {{SALARIO_NUMERO}} ({{SALARIO_LETRAS}}).

SEXTA - OBLIGACIONES: EL TRABAJADOR se obliga a prestar sus servicios de manera exclusiva a EL EMPLEADOR, a cumplir con las funciones propias del cargo y con todas las órdenes e instrucciones que le sean impartidas.

SÉPTIMA - TERMINACIÓN: El presente contrato podrá darse por terminado por cualquiera de las causales establecidas en el artículo 61 del Código Sustantivo del Trabajo.

OCTAVA - LEGISLACIÓN: En todo lo no previsto en el presente contrato, las partes se regirán por las normas del Código Sustantivo del Trabajo.

Para constancia se firma en dos ejemplares del mismo tenor, en la ciudad de {{LUGAR_TRABAJO}}, el {{FECHA_GENERACION}}.


_______________________                    _______________________
EL EMPLEADOR                               EL TRABAJADOR
{{NOMBRE_EMPLEADOR}}                       {{NOMBRE_EMPLEADO}}
NIT: {{NIT_EMPLEADOR}}                     C.C.: {{DOCUMENTO_EMPLEADO}}
"""
    
    def _get_plantilla_obra_labor(self) -> str:
        """Retorna la plantilla para contrato por obra o labor"""
        return """
{{TIPO_CONTRATO}}

Entre los suscritos, {{NOMBRE_EMPLEADOR}}, identificado con NIT {{NIT_EMPLEADOR}}, domiciliado en {{DIRECCION_EMPLEADOR}}, quien para efectos de este contrato se denominará EL EMPLEADOR, y {{NOMBRE_EMPLEADO}}, identificado con cédula de ciudadanía No. {{DOCUMENTO_EMPLEADO}}, quien para efectos de este contrato se denominará EL TRABAJADOR, se ha celebrado el presente Contrato Individual de Trabajo, regido por las siguientes cláusulas:

PRIMERA - OBJETO: EL EMPLEADOR contrata los servicios personales de EL TRABAJADOR para desempeñar el cargo de {{CARGO}}, y las funciones inherentes al mismo que se describen a continuación: {{FUNCIONES}}

SEGUNDA - DURACIÓN: El presente contrato durará por el tiempo que dure la realización de la obra o labor contratada, iniciando el día {{FECHA_INICIO}}.

TERCERA - JORNADA: EL TRABAJADOR se obliga a laborar la jornada ordinaria en los turnos y dentro de las horas señaladas por EL EMPLEADOR, {{HORARIO_TRABAJO}}.

CUARTA - MODALIDAD: El trabajo se desarrollará bajo la modalidad {{MODALIDAD_TRABAJO}} en {{LUGAR_TRABAJO}}.

QUINTA - SALARIO: EL EMPLEADOR pagará al TRABAJADOR por la prestación de sus servicios el salario mensual de {{SALARIO_NUMERO}} ({{SALARIO_LETRAS}}).

SEXTA - TERMINACIÓN: El contrato terminará una vez finalice la obra o labor para la cual fue contratado EL TRABAJADOR.

SÉPTIMA - LEGISLACIÓN: En todo lo no previsto en el presente contrato, las partes se regirán por las normas del Código Sustantivo del Trabajo.

Para constancia se firma en dos ejemplares del mismo tenor, en la ciudad de {{LUGAR_TRABAJO}}, el {{FECHA_GENERACION}}.


_______________________                    _______________________
EL EMPLEADOR                               EL TRABAJADOR
{{NOMBRE_EMPLEADOR}}                       {{NOMBRE_EMPLEADO}}
NIT: {{NIT_EMPLEADOR}}                     C.C.: {{DOCUMENTO_EMPLEADO}}
"""
    
    def _get_plantilla_domestico(self) -> str:
        """Retorna la plantilla para contrato de trabajo doméstico"""
        return """
{{TIPO_CONTRATO}}

Entre los suscritos, {{NOMBRE_EMPLEADOR}}, identificado con NIT {{NIT_EMPLEADOR}}, domiciliado en {{DIRECCION_EMPLEADOR}}, quien para efectos de este contrato se denominará EL EMPLEADOR, y {{NOMBRE_EMPLEADO}}, identificado con cédula de ciudadanía No. {{DOCUMENTO_EMPLEADO}}, quien para efectos de este contrato se denominará EL TRABAJADOR, se ha celebrado el presente Contrato de Trabajo para el Servicio Doméstico, regido por las siguientes cláusulas y por la Ley 1788 de 2016:

PRIMERA - OBJETO: EL EMPLEADOR contrata los servicios personales de EL TRABAJADOR para desempeñar labores propias del servicio doméstico en el domicilio del EMPLEADOR, incluyendo: {{FUNCIONES}}

SEGUNDA - DURACIÓN: El presente contrato es a término indefinido, iniciando el día {{FECHA_INICIO}}.

TERCERA - JORNADA: La jornada laboral será {{HORARIO_TRABAJO}}, respetando los límites establecidos en el Código Sustantivo del Trabajo.

CUARTA - MODALIDAD: El trabajo se desarrollará de manera {{MODALIDAD_TRABAJO}} en {{LUGAR_TRABAJO}}.

QUINTA - SALARIO: EL EMPLEADOR pagará al TRABAJADOR por la prestación de sus servicios el salario mensual de {{SALARIO_NUMERO}} ({{SALARIO_LETRAS}}). El empleador se obliga a pagar además todas las prestaciones sociales establecidas por la ley, incluyendo la prima de servicios.

SEXTA - OBLIGACIONES ESPECIALES:
1. EL EMPLEADOR deberá afiliar al TRABAJADOR al Sistema de Seguridad Social.
2. EL EMPLEADOR deberá respetar los derechos laborales del TRABAJADOR conforme a la Ley 1788 de 2016.
3. EL TRABAJADOR deberá cumplir con las labores asignadas con diligencia y cuidado.

SÉPTIMA - LEGISLACIÓN: Este contrato está regido especialmente por la Ley 1788 de 2016 y demás normas aplicables al trabajo doméstico.

Para constancia se firma en dos ejemplares del mismo tenor, en la ciudad de {{LUGAR_TRABAJO}}, el {{FECHA_GENERACION}}.


_______________________                    _______________________
EL EMPLEADOR                               EL TRABAJADOR
{{NOMBRE_EMPLEADOR}}                       {{NOMBRE_EMPLEADO}}
NIT: {{NIT_EMPLEADOR}}                     C.C.: {{DOCUMENTO_EMPLEADO}}
""" 
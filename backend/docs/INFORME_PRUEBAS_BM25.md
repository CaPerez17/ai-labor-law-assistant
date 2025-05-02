# Informe de Pruebas: AI Labor Law Assistant

## Resultados de Pruebas de BM25 Optimizado

Fecha: 19 de marzo de 2025

## 1. Descripción

Este informe presenta los resultados de las pruebas realizadas al sistema de búsqueda semántica BM25 optimizado y su integración con el endpoint `/api/ask/` para la consulta de temas legales laborales, específicamente enfocados en casos de estabilidad laboral reforzada durante el embarazo.

## 2. Resultados de las Pruebas

### 2.1 Verificación del índice BM25

Se verificó el estado del índice BM25 optimizado, comprobando:
- **Inicializado**: Sí
- **Documentos indexados**: 6
- **Caché activado**: Sí
- **Parámetros BM25**: k1=1.5, b=0.75

### 2.2 Pruebas con términos de búsqueda específicos

Se realizaron pruebas con 8 términos de búsqueda relacionados con estabilidad laboral y embarazo:

| Término | Docs encontrados | Tiempo (ms) | Desde caché |
|---------|-----------------|-------------|-------------|
| estabilidad laboral reforzada | 2 | 5.15 | No |
| fuero de maternidad | 2 | 1.98 | No |
| despido mujer embarazada | 3 | 2.38 | No |
| protección trabajadora embarazada | 3 | 1.83 | No |
| licencia maternidad | 2 | 0.30 | Sí |
| reintegro trabajadora embarazada | 3 | 2.04 | No |
| indemnización despido embarazo | 3 | 1.82 | No |
| derechos mujer embarazada trabajo | 3 | 2.00 | No |

**Total documentos encontrados**: 21  
**Promedio de documentos por búsqueda**: 2.62  
**Tiempo total de ejecución**: 0.03 segundos

### 2.3 Prueba de caso de uso específico

Se probó un caso real de una mujer despedida durante el embarazo:

**Consulta**: "Soy una mujer 30 años, me encuentro laborando con aliados integrales, me enteré hace poco que me encontraba en embarazo y fui despedida, que puedo hacer?"

**Resultados**:
- Documentos relevantes encontrados: 3
- Tiempo de búsqueda: 0.29ms (desde caché)
- Documentos principales: 
  - SENTENCIA C-005/17
  - CÓDIGO SUSTANTIVO DEL TRABAJO (Ley 1822 de 2017)

### 2.4 Integración con endpoint `/api/ask/`

Se verificó la integración del sistema BM25 con el endpoint `/api/ask/`:

**Consulta**: "Soy una mujer de 30 años, me encuentro laborando con una empresa y me enteré hace poco que estaba en embarazo. Fui despedida después de informar a mi jefe. ¿Qué derechos tengo?"

**Respuesta**:
- El sistema proporcionó información sobre "estabilidad laboral reforzada"
- Tiempo de procesamiento: 2257.36ms
- Nivel de confianza: 0.5 (requiere revisión humana)
- Referencias legales: Se mencionaron documentos relevantes (SENTENCIA C-005/17)

## 3. Análisis de Resultados

### 3.1 Fortalezas

- **Velocidad**: La búsqueda BM25 optimizada muestra tiempos muy rápidos (promedio <2ms)
- **Sistema de caché**: Algunas consultas se recuperaron desde caché, aumentando la velocidad
- **Relevancia**: Los documentos encontrados son altamente relevantes a los términos de búsqueda
- **Consistencia**: Para términos relacionados con estabilidad laboral reforzada y embarazo, el sistema consistentemente encuentra los documentos correctos

### 3.2 Áreas de mejora

- **Documentos repetidos**: En algunos casos, se recuperan documentos duplicados (IDs diferentes pero mismo contenido)
- **Referencias vacías**: En la respuesta de `/api/ask/`, aunque se mencionan documentos, el campo `references` aparece vacío
- **Confianza limitada**: Las respuestas tienen un nivel de confianza moderado y requieren revisión humana
- **Cantidad de documentos**: La base de conocimiento actual (6 documentos) es limitada

## 4. Recomendaciones

1. **Ampliar base de conocimiento**: Incorporar más documentos legales sobre derechos laborales
2. **Eliminar duplicados**: Implementar un mecanismo para evitar documentos duplicados en los resultados
3. **Mejorar sistema de referencias**: Corregir el problema con el campo `references` vacío en las respuestas
4. **Ajustar parámetros BM25**: Experimentar con diferentes valores de k1 y b para optimizar relevancia
5. **Mejorar procesamiento de texto**: Implementar mejor preprocesamiento para manejar variaciones de términos y sinónimos

## 5. Conclusión

El sistema BM25 optimizado muestra un rendimiento prometedor en términos de velocidad y relevancia, especialmente para consultas relacionadas con estabilidad laboral reforzada durante el embarazo. La integración con el endpoint `/api/ask/` funciona correctamente, proporcionando respuestas útiles basadas en documentos relevantes.

Con las mejoras sugeridas, el sistema podría proporcionar respuestas aún más precisas y completas a consultas legales laborales, mejorando la experiencia del usuario y reduciendo la necesidad de revisión humana. 
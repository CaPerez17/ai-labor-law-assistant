#!/usr/bin/env python3
"""
Prueba de Configuración Optimizada
----------------------------------
Este script verifica la configuración optimizada para reducir el consumo de tokens
y muestra estadísticas de uso.
"""

import os
import sys
import json
from pathlib import Path
import logging
from datetime import date, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("optimized_config")

# Asegurar que backend/ esté en sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Importar configuración
import config

def check_optimization_settings():
    """Verifica y muestra la configuración actual de optimización"""
    logger.info("=" * 70)
    logger.info("📊 CONFIGURACIÓN OPTIMIZADA DE TOKENS")
    logger.info("=" * 70)
    
    # Mostrar modelo configurado
    logger.info(f"🤖 Modelo GPT: {config.GPT_MODEL}")
    logger.info(f"📉 Modo economía: {'✅ Activado' if config.ECONOMY_MODE else '❌ Desactivado'}")
    
    # Mostrar límites de tokens
    logger.info(f"🔢 Límite de tokens de salida: {config.MAX_TOKENS_OUTPUT}")
    logger.info(f"📑 Máximo de documentos: {config.MAX_DOCUMENTS}")
    logger.info(f"📏 Máximo caracteres por documento: {config.MAX_CHARS_PER_DOC}")
    
    # Mostrar configuración de caché
    logger.info(f"💾 Caché activado: {'✅ Sí' if config.ENABLE_CACHE else '❌ No'}")
    logger.info(f"📁 Directorio de caché: {config.CACHE_DIR}")
    
    # Mostrar límite diario
    logger.info(f"📅 Límite diario de consultas: {config.DAILY_QUERY_LIMIT}")
    
    # Validar caché
    if not os.path.exists(config.CACHE_DIR):
        logger.warning(f"⚠️ El directorio de caché no existe: {config.CACHE_DIR}")
        try:
            os.makedirs(config.CACHE_DIR, exist_ok=True)
            logger.info(f"✅ Directorio de caché creado: {config.CACHE_DIR}")
        except Exception as e:
            logger.error(f"❌ Error al crear directorio de caché: {str(e)}")
    else:
        cache_files = list(Path(config.CACHE_DIR).glob("*.json"))
        logger.info(f"📊 Archivos en caché: {len(cache_files)}")

def show_usage_statistics():
    """Muestra estadísticas de uso diario"""
    logger.info("\n" + "=" * 70)
    logger.info("📊 ESTADÍSTICAS DE USO")
    logger.info("=" * 70)
    
    usage_file = os.path.join(backend_dir, "usage_stats.json")
    
    if not os.path.exists(usage_file):
        logger.info("❌ No hay estadísticas de uso disponibles.")
        return
        
    try:
        with open(usage_file, 'r', encoding='utf-8') as f:
            usage_data = json.load(f)
            
        if not usage_data:
            logger.info("❌ No hay registros de uso.")
            return
            
        # Mostrar uso diario
        logger.info("📅 Uso diario:")
        total_queries = 0
        
        # Ordenar por fecha (más reciente primero)
        sorted_dates = sorted(usage_data.keys(), reverse=True)
        
        for day in sorted_dates:
            queries = usage_data[day]
            total_queries += queries
            logger.info(f"  - {day}: {queries} consultas")
            
        # Calcular promedio
        avg_queries = total_queries / len(usage_data)
        logger.info(f"\n📈 Total consultas: {total_queries}")
        logger.info(f"📊 Promedio diario: {avg_queries:.2f}")
        
        # Estimar uso de tokens (aproximado)
        avg_tokens_per_query = 1000  # Estimación conservadora con las optimizaciones
        estimated_tokens = total_queries * avg_tokens_per_query
        estimated_cost = estimated_tokens / 1000 * 0.002  # Costo aproximado para gpt-3.5-turbo
        
        logger.info(f"\n💰 Estimación de costos:")
        logger.info(f"  - Tokens estimados: {estimated_tokens:,}")
        logger.info(f"  - Costo aproximado: ${estimated_cost:.2f} USD")
        
    except Exception as e:
        logger.error(f"❌ Error al leer estadísticas de uso: {str(e)}")

def estimate_savings():
    """Estima ahorros con configuración optimizada vs. no optimizada"""
    logger.info("\n" + "=" * 70)
    logger.info("💰 ESTIMACIÓN DE AHORROS")
    logger.info("=" * 70)
    
    # Parámetros originales (estimados)
    original_model = "gpt-4o"
    original_tokens_per_query = 4000  # Input + output
    original_cost_per_1k = 0.01  # $0.01 por 1K tokens para GPT-4
    
    # Parámetros optimizados
    optimized_model = config.GPT_MODEL
    optimized_tokens_per_query = 800  # Con límites estrictos
    optimized_cost_per_1k = 0.002  # $0.002 por 1K tokens para GPT-3.5-turbo
    
    # Calcular para 100 consultas
    sample_queries = 100
    
    # Costo original
    original_total_tokens = sample_queries * original_tokens_per_query
    original_cost = (original_total_tokens / 1000) * original_cost_per_1k
    
    # Costo optimizado
    optimized_total_tokens = sample_queries * optimized_tokens_per_query
    optimized_cost = (optimized_total_tokens / 1000) * optimized_cost_per_1k
    
    # Ahorros
    token_reduction = 100 - (optimized_total_tokens / original_total_tokens * 100)
    cost_savings = original_cost - optimized_cost
    savings_percentage = 100 - (optimized_cost / original_cost * 100)
    
    logger.info(f"Para {sample_queries} consultas:")
    logger.info(f"\n📉 Reducción de tokens: {token_reduction:.1f}%")
    logger.info(f"  - Original: {original_total_tokens:,} tokens ({original_model})")
    logger.info(f"  - Optimizado: {optimized_total_tokens:,} tokens ({optimized_model})")
    
    logger.info(f"\n💰 Ahorros en costos: ${cost_savings:.2f} USD ({savings_percentage:.1f}%)")
    logger.info(f"  - Costo original: ${original_cost:.2f} USD")
    logger.info(f"  - Costo optimizado: ${optimized_cost:.2f} USD")
    
    # Estimación para un presupuesto de $10
    queries_original = int(10 / original_cost * sample_queries)
    queries_optimized = int(10 / optimized_cost * sample_queries)
    
    logger.info(f"\n🔮 Con $10 USD de presupuesto:")
    logger.info(f"  - Configuración original: ~{queries_original} consultas")
    logger.info(f"  - Configuración optimizada: ~{queries_optimized} consultas")
    logger.info(f"  - Aumento de capacidad: {queries_optimized - queries_original} consultas adicionales")

if __name__ == "__main__":
    logger.info("🚀 Verificando configuración optimizada...")
    
    # Comprobar configuración
    check_optimization_settings()
    
    # Mostrar estadísticas
    show_usage_statistics()
    
    # Estimar ahorros
    estimate_savings()
    
    logger.info("\n✅ Verificación completa.") 
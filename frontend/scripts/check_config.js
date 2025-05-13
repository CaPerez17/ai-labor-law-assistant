#!/usr/bin/env node

/**
 * Script para verificar la configuración del frontend
 * --------------------------------------------------
 * Este script comprueba que todas las variables de entorno
 * estén configuradas correctamente para el despliegue.
 */

const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Función para comprobar el archivo .env.production
function checkEnvProduction() {
  console.log('Verificando archivo .env.production...');
  
  const envPath = path.resolve(__dirname, '../.env.production');
  
  if (!fs.existsSync(envPath)) {
    console.error('❌ No se encontró el archivo .env.production');
    return false;
  }
  
  const envConfig = dotenv.parse(fs.readFileSync(envPath));
  
  // Comprobar que las variables obligatorias estén definidas
  const requiredVars = ['VITE_BACKEND_URL', 'VITE_WEBSOCKET_URL'];
  const missingVars = [];
  
  for (const varName of requiredVars) {
    if (!envConfig[varName]) {
      missingVars.push(varName);
    }
  }
  
  if (missingVars.length > 0) {
    console.error('❌ Faltan las siguientes variables en .env.production:');
    missingVars.forEach(v => console.error(`   - ${v}`));
    return false;
  }
  
  // Comprobar que las URLs sean correctas
  const correctBackendUrl = 'https://legalassista.onrender.com';
  const correctWebsocketUrl = 'wss://legalassista.onrender.com/ws';
  
  if (envConfig['VITE_BACKEND_URL'] !== correctBackendUrl) {
    console.error(`❌ VITE_BACKEND_URL es incorrecta:`);
    console.error(`   - Actual: ${envConfig['VITE_BACKEND_URL']}`);
    console.error(`   - Esperada: ${correctBackendUrl}`);
    return false;
  }
  
  if (envConfig['VITE_WEBSOCKET_URL'] !== correctWebsocketUrl) {
    console.error(`❌ VITE_WEBSOCKET_URL es incorrecta:`);
    console.error(`   - Actual: ${envConfig['VITE_WEBSOCKET_URL']}`);
    console.error(`   - Esperada: ${correctWebsocketUrl}`);
    return false;
  }
  
  console.log('✅ El archivo .env.production está correcto');
  return true;
}

// Función para comprobar el archivo config.js
function checkConfigJs() {
  console.log('Verificando archivo src/config.js...');
  
  const configPath = path.resolve(__dirname, '../src/config.js');
  
  if (!fs.existsSync(configPath)) {
    console.error('❌ No se encontró el archivo src/config.js');
    return false;
  }
  
  const configContent = fs.readFileSync(configPath, 'utf8');
  
  // Comprobar que el fallback sea correcto
  const correctBackendUrl = 'https://legalassista.onrender.com';
  const fallbackPattern = /BACKEND_URL = import\.meta\.env\.VITE_BACKEND_URL \|\| ['"]([^'"]+)['"]/;
  
  const fallbackMatch = configContent.match(fallbackPattern);
  if (!fallbackMatch) {
    console.error('❌ No se encontró la definición de BACKEND_URL en config.js');
    return false;
  }
  
  const fallbackUrl = fallbackMatch[1];
  if (fallbackUrl !== correctBackendUrl) {
    console.error(`❌ El fallback de BACKEND_URL es incorrecto:`);
    console.error(`   - Actual: ${fallbackUrl}`);
    console.error(`   - Esperado: ${correctBackendUrl}`);
    return false;
  }
  
  console.log('✅ El archivo src/config.js está correcto');
  return true;
}

// Función para comprobar el archivo index.html
function checkIndexHtml() {
  console.log('Verificando archivo index.html...');
  
  const indexPath = path.resolve(__dirname, '../index.html');
  
  if (!fs.existsSync(indexPath)) {
    console.error('❌ No se encontró el archivo index.html');
    return false;
  }
  
  const indexContent = fs.readFileSync(indexPath, 'utf8');
  
  // Comprobar que contenga el script de emergencia
  const emergencyScriptPattern = /window\.CORRECT_BACKEND_URL = ['"]([^'"]+)['"]/;
  
  const scriptMatch = indexContent.match(emergencyScriptPattern);
  if (!scriptMatch) {
    console.error('❌ No se encontró el script de emergencia en index.html');
    return false;
  }
  
  const correctBackendUrl = 'https://legalassista.onrender.com';
  const scriptUrl = scriptMatch[1];
  if (scriptUrl !== correctBackendUrl) {
    console.error(`❌ La URL en el script de emergencia es incorrecta:`);
    console.error(`   - Actual: ${scriptUrl}`);
    console.error(`   - Esperada: ${correctBackendUrl}`);
    return false;
  }
  
  console.log('✅ El archivo index.html contiene el script de emergencia correcto');
  return true;
}

// Ejecutar todas las comprobaciones
function runAllChecks() {
  console.log('=== VERIFICANDO CONFIGURACIÓN DEL FRONTEND ===\n');
  
  const envCheck = checkEnvProduction();
  const configCheck = checkConfigJs();
  const indexCheck = checkIndexHtml();
  
  console.log('\n=== RESUMEN DE VERIFICACIÓN ===');
  console.log(`✓ .env.production: ${envCheck ? 'CORRECTO' : 'INCORRECTO'}`);
  console.log(`✓ src/config.js: ${configCheck ? 'CORRECTO' : 'INCORRECTO'}`);
  console.log(`✓ index.html: ${indexCheck ? 'CORRECTO' : 'INCORRECTO'}`);
  
  const allCorrect = envCheck && configCheck && indexCheck;
  
  if (allCorrect) {
    console.log('\n✅ CONFIGURACIÓN CORRECTA: El frontend debería conectarse correctamente al backend');
  } else {
    console.log('\n❌ CONFIGURACIÓN INCORRECTA: Es necesario corregir los problemas indicados');
  }
  
  return allCorrect;
}

// Si se ejecuta directamente
if (require.main === module) {
  const result = runAllChecks();
  process.exit(result ? 0 : 1);
}

module.exports = {
  checkEnvProduction,
  checkConfigJs,
  checkIndexHtml,
  runAllChecks
}; 
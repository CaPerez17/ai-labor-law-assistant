/**
 * Script para depurar problemas de login
 * --------------------------------------
 * Este archivo contiene funciones para probar y depurar la conexión
 * con el backend durante el proceso de autenticación.
 */

import { BACKEND_URL } from './config';
import axios from 'axios';

/**
 * Función para probar diferentes métodos de autenticación
 * y mostrar información detallada del proceso.
 */
export const testLoginConnection = async (email, password) => {
  console.log('==== INICIANDO PRUEBA DE CONEXIÓN DE LOGIN ====');
  console.log(`Backend URL: ${BACKEND_URL}`);
  
  // Puntos finales a probar
  const endpoints = [
    `${BACKEND_URL}/api/auth/login`,
    `${BACKEND_URL}/api/auth/status`
  ];
  
  // Comprobar que los endpoints están disponibles
  console.log('\n-- Comprobando disponibilidad de endpoints --');
  
  for (const endpoint of endpoints) {
    try {
      console.log(`Probando: ${endpoint}`);
      const response = await fetch(endpoint, { 
        method: 'GET',
        mode: 'cors'
      });
      
      console.log(`Status: ${response.status}`);
      if (response.ok) {
        const data = await response.json();
        console.log('Respuesta:', data);
      } else {
        console.log('Error en la respuesta');
      }
    } catch (error) {
      console.error(`Error al acceder a ${endpoint}:`, error.message);
    }
  }
  
  // Intentar login con diferentes formatos
  if (!email || !password) {
    console.log('\nNo se proporcionaron credenciales para probar login');
    return;
  }
  
  console.log('\n-- Probando login con diferentes formatos --');
  
  // Método 1: JSON con email/password
  try {
    console.log('\n1. Intentando login con JSON (email/password)');
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
      email: email,
      password: password
    }, {
      headers: { 'Content-Type': 'application/json' }
    });
    
    console.log('✅ Login exitoso con JSON:');
    console.log(`Status: ${response.status}`);
    console.log('Token:', response.data.access_token);
    console.log('User:', response.data.user);
    return response.data;
  } catch (error) {
    console.error('❌ Error con JSON (email/password):', error.message);
    if (error.response) {
      console.log(`Status: ${error.response.status}`);
      console.log('Headers:', error.response.headers);
      console.log('Data:', error.response.data);
    }
  }
  
  // Método 2: FormData
  try {
    console.log('\n2. Intentando login con FormData');
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    console.log('✅ Login exitoso con FormData:');
    console.log(`Status: ${response.status}`);
    console.log('Token:', response.data.access_token);
    console.log('User:', response.data.user);
    return response.data;
  } catch (error) {
    console.error('❌ Error con FormData:', error.message);
    if (error.response) {
      console.log(`Status: ${error.response.status}`);
      console.log('Headers:', error.response.headers);
      console.log('Data:', error.response.data);
    }
  }
  
  // Método 3: URL encoded form
  try {
    console.log('\n3. Intentando login con x-www-form-urlencoded');
    const urlEncodedData = new URLSearchParams();
    urlEncodedData.append('username', email);
    urlEncodedData.append('password', password);
    
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, urlEncodedData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    console.log('✅ Login exitoso con form-urlencoded:');
    console.log(`Status: ${response.status}`);
    console.log('Token:', response.data.access_token);
    console.log('User:', response.data.user);
    return response.data;
  } catch (error) {
    console.error('❌ Error con form-urlencoded:', error.message);
    if (error.response) {
      console.log(`Status: ${error.response.status}`);
      console.log('Headers:', error.response.headers);
      console.log('Data:', error.response.data);
    }
  }
  
  console.log('\n❌ Todos los intentos de login fallaron');
  return null;
};

// Exponer función para usar desde consola
window.testLogin = (email, password) => {
  testLoginConnection(email, password)
    .then(result => {
      if (result) {
        console.log('\n==== TEST DE LOGIN COMPLETADO CON ÉXITO ====');
      } else {
        console.log('\n==== TEST DE LOGIN FALLIDO ====');
      }
    });
};

// Instrucciones para usar desde consola
console.log(`
Para probar el login, abre la consola del navegador en la página de login
y ejecuta la siguiente función:

testLogin('email@ejemplo.com', 'contraseña')

Por ejemplo:
testLogin('admin@legalassista.com', 'admin123')
`);

export default {
  testLoginConnection
}; 
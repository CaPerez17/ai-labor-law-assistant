/**
 * Configuración inicial para pruebas E2E
 * =====================================
 */

const axios = require('axios');

// Configuración global de axios
axios.defaults.timeout = 30000;

// Configuración de variables de entorno para pruebas
process.env.NODE_ENV = 'test';
process.env.BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
process.env.FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// Función para verificar que el backend esté disponible
async function checkBackendHealth() {
    try {
        const response = await axios.get(`${process.env.BACKEND_URL}/health`);
        console.log('✅ Backend disponible');
        return true;
    } catch (error) {
        console.log('⚠️ Backend no disponible, continuando con pruebas...');
        return false;
    }
}

// Función para crear usuario de prueba si no existe
async function createTestUser() {
    try {
        const userData = {
            nombre: 'Abogado Test',
            email: 'abogado@legalassista.com',
            password: 'Abogado123!',
            rol: 'abogado'
        };

        const response = await axios.post(
            `${process.env.BACKEND_URL}/api/v1/auth/register`,
            userData
        );

        console.log('✅ Usuario de prueba creado');
        return true;
    } catch (error) {
        if (error.response?.status === 400 && error.response?.data?.detail?.includes('already registered')) {
            console.log('✅ Usuario de prueba ya existe');
            return true;
        }
        console.log('⚠️ No se pudo crear usuario de prueba:', error.response?.data || error.message);
        return false;
    }
}

// Configuración inicial
beforeAll(async () => {
    console.log('🔧 Configurando entorno de pruebas...');
    
    await checkBackendHealth();
    await createTestUser();
    
    console.log('✅ Configuración completada');
});

module.exports = {
    checkBackendHealth,
    createTestUser
}; 
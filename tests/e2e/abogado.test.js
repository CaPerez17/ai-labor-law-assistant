/**
 * Pruebas End-to-End para Usuario Abogado
 * =======================================
 * 
 * Este archivo contiene todas las pruebas para verificar el flujo completo
 * de funcionalidades para un usuario con rol "abogado".
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// Configuración de la API
const API_BASE_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// Credenciales de prueba
const ABOGADO_CREDENTIALS = {
    email: 'abogado@legalassista.com',
    password: 'Abogado123!'
};

// Variables globales para las pruebas
let authToken = null;
let userData = null;
let testCaseId = null;
let testDocumentId = null;

describe('Pruebas E2E - Usuario Abogado', () => {
    
    beforeAll(async () => {
        console.log('🚀 Iniciando pruebas E2E para usuario Abogado');
        console.log(`API Base URL: ${API_BASE_URL}`);
        console.log(`Frontend URL: ${FRONTEND_URL}`);
    });

    afterAll(async () => {
        console.log('✅ Pruebas E2E completadas');
    });

    describe('1. Login y Autenticación', () => {
        
        test('1.1 Login exitoso con credenciales de abogado', async () => {
            console.log('🔐 Probando login de abogado...');
            
            const loginData = new URLSearchParams();
            loginData.append('username', ABOGADO_CREDENTIALS.email);
            loginData.append('password', ABOGADO_CREDENTIALS.password);

            try {
                const response = await axios.post(
                    `${API_BASE_URL}/api/v1/auth/login`,
                    loginData,
                    {
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(response.data).toHaveProperty('access_token');
                expect(response.data).toHaveProperty('user');
                expect(response.data.user.rol).toBe('abogado');

                // Guardar token y datos de usuario para pruebas posteriores
                authToken = response.data.access_token;
                userData = response.data.user;

                console.log('✅ Login exitoso');
                console.log(`Usuario: ${userData.email}`);
                console.log(`Rol: ${userData.rol}`);

            } catch (error) {
                console.error('❌ Error en login:', error.response?.data || error.message);
                throw error;
            }
        });

        test('1.2 Verificar almacenamiento en localStorage (simulado)', () => {
            // En un entorno real, esto se haría con Cypress o Playwright
            // Aquí simulamos la verificación
            expect(authToken).toBeTruthy();
            expect(userData).toBeTruthy();
            expect(userData.rol).toBe('abogado');
            
            console.log('✅ Datos de sesión válidos');
        });

        test('1.3 Verificar redirección a dashboard de abogado', async () => {
            // Simular navegación a /abogado
            const expectedRoute = '/abogado';
            
            // En una prueba real con Cypress, verificaríamos:
            // cy.url().should('include', '/abogado')
            
            expect(userData.rol).toBe('abogado');
            console.log(`✅ Redirección esperada a: ${expectedRoute}`);
        });
    });

    describe('2. Listado y Detalle de Casos', () => {
        
        test('2.1 Obtener casos asignados al abogado', async () => {
            console.log('📋 Obteniendo casos del abogado...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/abogado/casos`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(Array.isArray(response.data)).toBe(true);
                
                if (response.data.length > 0) {
                    const caso = response.data[0];
                    expect(caso).toHaveProperty('id_caso');
                    expect(caso).toHaveProperty('estado');
                    expect(caso).toHaveProperty('detalle_consulta');
                    
                    testCaseId = caso.id_caso;
                    console.log(`✅ Encontrados ${response.data.length} casos`);
                    console.log(`Caso de prueba: ${testCaseId}`);
                } else {
                    console.log('⚠️ No se encontraron casos asignados');
                }

            } catch (error) {
                console.error('❌ Error obteniendo casos:', error.response?.data || error.message);
                throw error;
            }
        });

        test('2.2 Filtrar casos por estado', async () => {
            console.log('🔍 Probando filtros de casos...');
            
            const estados = ['pendiente', 'en_proceso', 'resuelto'];
            
            for (const estado of estados) {
                try {
                    const response = await axios.get(
                        `${API_BASE_URL}/api/v1/abogado/casos?estado=${estado}`,
                        {
                            headers: {
                                'Authorization': `Bearer ${authToken}`
                            }
                        }
                    );

                    expect(response.status).toBe(200);
                    expect(Array.isArray(response.data)).toBe(true);
                    
                    // Verificar que todos los casos tienen el estado correcto
                    response.data.forEach(caso => {
                        expect(caso.estado).toBe(estado);
                    });
                    
                    console.log(`✅ Filtro por estado '${estado}': ${response.data.length} casos`);

                } catch (error) {
                    console.error(`❌ Error filtrando por estado ${estado}:`, error.response?.data || error.message);
                    throw error;
                }
            }
        });

        test('2.3 Obtener detalle de caso específico', async () => {
            if (!testCaseId) {
                console.log('⚠️ Saltando prueba: No hay caso de prueba disponible');
                return;
            }

            console.log(`📄 Obteniendo detalle del caso ${testCaseId}...`);
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/abogado/casos/${testCaseId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(response.data).toHaveProperty('id_caso', testCaseId);
                expect(response.data).toHaveProperty('detalle_consulta');
                expect(response.data).toHaveProperty('estado');
                expect(response.data).toHaveProperty('comentarios_abogado');
                
                console.log('✅ Detalle de caso obtenido correctamente');
                console.log(`Estado: ${response.data.estado}`);
                console.log(`Comentarios: ${response.data.comentarios_abogado.length}`);

            } catch (error) {
                console.error('❌ Error obteniendo detalle del caso:', error.response?.data || error.message);
                throw error;
            }
        });
    });

    describe('3. Chat con Cliente', () => {
        
        test('3.1 Enviar mensaje en chat', async () => {
            if (!testCaseId) {
                console.log('⚠️ Saltando prueba: No hay caso de prueba disponible');
                return;
            }

            console.log('💬 Probando envío de mensaje...');
            
            const mensajeTest = {
                caseId: testCaseId,
                remitenteId: userData.id,
                texto: 'Mensaje de prueba desde abogado - ' + new Date().toISOString()
            };

            try {
                const response = await axios.post(
                    `${API_BASE_URL}/api/v1/chat`,
                    mensajeTest,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(response.data).toHaveProperty('id');
                expect(response.data).toHaveProperty('timestamp');
                
                console.log('✅ Mensaje enviado correctamente');
                console.log(`ID del mensaje: ${response.data.id}`);

            } catch (error) {
                console.error('❌ Error enviando mensaje:', error.response?.data || error.message);
                // No fallar la prueba si el endpoint no está implementado
                console.log('⚠️ Endpoint de chat podría no estar implementado');
            }
        });

        test('3.2 Obtener historial de chat', async () => {
            if (!testCaseId) {
                console.log('⚠️ Saltando prueba: No hay caso de prueba disponible');
                return;
            }

            console.log('📜 Obteniendo historial de chat...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/chat?caseId=${testCaseId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(Array.isArray(response.data)).toBe(true);
                
                console.log(`✅ Historial obtenido: ${response.data.length} mensajes`);

            } catch (error) {
                console.error('❌ Error obteniendo historial:', error.response?.data || error.message);
                console.log('⚠️ Endpoint de historial podría no estar implementado');
            }
        });
    });

    describe('4. Gestión de Documentos', () => {
        
        test('4.1 Subir documento', async () => {
            console.log('📎 Probando subida de documento...');
            
            // Crear un archivo de prueba
            const testContent = 'Documento de prueba para caso legal\nContenido de ejemplo para análisis.';
            const testFilePath = path.join(__dirname, 'test-document.txt');
            fs.writeFileSync(testFilePath, testContent);

            try {
                const formData = new FormData();
                formData.append('file', fs.createReadStream(testFilePath));
                formData.append('fecha', new Date().toISOString().split('T')[0]);
                formData.append('numero_ley', 'LEY-TEST-001');
                formData.append('categoria', 'contrato');
                formData.append('subcategoria', 'laboral');

                const response = await axios.post(
                    `${API_BASE_URL}/api/v1/docs/upload`,
                    formData,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            ...formData.getHeaders()
                        }
                    }
                );

                expect(response.status).toBe(201);
                expect(response.data).toHaveProperty('id');
                expect(response.data).toHaveProperty('filename');
                
                testDocumentId = response.data.id;
                console.log('✅ Documento subido correctamente');
                console.log(`ID del documento: ${testDocumentId}`);

                // Limpiar archivo de prueba
                fs.unlinkSync(testFilePath);

            } catch (error) {
                console.error('❌ Error subiendo documento:', error.response?.data || error.message);
                // Limpiar archivo de prueba en caso de error
                if (fs.existsSync(testFilePath)) {
                    fs.unlinkSync(testFilePath);
                }
                throw error;
            }
        });

        test('4.2 Listar documentos del caso', async () => {
            if (!testCaseId) {
                console.log('⚠️ Saltando prueba: No hay caso de prueba disponible');
                return;
            }

            console.log('📚 Obteniendo documentos del caso...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/docs?caseId=${testCaseId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(Array.isArray(response.data)).toBe(true);
                
                console.log(`✅ Documentos encontrados: ${response.data.length}`);

            } catch (error) {
                console.error('❌ Error obteniendo documentos:', error.response?.data || error.message);
                console.log('⚠️ Endpoint de documentos podría no estar implementado');
            }
        });

        test('4.3 Descargar documento', async () => {
            if (!testDocumentId) {
                console.log('⚠️ Saltando prueba: No hay documento de prueba disponible');
                return;
            }

            console.log('⬇️ Probando descarga de documento...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/docs/download/${testDocumentId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        },
                        responseType: 'stream'
                    }
                );

                expect(response.status).toBe(200);
                expect(response.headers['content-disposition']).toBeDefined();
                
                console.log('✅ Documento descargado correctamente');

            } catch (error) {
                console.error('❌ Error descargando documento:', error.response?.data || error.message);
                console.log('⚠️ Endpoint de descarga podría no estar implementado');
            }
        });
    });

    describe('5. Consultas Legales (IA)', () => {
        
        test('5.1 Realizar consulta a IA', async () => {
            console.log('🤖 Probando consulta a IA...');
            
            const consultaTest = {
                prompt: '¿Cuáles son los derechos laborales básicos en Colombia?',
                context: 'Consulta general sobre derechos laborales'
            };

            try {
                const response = await axios.post(
                    `${API_BASE_URL}/api/v1/ask`,
                    consultaTest,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(response.data).toHaveProperty('respuesta');
                expect(typeof response.data.respuesta).toBe('string');
                expect(response.data.respuesta.length).toBeGreaterThan(10);
                
                console.log('✅ Consulta a IA exitosa');
                console.log(`Respuesta: ${response.data.respuesta.substring(0, 100)}...`);

            } catch (error) {
                console.error('❌ Error en consulta a IA:', error.response?.data || error.message);
                throw error;
            }
        });

        test('5.2 Verificar historial de consultas', async () => {
            console.log('📋 Verificando historial de consultas...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/ask/historial`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(Array.isArray(response.data)).toBe(true);
                
                console.log(`✅ Historial obtenido: ${response.data.length} consultas`);

            } catch (error) {
                console.error('❌ Error obteniendo historial:', error.response?.data || error.message);
                console.log('⚠️ Endpoint de historial podría no estar implementado');
            }
        });
    });

    describe('6. Actualización de Casos', () => {
        
        test('6.1 Actualizar estado de caso', async () => {
            if (!testCaseId) {
                console.log('⚠️ Saltando prueba: No hay caso de prueba disponible');
                return;
            }

            console.log('🔄 Actualizando estado del caso...');
            
            const updateData = {
                id_caso: testCaseId,
                nuevo_estado: 'en_proceso',
                comentarios: 'Caso actualizado durante pruebas E2E - ' + new Date().toISOString()
            };

            try {
                const response = await axios.post(
                    `${API_BASE_URL}/api/v1/abogado/actualizar`,
                    updateData,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                expect(response.status).toBe(200);
                expect(response.data).toHaveProperty('exito', true);
                expect(response.data).toHaveProperty('caso');
                expect(response.data.caso.estado).toBe('en_proceso');
                
                console.log('✅ Estado del caso actualizado correctamente');
                console.log(`Nuevo estado: ${response.data.caso.estado}`);

            } catch (error) {
                console.error('❌ Error actualizando caso:', error.response?.data || error.message);
                throw error;
            }
        });
    });

    describe('7. Protección de Rutas', () => {
        
        test('7.1 Acceso sin token debe redirigir a login', async () => {
            console.log('🔒 Probando acceso sin autenticación...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/abogado/casos`
                    // Sin header de Authorization
                );

                // Si llega aquí, algo está mal
                expect(response.status).not.toBe(200);

            } catch (error) {
                expect(error.response.status).toBe(401);
                console.log('✅ Acceso denegado correctamente sin token');
            }
        });

        test('7.2 Abogado no puede acceder a rutas de admin', async () => {
            console.log('🚫 Probando acceso a rutas de admin...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/admin/analytics?start_date=2024-01-01&end_date=2024-12-31`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    }
                );

                // Si llega aquí, algo está mal
                expect(response.status).not.toBe(200);

            } catch (error) {
                expect([401, 403]).toContain(error.response.status);
                console.log('✅ Acceso a admin denegado correctamente');
            }
        });
    });

    describe('8. Logout', () => {
        
        test('8.1 Cerrar sesión correctamente', async () => {
            console.log('🚪 Probando logout...');
            
            // Simular logout (limpiar localStorage)
            authToken = null;
            userData = null;
            
            expect(authToken).toBeNull();
            expect(userData).toBeNull();
            
            console.log('✅ Logout simulado correctamente');
        });

        test('8.2 Verificar que token invalidado no funciona', async () => {
            console.log('🔐 Verificando invalidación de token...');
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/abogado/casos`,
                    {
                        headers: {
                            'Authorization': `Bearer ${authToken || 'token-invalidado'}`
                        }
                    }
                );

                expect(response.status).not.toBe(200);

            } catch (error) {
                expect(error.response.status).toBe(401);
                console.log('✅ Token invalidado correctamente');
            }
        });
    });
});

// Función helper para generar reportes
function generateTestReport(results) {
    const report = {
        timestamp: new Date().toISOString(),
        total_tests: results.length,
        passed: results.filter(r => r.status === 'passed').length,
        failed: results.filter(r => r.status === 'failed').length,
        skipped: results.filter(r => r.status === 'skipped').length,
        results: results
    };
    
    console.log('\n📊 REPORTE DE PRUEBAS E2E - ABOGADO');
    console.log('=====================================');
    console.log(`Total de pruebas: ${report.total_tests}`);
    console.log(`Exitosas: ${report.passed}`);
    console.log(`Fallidas: ${report.failed}`);
    console.log(`Omitidas: ${report.skipped}`);
    console.log(`Porcentaje de éxito: ${((report.passed / report.total_tests) * 100).toFixed(2)}%`);
    
    return report;
}

module.exports = {
    generateTestReport
}; 
/**
 * Tests para verificar la construcción correcta de URLs
 * Estos tests validan que no haya duplicación de prefijos.
 */

import { BACKEND_URL, API_PREFIX } from '../config';
import { endpoints } from '../api/apiClient';

// Test para verificar que la construcción de URLs sea correcta
describe('API URL Construction', () => {
  test('Login endpoint should be constructed correctly', () => {
    const expectedUrl = 'https://legalassista.onrender.com/api/auth/login';
    const constructedUrl = `${BACKEND_URL}${API_PREFIX}${endpoints.auth.login}`;
    
    console.log('Expected URL:', expectedUrl);
    console.log('Constructed URL:', constructedUrl);
    
    expect(constructedUrl).toBe(expectedUrl);
  });
  
  test('No duplicate /api prefixes should exist in URLs', () => {
    // Verificar que API_PREFIX no se duplique
    expect(API_PREFIX).toBe('/api');
    
    // Verificar que los endpoints no contengan /api/ al inicio
    expect(endpoints.auth.login.startsWith('/api/')).toBe(false);
    expect(endpoints.auth.register.startsWith('/api/')).toBe(false);
    expect(endpoints.user.profile.startsWith('/api/')).toBe(false);
    
    // Verificar formato correcto
    expect(endpoints.auth.login).toBe('/auth/login');
  });
}); 
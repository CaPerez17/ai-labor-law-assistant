import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

/**
 * Componente para proteger rutas basado en autenticación y roles
 * @param {Object} props
 * @param {React.ReactNode} props.children - Componentes hijos a renderizar si la autenticación es exitosa
 * @param {string} props.requiredRole - Rol requerido para acceder a esta ruta (opcional)
 * @param {React.ReactNode} props.fallback - Componente a mostrar si hay un error (opcional)
 */
const ProtectedRoute = ({ children, requiredRole, fallback }) => {
    console.log('[ProtectedRoute] Verificando acceso...');
    
    // Obtener token y usuario del localStorage
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    console.log('[ProtectedRoute] Token presente:', !!token);
    console.log('[ProtectedRoute] Usuario en localStorage:', !!userStr);
    
    // Si no hay token, redirigir al login
    if (!token) {
        console.log('[ProtectedRoute] No hay token, redirigiendo al login');
        return fallback || <Navigate to="/login" replace />;
    }
    
    // Intentar parsear el usuario
    let user = null;
    try {
        user = userStr ? JSON.parse(userStr) : null;
    } catch (error) {
        console.error('[ProtectedRoute] Error al parsear usuario:', error);
        // Si hay error al parsear, limpiar localStorage y redirigir
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return fallback || <Navigate to="/login" replace />;
    }
    
    // Si no hay usuario válido, redirigir al login
    if (!user) {
        console.log('[ProtectedRoute] No hay usuario válido, redirigiendo al login');
        localStorage.removeItem('token'); // Limpiar token inválido
        return fallback || <Navigate to="/login" replace />;
    }
    
    console.log('[ProtectedRoute] Usuario encontrado:', user.email, 'Rol:', user.rol || user.role);
    
    // Si se requiere un rol específico, verificarlo
    if (requiredRole) {
        const userRole = user.rol || user.role;
        if (userRole !== requiredRole) {
            console.log(`[ProtectedRoute] Rol requerido: ${requiredRole}, rol del usuario: ${userRole}`);
            // Redirigir según el rol del usuario
            if (userRole === 'admin') {
                return <Navigate to="/admin/metricas" replace />;
            } else if (userRole === 'abogado') {
                return <Navigate to="/abogado" replace />;
            } else if (userRole === 'cliente') {
                return <Navigate to="/cliente" replace />;
            } else {
                return <Navigate to="/dashboard" replace />;
            }
        }
    }
    
    console.log('[ProtectedRoute] Acceso autorizado');
    // Si todo está bien, renderizar el contenido protegido
    return children || <Outlet />;
};

export default ProtectedRoute; 
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const PrivateRoute = ({ children, roles }) => {
    const location = useLocation();
    
    console.log('[PrivateRoute] Verificando acceso a ruta protegida');
    
    // Recuperar datos de autenticación con manejo seguro
    const userStr = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    
    console.log('[PrivateRoute] Token existe:', !!token);
    console.log('[PrivateRoute] User data existe:', !!userStr);
    
    // Intentar parsear el usuario con verificación
    let user = null;
    if (userStr) {
        try {
            user = JSON.parse(userStr);
            console.log('[PrivateRoute] Datos de usuario parseados:', user);
            
            // Normalizar el rol para manejar diferentes formatos
            if (!user.rol && user.role) {
                console.log('[PrivateRoute] Normalizando formato de rol (role → rol)');
                user.rol = user.role;
            }
            
            // Normalizar a minúscula para comparaciones consistentes
            if (user.rol) {
                user.rol = user.rol.toLowerCase();
                console.log('[PrivateRoute] Rol normalizado:', user.rol);
            } else {
                console.error('[PrivateRoute] Usuario sin rol definido');
            }
            
        } catch (e) {
            console.error('[PrivateRoute] Error al parsear datos de usuario:', e);
            // Si hay un error de parseo, limpiar el localStorage y redirigir al login
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            return <Navigate to="/login" state={{ from: location }} replace />;
        }
    }

    if (!token || !user) {
        console.log('[PrivateRoute] Acceso denegado: No hay token o datos de usuario');
        // Redirigir al login si no hay token o usuario
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    // Normalizar los roles de entrada a minúscula para comparación
    const normalizedRoles = roles ? roles.map(r => r.toLowerCase()) : [];
    
    if (roles && !normalizedRoles.includes(user.rol)) {
        console.log('[PrivateRoute] Acceso denegado: Rol no autorizado');
        console.log(`[PrivateRoute] Rol del usuario: ${user.rol}, Roles permitidos:`, normalizedRoles);
        
        // Redirigir al dashboard correspondiente según el rol
        switch (user.rol) {
            case 'admin':
                console.log('[PrivateRoute] Redirigiendo a dashboard de admin');
                return <Navigate to="/admin/metricas" replace />;
            case 'abogado':
            case 'lawyer':
                console.log('[PrivateRoute] Redirigiendo a dashboard de abogado');
                return <Navigate to="/abogado" replace />;
            case 'cliente':
            case 'client':
                console.log('[PrivateRoute] Redirigiendo a dashboard de cliente');
                return <Navigate to="/cliente" replace />;
            default:
                console.log('[PrivateRoute] Rol desconocido, redirigiendo al login');
                return <Navigate to="/login" replace />;
        }
    }

    console.log('[PrivateRoute] Acceso permitido');
    return children;
};

export default PrivateRoute; 
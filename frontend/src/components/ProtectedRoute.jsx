import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import ErrorScreen from './ErrorScreen';

/**
 * Componente para proteger rutas basado en autenticación y roles
 * @param {Object} props
 * @param {React.ReactNode} props.children - Componentes hijos a renderizar si la autenticación es exitosa
 * @param {Array<string>} props.roles - Roles permitidos para acceder a esta ruta (opcional)
 * @param {Object} props.user - Objeto de usuario autenticado (opcional)
 * @param {boolean} props.requireAuth - Si se requiere autenticación para esta ruta (por defecto true)
 * @param {React.ReactNode} props.fallback - Componente a mostrar si hay un error (opcional)
 */
const ProtectedRoute = ({ 
    children, 
    roles, 
    user: propUser = null,
    requireAuth = true,
    fallback = null 
}) => {
    const location = useLocation();
    
    console.log('[ProtectedRoute] Verificando acceso a ruta protegida');
    console.log('[ProtectedRoute] Usuario pasado como prop:', propUser);
    
    // Recuperar datos de autenticación solo si no se pasó el usuario como prop
    const userFromStorage = React.useMemo(() => {
        if (propUser) return propUser;
        
        // Solo intentar leer del localStorage si no hay usuario pasado como prop
        const userStr = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        
        console.log('[ProtectedRoute] Token existe:', !!token);
        console.log('[ProtectedRoute] User data existe:', !!userStr);
        
        if (!userStr || !token) return null;
        
        try {
            const parsedUser = JSON.parse(userStr);
            console.log('[ProtectedRoute] Datos de usuario parseados:', parsedUser);
            
            // Normalizar el rol para manejar diferentes formatos
            if (!parsedUser.rol && parsedUser.role) {
                console.log('[ProtectedRoute] Normalizando formato de rol (role → rol)');
                parsedUser.rol = parsedUser.role;
            }
            
            // Normalizar a minúscula para comparaciones consistentes
            if (parsedUser.rol) {
                parsedUser.rol = parsedUser.rol.toLowerCase();
                console.log('[ProtectedRoute] Rol normalizado:', parsedUser.rol);
            } else {
                console.error('[ProtectedRoute] Usuario sin rol definido');
            }
            
            // Marcar esta sesión como restaurada del localStorage para diferenciarlo
            // de las sesiones que vienen de login directo
            parsedUser._restored = true;
            
            return parsedUser;
        } catch (e) {
            console.error('[ProtectedRoute] Error al parsear datos de usuario:', e);
            // No limpiar localStorage aquí, eso podría causar bucles de redirección
            return null;
        }
    }, [propUser]);
    
    // Usuario final a utilizar (prop o localStorage)
    const user = propUser || userFromStorage;
    
    // Verificar autenticación
    if (requireAuth && !user) {
        console.log('[ProtectedRoute] Acceso denegado: No hay datos de usuario válidos');
        
        // Mostrar fallback si existe, sino redirigir
        if (fallback) {
            return fallback;
        }
        
        // Verificar si estamos justo después de login para evitar redireccionamiento circular
        const lastAuthAttempt = sessionStorage.getItem('lastAuthAttempt');
        const now = new Date().getTime();
        
        // Si hubo un intento de autenticación hace menos de 2 segundos, mostrar error en lugar de redirigir
        if (lastAuthAttempt && (now - parseInt(lastAuthAttempt)) < 2000) {
            console.warn('[ProtectedRoute] Posible redirección circular detectada');
            return <ErrorScreen message="Error de autenticación. Intentando restaurar sesión..." />;
        }
        
        // Registrar este intento de autenticación
        sessionStorage.setItem('lastAuthAttempt', now.toString());
        
        // Verificar si hay un token en el localStorage pero no se pudo parsear el usuario
        const token = localStorage.getItem('token');
        if (token) {
            console.warn('[ProtectedRoute] Hay token pero no se pudo recuperar el usuario');
            return <ErrorScreen message="Error al cargar datos de usuario. Por favor intente de nuevo." />;
        }
        
        // Redirigir al login si no hay usuario o fallback
        console.log('[ProtectedRoute] Redirigiendo a login');
        return <Navigate to="/login" state={{ from: location }} replace />;
    }
    
    // Si no se requiere verificación de roles o no hay roles definidos, permitir acceso
    if (!roles || roles.length === 0) {
        console.log('[ProtectedRoute] No se requiere verificación de roles, acceso permitido');
        return children || <Outlet />;
    }
    
    // Normalizar los roles de entrada a minúscula para comparación
    const normalizedRoles = roles.map(r => r.toLowerCase());
    
    // Si el usuario tiene un rol pero no está definido, intentar corregirlo
    if (!user.rol && user.role) {
        user.rol = user.role.toLowerCase();
    }
    
    // Verificar que el usuario tenga un rol válido
    if (!user.rol) {
        console.error('[ProtectedRoute] Usuario sin rol definido');
        
        // Mostrar fallback personalizado o error general
        if (fallback) {
            return fallback;
        }
        
        return <Navigate to="/login" state={{ from: location }} replace />;
    }
    
    // Verificar si el rol del usuario está entre los permitidos
    if (!normalizedRoles.includes(user.rol)) {
        console.log('[ProtectedRoute] Acceso denegado: Rol no autorizado');
        console.log(`[ProtectedRoute] Rol del usuario: ${user.rol}, Roles permitidos:`, normalizedRoles);
        
        // Redirigir al dashboard correspondiente según el rol
        switch (user.rol) {
            case 'admin':
                console.log('[ProtectedRoute] Redirigiendo a dashboard de admin');
                return <Navigate to="/admin/metricas" replace />;
            case 'abogado':
            case 'lawyer':
                console.log('[ProtectedRoute] Redirigiendo a dashboard de abogado');
                return <Navigate to="/abogado" replace />;
            case 'cliente':
            case 'client':
                console.log('[ProtectedRoute] Redirigiendo a dashboard de cliente');
                return <Navigate to="/cliente" replace />;
            default:
                // Si tiene un rol desconocido, mostrar fallback o redirigir a login
                if (fallback) {
                    return fallback;
                }
                return <Navigate to="/login" state={{ from: location }} replace />;
        }
    }

    // Si el usuario tiene el rol correcto, mostrar el contenido protegido
    console.log('[ProtectedRoute] Acceso permitido');
    return children || <Outlet />;
};

export default ProtectedRoute; 
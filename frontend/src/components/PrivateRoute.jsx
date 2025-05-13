import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const PrivateRoute = ({ children, roles }) => {
    const location = useLocation();
    
    // Recuperar datos de autenticación con manejo seguro
    const userStr = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    
    // Intentar parsear el usuario con verificación
    let user = null;
    if (userStr) {
        try {
            user = JSON.parse(userStr);
        } catch (e) {
            console.error('Error al parsear datos de usuario:', e);
            // Si hay un error de parseo, limpiar el localStorage y redirigir al login
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            return <Navigate to="/login" state={{ from: location }} replace />;
        }
    }

    if (!token || !user) {
        // Redirigir al login si no hay token o usuario
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (roles && !roles.includes(user.rol)) {
        // Redirigir al dashboard correspondiente según el rol
        switch (user.rol) {
            case 'ADMIN':
                return <Navigate to="/admin" replace />;
            case 'ABOGADO':
                return <Navigate to="/abogado" replace />;
            case 'CLIENTE':
                return <Navigate to="/cliente" replace />;
            default:
                return <Navigate to="/login" replace />;
        }
    }

    return children;
};

export default PrivateRoute; 
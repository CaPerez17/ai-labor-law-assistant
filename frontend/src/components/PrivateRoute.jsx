import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const PrivateRoute = ({ children, roles }) => {
    const location = useLocation();
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('token');

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
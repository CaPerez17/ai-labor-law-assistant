import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Componente para mostrar pantalla de error reutilizable
 * @param {Object} props - Propiedades del componente
 * @param {string} props.message - Mensaje de error a mostrar
 * @param {Function} props.onRetry - Función a ejecutar al hacer clic en el botón de reintentar (opcional)
 * @param {string} props.buttonText - Texto del botón (opcional, default: "Volver al inicio")
 * @param {Function} props.onBack - Función para volver atrás (opcional)
 */
const ErrorScreen = ({ 
    message = "Ha ocurrido un error inesperado", 
    onRetry, 
    buttonText = "Volver al inicio",
    onBack 
}) => {
    const navigate = useNavigate();
    
    const handleClick = () => {
        if (onRetry) {
            onRetry();
        } else {
            // Verificar si hay un usuario autenticado
            const userStr = localStorage.getItem('user');
            const token = localStorage.getItem('token');
            
            if (userStr && token) {
                try {
                    const user = JSON.parse(userStr);
                    // Redirigir según el rol
                    if (user.rol === 'admin' || user.role === 'admin') {
                        navigate('/admin');
                    } else if (user.rol === 'abogado' || user.role === 'abogado') {
                        navigate('/abogado');
                    } else if (user.rol === 'cliente' || user.role === 'cliente') {
                        navigate('/cliente');
                    } else {
                        navigate('/');
                    }
                } catch (e) {
                    // Si hay error al parsear, ir a la raíz
                    navigate('/');
                }
            } else {
                // Si no hay sesión, ir a login
                navigate('/login');
            }
        }
    };
    
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
            <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                    <svg
                        className="h-10 w-10 text-red-600"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        aria-hidden="true"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Ha ocurrido un error</h2>
                <p className="text-gray-600 mb-6">{message}</p>
                
                <div className="flex flex-col sm:flex-row justify-center space-y-2 sm:space-y-0 sm:space-x-2">
                    {onBack && (
                        <button
                            onClick={onBack}
                            className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 focus:outline-none"
                        >
                            Volver atrás
                        </button>
                    )}
                    
                    <button
                        onClick={handleClick}
                        className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none"
                    >
                        {buttonText}
                    </button>
                </div>
                
                <div className="mt-4 text-xs text-gray-500">
                    <p>Si el problema persiste, por favor contacta a soporte técnico.</p>
                </div>
            </div>
        </div>
    );
};

export default ErrorScreen; 
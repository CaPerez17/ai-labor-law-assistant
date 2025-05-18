import React from 'react';

/**
 * Componente para mostrar pantalla de error reutilizable
 * @param {Object} props - Propiedades del componente
 * @param {string} props.message - Mensaje de error a mostrar
 * @param {Function} props.onRetry - Función a ejecutar al hacer clic en el botón de reintentar (opcional)
 * @param {string} props.buttonText - Texto del botón (opcional, default: "Volver a intentar")
 * @param {Function} props.onBack - Función para volver atrás (opcional)
 */
const ErrorScreen = ({ 
    message = "Ha ocurrido un error inesperado", 
    onRetry, 
    buttonText = "Volver a intentar",
    onBack 
}) => {
    
    // Función por defecto que redirige al login
    const handleDefaultAction = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    };
    
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 px-4">
            <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
                <svg className="h-12 w-12 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <h2 className="text-xl font-semibold text-gray-800 mb-2">Ha ocurrido un error</h2>
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
                        onClick={onRetry || handleDefaultAction}
                        className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 focus:outline-none"
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
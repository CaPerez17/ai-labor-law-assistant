import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const ActivacionCuenta = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        const activarCuenta = async () => {
            try {
                const token = searchParams.get('token');
                if (!token) {
                    throw new Error('Token no proporcionado');
                }

                const response = await axios.post(
                    `${process.env.REACT_APP_API_URL}/auth/activar/${token}`
                );

                setSuccess(true);
                setTimeout(() => {
                    navigate('/login', {
                        state: { message: 'Cuenta activada exitosamente. Por favor, inicia sesión.' }
                    });
                }, 3000);
            } catch (error) {
                setError(error.response?.data?.detail || 'Error al activar la cuenta');
            } finally {
                setLoading(false);
            }
        };

        activarCuenta();
    }, [searchParams, navigate]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-gray-900">
                            Activando tu cuenta...
                        </h2>
                        <div className="mt-4">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-red-600">
                            Error al activar la cuenta
                        </h2>
                        <p className="mt-4 text-gray-600">{error}</p>
                        <button
                            onClick={() => navigate('/login')}
                            className="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                        >
                            Volver al inicio de sesión
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (success) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-green-600">
                            ¡Cuenta activada exitosamente!
                        </h2>
                        <p className="mt-4 text-gray-600">
                            Serás redirigido al inicio de sesión en unos segundos...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return null;
};

export default ActivacionCuenta; 
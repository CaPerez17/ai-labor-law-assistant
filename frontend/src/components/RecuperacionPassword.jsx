import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const RecuperacionPassword = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [formData, setFormData] = useState({
        email: '',
        nueva_password: '',
        confirmar_password: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (searchParams.get('token')) {
                // Restablecer contraseña
                if (formData.nueva_password !== formData.confirmar_password) {
                    throw new Error('Las contraseñas no coinciden');
                }

                if (formData.nueva_password.length < 8) {
                    throw new Error('La contraseña debe tener al menos 8 caracteres');
                }

                await axios.post(
                    `${process.env.REACT_APP_API_URL}/auth/restablecer-password`,
                    {
                        token: searchParams.get('token'),
                        nueva_password: formData.nueva_password
                    }
                );

                setSuccess(true);
                setTimeout(() => {
                    navigate('/login', {
                        state: { message: 'Contraseña restablecida exitosamente. Por favor, inicia sesión.' }
                    });
                }, 3000);
            } else {
                // Solicitar recuperación
                await axios.post(
                    `${process.env.REACT_APP_API_URL}/auth/recuperar-password`,
                    { email: formData.email }
                );

                setSuccess(true);
                setTimeout(() => {
                    navigate('/login', {
                        state: { message: 'Se ha enviado un correo con instrucciones para restablecer tu contraseña.' }
                    });
                }, 3000);
            }
        } catch (error) {
            setError(error.response?.data?.detail || error.message);
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-green-600">
                            ¡Operación exitosa!
                        </h2>
                        <p className="mt-4 text-gray-600">
                            Serás redirigido al inicio de sesión en unos segundos...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
                <div>
                    <h2 className="text-center text-3xl font-extrabold text-gray-900">
                        {searchParams.get('token') ? 'Restablecer Contraseña' : 'Recuperar Contraseña'}
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        {searchParams.get('token')
                            ? 'Ingresa tu nueva contraseña'
                            : 'Ingresa tu correo electrónico para recibir instrucciones'}
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-400 p-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {!searchParams.get('token') ? (
                        <div>
                            <label htmlFor="email" className="sr-only">
                                Correo electrónico
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Correo electrónico"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </div>
                    ) : (
                        <>
                            <div>
                                <label htmlFor="nueva_password" className="sr-only">
                                    Nueva contraseña
                                </label>
                                <input
                                    id="nueva_password"
                                    name="nueva_password"
                                    type="password"
                                    required
                                    className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                    placeholder="Nueva contraseña"
                                    value={formData.nueva_password}
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label htmlFor="confirmar_password" className="sr-only">
                                    Confirmar contraseña
                                </label>
                                <input
                                    id="confirmar_password"
                                    name="confirmar_password"
                                    type="password"
                                    required
                                    className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                    placeholder="Confirmar contraseña"
                                    value={formData.confirmar_password}
                                    onChange={handleChange}
                                />
                            </div>
                        </>
                    )}

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                        >
                            {loading ? (
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                            ) : (
                                searchParams.get('token') ? 'Restablecer Contraseña' : 'Enviar Instrucciones'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default RecuperacionPassword; 
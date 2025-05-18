import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/apiClient';

const RegistroForm = () => {
    const [formData, setFormData] = useState({
        nombre: '',
        apellido: '',
        email: '',
        password: '',
        confirmPassword: '',
        rol: 'cliente', // Valor por defecto
        telefono: '',
        empresa: ''
    });
    
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };
    
    const validateForm = () => {
        // Validación básica
        if (!formData.nombre || !formData.email || !formData.password) {
            setError('Por favor complete todos los campos obligatorios');
            return false;
        }
        
        // Validar formato de email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            setError('Por favor ingrese un correo electrónico válido');
            return false;
        }
        
        // Validar contraseña
        if (formData.password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres');
            return false;
        }
        
        // Validar que las contraseñas coincidan
        if (formData.password !== formData.confirmPassword) {
            setError('Las contraseñas no coinciden');
            return false;
        }
        
        return true;
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        setLoading(true);
        setError('');
        
        try {
            // Crear objeto con los datos a enviar
            const userData = {
                email: formData.email,
                password: formData.password,
                first_name: formData.nombre,
                last_name: formData.apellido,
                role: formData.rol,
                phone: formData.telefono,
                company: formData.empresa
            };
            
            console.log('Registrando usuario con apiClient');
            const response = await apiClient.post('/auth/register', userData);
            
            setSuccess(true);
            
            // Redirigir al login después de un registro exitoso
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        } catch (err) {
            console.error('Error de registro:', err);
            
            if (err.response) {
                // El servidor respondió con un error
                setError(err.response.data.detail || 'Error al crear la cuenta');
            } else if (err.request) {
                // No se recibió respuesta
                setError('No se pudo contactar con el servidor. Intente más tarde.');
            } else {
                setError('Error al procesar la solicitud');
            }
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-md">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Crear cuenta en LegalAssista
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Únete a nuestra plataforma de asistencia legal
                    </p>
                </div>
                
                {error && (
                    <div className="bg-red-50 border-l-4 border-red-400 p-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                    </div>
                )}
                
                {success ? (
                    <div className="bg-green-50 border-l-4 border-green-400 p-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-green-700">
                                    Cuenta creada exitosamente. Redirigiendo al inicio de sesión...
                                </p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                        <div className="rounded-md shadow-sm -space-y-px">
                            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                                <div className="sm:col-span-3">
                                    <label htmlFor="nombre" className="block text-sm font-medium text-gray-700">
                                        Nombre*
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="text"
                                            name="nombre"
                                            id="nombre"
                                            required
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.nombre}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                <div className="sm:col-span-3">
                                    <label htmlFor="apellido" className="block text-sm font-medium text-gray-700">
                                        Apellido
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="text"
                                            name="apellido"
                                            id="apellido"
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.apellido}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>
                                
                                <div className="sm:col-span-6">
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                        Correo electrónico*
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="email"
                                            name="email"
                                            id="email"
                                            required
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.email}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>
                                
                                <div className="sm:col-span-6">
                                    <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                                        Contraseña*
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="password"
                                            name="password"
                                            id="password"
                                            required
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.password}
                                            onChange={handleChange}
                                            placeholder="Mínimo 6 caracteres"
                                        />
                                    </div>
                                </div>
                                
                                <div className="sm:col-span-6">
                                    <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                                        Confirmar contraseña*
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="password"
                                            name="confirmPassword"
                                            id="confirmPassword"
                                            required
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>
                                
                                <div className="sm:col-span-6">
                                    <label htmlFor="rol" className="block text-sm font-medium text-gray-700">
                                        Tipo de usuario*
                                    </label>
                                    <div className="mt-1">
                                        <select
                                            id="rol"
                                            name="rol"
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.rol}
                                            onChange={handleChange}
                                        >
                                            <option value="cliente">Cliente</option>
                                            <option value="lawyer">Abogado</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <div className="sm:col-span-6">
                                    <label htmlFor="telefono" className="block text-sm font-medium text-gray-700">
                                        Teléfono
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="text"
                                            name="telefono"
                                            id="telefono"
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.telefono}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>
                                
                                <div className="sm:col-span-6">
                                    <label htmlFor="empresa" className="block text-sm font-medium text-gray-700">
                                        Empresa (opcional)
                                    </label>
                                    <div className="mt-1">
                                        <input
                                            type="text"
                                            name="empresa"
                                            id="empresa"
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                            value={formData.empresa}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                                {loading ? (
                                    <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                                        <svg className="animate-spin h-5 w-5 text-indigo-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                    </span>
                                ) : (
                                    <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                                        <svg className="h-5 w-5 text-indigo-500 group-hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                                        </svg>
                                    </span>
                                )}
                                {loading ? 'Registrando...' : 'Registrarse'}
                            </button>
                        </div>
                        
                        <div className="text-sm text-center">
                            <p>
                                ¿Ya tienes una cuenta?{' '}
                                <a href="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
                                    Inicia sesión
                                </a>
                            </p>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default RegistroForm; 
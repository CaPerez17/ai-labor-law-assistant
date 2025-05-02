import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

const FacturacionUsuario = () => {
    const [facturas, setFacturas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filtroEstado, setFiltroEstado] = useState('todos');
    const [mostrarModalPago, setMostrarModalPago] = useState(false);
    const [facturaSeleccionada, setFacturaSeleccionada] = useState(null);
    const [searchParams] = useSearchParams();
    const location = useLocation();

    const navigate = useNavigate();

    useEffect(() => {
        cargarFacturas();
        
        // Verificar si venimos de una redirección de MercadoPago
        const path = location.pathname;
        if (path.includes('/facturas/success')) {
            const payment_id = searchParams.get('payment_id');
            const external_reference = searchParams.get('external_reference');
            if (external_reference) {
                verificarPago(external_reference);
            }
        }
    }, [location.pathname, searchParams]);

    const cargarFacturas = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const user = JSON.parse(localStorage.getItem('user'));
            
            if (!token || !user) {
                navigate('/login');
                return;
            }

            const url = filtroEstado === 'todos' 
                ? `${BACKEND_URL}/api/facturas/usuario/${user.id}`
                : `${BACKEND_URL}/api/facturas/usuario/${user.id}?estado=${filtroEstado}`;

            const response = await axios.get(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            setFacturas(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error al cargar las facturas');
        } finally {
            setLoading(false);
        }
    };

    const verificarPago = async (external_reference) => {
        try {
            const response = await axios.get(
                `${BACKEND_URL}/api/v1/pagos/verificar/${external_reference}`,
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
            
            if (response.data.estado === 'pagada') {
                // Recargar facturas y mostrar mensaje de éxito
                await cargarFacturas();
                alert('¡Pago realizado con éxito!');
            } else if (response.data.estado === 'pendiente_pago') {
                alert('Su pago está siendo procesado. El estado se actualizará cuando se complete.');
                await cargarFacturas();
            } else if (response.data.estado === 'rechazada') {
                alert('Lo sentimos, su pago fue rechazado. Por favor intente con otro método de pago.');
                await cargarFacturas();
            }
        } catch (error) {
            setError('Error al verificar el estado del pago');
        }
    };

    const descargarFactura = async (factura) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(
                `${BACKEND_URL}/api/facturas/${factura.id}/pdf`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    responseType: 'blob'
                }
            );

            // Crear URL del blob y descargar
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `factura-${factura.numero_factura}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            setError('Error al descargar la factura');
        }
    };

    const getEstadoColor = (estado) => {
        switch (estado) {
            case 'pendiente':
                return 'bg-yellow-100 text-yellow-800';
            case 'pendiente_pago':
                return 'bg-blue-100 text-blue-800';
            case 'pagada':
                return 'bg-green-100 text-green-800';
            case 'anulada':
                return 'bg-red-100 text-red-800';
            case 'rechazada':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const iniciarPago = async (facturaId) => {
        try {
            setLoading(true);
            const response = await axios.post(
                `${BACKEND_URL}/api/v1/pagos/crear-preferencia/${facturaId}`,
                {},
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
            
            // Redirigir a la página de pago de MercadoPago
            window.location.href = response.data.url;
        } catch (error) {
            setError('Error al iniciar el proceso de pago');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center">
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
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-4">
                    Mis Facturas
                </h1>
                
                <div className="flex space-x-4 mb-4">
                    <select
                        value={filtroEstado}
                        onChange={(e) => setFiltroEstado(e.target.value)}
                        className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                        <option value="todos">Todos los estados</option>
                        <option value="pendiente">Pendientes</option>
                        <option value="pendiente_pago">En proceso de pago</option>
                        <option value="pagada">Pagadas</option>
                        <option value="anulada">Anuladas</option>
                        <option value="rechazada">Rechazadas</option>
                    </select>
                </div>

                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul className="divide-y divide-gray-200">
                        {facturas.map((factura) => (
                            <li key={factura.id}>
                                <div className="px-4 py-4 sm:px-6">
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-indigo-600 truncate">
                                                {factura.numero_factura}
                                            </p>
                                            <p className="mt-1 text-sm text-gray-500">
                                                {factura.servicio}
                                            </p>
                                            {factura.descripcion && (
                                                <p className="mt-1 text-sm text-gray-500">
                                                    {factura.descripcion}
                                                </p>
                                            )}
                                        </div>
                                        <div className="ml-4 flex-shrink-0 flex items-center space-x-4">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoColor(factura.estado)}`}>
                                                {factura.estado}
                                            </span>
                                            <span className="text-sm font-medium text-gray-900">
                                                ${factura.monto.toFixed(2)}
                                            </span>
                                            {(factura.estado === 'pendiente' || factura.estado === 'rechazada') && (
                                                <button
                                                    onClick={() => iniciarPago(factura.id)}
                                                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                                                >
                                                    Pagar con MercadoPago
                                                </button>
                                            )}
                                            {factura.estado === 'pagada' && (
                                                <button
                                                    onClick={() => descargarFactura(factura)}
                                                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                                                >
                                                    Descargar
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                    <div className="mt-2 flex justify-between text-sm text-gray-500">
                                        <div>
                                            <p>
                                                Fecha de emisión: {
                                                    format(new Date(factura.fecha_emision), 'dd/MM/yyyy', { locale: es })
                                                }
                                            </p>
                                        </div>
                                        {factura.fecha_pago && (
                                            <div>
                                                <p>
                                                    Fecha de pago: {
                                                        format(new Date(factura.fecha_pago), 'dd/MM/yyyy', { locale: es })
                                                    }
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                    {factura.metodo_pago && (
                                        <div className="mt-1 text-sm text-gray-500">
                                            <p>Método de pago: {factura.metodo_pago}</p>
                                        </div>
                                    )}
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default FacturacionUsuario; 
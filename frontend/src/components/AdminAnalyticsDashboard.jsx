import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const AdminAnalyticsDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);
    const [dateRange, setDateRange] = useState({
        start: format(new Date().setDate(new Date().getDate() - 30), 'yyyy-MM-dd'),
        end: format(new Date(), 'yyyy-MM-dd')
    });

    useEffect(() => {
        cargarMetricas();
    }, [dateRange]);

    const cargarMetricas = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_URL}/admin/analytics`,
                {
                    params: dateRange,
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
            setData(response.data);
        } catch (error) {
            setError(error.response?.data?.detail || 'Error al cargar las métricas');
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

    if (!data) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <p className="text-gray-500">No hay datos disponibles</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Dashboard de Analytics</h1>
                <p className="mt-2 text-gray-600">Métricas y estadísticas del sistema</p>
            </div>

            {/* Filtros de fecha */}
            <div className="mb-8 flex gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Fecha inicio</label>
                    <input
                        type="date"
                        value={dateRange.start}
                        onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Fecha fin</label>
                    <input
                        type="date"
                        value={dateRange.end}
                        onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                </div>
            </div>

            {/* Tarjetas de métricas */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900">Total Usuarios</h3>
                    <div className="mt-2">
                        <p className="text-2xl font-semibold text-indigo-600">
                            {Object.values(data.total_usuarios).reduce((a, b) => a + b, 0)}
                        </p>
                        <div className="mt-2 text-sm text-gray-500">
                            <p>Admin: {data.total_usuarios.admin}</p>
                            <p>Abogados: {data.total_usuarios.abogado}</p>
                            <p>Clientes: {data.total_usuarios.cliente}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900">Casos</h3>
                    <div className="mt-2">
                        <p className="text-2xl font-semibold text-indigo-600">
                            {data.total_casos}
                        </p>
                        <p className="text-sm text-gray-500">
                            {data.casos_resueltos} resueltos
                        </p>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900">Ingresos Totales</h3>
                    <div className="mt-2">
                        <p className="text-2xl font-semibold text-indigo-600">
                            ${data.ingresos_totales.toLocaleString()}
                        </p>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900">Calificación Promedio</h3>
                    <div className="mt-2">
                        <p className="text-2xl font-semibold text-indigo-600">
                            {data.promedio_calificaciones.toFixed(1)}/5
                        </p>
                    </div>
                </div>
            </div>

            {/* Gráficos */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Gráfico de casos */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Evolución de Casos</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data.evolucion_casos}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="fecha"
                                    tickFormatter={(date) => format(new Date(date), 'dd/MM', { locale: es })}
                                />
                                <YAxis />
                                <Tooltip
                                    labelFormatter={(date) => format(new Date(date), 'dd/MM/yyyy', { locale: es })}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="total"
                                    stroke="#4F46E5"
                                    name="Casos"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Gráfico de ingresos */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Evolución de Ingresos</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data.evolucion_ingresos}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="fecha"
                                    tickFormatter={(date) => format(new Date(date), 'dd/MM', { locale: es })}
                                />
                                <YAxis
                                    tickFormatter={(value) => `$${value.toLocaleString()}`}
                                />
                                <Tooltip
                                    labelFormatter={(date) => format(new Date(date), 'dd/MM/yyyy', { locale: es })}
                                    formatter={(value) => [`$${value.toLocaleString()}`, 'Ingresos']}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="total"
                                    stroke="#10B981"
                                    name="Ingresos"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminAnalyticsDashboard; 
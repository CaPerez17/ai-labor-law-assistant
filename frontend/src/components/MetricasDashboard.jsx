import React, { useState, useEffect } from 'react';
import apiClient, { endpoints } from '../api/apiClient';

const MetricasDashboard = () => {
    const [estadisticas, setEstadisticas] = useState(null);
    const [error, setError] = useState(null);
    const [cargando, setCargando] = useState(true);
    const [exportando, setExportando] = useState(false);

    const cargarEstadisticas = async () => {
        try {
            const response = await apiClient.get(endpoints.metricas.estadisticas);
            setEstadisticas(response.data);
            setError(null);
        } catch (err) {
            console.error('Error al cargar métricas:', err);
            setError(err.response?.data?.detail || err.message || 'Error al cargar métricas');
        } finally {
            setCargando(false);
        }
    };

    const exportarMetricas = async () => {
        setExportando(true);
        try {
            const response = await apiClient.get(endpoints.metricas.exportar, {
                responseType: 'blob'
            });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'metricas_exportadas.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error al exportar métricas:', err);
            setError(err.response?.data?.detail || err.message || 'Error al exportar métricas');
        } finally {
            setExportando(false);
        }
    };

    useEffect(() => {
        cargarEstadisticas();
    }, []);

    if (cargando) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-600">{error}</p>
                <button
                    onClick={cargarEstadisticas}
                    className="mt-2 px-4 py-2 text-sm text-red-600 hover:text-red-800"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900">
                    Dashboard de Métricas
                </h2>
                <button
                    onClick={exportarMetricas}
                    disabled={exportando}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                    {exportando ? 'Exportando...' : 'Exportar CSV'}
                </button>
            </div>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {/* Total de Interacciones */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="p-5">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                            </div>
                            <div className="ml-5 w-0 flex-1">
                                <dl>
                                    <dt className="text-sm font-medium text-gray-500 truncate">
                                        Total de Interacciones
                                    </dt>
                                    <dd className="text-lg font-semibold text-gray-900">
                                        {estadisticas?.total_interacciones || 0}
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Tasa de Éxito */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="p-5">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div className="ml-5 w-0 flex-1">
                                <dl>
                                    <dt className="text-sm font-medium text-gray-500 truncate">
                                        Tasa de Éxito
                                    </dt>
                                    <dd className="text-lg font-semibold text-gray-900">
                                        {estadisticas?.tasa_exito || 0}%
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Calificación Promedio */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="p-5">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                                </svg>
                            </div>
                            <div className="ml-5 w-0 flex-1">
                                <dl>
                                    <dt className="text-sm font-medium text-gray-500 truncate">
                                        Calificación Promedio
                                    </dt>
                                    <dd className="text-lg font-semibold text-gray-900">
                                        {estadisticas?.calificacion_promedio?.toFixed(1) || '0.0'}
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Distribución de Flujos */}
            <div className="mt-8">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Distribución de Flujos
                </h3>
                <div className="bg-white shadow rounded-lg">
                    <div className="p-6">
                        <div className="space-y-4">
                            {estadisticas?.distribucion_flujos?.map((flujo) => (
                                <div key={flujo.flujo} className="flex items-center">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-gray-900">
                                                {flujo.flujo}
                                            </span>
                                            <span className="text-sm text-gray-500">
                                                {flujo.porcentaje}%
                                            </span>
                                        </div>
                                        <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-indigo-600 h-2 rounded-full"
                                                style={{ width: `${flujo.porcentaje}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MetricasDashboard; 
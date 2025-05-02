import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

const AbogadoDashboard = () => {
    const [casos, setCasos] = useState([]);
    const [casoSeleccionado, setCasoSeleccionado] = useState(null);
    const [filtroEstado, setFiltroEstado] = useState('');
    const [filtroRiesgo, setFiltroRiesgo] = useState('');
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);
    const [actualizando, setActualizando] = useState(false);
    const [nuevoComentario, setNuevoComentario] = useState('');
    const [nuevoEstado, setNuevoEstado] = useState('');

    const cargarCasos = async () => {
        setCargando(true);
        setError(null);
        try {
            const params = new URLSearchParams();
            if (filtroEstado) params.append('estado', filtroEstado);
            if (filtroRiesgo) params.append('nivel_riesgo', filtroRiesgo);
            
            const response = await axios.get(`${BACKEND_URL}/api/abogado/casos?${params}`);
            setCasos(response.data);
        } catch (err) {
            setError('Error al cargar los casos');
            console.error('Error:', err);
        } finally {
            setCargando(false);
        }
    };

    useEffect(() => {
        cargarCasos();
    }, [filtroEstado, filtroRiesgo]);

    const handleSeleccionarCaso = async (idCaso) => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/abogado/casos/${idCaso}`);
            setCasoSeleccionado(response.data);
            setNuevoEstado(response.data.estado);
        } catch (err) {
            setError('Error al cargar el caso');
            console.error('Error:', err);
        }
    };

    const handleActualizarCaso = async (e) => {
        e.preventDefault();
        if (!casoSeleccionado) return;

        setActualizando(true);
        setError(null);

        try {
            const response = await axios.post(`${BACKEND_URL}/api/abogado/actualizar`, {
                id_caso: casoSeleccionado.id_caso,
                nuevo_estado: nuevoEstado,
                comentarios: nuevoComentario
            });

            if (response.data.exito) {
                setCasoSeleccionado(response.data.caso);
                setNuevoComentario('');
                await cargarCasos();
            } else {
                setError(response.data.mensaje);
            }
        } catch (err) {
            setError('Error al actualizar el caso');
            console.error('Error:', err);
        } finally {
            setActualizando(false);
        }
    };

    const getEstadoColor = (estado) => {
        switch (estado) {
            case 'pendiente':
                return 'bg-yellow-100 text-yellow-800';
            case 'en_proceso':
                return 'bg-blue-100 text-blue-800';
            case 'resuelto':
                return 'bg-green-100 text-green-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const getRiesgoColor = (riesgo) => {
        switch (riesgo) {
            case 'alto':
                return 'bg-red-100 text-red-800';
            case 'medio':
                return 'bg-orange-100 text-orange-800';
            case 'bajo':
                return 'bg-green-100 text-green-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900">
                    Dashboard de Abogados
                </h2>
                <div className="flex space-x-4">
                    <select
                        value={filtroEstado}
                        onChange={(e) => setFiltroEstado(e.target.value)}
                        className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                        <option value="">Todos los estados</option>
                        <option value="pendiente">Pendiente</option>
                        <option value="en_proceso">En Proceso</option>
                        <option value="resuelto">Resuelto</option>
                    </select>
                    <select
                        value={filtroRiesgo}
                        onChange={(e) => setFiltroRiesgo(e.target.value)}
                        className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                        <option value="">Todos los riesgos</option>
                        <option value="bajo">Bajo</option>
                        <option value="medio">Medio</option>
                        <option value="alto">Alto</option>
                    </select>
                </div>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-red-600">{error}</p>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Lista de Casos */}
                <div className="lg:col-span-1">
                    <div className="bg-white shadow rounded-lg">
                        <div className="p-4 border-b border-gray-200">
                            <h3 className="text-lg font-medium text-gray-900">
                                Casos
                            </h3>
                        </div>
                        <div className="divide-y divide-gray-200">
                            {cargando ? (
                                <div className="p-4 text-center">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
                                </div>
                            ) : casos.length === 0 ? (
                                <div className="p-4 text-center text-gray-500">
                                    No hay casos disponibles
                                </div>
                            ) : (
                                casos.map((caso) => (
                                    <button
                                        key={caso.id_caso}
                                        onClick={() => handleSeleccionarCaso(caso.id_caso)}
                                        className={`w-full p-4 text-left hover:bg-gray-50 ${
                                            casoSeleccionado?.id_caso === caso.id_caso
                                                ? 'bg-indigo-50'
                                                : ''
                                        }`}
                                    >
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">
                                                    Caso #{caso.id_caso}
                                                </p>
                                                <p className="text-sm text-gray-500 truncate">
                                                    {caso.detalle_consulta}
                                                </p>
                                            </div>
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(caso.estado)}`}>
                                                {caso.estado}
                                            </span>
                                        </div>
                                        <div className="mt-2 flex items-center space-x-2">
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiesgoColor(caso.nivel_riesgo)}`}>
                                                {caso.nivel_riesgo}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(caso.fecha_creacion).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </button>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Detalles del Caso */}
                <div className="lg:col-span-2">
                    {casoSeleccionado ? (
                        <div className="bg-white shadow rounded-lg">
                            <div className="p-6">
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">
                                            Caso #{casoSeleccionado.id_caso}
                                        </h3>
                                        <p className="text-sm text-gray-500">
                                            Creado el {new Date(casoSeleccionado.fecha_creacion).toLocaleString()}
                                        </p>
                                    </div>
                                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getEstadoColor(casoSeleccionado.estado)}`}>
                                        {casoSeleccionado.estado}
                                    </span>
                                </div>

                                <div className="space-y-6">
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                                            Detalles del Caso
                                        </h4>
                                        <p className="text-gray-600 bg-gray-50 p-4 rounded-md">
                                            {casoSeleccionado.detalle_consulta}
                                        </p>
                                    </div>

                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                                            Información Adicional
                                        </h4>
                                        <dl className="grid grid-cols-2 gap-4">
                                            <div>
                                                <dt className="text-sm text-gray-500">Flujo</dt>
                                                <dd className="text-sm text-gray-900">{casoSeleccionado.flujo}</dd>
                                            </div>
                                            <div>
                                                <dt className="text-sm text-gray-500">Nivel de Riesgo</dt>
                                                <dd className="text-sm text-gray-900">{casoSeleccionado.nivel_riesgo}</dd>
                                            </div>
                                            {casoSeleccionado.numero_whatsapp && (
                                                <div className="col-span-2">
                                                    <dt className="text-sm text-gray-500">WhatsApp</dt>
                                                    <dd className="text-sm text-gray-900">{casoSeleccionado.numero_whatsapp}</dd>
                                                </div>
                                            )}
                                        </dl>
                                    </div>

                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                                            Comentarios
                                        </h4>
                                        <div className="space-y-4">
                                            {casoSeleccionado.comentarios_abogado.map((comentario, index) => (
                                                <div key={index} className="bg-gray-50 p-4 rounded-md">
                                                    <p className="text-sm text-gray-600">{comentario.texto}</p>
                                                    <p className="text-xs text-gray-500 mt-2">
                                                        {new Date(comentario.fecha).toLocaleString()}
                                                    </p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <form onSubmit={handleActualizarCaso} className="space-y-4">
                                        <div>
                                            <label htmlFor="estado" className="block text-sm font-medium text-gray-700">
                                                Estado
                                            </label>
                                            <select
                                                id="estado"
                                                value={nuevoEstado}
                                                onChange={(e) => setNuevoEstado(e.target.value)}
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                            >
                                                <option value="pendiente">Pendiente</option>
                                                <option value="en_proceso">En Proceso</option>
                                                <option value="resuelto">Resuelto</option>
                                            </select>
                                        </div>

                                        <div>
                                            <label htmlFor="comentario" className="block text-sm font-medium text-gray-700">
                                                Nuevo Comentario
                                            </label>
                                            <textarea
                                                id="comentario"
                                                value={nuevoComentario}
                                                onChange={(e) => setNuevoComentario(e.target.value)}
                                                rows="4"
                                                maxLength="1000"
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                                placeholder="Agrega un comentario sobre el caso..."
                                            />
                                            <p className="mt-1 text-sm text-gray-500">
                                                {nuevoComentario.length}/1000 caracteres
                                            </p>
                                        </div>

                                        <div className="flex justify-end">
                                            <button
                                                type="submit"
                                                disabled={actualizando}
                                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                                            >
                                                {actualizando ? 'Actualizando...' : 'Actualizar Caso'}
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-white shadow rounded-lg p-6 text-center text-gray-500">
                            Selecciona un caso para ver sus detalles
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AbogadoDashboard; 
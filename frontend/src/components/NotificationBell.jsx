import React, { useState, useEffect, useRef } from 'react';
import apiClient from '../api/apiClient';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const NotificationBell = () => {
    const [notificaciones, setNotificaciones] = useState([]);
    const [noLeidas, setNoLeidas] = useState(0);
    const [mostrarDropdown, setMostrarDropdown] = useState(false);
    const dropdownRef = useRef(null);

    useEffect(() => {
        cargarNotificaciones();
        const intervalo = setInterval(cargarNotificaciones, 30000); // Actualizar cada 30 segundos
        return () => clearInterval(intervalo);
    }, []);

    useEffect(() => {
        const handleClickFuera = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setMostrarDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickFuera);
        return () => document.removeEventListener('mousedown', handleClickFuera);
    }, []);

    const cargarNotificaciones = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const [notificacionesRes, noLeidasRes] = await Promise.all([
                apiClient.get('/notificaciones'),
                apiClient.get('/notificaciones/contar-no-leidas')
            ]);

            setNotificaciones(notificacionesRes.data);
            setNoLeidas(noLeidasRes.data.count);
        } catch (error) {
            console.error('Error al cargar notificaciones:', error);
        }
    };

    const marcarComoLeida = async (id) => {
        try {
            await apiClient.post(`/notificaciones/${id}/marcar-leida`);
            cargarNotificaciones();
        } catch (error) {
            console.error('Error al marcar notificación como leída:', error);
        }
    };

    const marcarTodasComoLeidas = async () => {
        try {
            await apiClient.post('/notificaciones/marcar-todas-leidas');
            cargarNotificaciones();
        } catch (error) {
            console.error('Error al marcar todas las notificaciones como leídas:', error);
        }
    };

    const getIconoPorTipo = (tipo) => {
        switch (tipo) {
            case 'escalamiento':
                return '🚨';
            case 'mensaje':
                return '💬';
            case 'factura':
                return '📄';
            case 'pago':
                return '💰';
            default:
                return '📢';
        }
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setMostrarDropdown(!mostrarDropdown)}
                className="relative p-2 text-gray-600 hover:text-gray-800 focus:outline-none"
            >
                <svg
                    className="h-6 w-6"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                </svg>
                {noLeidas > 0 && (
                    <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                        {noLeidas}
                    </span>
                )}
            </button>

            {mostrarDropdown && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg overflow-hidden z-50">
                    <div className="p-4 border-b border-gray-200">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-semibold text-gray-900">Notificaciones</h3>
                            {noLeidas > 0 && (
                                <button
                                    onClick={marcarTodasComoLeidas}
                                    className="text-sm text-indigo-600 hover:text-indigo-800"
                                >
                                    Marcar todas como leídas
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                        {notificaciones.length === 0 ? (
                            <div className="p-4 text-center text-gray-500">
                                No hay notificaciones
                            </div>
                        ) : (
                            notificaciones.map((notificacion) => (
                                <div
                                    key={notificacion.id}
                                    className={`p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer ${
                                        !notificacion.leido ? 'bg-indigo-50' : ''
                                    }`}
                                    onClick={() => marcarComoLeida(notificacion.id)}
                                >
                                    <div className="flex items-start">
                                        <span className="text-xl mr-3">
                                            {getIconoPorTipo(notificacion.tipo)}
                                        </span>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-gray-900">
                                                {notificacion.titulo}
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                {notificacion.mensaje}
                                            </p>
                                            <p className="text-xs text-gray-400 mt-1">
                                                {format(new Date(notificacion.fecha_creacion), 'PPp', { locale: es })}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationBell; 
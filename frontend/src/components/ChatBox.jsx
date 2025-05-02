import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const ChatBox = () => {
    const [conversaciones, setConversaciones] = useState([]);
    const [conversacionActual, setConversacionActual] = useState(null);
    const [mensajes, setMensajes] = useState([]);
    const [nuevoMensaje, setNuevoMensaje] = useState('');
    const [ws, setWs] = useState(null);
    const [error, setError] = useState(null);
    const mensajesEndRef = useRef(null);

    const scrollToBottom = () => {
        mensajesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        cargarConversaciones();
        const user = JSON.parse(localStorage.getItem('user'));
        if (user) {
            const wsClient = new WebSocket(`${process.env.REACT_APP_WS_URL}/ws/${user.id}`);
            
            wsClient.onopen = () => {
                console.log('Conexión WebSocket establecida');
            };
            
            wsClient.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'message') {
                    setMensajes(prev => [...prev, data.data]);
                    marcarMensajeLeido(data.data.id);
                }
            };
            
            wsClient.onerror = (error) => {
                console.error('Error en WebSocket:', error);
                setError('Error en la conexión del chat');
            };
            
            setWs(wsClient);
            
            return () => {
                wsClient.close();
            };
        }
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [mensajes]);

    const cargarConversaciones = async () => {
        try {
            const response = await axios.get(
                `${process.env.REACT_APP_API_URL}/chat/conversaciones`,
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
            setConversaciones(response.data);
        } catch (error) {
            setError('Error al cargar las conversaciones');
        }
    };

    const cargarMensajes = async (userId) => {
        try {
            const response = await axios.get(
                `${process.env.REACT_APP_API_URL}/chat/mensajes/${userId}`,
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
            setMensajes(response.data);
            setConversacionActual(userId);
        } catch (error) {
            setError('Error al cargar los mensajes');
        }
    };

    const marcarMensajeLeido = async (messageId) => {
        try {
            await axios.post(
                `${process.env.REACT_APP_API_URL}/chat/mensajes/${messageId}/leer`,
                {},
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
        } catch (error) {
            console.error('Error al marcar mensaje como leído:', error);
        }
    };

    const enviarMensaje = async (e) => {
        e.preventDefault();
        if (!nuevoMensaje.trim() || !ws || !conversacionActual) return;

        try {
            ws.send(JSON.stringify({
                type: 'message',
                content: nuevoMensaje,
                receiver_id: conversacionActual
            }));
            setNuevoMensaje('');
        } catch (error) {
            setError('Error al enviar el mensaje');
        }
    };

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
        <div className="flex h-screen bg-gray-100">
            {/* Lista de conversaciones */}
            <div className="w-1/4 bg-white border-r">
                <div className="p-4 border-b">
                    <h2 className="text-xl font-semibold text-gray-800">Conversaciones</h2>
                </div>
                <div className="overflow-y-auto h-[calc(100vh-4rem)]">
                    {conversaciones.map((conv) => (
                        <div
                            key={conv.id}
                            onClick={() => cargarMensajes(conv.id)}
                            className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                                conversacionActual === conv.id ? 'bg-indigo-50' : ''
                            }`}
                        >
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="font-medium text-gray-900">{conv.nombre}</h3>
                                    <p className="text-sm text-gray-500 truncate">
                                        {conv.ultimo_mensaje || 'No hay mensajes'}
                                    </p>
                                </div>
                                <div className="flex items-center">
                                    {conv.no_leidos > 0 && (
                                        <span className="bg-indigo-600 text-white text-xs px-2 py-1 rounded-full">
                                            {conv.no_leidos}
                                        </span>
                                    )}
                                    <span className={`ml-2 w-2 h-2 rounded-full ${
                                        conv.online ? 'bg-green-500' : 'bg-gray-300'
                                    }`} />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Área de chat */}
            <div className="flex-1 flex flex-col">
                {conversacionActual ? (
                    <>
                        {/* Cabecera del chat */}
                        <div className="p-4 border-b bg-white">
                            <h2 className="text-xl font-semibold text-gray-800">
                                {conversaciones.find(c => c.id === conversacionActual)?.nombre}
                            </h2>
                        </div>

                        {/* Mensajes */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {mensajes.map((mensaje) => {
                                const esPropio = mensaje.remitente_id === JSON.parse(localStorage.getItem('user')).id;
                                return (
                                    <div
                                        key={mensaje.id}
                                        className={`flex ${esPropio ? 'justify-end' : 'justify-start'}`}
                                    >
                                        <div
                                            className={`max-w-[70%] rounded-lg p-3 ${
                                                esPropio
                                                    ? 'bg-indigo-600 text-white'
                                                    : 'bg-gray-200 text-gray-800'
                                            }`}
                                        >
                                            <p>{mensaje.contenido}</p>
                                            <p className={`text-xs mt-1 ${
                                                esPropio ? 'text-indigo-200' : 'text-gray-500'
                                            }`}>
                                                {format(new Date(mensaje.timestamp), 'HH:mm', { locale: es })}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })}
                            <div ref={mensajesEndRef} />
                        </div>

                        {/* Formulario de envío */}
                        <form onSubmit={enviarMensaje} className="p-4 border-t bg-white">
                            <div className="flex space-x-4">
                                <input
                                    type="text"
                                    value={nuevoMensaje}
                                    onChange={(e) => setNuevoMensaje(e.target.value)}
                                    placeholder="Escribe un mensaje..."
                                    className="flex-1 rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                                    maxLength={500}
                                />
                                <button
                                    type="submit"
                                    disabled={!nuevoMensaje.trim()}
                                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                                >
                                    Enviar
                                </button>
                            </div>
                        </form>
                    </>
                ) : (
                    <div className="flex-1 flex items-center justify-center">
                        <p className="text-gray-500">Selecciona una conversación para comenzar</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatBox; 
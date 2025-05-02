import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

const FeedbackForm = ({ 
    usuarioId,
    flujo,
    onEnviado,
    onCancelar
}) => {
    const [calificacion, setCalificacion] = useState(0);
    const [comentario, setComentario] = useState('');
    const [error, setError] = useState(null);
    const [enviando, setEnviando] = useState(false);
    const [mostrarConfirmacion, setMostrarConfirmacion] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (calificacion === 0) {
            setError('Por favor, selecciona una calificación');
            return;
        }

        setEnviando(true);
        setError(null);

        try {
            const response = await axios.post(`${BACKEND_URL}/api/metricas/feedback/enviar`, {
                usuario_id: usuarioId,
                flujo: flujo,
                calificacion: calificacion,
                comentario: comentario.trim() || undefined
            });

            setMostrarConfirmacion(true);
            if (onEnviado) {
                onEnviado(response.data);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Error al enviar el feedback');
        } finally {
            setEnviando(false);
        }
    };

    if (mostrarConfirmacion) {
        return (
            <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
                <div className="text-center">
                    <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
                        <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        ¡Gracias por tu feedback!
                    </h3>
                    <p className="text-gray-600 mb-4">
                        Tu opinión nos ayuda a mejorar nuestro servicio.
                    </p>
                    <button
                        onClick={onCancelar}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Volver al inicio
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <div className="text-center mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                    ¿Cómo calificarías tu experiencia?
                </h3>
                <p className="text-gray-600">
                    Tu opinión es muy importante para nosotros
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex justify-center space-x-2">
                    {[1, 2, 3, 4, 5].map((estrella) => (
                        <button
                            key={estrella}
                            type="button"
                            onClick={() => setCalificacion(estrella)}
                            className={`p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                                calificacion >= estrella
                                    ? 'text-yellow-400'
                                    : 'text-gray-300'
                            }`}
                        >
                            <svg
                                className="h-8 w-8"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M10 15.585l-6.327 3.323 1.209-7.037L.172 7.323l7.037-1.023L10 0l2.791 6.3 7.037 1.023-4.71 4.548 1.209 7.037L10 15.585z"
                                    clipRule="evenodd"
                                />
                            </svg>
                        </button>
                    ))}
                </div>

                <div>
                    <label htmlFor="comentario" className="block text-sm font-medium text-gray-700 mb-2">
                        Comentario (opcional)
                    </label>
                    <textarea
                        id="comentario"
                        value={comentario}
                        onChange={(e) => setComentario(e.target.value)}
                        maxLength={500}
                        rows="4"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        placeholder="Cuéntanos qué te pareció la experiencia..."
                    />
                    <p className="mt-1 text-sm text-gray-500">
                        {comentario.length}/500 caracteres
                    </p>
                </div>

                {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-red-600">{error}</p>
                    </div>
                )}

                <div className="flex justify-end space-x-4">
                    <button
                        type="button"
                        onClick={onCancelar}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Omitir
                    </button>
                    <button
                        type="submit"
                        disabled={enviando}
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                        {enviando ? 'Enviando...' : 'Enviar feedback'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default FeedbackForm; 
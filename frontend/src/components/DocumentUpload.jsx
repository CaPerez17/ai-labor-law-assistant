import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useSnackbar } from 'notistack';
import apiClient from '../api/apiClient';

const DocumentUpload = () => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [formData, setFormData] = useState({
        fecha: '',
        numeroLey: '',
        categoria: '',
        subcategoria: ''
    });
    const { enqueueSnackbar } = useSnackbar();

    const onDrop = useCallback(acceptedFiles => {
        if (acceptedFiles.length > 0) {
            setFile(acceptedFiles[0]);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        },
        maxFiles: 1
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!file) {
            enqueueSnackbar('Por favor seleccione un archivo', { variant: 'error' });
            return;
        }

        if (!formData.fecha || !formData.numeroLey || !formData.categoria || !formData.subcategoria) {
            enqueueSnackbar('Por favor complete todos los campos', { variant: 'error' });
            return;
        }

        setUploading(true);

        try {
            const data = new FormData();
            data.append('file', file);
            data.append('fecha', formData.fecha);
            data.append('numero_ley', formData.numeroLey);
            data.append('categoria', formData.categoria);
            data.append('subcategoria', formData.subcategoria);

            const response = await apiClient.post('/docs/upload', data, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    console.log(`Upload Progress: ${percentCompleted}%`);
                }
            });

            enqueueSnackbar('Documento subido exitosamente', { variant: 'success' });
            
            // Limpiar formulario
            setFile(null);
            setFormData({
                fecha: '',
                numeroLey: '',
                categoria: '',
                subcategoria: ''
            });
        } catch (error) {
            console.error('Error uploading document:', error);
            enqueueSnackbar(
                error.response?.data?.detail || 'Error al subir el documento',
                { variant: 'error' }
            );
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6">
            <h2 className="text-2xl font-bold mb-6">Subir Documento Legal</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
                <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                        ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'}`}
                >
                    <input {...getInputProps()} />
                    {file ? (
                        <div className="text-indigo-600">
                            <p className="font-medium">{file.name}</p>
                            <p className="text-sm text-gray-500">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                        </div>
                    ) : (
                        <div>
                            <p className="text-gray-600">
                                Arrastre un archivo PDF o DOCX aquí, o haga clic para seleccionar
                            </p>
                            <p className="text-sm text-gray-500 mt-2">
                                Formatos soportados: PDF, DOCX
                            </p>
                        </div>
                    )}
                </div>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Fecha del Documento
                        </label>
                        <input
                            type="date"
                            name="fecha"
                            value={formData.fecha}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Número de Ley
                        </label>
                        <input
                            type="text"
                            name="numeroLey"
                            value={formData.numeroLey}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Categoría
                        </label>
                        <select
                            name="categoria"
                            value={formData.categoria}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            required
                        >
                            <option value="">Seleccione una categoría</option>
                            <option value="contrato">Contrato</option>
                            <option value="despido">Despido</option>
                            <option value="beneficios">Beneficios</option>
                            <option value="seguridad_social">Seguridad Social</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Subcategoría
                        </label>
                        <input
                            type="text"
                            name="subcategoria"
                            value={formData.subcategoria}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            required
                        />
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={uploading || !file}
                        className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white
                            ${uploading || !file
                                ? 'bg-indigo-400 cursor-not-allowed'
                                : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                            }`}
                    >
                        {uploading ? 'Subiendo...' : 'Subir Documento'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default DocumentUpload; 
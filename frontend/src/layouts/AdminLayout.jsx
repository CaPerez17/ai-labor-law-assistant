import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AdminNavbar from '../components/AdminNavbar';
import MetricasDashboard from '../components/MetricasDashboard';
import UsuariosDashboard from '../components/UsuariosDashboard';
import AdminAnalyticsDashboard from '../components/AdminAnalyticsDashboard';

/**
 * Componente de layout para las rutas de administrador
 * Maneja la navegación y las rutas anidadas dentro de /admin
 */
const AdminLayout = ({ user, onLogout }) => {
    // Registrar cada renderizado para debugging
    console.log('[AdminLayout] Renderizando con usuario:', user?.email);
    
    return (
        <div className="min-h-screen bg-gray-100">
            <AdminNavbar user={user} onLogout={onLogout} />
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <Routes>
                    {/* Ruta index redirige automáticamente a métricas */}
                    <Route index element={<Navigate to="metricas" replace />} />
                    
                    {/* Rutas específicas del panel admin */}
                    <Route path="metricas" element={<MetricasDashboard />} />
                    <Route path="usuarios" element={<UsuariosDashboard />} />
                    <Route path="analytics" element={<AdminAnalyticsDashboard />} />
                    
                    {/* Cualquier otra ruta dentro de /admin redirige a métricas */}
                    <Route path="*" element={<Navigate to="metricas" replace />} />
                </Routes>
            </main>
        </div>
    );
};

export default AdminLayout; 
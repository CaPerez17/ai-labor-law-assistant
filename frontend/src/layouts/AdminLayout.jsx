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
    return (
        <>
            <AdminNavbar user={user} onLogout={onLogout} />
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <Routes>
                    <Route index element={<MetricasDashboard />} />
                    <Route path="metricas" element={<MetricasDashboard />} />
                    <Route path="usuarios" element={<UsuariosDashboard />} />
                    <Route path="analytics" element={<AdminAnalyticsDashboard />} />
                    <Route path="*" element={<Navigate to="metricas" replace />} />
                </Routes>
            </main>
        </>
    );
};

export default AdminLayout; 
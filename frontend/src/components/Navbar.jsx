import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      setIsLoggedIn(true);
      try {
        const user = JSON.parse(userStr);
        setUserRole(user.role || 'cliente');
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
    } else {
      setIsLoggedIn(false);
      setUserRole(null);
    }
  }, [location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUserRole(null);
    navigate('/login');
  };

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  return (
    <nav className="bg-indigo-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0">
              <img
                className="h-8 w-auto"
                src="/logo.png"
                alt="LegalAssista"
              />
            </Link>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link
                  to="/"
                  className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                  onClick={closeMenu}
                >
                  Inicio
                </Link>
                <Link
                  to="/servicios"
                  className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                  onClick={closeMenu}
                >
                  Servicios
                </Link>
                {isLoggedIn && (
                  <>
                    <Link
                      to="/asistente"
                      className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                      onClick={closeMenu}
                    >
                      Asistente Legal
                    </Link>
                    <Link
                      to="/documentos"
                      className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                      onClick={closeMenu}
                    >
                      Mis Documentos
                    </Link>
                    <Link
                      to="/indemnizacion"
                      className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                      onClick={closeMenu}
                    >
                      Calculadora
                    </Link>
                    {userRole === 'admin' && (
                      <Link
                        to="/admin"
                        className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                        onClick={closeMenu}
                      >
                        Panel Admin
                      </Link>
                    )}
                    {userRole === 'lawyer' && (
                      <Link
                        to="/abogado"
                        className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                        onClick={closeMenu}
                      >
                        Panel Abogado
                      </Link>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6">
              {isLoggedIn ? (
                <button
                  onClick={handleLogout}
                  className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Cerrar Sesión
                </button>
              ) : (
                <div className="flex space-x-4">
                  <Link
                    to="/login"
                    className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Iniciar Sesión
                  </Link>
                  <Link
                    to="/registro"
                    className="bg-white text-indigo-800 hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Registrarse
                  </Link>
                </div>
              )}
            </div>
          </div>
          <div className="-mr-2 flex md:hidden">
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-white hover:text-white hover:bg-indigo-700 focus:outline-none"
            >
              <span className="sr-only">Abrir menú principal</span>
              {isOpen ? (
                <svg
                  className="h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  className="h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Menú móvil */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link
              to="/"
              className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
              onClick={closeMenu}
            >
              Inicio
            </Link>
            <Link
              to="/servicios"
              className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
              onClick={closeMenu}
            >
              Servicios
            </Link>
            {isLoggedIn && (
              <>
                <Link
                  to="/asistente"
                  className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
                  onClick={closeMenu}
                >
                  Asistente Legal
                </Link>
                <Link
                  to="/documentos"
                  className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
                  onClick={closeMenu}
                >
                  Mis Documentos
                </Link>
                <Link
                  to="/indemnizacion"
                  className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
                  onClick={closeMenu}
                >
                  Calculadora
                </Link>
                {userRole === 'admin' && (
                  <Link
                    to="/admin"
                    className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
                    onClick={closeMenu}
                  >
                    Panel Admin
                  </Link>
                )}
                {userRole === 'lawyer' && (
                  <Link
                    to="/abogado"
                    className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
                    onClick={closeMenu}
                  >
                    Panel Abogado
                  </Link>
                )}
              </>
            )}
          </div>
          <div className="pt-4 pb-3 border-t border-indigo-700">
            <div className="px-2 space-y-1">
              {isLoggedIn ? (
                <button
                  onClick={() => {
                    handleLogout();
                    closeMenu();
                  }}
                  className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium w-full text-left"
                >
                  Cerrar Sesión
                </button>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-white hover:bg-indigo-700 block px-3 py-2 rounded-md text-base font-medium"
                    onClick={closeMenu}
                  >
                    Iniciar Sesión
                  </Link>
                  <Link
                    to="/registro"
                    className="bg-white text-indigo-800 hover:bg-gray-200 block px-3 py-2 rounded-md text-base font-medium"
                    onClick={closeMenu}
                  >
                    Registrarse
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar; 
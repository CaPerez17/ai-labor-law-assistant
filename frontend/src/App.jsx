import React from 'react'
import LegalAssistant from './components/LegalAssistant'

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-700 text-white py-4 shadow-md">
        <div className="container mx-auto px-4">
          <h1 className="text-2xl font-bold">Asistente Legal Laboral con IA</h1>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <LegalAssistant />
      </main>
      <footer className="bg-gray-200 py-4 mt-auto">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>© {new Date().getFullYear()} AI Labor Law Assistant</p>
        </div>
      </footer>
    </div>
  )
}

export default App 
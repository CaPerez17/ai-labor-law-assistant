import React from 'react';

const AlertaRevision = ({ needsReview, reviewReason, onContactRequest }) => {
  if (!needsReview) {
    return (
      <div className="mt-6">
        <button
          onClick={onContactRequest}
          className="text-blue-600 hover:underline text-sm flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Solicitar revisión profesional
        </button>
      </div>
    );
  }

  return (
    <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4 transform transition-opacity duration-300 ease-in-out">
      <p className="text-yellow-700 font-medium">Esta respuesta requiere revisión profesional</p>
      {reviewReason && <p className="text-yellow-600">{reviewReason}</p>}
      
      <button
        onClick={onContactRequest}
        className="mt-3 bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 transition duration-200"
      >
        Solicitar revisión profesional
      </button>
    </div>
  );
};

export default AlertaRevision; 
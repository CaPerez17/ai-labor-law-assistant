import React from 'react';
import AlertaRevision from './AlertaRevision';

const RespuestaLegal = ({ respuesta, onContactRequest }) => {
  if (!respuesta) return null;

  const { 
    response,
    references,
    confidence_score,
    needs_human_review,
    review_reason,
    processing_time_ms
  } = respuesta;

  return (
    <div className="mt-6 transform transition-all duration-500 ease-in-out opacity-100 translate-y-0">
      <div className="border-t pt-4">
        <h3 className="text-lg font-medium mb-3">Respuesta:</h3>
        <p className="text-gray-800 whitespace-pre-line mb-4">{response}</p>
        
        {processing_time_ms && (
          <p className="text-xs text-gray-500 mb-2">
            Tiempo de respuesta: {processing_time_ms / 1000} segundos
          </p>
        )}
        
        {needs_human_review && (
          <AlertaRevision 
            needsReview={true} 
            reviewReason={review_reason} 
            onContactRequest={onContactRequest} 
          />
        )}
        
        {references && references.length > 0 && (
          <div className="mt-4 transform transition-opacity duration-300 ease-in-out">
            <h4 className="text-md font-medium mb-2">Referencias legales:</h4>
            <ul className="list-disc pl-5 text-gray-700">
              {references.map((ref, index) => (
                <li key={index} className="mb-1">{ref}</li>
              ))}
            </ul>
          </div>
        )}
        
        {confidence_score !== undefined && (
          <div className="mt-4 flex items-center transform transition-opacity duration-300 ease-in-out">
            <span className="text-sm text-gray-600 mr-2">Nivel de confianza:</span>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className={`h-2.5 rounded-full ${
                  confidence_score > 0.7 ? 'bg-green-500' : 
                  confidence_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                } transition-all duration-700 ease-in-out`}
                style={{ width: `${confidence_score * 100}%` }}
              ></div>
            </div>
            <span className="text-sm text-gray-600 ml-2">
              {Math.round(confidence_score * 100)}%
            </span>
          </div>
        )}
        
        {!needs_human_review && (
          <AlertaRevision 
            needsReview={false} 
            onContactRequest={onContactRequest} 
          />
        )}
      </div>
    </div>
  );
};

export default RespuestaLegal; 
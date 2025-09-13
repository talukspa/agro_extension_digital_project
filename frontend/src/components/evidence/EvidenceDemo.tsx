'use client';

import { useState } from 'react';
import { EvidenceUpload, EvidenceList } from '@/components/evidence';

// Componente de demostración para mostrar cómo funciona la evidencia
export default function EvidenceDemo() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadComplete = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const sampleQuestion = {
    id: 'demo_question_001',
    action: '¿La finca cuenta con registros actualizados de todas las actividades productivas?',
    valid_answers: ['Sí, cumple totalmente', 'Cumple parcialmente', 'No cumple'],
    verification_detail: 'Revisión de registros físicos o digitales de actividades productivas',
    level: 'Básico',
    points: 3
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">
          Demostración - Evidencia en Preguntas
        </h1>
        <p className="text-gray-600">
          Ejemplo de cómo los usuarios pueden subir evidencia opcional para cada pregunta del estándar
        </p>
      </div>

      {/* Ejemplo de pregunta con evidencia */}
      <div className="border border-gray-200 rounded-lg p-6 bg-white shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <div className="text-lg font-semibold text-gray-900 flex-1">
            {sampleQuestion.action}
          </div>
          <span className="inline-block bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded">
            {sampleQuestion.level}
          </span>
          <span className="inline-block bg-green-500 text-white text-xs font-bold px-2 py-1 rounded">
            {sampleQuestion.points} pts
          </span>
        </div>

        {/* Opciones de respuesta */}
        <div className="mb-4">
          <div className="text-sm font-medium text-gray-700 mb-2">
            Selecciona una opción:
          </div>
          <div className="flex flex-col gap-2">
            {sampleQuestion.valid_answers.map((answer, idx) => (
              <label key={idx} className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={`demo-answer-${sampleQuestion.id}`}
                  className="form-radio text-blue-500 focus:ring-blue-500"
                  defaultChecked={idx === 0} // Seleccionar la primera por defecto para demo
                />
                <span className="text-gray-700 text-sm">{answer}</span>
              </label>
            ))}
          </div>
          
          <div className="mt-3 text-sm text-gray-500 italic">
            Medio de verificación: {sampleQuestion.verification_detail}
          </div>
        </div>

        {/* Componentes de Evidencia */}
        <EvidenceUpload
          questionId={sampleQuestion.id}
          onUploadComplete={handleUploadComplete}
          disabled={false}
        />

        <EvidenceList
          questionId={sampleQuestion.id}
          refreshTrigger={refreshTrigger}
        />
      </div>

      {/* Información adicional */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          ✨ Características de la Evidencia
        </h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-blue-800 mb-2">📁 Tipos de Archivo Soportados</h4>
            <ul className="text-blue-700 space-y-1">
              <li>• Imágenes: JPG, PNG, WEBP</li>
              <li>• Documentos: PDF, DOC, DOCX</li>
              <li>• Tamaño máximo: 10MB</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-blue-800 mb-2">👥 Permisos por Usuario</h4>
            <ul className="text-blue-700 space-y-1">
              <li>• <strong>Business User:</strong> Subir y gestionar su evidencia</li>
              <li>• <strong>Auditor:</strong> Ver toda la evidencia</li>
              <li>• <strong>Admin:</strong> Ver y gestionar toda la evidencia</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-900 mb-3">
          🎯 Flujo de Uso
        </h3>
        <div className="text-sm text-green-800 space-y-2">
          <div className="flex items-center gap-2">
            <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">1</span>
            <span>Responde la pregunta seleccionando una de las opciones</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">2</span>
            <span>Opcionalmente, agrega evidencia arrastrando un archivo o haciendo clic</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">3</span>
            <span>Añade una descripción para contextualizar la evidencia</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">4</span>
            <span>Ve, descarga o elimina la evidencia cuando sea necesario</span>
          </div>
        </div>
      </div>
    </div>
  );
}
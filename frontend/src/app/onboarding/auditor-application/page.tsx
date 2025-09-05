'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { createAuditorProfile, updateUserProfile } from '@/lib/firebase/firestore';
import { USER_TYPES } from '@/lib/types/permissions';

export default function AuditorApplicationPage() {
  const [formData, setFormData] = useState({
    certifications: [''],
    specializations: [''],
    experience: '',
    education: '',
    motivation: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { user, refreshUserData } = useAuth();
  const router = useRouter();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleArrayChange = (field: 'certifications' | 'specializations', index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }));
  };

  const addArrayItem = (field: 'certifications' | 'specializations') => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }));
  };

  const removeArrayItem = (field: 'certifications' | 'specializations', index: number) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsLoading(true);
    setError('');

    try {
      // Filter out empty strings from arrays
      const cleanCertifications = formData.certifications.filter(cert => cert.trim() !== '');
      const cleanSpecializations = formData.specializations.filter(spec => spec.trim() !== '');

      // Create auditor profile
      const auditorProfileId = await createAuditorProfile({
        userId: user.uid,
        certifications: cleanCertifications,
        specializations: cleanSpecializations,
        status: 'pending',
        isActive: true
      });

      // Update user profile to auditor type
      await updateUserProfile(user.uid, {
        userTypeId: USER_TYPES.AUDITOR,
        auditorProfileId: auditorProfileId,
        status: 'pending' // Auditor needs admin approval
      });

      // Refresh user data
      await refreshUserData();

      // Redirect to pending approval page
      router.push('/pending-approval');
      
    } catch (err: any) {
      setError('Error al enviar la aplicación: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Aplicación para Auditor
          </h1>
          <p className="text-lg text-gray-600">
            Completa tu perfil para solicitar convertirte en auditor certificado.
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-8 space-y-8">
          
          {/* Certifications */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Certificaciones *
            </label>
            <p className="text-sm text-gray-500 mb-4">
              Lista tus certificaciones relevantes para auditorías agrícolas
            </p>
            {formData.certifications.map((cert, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={cert}
                  onChange={(e) => handleArrayChange('certifications', index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Ej: Certificación en Agricultura Orgánica ISO 17065"
                  required={index === 0}
                />
                {formData.certifications.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeArrayItem('certifications', index)}
                    className="px-3 py-2 text-red-600 hover:text-red-800"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={() => addArrayItem('certifications')}
              className="mt-2 text-green-600 hover:text-green-800 text-sm font-medium"
            >
              + Agregar certificación
            </button>
          </div>

          {/* Specializations */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Especializaciones *
            </label>
            <p className="text-sm text-gray-500 mb-4">
              Indica tus áreas de especialización en auditorías
            </p>
            {formData.specializations.map((spec, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <select
                  value={spec}
                  onChange={(e) => handleArrayChange('specializations', index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required={index === 0}
                >
                  <option value="">Selecciona una especialización</option>
                  <option value="organic">Agricultura Orgánica</option>
                  <option value="food_safety">Seguridad Alimentaria</option>
                  <option value="good_practices">Buenas Prácticas Agrícolas</option>
                  <option value="sustainability">Sostenibilidad</option>
                  <option value="livestock">Ganadería</option>
                  <option value="aquaculture">Acuicultura</option>
                  <option value="forestry">Silvicultura</option>
                  <option value="processing">Procesamiento de Alimentos</option>
                  <option value="other">Otra</option>
                </select>
                {formData.specializations.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeArrayItem('specializations', index)}
                    className="px-3 py-2 text-red-600 hover:text-red-800"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={() => addArrayItem('specializations')}
              className="mt-2 text-green-600 hover:text-green-800 text-sm font-medium"
            >
              + Agregar especialización
            </button>
          </div>

          {/* Experience */}
          <div>
            <label htmlFor="experience" className="block text-sm font-medium text-gray-700 mb-2">
              Experiencia Relevante *
            </label>
            <textarea
              name="experience"
              id="experience"
              rows={4}
              required
              value={formData.experience}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Describe tu experiencia en auditorías, agricultura, o campos relacionados..."
            />
          </div>

          {/* Education */}
          <div>
            <label htmlFor="education" className="block text-sm font-medium text-gray-700 mb-2">
              Educación *
            </label>
            <textarea
              name="education"
              id="education"
              rows={3}
              required
              value={formData.education}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Incluye grados académicos, cursos relevantes, etc..."
            />
          </div>

          {/* Motivation */}
          <div>
            <label htmlFor="motivation" className="block text-sm font-medium text-gray-700 mb-2">
              Motivación
            </label>
            <textarea
              name="motivation"
              id="motivation"
              rows={3}
              value={formData.motivation}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="¿Por qué quieres ser auditor en nuestra plataforma?"
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-blue-800 text-sm">
                  <strong>Proceso de Revisión:</strong> Tu aplicación será revisada por nuestro equipo de administradores. 
                  Te contactaremos para una entrevista y verificación de credenciales antes de la aprobación final.
                </p>
              </div>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => router.push('/onboarding/user-type')}
              className="flex-1 py-3 px-4 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 font-medium transition-colors duration-200"
            >
              Volver
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className={`flex-1 py-3 px-4 rounded-md font-medium transition-colors duration-200 ${
                isLoading
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Enviando Aplicación...
                </div>
              ) : (
                'Enviar Aplicación'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

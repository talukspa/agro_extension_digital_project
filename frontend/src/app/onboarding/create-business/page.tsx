'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { AppLayout } from '@/components/layouts/AppLayout';
import { Button } from '@/components/ui/Button';
import { createBusiness, updateUserProfile } from '@/lib/firebase/firestore';
import { USER_TYPES } from '@/lib/types/permissions';

export default function CreateBusinessPage() {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    address: '',
    phone: '',
    website: '',
    contactEmail: '',
    industry: 'agriculture', // Default industry
    size: 'small'
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { user, refreshUserData } = useAuth();
  const router = useRouter();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsLoading(true);
    setError('');

    try {
      // Create the business
      const businessId = await createBusiness({
        businessName: formData.name,
        description: formData.description,
        location: formData.address,
        contactPhone: formData.phone,
        website: formData.website,
        contactEmail: formData.contactEmail || user.email,
        businessType: formData.industry,
        ownerId: user.uid,
        status: 'pending',
        subscriptionTier: 'basic',
        isActive: true
      });

      // Update user profile to business_owner type
      await updateUserProfile(user.uid, {
        userTypeId: USER_TYPES.BUSINESS_OWNER,
        businessProfileId: businessId,
        status: 'pending' // Business needs admin approval
      });

      // Reload user data to reflect changes
      await refreshUserData();

      // Redirect to pending approval page
      router.push('/pending-approval');
      
    } catch (err: any) {
      setError('Error al crear la empresa: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-4">
            Registrar Mi Empresa
          </h1>
          <p className="text-lg text-muted-foreground">
            Como propietario, registra tu empresa para obtener certificación agrícola. 
            Podrás gestionar empleados y aprobar solicitudes de acceso.
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

        <form onSubmit={handleSubmit} className="bg-white dark:bg-plum-900 shadow rounded-lg p-8 space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
              Nombre de la Empresa *
            </label>
            <input
              type="text"
              name="name"
              id="name"
              required
              value={formData.name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
              placeholder="Ej: Frutas del Valle S.A."
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
              Descripción
            </label>
            <textarea
              name="description"
              id="description"
              rows={3}
              value={formData.description}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
              placeholder="Describe brevemente tu empresa y actividades principales..."
            />
          </div>

          <div>
            <label htmlFor="industry" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
              Sector *
            </label>
            <select
              name="industry"
              id="industry"
              required
              value={formData.industry}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
            >
              <option value="agriculture">Agricultura</option>
              <option value="livestock">Ganadería</option>
              <option value="forestry">Silvicultura</option>
              <option value="aquaculture">Acuicultura</option>
              <option value="food_processing">Procesamiento de Alimentos</option>
              <option value="other">Otro</option>
            </select>
          </div>

          <div>
            <label htmlFor="size" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
              Tamaño de la Empresa *
            </label>
            <select
              name="size"
              id="size"
              required
              value={formData.size}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
            >
              <option value="small">Pequeña (1-10 empleados)</option>
              <option value="medium">Mediana (11-50 empleados)</option>
              <option value="large">Grande (51+ empleados)</option>
            </select>
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
              Dirección *
            </label>
            <input
              type="text"
              name="address"
              id="address"
              required
              value={formData.address}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
              placeholder="Dirección completa de la empresa"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
                Teléfono *
              </label>
              <input
                type="tel"
                name="phone"
                id="phone"
                required
                value={formData.phone}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
                placeholder="+56 9 1234 5678"
              />
            </div>

            <div>
              <label htmlFor="website" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
                Sitio Web
              </label>
              <input
                type="url"
                name="website"
                id="website"
                value={formData.website}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
                placeholder="https://www.tuempresa.cl"
              />
            </div>
          </div>

          <div>
            <label htmlFor="contactEmail" className="block text-sm font-medium text-plum-800 dark:text-plum-200 mb-2">
              Email de Contacto
            </label>
            <input
              type="email"
              name="contactEmail"
              id="contactEmail"
              value={formData.contactEmail}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
              placeholder={user.email}
            />
            <p className="mt-1 text-sm text-plum-600 dark:text-plum-400">
              Si no se especifica, se usará tu email de registro: {user.email}
            </p>
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
                  <strong>Nota:</strong> Tu solicitud será revisada por nuestro equipo de administradores. 
                  Te notificaremos por email cuando tu empresa sea aprobada y puedas comenzar el proceso de certificación.
                </p>
              </div>
            </div>
          </div>

          <div className="flex space-x-4">
            <Button
              variant="outline"
              onClick={() => router.push('/onboarding/user-type')}
              fullWidth
            >
              Volver
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              variant="primary"
              fullWidth
              isLoading={isLoading}
            >
              {isLoading ? 'Creando Empresa...' : 'Crear Empresa'}
            </Button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
}

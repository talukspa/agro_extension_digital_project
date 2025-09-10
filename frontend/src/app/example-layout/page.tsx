'use client';

import { AppLayout } from '@/components/layouts/AppLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { USER_TYPES } from '@/lib/types/permissions';

export default function ExamplePage() {
  return (
    <ProtectedRoute requiredUserTypes={[USER_TYPES.ADMIN, USER_TYPES.AUDITOR, USER_TYPES.BUSINESS_USER]}>
      <AppLayout>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-border rounded-lg h-96 p-8">
              <h1 className="text-2xl font-bold text-foreground mb-4">
                Página de Ejemplo con Layout
              </h1>
              <p className="text-muted-foreground mb-4">
                Esta página muestra cómo usar el nuevo AppLayout que incluye:
              </p>
              <ul className="list-disc list-inside text-muted-foreground space-y-2">
                <li>Header con navegación</li>
                <li>Botón de cambio de tema</li>
                <li>Información del usuario</li>
                <li>Avatar con colores por tipo de usuario</li>
                <li>Footer</li>
                <li>Todas las variables semánticas CSS aplicadas</li>
              </ul>
            </div>
          </div>
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}

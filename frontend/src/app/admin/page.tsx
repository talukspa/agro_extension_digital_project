'use client';

import { useAuth } from '@/lib/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { 
  getPendingUsers, 
  getPendingBusinesses, 
  getPendingAuditors, 
  approveUser, 
  rejectUser,
  approveBusiness,
  rejectBusiness,
  approveAuditor,
  rejectAuditor,
  getBusinessUserRequests,
  approveBusinessUser,
  rejectBusinessUser,
  getUserProfile,
  getBusiness
} from '@/lib/firebase/firestore';
import { User, Business, AuditorProfile, BusinessUserRequest } from '@/lib/types/auth';
import ProtectedRoute from '@/components/ProtectedRoute';

function AdminDashboard() {
  const { user, userType, loading, signOut } = useAuth();
  const router = useRouter();
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [pendingBusinesses, setPendingBusinesses] = useState<Business[]>([]);
  const [pendingAuditors, setPendingAuditors] = useState<AuditorProfile[]>([]);
  const [pendingBusinessUsers, setPendingBusinessUsers] = useState<(BusinessUserRequest & { user?: User | null; business?: Business | null })[]>([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'users' | 'businesses' | 'auditors' | 'business-users'>('users');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!loading && user && userType?.name === 'admin') {
      loadPendingData();
    }
  }, [user, userType, loading]);

  const loadPendingData = async () => {
    try {
      setDataLoading(true);
      const [users, businesses, auditors, businessUserRequests] = await Promise.all([
        getPendingUsers(),
        getPendingBusinesses(),
        getPendingAuditors(),
        getBusinessUserRequests()
      ]);
      
      setPendingUsers(users);
      setPendingBusinesses(businesses);
      setPendingAuditors(auditors);
      
      // Load additional data for business user requests
      const enrichedBusinessUserRequests = await Promise.all(
        businessUserRequests.map(async (request) => {
          try {
            const [userProfile, businessProfile] = await Promise.all([
              getUserProfile(request.userId),
              getBusiness(request.businessId)
            ]);
            return {
              ...request,
              user: userProfile,
              business: businessProfile
            };
          } catch (error) {
            console.error('Error loading request details:', error);
            return request;
          }
        })
      );
      
      setPendingBusinessUsers(enrichedBusinessUserRequests);
    } catch (error) {
      console.error('Error loading pending data:', error);
    } finally {
      setDataLoading(false);
    }
  };

  const handleApproveUser = async (userId: string) => {
    try {
      await approveUser(userId, user!.uid);
      await loadPendingData();
    } catch (error) {
      console.error('Error approving user:', error);
    }
  };

  const handleRejectUser = async (userId: string, reason: string) => {
    try {
      await rejectUser(userId, user!.uid, reason);
      await loadPendingData();
    } catch (error) {
      console.error('Error rejecting user:', error);
    }
  };

  const handleApproveBusiness = async (businessId: string) => {
    try {
      await approveBusiness(businessId, user!.uid);
      await loadPendingData();
    } catch (error) {
      console.error('Error approving business:', error);
    }
  };

  const handleRejectBusiness = async (businessId: string, reason: string) => {
    try {
      await rejectBusiness(businessId, user!.uid, reason);
      await loadPendingData();
    } catch (error) {
      console.error('Error rejecting business:', error);
    }
  };

  const handleApproveAuditor = async (auditorId: string) => {
    try {
      await approveAuditor(auditorId, user!.uid);
      await loadPendingData();
    } catch (error) {
      console.error('Error approving auditor:', error);
    }
  };

  const handleRejectAuditor = async (auditorId: string, reason: string) => {
    try {
      await rejectAuditor(auditorId, user!.uid, reason);
      await loadPendingData();
    } catch (error) {
      console.error('Error rejecting auditor:', error);
    }
  };

  const handleApproveBusinessUser = async (requestId: string) => {
    try {
      await approveBusinessUser(requestId, user!.uid);
      await loadPendingData();
    } catch (error) {
      console.error('Error approving business user:', error);
    }
  };

  const handleRejectBusinessUser = async (requestId: string, reason: string) => {
    try {
      await rejectBusinessUser(requestId, user!.uid, reason);
      await loadPendingData();
    } catch (error) {
      console.error('Error rejecting business user:', error);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  // Filter functions
  const filterUsers = (users: User[]) => {
    if (!searchTerm) return users;
    return users.filter(user => 
      user.displayName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const filterBusinesses = (businesses: Business[]) => {
    if (!searchTerm) return businesses;
    return businesses.filter(business => 
      business.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      business.contactEmail?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const filterAuditors = (auditors: AuditorProfile[]) => {
    if (!searchTerm) return auditors;
    return auditors.filter(auditor => 
      auditor.certifications?.some(cert => cert.toLowerCase().includes(searchTerm.toLowerCase())) ||
      auditor.specializations?.some(spec => spec.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  const filterBusinessUsers = (businessUsers: (BusinessUserRequest & { user?: User | null; business?: Business | null })[]) => {
    if (!searchTerm) return businessUsers;
    return businessUsers.filter(request => 
      request.user?.displayName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.user?.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.business?.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.requestedRole?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  if (loading || dataLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-plum-50 dark:bg-plum-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-plum-600 mx-auto"></div>
          <p className="mt-4 text-plum-700 dark:text-plum-300">Cargando panel de administración...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-plum-50 dark:bg-plum-950">
      {/* Navigation */}
      <nav className="bg-white dark:bg-plum-900 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-plum-900 dark:text-plum-100">
                  Panel de Administración
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-plum-800 dark:text-plum-200">
                {user?.displayName || user?.email}
              </div>
              <button
                onClick={handleSignOut}
                className="bg-plum-600 hover:bg-plum-700 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Stats Cards */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="bg-white dark:bg-plum-900 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                      <span className="text-yellow-600 font-semibold">{pendingUsers.length}</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-plum-600 dark:text-plum-400 truncate">
                        Usuarios Pendientes
                      </dt>
                      <dd className="text-lg font-medium text-plum-900 dark:text-plum-100">
                        Esperando aprobación
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-plum-900 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">{pendingBusinesses.length}</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-plum-600 dark:text-plum-400 truncate">
                        Empresas Pendientes
                      </dt>
                      <dd className="text-lg font-medium text-plum-900 dark:text-plum-100">
                        Esperando aprobación
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-plum-900 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <span className="text-purple-600 font-semibold">{pendingAuditors.length}</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-plum-600 dark:text-plum-400 truncate">
                        Auditores Pendientes
                      </dt>
                      <dd className="text-lg font-medium text-plum-900 dark:text-plum-100">
                        Esperando aprobación
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-plum-900 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-fresh-100 dark:bg-fresh-900 rounded-full flex items-center justify-center">
                      <span className="text-fresh-600 dark:text-fresh-400 font-semibold">{pendingBusinessUsers.length}</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-plum-600 dark:text-plum-400 truncate">
                        Accesos a Empresas
                      </dt>
                      <dd className="text-lg font-medium text-plum-900 dark:text-plum-100">
                        Solicitudes pendientes
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Search and Tabs */}
          <div className="bg-white dark:bg-plum-900 shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              {/* Search */}
              <div className="mb-4">
                <input
                  type="text"
                  placeholder="Buscar por nombre, email o empresa..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-plum-300 dark:border-plum-700 rounded-md focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
                />
              </div>

              {/* Tabs */}
              <div className="border-b border-plum-200 dark:border-plum-800">
                <nav className="-mb-px flex space-x-8">
                  <button
                    onClick={() => setActiveTab('users')}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'users'
                        ? 'border-plum-500 text-fresh-600 dark:text-fresh-400'
                        : 'border-transparent text-plum-600 dark:text-plum-400 hover:text-plum-800 dark:text-plum-200 hover:border-plum-300 dark:border-plum-700'
                    }`}
                  >
                    Usuarios ({pendingUsers.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('businesses')}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'businesses'
                        ? 'border-plum-500 text-fresh-600 dark:text-fresh-400'
                        : 'border-transparent text-plum-600 dark:text-plum-400 hover:text-plum-800 dark:text-plum-200 hover:border-plum-300 dark:border-plum-700'
                    }`}
                  >
                    Empresas ({pendingBusinesses.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('auditors')}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'auditors'
                        ? 'border-plum-500 text-fresh-600 dark:text-fresh-400'
                        : 'border-transparent text-plum-600 dark:text-plum-400 hover:text-plum-800 dark:text-plum-200 hover:border-plum-300 dark:border-plum-700'
                    }`}
                  >
                    Auditores ({pendingAuditors.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('business-users')}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'business-users'
                        ? 'border-plum-500 text-fresh-600 dark:text-fresh-400'
                        : 'border-transparent text-plum-600 dark:text-plum-400 hover:text-plum-800 dark:text-plum-200 hover:border-plum-300 dark:border-plum-700'
                    }`}
                  >
                    Accesos a Empresas ({pendingBusinessUsers.length})
                  </button>
                </nav>
              </div>
            </div>
          </div>

          {/* Tab Content */}
          <div className="bg-white dark:bg-plum-900 shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              
              {/* Users Tab */}
              {activeTab === 'users' && (
                <div>
                  <h3 className="text-lg leading-6 font-medium text-plum-900 dark:text-plum-100 mb-4">
                    Usuarios Pendientes de Aprobación
                  </h3>
                  {filterUsers(pendingUsers).length > 0 ? (
                    <div className="space-y-4">
                      {filterUsers(pendingUsers).map((pendingUser) => (
                        <div key={pendingUser.uid} className="border border-plum-200 dark:border-plum-800 rounded-lg p-4 hover:bg-plum-50 dark:bg-plum-950">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <div className="flex-shrink-0">
                                  <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                                    <span className="text-sm font-medium text-plum-800 dark:text-plum-200">
                                      {pendingUser.displayName?.charAt(0) || pendingUser.email.charAt(0)}
                                    </span>
                                  </div>
                                </div>
                                <div>
                                  <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
                                    {pendingUser.displayName || 'Sin nombre'}
                                  </h4>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">{pendingUser.email}</p>
                                  <div className="flex items-center space-x-4 mt-1">
                                    <p className="text-xs text-gray-400">
                                      Solicitado: {pendingUser.requestedAt ? new Date(pendingUser.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
                                    </p>
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                      Pendiente
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleApproveUser(pendingUser.uid)}
                                className="bg-plum-600 hover:bg-plum-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Aprobar
                              </button>
                              <button
                                onClick={() => {
                                  const reason = prompt('Razón del rechazo (opcional):');
                                  if (reason !== null) {
                                    handleRejectUser(pendingUser.uid, reason);
                                  }
                                }}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Rechazar
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-plum-600 dark:text-plum-400">
                        {searchTerm ? 'No se encontraron usuarios que coincidan con la búsqueda.' : 'No hay usuarios pendientes de aprobación.'}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Businesses Tab */}
              {activeTab === 'businesses' && (
                <div>
                  <h3 className="text-lg leading-6 font-medium text-plum-900 dark:text-plum-100 mb-4">
                    Empresas Pendientes de Aprobación
                  </h3>
                  {filterBusinesses(pendingBusinesses).length > 0 ? (
                    <div className="space-y-4">
                      {filterBusinesses(pendingBusinesses).map((business) => (
                        <div key={business.id} className="border border-plum-200 dark:border-plum-800 rounded-lg p-4 hover:bg-plum-50 dark:bg-plum-950">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <div className="flex-shrink-0">
                                  <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                                    <span className="text-sm font-medium text-blue-700">
                                      {business.businessName?.charAt(0) || 'E'}
                                    </span>
                                  </div>
                                </div>
                                <div>
                                  <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
                                    {business.businessName || 'Sin nombre'}
                                  </h4>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">
                                    Tipo: {business.businessType || 'No especificado'}
                                  </p>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">
                                    Contacto: {business.contactEmail || 'No especificado'}
                                  </p>
                                  <div className="flex items-center space-x-4 mt-1">
                                    <p className="text-xs text-gray-400">
                                      Solicitado: {business.requestedAt ? new Date(business.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
                                    </p>
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                      Pendiente
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleApproveBusiness(business.id)}
                                className="bg-plum-600 hover:bg-plum-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Aprobar
                              </button>
                              <button
                                onClick={() => {
                                  const reason = prompt('Razón del rechazo (opcional):');
                                  if (reason !== null) {
                                    handleRejectBusiness(business.id, reason);
                                  }
                                }}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Rechazar
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-plum-600 dark:text-plum-400">
                        {searchTerm ? 'No se encontraron empresas que coincidan con la búsqueda.' : 'No hay empresas pendientes de aprobación.'}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Auditors Tab */}
              {activeTab === 'auditors' && (
                <div>
                  <h3 className="text-lg leading-6 font-medium text-plum-900 dark:text-plum-100 mb-4">
                    Auditores Pendientes de Aprobación
                  </h3>
                  {filterAuditors(pendingAuditors).length > 0 ? (
                    <div className="space-y-4">
                      {filterAuditors(pendingAuditors).map((auditor) => (
                        <div key={auditor.id} className="border border-plum-200 dark:border-plum-800 rounded-lg p-4 hover:bg-plum-50 dark:bg-plum-950">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <div className="flex-shrink-0">
                                  <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                                    <span className="text-sm font-medium text-purple-700">A</span>
                                  </div>
                                </div>
                                <div>
                                  <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
                                    Solicitud de Auditor
                                  </h4>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">
                                    Usuario: {auditor.userId}
                                  </p>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">
                                    Certificaciones: {auditor.certifications?.join(', ') || 'N/A'}
                                  </p>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">
                                    Especializaciones: {auditor.specializations?.join(', ') || 'N/A'}
                                  </p>
                                  <div className="flex items-center space-x-4 mt-1">
                                    <p className="text-xs text-gray-400">
                                      Solicitado: {auditor.requestedAt ? new Date(auditor.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
                                    </p>
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                      Pendiente
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleApproveAuditor(auditor.id)}
                                className="bg-plum-600 hover:bg-plum-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Aprobar
                              </button>
                              <button
                                onClick={() => {
                                  const reason = prompt('Razón del rechazo (opcional):');
                                  if (reason !== null) {
                                    handleRejectAuditor(auditor.id, reason);
                                  }
                                }}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Rechazar
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-plum-600 dark:text-plum-400">
                        {searchTerm ? 'No se encontraron auditores que coincidan con la búsqueda.' : 'No hay auditores pendientes de aprobación.'}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Business Users Tab */}
              {activeTab === 'business-users' && (
                <div>
                  <h3 className="text-lg leading-6 font-medium text-plum-900 dark:text-plum-100 mb-4">
                    Solicitudes de Acceso a Empresas
                  </h3>
                  {filterBusinessUsers(pendingBusinessUsers).length > 0 ? (
                    <div className="space-y-4">
                      {filterBusinessUsers(pendingBusinessUsers).map((request) => (
                        <div key={request.id} className="border border-plum-200 dark:border-plum-800 rounded-lg p-4 hover:bg-plum-50 dark:bg-plum-950">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <div className="flex-shrink-0">
                                  <div className="h-10 w-10 rounded-full bg-fresh-100 dark:bg-fresh-900 flex items-center justify-center">
                                    <span className="text-sm font-medium text-fresh-700 dark:text-fresh-300">
                                      {request.user?.displayName?.charAt(0) || request.user?.email?.charAt(0) || 'U'}
                                    </span>
                                  </div>
                                </div>
                                <div>
                                  <h4 className="text-sm font-medium text-plum-900 dark:text-plum-100">
                                    {request.user?.displayName || request.user?.email || 'Usuario desconocido'}
                                  </h4>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">
                                    Quiere unirse a: <span className="font-medium">{request.business?.businessName || 'Empresa desconocida'}</span>
                                  </p>
                                  <p className="text-sm text-plum-600 dark:text-plum-400">
                                    Rol solicitado: <span className="font-medium">{request.requestedRole}</span>
                                  </p>
                                  {request.message && (
                                    <p className="text-sm text-plum-600 dark:text-plum-400">
                                      Mensaje: "{request.message}"
                                    </p>
                                  )}
                                  <div className="flex items-center space-x-4 mt-1">
                                    <p className="text-xs text-gray-400">
                                      Solicitado: {request.requestedAt ? new Date(request.requestedAt).toLocaleDateString('es-ES') : 'N/A'}
                                    </p>
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-fresh-100 dark:bg-fresh-900 text-fresh-800 dark:text-fresh-100">
                                      Pendiente
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleApproveBusinessUser(request.id)}
                                className="bg-plum-600 hover:bg-plum-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Aprobar
                              </button>
                              <button
                                onClick={() => {
                                  const reason = prompt('Razón del rechazo (opcional):');
                                  if (reason !== null) {
                                    handleRejectBusinessUser(request.id, reason);
                                  }
                                }}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                              >
                                Rechazar
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-plum-600 dark:text-plum-400">
                        {searchTerm ? 'No se encontraron solicitudes que coincidan con la búsqueda.' : 'No hay solicitudes de acceso a empresas pendientes.'}
                      </p>
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>

          {/* Summary when all tabs are empty */}
          {pendingUsers.length === 0 && pendingBusinesses.length === 0 && pendingAuditors.length === 0 && pendingBusinessUsers.length === 0 && !searchTerm && (
            <div className="bg-white dark:bg-plum-900 shadow rounded-lg mt-6">
              <div className="px-4 py-5 sm:p-6 text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-fresh-100 dark:bg-fresh-900 mb-4">
                  <svg className="h-6 w-6 text-fresh-600 dark:text-fresh-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-lg leading-6 font-medium text-plum-900 dark:text-plum-100 mb-2">
                  ¡Todo está al día!
                </h3>
                <p className="text-sm text-plum-600 dark:text-plum-400">
                  No hay solicitudes pendientes de aprobación en este momento.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default function AdminPage() {
  return (
    <ProtectedRoute requiredUserTypes={['admin']} requireApproval={true}>
      <AdminDashboard />
    </ProtectedRoute>
  );
}

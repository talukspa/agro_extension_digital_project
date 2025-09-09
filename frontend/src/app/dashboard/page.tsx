'use client';

import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/lib/contexts/AuthContext';
import { USER_TYPES } from '@/lib/types/permissions';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
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

export default function DashboardPage() {
  const { user, userType, loading, signOut, activeBusiness } = useAuth();
  const router = useRouter();
  
  // Admin states
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [pendingBusinesses, setPendingBusinesses] = useState<Business[]>([]);
  const [pendingAuditors, setPendingAuditors] = useState<AuditorProfile[]>([]);
  const [pendingBusinessUsers, setPendingBusinessUsers] = useState<(BusinessUserRequest & { user?: User | null; business?: Business | null })[]>([]);
  const [adminDataLoading, setAdminDataLoading] = useState(false);
  const [activeAdminTab, setActiveAdminTab] = useState<'users' | 'businesses' | 'auditors' | 'business-users'>('users');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  // Load admin data if user is admin
  useEffect(() => {
    if (user && userType?.name === 'admin' && !loading) {
      loadAdminData();
    }
  }, [user, userType, loading]);

  const loadAdminData = async () => {
    try {
      setAdminDataLoading(true);
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
      console.error('Error loading admin data:', error);
    } finally {
      setAdminDataLoading(false);
    }
  };

  useEffect(() => {
    // Redirect based on user type and status
    if (user && !loading) {
      // If user doesn't have a userType, redirect to onboarding
      if (!userType) {
        router.push('/onboarding/user-type');
        return;
      }

      if (user.status === 'pending') {
        router.push('/pending-approval');
        return;
      }
      
      if (user.status === 'rejected') {
        router.push('/access-denied');
        return;
      }

      // Redirect approved users to their appropriate panels
      if (user.status === 'approved') {
        switch (userType.name) {
          case USER_TYPES.ADMIN:
            // Admins stay on dashboard with admin features
            break;
          case USER_TYPES.AUDITOR:
            // TODO: Uncomment when auditor page is ready
            // router.push('/auditor');
            // return;
            break;
          case USER_TYPES.BUSINESS_USER:
            // TODO: Uncomment when business setup flow is ready
            // if (!activeBusiness) {
            //   router.push('/business-setup');
            //   return;
            // }
            break;
          case USER_TYPES.BUSINESS_OWNER:
            // TODO: Uncomment when business setup flow is ready
            // if (!activeBusiness) {
            //   router.push('/business-setup');
            //   return;
            // }
            // Stay on dashboard for business users with active business
            break;
        }
      }
    }
  }, [user, userType, activeBusiness, loading, router]);

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  // Admin approval functions
  const handleApproveUser = async (userId: string) => {
    try {
      await approveUser(userId, user!.uid);
      await loadAdminData();
    } catch (error) {
      console.error('Error approving user:', error);
    }
  };

  const handleRejectUser = async (userId: string, reason: string) => {
    try {
      await rejectUser(userId, user!.uid, reason);
      await loadAdminData();
    } catch (error) {
      console.error('Error rejecting user:', error);
    }
  };

  const handleApproveBusiness = async (businessId: string) => {
    try {
      await approveBusiness(businessId, user!.uid);
      await loadAdminData();
    } catch (error) {
      console.error('Error approving business:', error);
    }
  };

  const handleRejectBusiness = async (businessId: string, reason: string) => {
    try {
      await rejectBusiness(businessId, user!.uid, reason);
      await loadAdminData();
    } catch (error) {
      console.error('Error rejecting business:', error);
    }
  };

  const handleApproveAuditor = async (auditorId: string) => {
    try {
      await approveAuditor(auditorId, user!.uid);
      await loadAdminData();
    } catch (error) {
      console.error('Error approving auditor:', error);
    }
  };

  const handleRejectAuditor = async (auditorId: string, reason: string) => {
    try {
      await rejectAuditor(auditorId, user!.uid, reason);
      await loadAdminData();
    } catch (error) {
      console.error('Error rejecting auditor:', error);
    }
  };

  const handleApproveBusinessUser = async (requestId: string) => {
    try {
      await approveBusinessUser(requestId, user!.uid);
      await loadAdminData();
    } catch (error) {
      console.error('Error approving business user:', error);
    }
  };

  const handleRejectBusinessUser = async (requestId: string, reason: string) => {
    try {
      await rejectBusinessUser(requestId, user!.uid, reason);
      await loadAdminData();
    } catch (error) {
      console.error('Error rejecting business user:', error);
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  if (!userType) {
    // This should redirect to onboarding, but show loading in case of race condition
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Configurando perfil...</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-fresh-100 dark:bg-fresh-900 text-fresh-800 dark:text-fresh-100';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'suspended': return 'bg-muted text-foreground';
      default: return 'bg-muted text-foreground';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved': return 'Aprobado';
      case 'pending': return 'Pendiente';
      case 'rejected': return 'Rechazado';
      case 'suspended': return 'Suspendido';
      default: return 'Desconocido';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="bg-card shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-foreground">
                  Agro Extension Digital
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {userType?.name === 'admin' && (
                <Button
                  onClick={() => router.push('/admin')}
                  variant="accent"
                  size="sm"
                >
                  Panel Admin Completo
                </Button>
              )}
              <div className="text-sm text-foreground">
                Hola, {user.displayName || user.email}
              </div>
              <Button
                onClick={handleSignOut}
                variant="secondary"
                size="sm"
              >
                Cerrar sesión
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-card overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-foreground mb-4">
                Panel de Control
              </h2>
              
              {/* User Info */}
              <div className="bg-background rounded-lg p-4 mb-6">
                <h3 className="text-sm font-medium text-foreground mb-2">
                  Información del Usuario
                </h3>
                <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Email:</dt>
                    <dd className="text-sm text-foreground">{user.email}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Nombre:</dt>
                    <dd className="text-sm text-foreground">{user.displayName || 'No especificado'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Tipo de Usuario:</dt>
                    <dd className="text-sm text-foreground">{userType?.displayName || 'Cargando...'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Estado:</dt>
                    <dd className="text-sm text-foreground">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(user.status)}`}>
                        {getStatusText(user.status)}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Activo:</dt>
                    <dd className="text-sm text-foreground">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.isActive 
                          ? 'bg-fresh-100 dark:bg-fresh-900 text-fresh-800 dark:text-fresh-100' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.isActive ? 'Sí' : 'No'}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">UID:</dt>
                    <dd className="text-sm text-foreground font-mono">{user.uid}</dd>
                  </div>
                </dl>
              </div>

              {/* Business Info */}
              {activeBusiness && (
                <div className="bg-blue-50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium text-foreground mb-2">
                    Empresa Activa
                  </h3>
                  <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Nombre:</dt>
                      <dd className="text-sm text-foreground">{activeBusiness.businessName}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Plan:</dt>
                      <dd className="text-sm text-foreground">
                        <span className="capitalize">{activeBusiness.subscriptionTier}</span>
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Estado:</dt>
                      <dd className="text-sm text-foreground">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(activeBusiness.status)}`}>
                          {getStatusText(activeBusiness.status)}
                        </span>
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-muted-foreground">Activa:</dt>
                      <dd className="text-sm text-foreground">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          activeBusiness.isActive 
                            ? 'bg-fresh-100 dark:bg-fresh-900 text-fresh-800 dark:text-fresh-100' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {activeBusiness.isActive ? 'Sí' : 'No'}
                        </span>
                      </dd>
                    </div>
                  </dl>
                </div>
              )}

              {/* Status-based Information */}
              {user.status === 'pending' && (
                <div className="bg-yellow-50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium text-foreground mb-2">
                    Estado de Aprobación
                  </h3>
                  <p className="text-sm text-foreground">
                    Tu cuenta está pendiente de aprobación por parte del administrador. 
                    Recibirás una notificación una vez que sea revisada.
                  </p>
                  {user.requestedAt && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Solicitado el: {new Date(user.requestedAt).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )}

              {user.status === 'rejected' && (
                <div className="bg-red-50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium text-foreground mb-2">
                    Acceso Denegado
                  </h3>
                  <p className="text-sm text-foreground">
                    Tu solicitud de acceso ha sido rechazada.
                  </p>
                  {user.rejectionReason && (
                    <p className="text-sm text-muted-foreground mt-2">
                      Razón: {user.rejectionReason}
                    </p>
                  )}
                </div>
              )}

              {/* Admin Panel Section */}
              {user.status === 'approved' && userType?.name === 'admin' && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-foreground mb-4">
                    Panel de Administración
                  </h3>
                  
                  {/* Admin Stats Cards */}
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
                    <div className="bg-card overflow-hidden shadow rounded-lg border border-yellow-200">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                              <span className="text-yellow-600 font-semibold">{pendingUsers.length}</span>
                            </div>
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-muted-foreground truncate">
                                Usuarios Pendientes
                              </dt>
                              <dd className="text-lg font-medium text-foreground">
                                Esperando aprobación
                              </dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-card overflow-hidden shadow rounded-lg border border-blue-200">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-blue-600 font-semibold">{pendingBusinesses.length}</span>
                            </div>
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-muted-foreground truncate">
                                Empresas Pendientes
                              </dt>
                              <dd className="text-lg font-medium text-foreground">
                                Esperando aprobación
                              </dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-card overflow-hidden shadow rounded-lg border border-purple-200">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                              <span className="text-purple-600 font-semibold">{pendingAuditors.length}</span>
                            </div>
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-muted-foreground truncate">
                                Auditores Pendientes
                              </dt>
                              <dd className="text-lg font-medium text-foreground">
                                Esperando aprobación
                              </dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-card overflow-hidden shadow rounded-lg border border-green-200">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-fresh-100 dark:bg-fresh-900 rounded-full flex items-center justify-center">
                              <span className="text-green-600 font-semibold">{pendingBusinessUsers.length}</span>
                            </div>
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-muted-foreground truncate">
                                Accesos a Empresas
                              </dt>
                              <dd className="text-lg font-medium text-foreground">
                                Solicitudes pendientes
                              </dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Information Banner */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-blue-800">
                          Proceso de Aprobación de Empresas
                        </h3>
                        <div className="mt-2 text-sm text-blue-700">
                          <p>
                            Cuando apruebas una empresa, automáticamente se aprueba también el propietario (business_owner). 
                            Si rechazas la empresa, el propietario también será rechazado.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Admin Quick Actions */}
                  <div className="bg-card shadow rounded-lg mb-6">
                    <div className="px-4 py-5 sm:p-6">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="text-lg font-medium text-foreground">
                          Gestión de Solicitudes
                        </h4>
                        <Button
                          onClick={() => router.push('/admin')}
                          size="sm"
                        >
                          Ver Panel Completo
                        </Button>
                      </div>
                      
                      {/* Quick tabs */}
                      <div className="border-b border-gray-200 mb-4">
                        <nav className="-mb-px flex space-x-8">
                          <Button
                            onClick={() => setActiveAdminTab('users')}
                            variant="ghost"
                            size="sm"
                            className={`py-2 px-1 border-b-2 font-medium text-sm ${
                              activeAdminTab === 'users'
                                ? 'border-plum-500 text-muted-foreground'
                                : 'border-transparent text-muted-foreground hover:text-plum-800 dark:hover:text-plum-200 hover:border-gray-300'
                            }`}
                          >
                            Usuarios ({pendingUsers.length})
                          </Button>
                          <Button
                            onClick={() => setActiveAdminTab('businesses')}
                            variant="ghost"
                            size="sm"
                            className={`py-2 px-1 border-b-2 font-medium text-sm ${
                              activeAdminTab === 'businesses'
                                ? 'border-plum-500 text-muted-foreground'
                                : 'border-transparent text-muted-foreground hover:text-plum-800 dark:hover:text-plum-200 hover:border-gray-300'
                            }`}
                          >
                            Empresas ({pendingBusinesses.length})
                          </Button>
                          <Button
                            onClick={() => setActiveAdminTab('auditors')}
                            variant="ghost"
                            size="sm"
                            className={`py-2 px-1 border-b-2 font-medium text-sm ${
                              activeAdminTab === 'auditors'
                                ? 'border-plum-500 text-muted-foreground'
                                : 'border-transparent text-muted-foreground hover:text-plum-800 dark:hover:text-plum-200 hover:border-gray-300'
                            }`}
                          >
                            Auditores ({pendingAuditors.length})
                          </Button>
                          <Button
                            onClick={() => setActiveAdminTab('business-users')}
                            variant="ghost"
                            size="sm"
                            className={`py-2 px-1 border-b-2 font-medium text-sm ${
                              activeAdminTab === 'business-users'
                                ? 'border-plum-500 text-muted-foreground'
                                : 'border-transparent text-muted-foreground hover:text-plum-800 dark:hover:text-plum-200 hover:border-gray-300'
                            }`}
                          >
                            Accesos ({pendingBusinessUsers.length})
                          </Button>
                        </nav>
                      </div>

                      {/* Tab Content - Simplified view */}
                      <div className="max-h-96 overflow-y-auto">
                        {activeAdminTab === 'users' && (
                          <div className="space-y-3">
                            {pendingUsers.slice(0, 5).map((pendingUser) => (
                              <div key={pendingUser.uid} className="flex items-center justify-between p-3 bg-background rounded-lg">
                                <div>
                                  <p className="font-medium text-foreground">{pendingUser.displayName || pendingUser.email}</p>
                                  <p className="text-sm text-muted-foreground">{pendingUser.email}</p>
                                </div>
                                <div className="flex space-x-2">
                                  <Button
                                    onClick={() => handleApproveUser(pendingUser.uid)}
                                    variant="success"
                                    size="sm"
                                  >
                                    Aprobar
                                  </Button>
                                  <Button
                                    onClick={() => {
                                      const reason = prompt('Razón del rechazo (opcional):');
                                      if (reason !== null) {
                                        handleRejectUser(pendingUser.uid, reason);
                                      }
                                    }}
                                    variant="error"
                                    size="sm"
                                  >
                                    Rechazar
                                  </Button>
                                </div>
                              </div>
                            ))}
                            {pendingUsers.length === 0 && (
                              <p className="text-muted-foreground text-center py-4">No hay usuarios pendientes</p>
                            )}
                            {pendingUsers.length > 5 && (
                              <p className="text-sm text-muted-foreground text-center">
                                Y {pendingUsers.length - 5} más... 
                                <button 
                                  onClick={() => router.push('/admin')} 
                                  className="text-green-600 hover:text-green-700 ml-1"
                                >
                                  Ver todos
                                </button>
                              </p>
                            )}
                          </div>
                        )}

                        {activeAdminTab === 'businesses' && (
                          <div className="space-y-3">
                            {pendingBusinesses.slice(0, 5).map((business) => (
                              <div key={business.id} className="flex items-center justify-between p-3 bg-background rounded-lg">
                                <div className="flex-1">
                                  <p className="font-medium text-foreground">{business.businessName}</p>
                                  <p className="text-sm text-muted-foreground">{business.businessType}</p>
                                  {(business as any).ownerInfo && (
                                    <p className="text-xs text-blue-600 mt-1">
                                      Propietario: {(business as any).ownerInfo.displayName || (business as any).ownerInfo.email}
                                      {(business as any).ownerInfo.status === 'pending' && (
                                        <span className="ml-1 text-orange-600">(También pendiente)</span>
                                      )}
                                    </p>
                                  )}
                                </div>
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => handleApproveBusiness(business.id)}
                                    className="bg-plum-600 hover:bg-plum-700 text-white px-3 py-1 rounded text-sm"
                                    title={(business as any).ownerInfo?.status === 'pending' ? 'Aprobará tanto la empresa como el propietario' : 'Aprobar empresa'}
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
                                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                                    title={(business as any).ownerInfo?.status === 'pending' ? 'Rechazará tanto la empresa como el propietario' : 'Rechazar empresa'}
                                  >
                                    Rechazar
                                  </button>
                                </div>
                              </div>
                            ))}
                            {pendingBusinesses.length === 0 && (
                              <p className="text-muted-foreground text-center py-4">No hay empresas pendientes</p>
                            )}
                            {pendingBusinesses.length > 5 && (
                              <p className="text-sm text-muted-foreground text-center">
                                Y {pendingBusinesses.length - 5} más... 
                                <button 
                                  onClick={() => router.push('/admin')} 
                                  className="text-green-600 hover:text-green-700 ml-1"
                                >
                                  Ver todos
                                </button>
                              </p>
                            )}
                          </div>
                        )}

                        {activeAdminTab === 'auditors' && (
                          <div className="space-y-3">
                            {pendingAuditors.slice(0, 5).map((auditor) => (
                              <div key={auditor.id} className="flex items-center justify-between p-3 bg-background rounded-lg">
                                <div>
                                  <p className="font-medium text-foreground">Auditor: {auditor.userId}</p>
                                  <p className="text-sm text-muted-foreground">
                                    {auditor.certifications?.slice(0, 2).join(', ')}
                                    {auditor.certifications && auditor.certifications.length > 2 && '...'}
                                  </p>
                                </div>
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => handleApproveAuditor(auditor.id)}
                                    className="bg-plum-600 hover:bg-plum-700 text-white px-3 py-1 rounded text-sm"
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
                                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                                  >
                                    Rechazar
                                  </button>
                                </div>
                              </div>
                            ))}
                            {pendingAuditors.length === 0 && (
                              <p className="text-muted-foreground text-center py-4">No hay auditores pendientes</p>
                            )}
                            {pendingAuditors.length > 5 && (
                              <p className="text-sm text-muted-foreground text-center">
                                Y {pendingAuditors.length - 5} más... 
                                <button 
                                  onClick={() => router.push('/admin')} 
                                  className="text-green-600 hover:text-green-700 ml-1"
                                >
                                  Ver todos
                                </button>
                              </p>
                            )}
                          </div>
                        )}

                        {activeAdminTab === 'business-users' && (
                          <div className="space-y-3">
                            {pendingBusinessUsers.slice(0, 5).map((request) => (
                              <div key={request.id} className="flex items-center justify-between p-3 bg-background rounded-lg">
                                <div>
                                  <p className="font-medium text-foreground">
                                    {request.user?.displayName || request.user?.email}
                                  </p>
                                  <p className="text-sm text-muted-foreground">
                                    → {request.business?.businessName} ({request.requestedRole})
                                  </p>
                                </div>
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => handleApproveBusinessUser(request.id)}
                                    className="bg-plum-600 hover:bg-plum-700 text-white px-3 py-1 rounded text-sm"
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
                                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                                  >
                                    Rechazar
                                  </button>
                                </div>
                              </div>
                            ))}
                            {pendingBusinessUsers.length === 0 && (
                              <p className="text-muted-foreground text-center py-4">No hay solicitudes de acceso pendientes</p>
                            )}
                            {pendingBusinessUsers.length > 5 && (
                              <p className="text-sm text-muted-foreground text-center">
                                Y {pendingBusinessUsers.length - 5} más... 
                                <button 
                                  onClick={() => router.push('/admin')} 
                                  className="text-green-600 hover:text-green-700 ml-1"
                                >
                                  Ver todos
                                </button>
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Quick Actions */}
              {user.status === 'approved' && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium text-foreground mb-4">
                    Acciones Rápidas
                  </h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <button 
                      className="bg-plum-600 hover:bg-plum-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Ver Estándares
                    </button>
                    <button 
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Subir Evidencia
                    </button>
                    <button 
                      className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Ver Auditorías
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

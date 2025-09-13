"use client";

import React, { useEffect, useState } from "react";
import { collection, getDocs, db } from "@/lib/firebase/utils";
import { useAuth } from "@/lib/contexts/AuthContext";
import { Button } from "@/components/ui/Button";
import { Avatar } from "@/components/ui/Avatar";
import { USER_TYPE_DISPLAY_NAMES, USER_TYPES } from "@/lib/types/permissions";
import { useTheme } from "@/lib/contexts/ThemeContext";
import { EvidenceUpload, EvidenceList } from "@/components/evidence";
import { Tabs, type NestedTabItem } from "@/components/ui/Tabs";

// Helper para obtener el total de acciones y respuestas seleccionadas por theme
function getProgress(actions: [string, Action][], answers: Record<string, string | undefined>) {
  const total = actions.length;
  const answered = actions.filter(([key]) => answers[key] !== undefined).length;
  const percent = total === 0 ? 0 : Math.round((answered / total) * 100);
  return { total, answered, percent };
}

interface Action {
  theme?: string;
  standard_code?: string;
  resources?: string;
  dimension?: string;
  valid_answers?: string[];
  link?: string;
  action?: string;
  good_practice?: string;
  level?: string;
  points?: number;
  verification_type?: string;
  verification_detail?: string;
  [key: string]: any;
}

interface Standard {
  id: string;
  description: string;
  actions: { [key: string]: Action };
}

export default function SurveyPage() {
  // Declaración única de todos los estados principales
  const { user, userType, activeBusiness, loading: authLoading, signOut } = useAuth();
  const { theme, setTheme, currentTheme } = useTheme();
  const [standards, setStandards] = useState<Standard[]>([]);
  const [selected, setSelected] = useState<Standard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Debug logs
  console.log('Survey Page - Debug Info:', {
    authLoading,
    user: user ? { uid: user.uid, email: user.email, displayName: user.displayName, businessProfileId: user.businessProfileId } : null,
    userType: userType ? { name: userType.name } : null,
    activeBusiness: activeBusiness ? { 
      id: activeBusiness.id, 
      legal_name: activeBusiness.legal_name, 
      businessName: activeBusiness.businessName,
      rut: activeBusiness.rut,
      region: activeBusiness.region,
      commune: activeBusiness.commune
    } : null
  });
  const [activeDimension, setActiveDimension] = useState<string | null>(null);
  const [activeTheme, setActiveTheme] = useState<string | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string | undefined>>({});
  const [evidenceRefreshTriggers, setEvidenceRefreshTriggers] = useState<Record<string, number>>({});

  // Cerrar menú cuando se hace clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (isMenuOpen && !target.closest('.menu-container')) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isMenuOpen]);

  const userInitials = user?.displayName?.charAt(0) || user?.email?.charAt(0) || 'U';
  const userTypeDisplay = userType?.name ? USER_TYPE_DISPLAY_NAMES[userType.name as keyof typeof USER_TYPE_DISPLAY_NAMES] : 'Usuario';

  // Función para manejar cuando se completa la carga de evidencia
  const handleEvidenceUploadComplete = (questionId: string) => {
    setEvidenceRefreshTriggers(prev => ({
      ...prev,
      [questionId]: (prev[questionId] || 0) + 1
    }));
  };

  // Verificar si el usuario puede subir evidencia
  const canUploadEvidence = userType?.id === USER_TYPES.BUSINESS_USER;
  const canViewEvidence = [USER_TYPES.BUSINESS_USER, USER_TYPES.AUDITOR, USER_TYPES.ADMIN].includes(userType?.id as any);

  useEffect(() => {
    async function fetchStandards() {
      setLoading(true);
      setError(null);
      try {
        const querySnapshot = await getDocs(collection(db, "standards"));
        const data: Standard[] = querySnapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as Standard[];
        setStandards(data);
        
        // Seleccionar el primer estándar por defecto
        if (data.length > 0 && !selected) {
          setSelected(data[0]);
        }
      } catch (err: any) {
        setError("Error al cargar los estándares");
      } finally {
        setLoading(false);
      }
    }
    fetchStandards();
  }, []);


  // Agrupar acciones por dimension y theme
  const getActionsByDimensionAndTheme = (actionsObj: { [key: string]: Action }) => {
    const grouped: { [dimension: string]: { [theme: string]: [string, Action][] } } = {};
    Object.entries(actionsObj || {}).forEach(([key, action]) => {
      const dim = action.dimension || "Sin dimensión";
      const theme = action.theme || "Sin tema";
      if (!grouped[dim]) grouped[dim] = {};
      if (!grouped[dim][theme]) grouped[dim][theme] = [];
      grouped[dim][theme].push([key, action]);
    });
    return grouped;
  };

  // Crear estructura de tabs para el componente Tabs
  const createTabsFromActions = (actionsObj: { [key: string]: Action }): NestedTabItem[] => {
    const actionsByDimension = getActionsByDimensionAndTheme(actionsObj);
    
    return Object.entries(actionsByDimension).map(([dimension, themes]) => {
      const allDimensionActions = Object.values(themes).flat();
      const dimensionProgress = getProgress(allDimensionActions, selectedAnswers);
      
      const subTabs = Object.entries(themes).map(([theme, actions]) => {
        const themeProgress = getProgress(actions, selectedAnswers);
        
        return {
          id: theme,
          label: theme,
          progress: themeProgress,
          content: (
            <div className="grid gap-4">
              {actions.length > 0 ? (
                actions.map(([key, action]) => {
                  const isAnswered = selectedAnswers[key] !== undefined;
                  return (
                    <div 
                      key={key} 
                      className={`rounded border p-4 transition-all duration-300 ${
                        isAnswered
                          ? 'border-success bg-success-background shadow-md'
                          : 'border-border bg-card hover:border-primary/50'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`text-base font-semibold flex-1 ${
                          isAnswered ? 'text-success' : 'text-primary'
                        }`}>
                          {action.action || key}
                        </div>
                        {/* Indicador visual de completitud */}
                        {isAnswered && (
                          <div className="flex-shrink-0">
                            <svg className="w-5 h-5 text-success" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        )}
                        {action.level && <span className="inline-block bg-primary text-primary-foreground text-xs font-bold px-2 py-0.5 rounded">{action.level}</span>}
                        {action.points !== undefined && <span className="inline-block bg-success text-success-foreground text-xs font-bold px-2 py-0.5 rounded ml-2">{action.points} pts</span>}
                      </div>
                      {Array.isArray(action.valid_answers) && action.valid_answers.length > 0 && (
                        <div className="mt-4">
                          <div className="text-sm font-medium text-foreground mb-1">Selecciona una opción:</div>
                          <div className="flex flex-col gap-2">
                            {action.valid_answers.map((answer, idx) => (
                              <label key={idx} className="inline-flex items-center gap-2 cursor-pointer">
                                <input
                                  type="radio"
                                  name={`answer-${key}`}
                                  className="form-radio text-primary focus:ring-ring"
                                  checked={selectedAnswers[key] === answer}
                                  onChange={() => setSelectedAnswers((prev) => ({ ...prev, [key]: answer }))}
                                />
                                <span className="text-card-foreground text-sm">{answer}</span>
                              </label>
                            ))}
                          </div>
                          {action.verification_detail && (
                            <div className="mt-3 text-sm text-muted-foreground italic">Medio de verificación: {action.verification_detail}</div>
                          )}

                          {/* Componentes de Evidencia */}
                          {canUploadEvidence && (
                            <EvidenceUpload
                              questionId={key}
                              onUploadComplete={() => handleEvidenceUploadComplete(key)}
                              disabled={false}
                            />
                          )}

                          {canViewEvidence && (
                            <EvidenceList
                              questionId={key}
                              refreshTrigger={evidenceRefreshTriggers[key]}
                            />
                          )}
                        </div>
                      )}
                    </div>
                  );
                })
              ) : (
                <div className="text-muted-foreground">No hay acciones registradas para este tema.</div>
              )}
            </div>
          )
        };
      });

      return {
        id: dimension,
        label: dimension,
        progress: dimensionProgress,
        content: <div />, // Content will be shown via subTabs
        subTabs
      };
    });
  };

  // Handle tab changes
  const handleTabChange = (dimensionId: string, themeId?: string) => {
    setActiveDimension(dimensionId);
    setActiveTheme(themeId || null);
  };



  useEffect(() => {
    if (selected) {
      const dims = Object.keys(getActionsByDimensionAndTheme(selected.actions));
      setActiveDimension((prev) => prev && dims.includes(prev) ? prev : dims[0] || null);
    } else {
      setActiveDimension(null);
    }
    setActiveTheme(null);
    setSelectedAnswers({}); // Limpiar respuestas al cambiar de estándar
    // eslint-disable-next-line
  }, [selected]);

  useEffect(() => {
    if (selected && activeDimension) {
      const themes = Object.keys(getActionsByDimensionAndTheme(selected.actions)[activeDimension] || {});
      setActiveTheme((prev) => prev && themes.includes(prev) ? prev : themes[0] || null);
    } else {
      setActiveTheme(null);
    }
    // eslint-disable-next-line
  }, [activeDimension, selected]);

  // Verificar si la encuesta está completamente respondida
  const isEncuestaCompleta = () => {
    if (!selected) return false;
    
    const allActions = Object.values(getActionsByDimensionAndTheme(selected.actions))
      .flatMap(themes => Object.values(themes))
      .flat();
    
    return allActions.every(([key, action]) => {
      // Solo verificar acciones que tienen valid_answers
      if (!Array.isArray(action.valid_answers) || action.valid_answers.length === 0) {
        return true; // Considerar como completada si no tiene opciones
      }
      return selectedAnswers[key] !== undefined;
    });
  };

  const handleEnviarEncuesta = () => {
    if (!isEncuestaCompleta()) return;
    
    // Aquí iría la lógica para enviar la encuesta
    console.log('Enviando encuesta:', {
      standard: selected,
      answers: selectedAnswers
    });
    
    // Mostrar confirmación
    alert('Encuesta enviada exitosamente');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header/Navigation Bar - Siguiendo el patrón del proyecto */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo, título y navegación */}
            <div className="flex items-center">
              {/* Menú hamburguesa */}
              <div className="relative mr-4 menu-container">
                <button
                  onClick={() => setIsMenuOpen(!isMenuOpen)}
                  className="flex items-center justify-center w-10 h-10 rounded-lg border border-border bg-background text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
                  aria-label="Abrir menú de navegación"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 6h16M4 12h16M4 18h16"
                    />
                  </svg>
                </button>

                {/* Dropdown del menú */}
                {isMenuOpen && (
                  <div className="absolute top-12 left-0 w-48 bg-background border border-border rounded-lg shadow-lg z-50">
                    <div className="py-2">
                      <a
                        href="/dashboard"
                        className="block px-4 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-muted transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        📊 Dashboard
                      </a>
                      <div className="block px-4 py-2 text-sm text-primary bg-muted/50 font-medium">
                        📋 Encuesta de Estándares
                      </div>
                      {userType?.name === 'admin' && (
                        <a
                          href="/admin"
                          className="block px-4 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-muted transition-colors"
                          onClick={() => setIsMenuOpen(false)}
                        >
                          ⚙️ Administración
                        </a>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-primary">
                  AgroExtensión Digital
                </h1>
                <p className="text-xs text-muted-foreground">
                  Encuesta de Estándares
                </p>
              </div>
            </div>

            {/* Controles del usuario */}
            <div className="flex items-center space-x-4">
              {/* Información del negocio activo */}
              {!authLoading && activeBusiness && (
                <div className="hidden lg:block border-r border-border pr-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-foreground">
                      {activeBusiness.legal_name || activeBusiness.businessName}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      RUT: {activeBusiness.rut} • {activeBusiness.region}, {activeBusiness.commune}
                    </p>
                  </div>
                </div>
              )}
              
              {/* Información del usuario */}
              {!authLoading && user && (
                <div className="flex items-center space-x-3">
                  {/* Información del negocio para móviles */}
                  {activeBusiness && (
                    <div className="lg:hidden text-right">
                      <p className="text-xs font-medium text-foreground truncate max-w-32">
                        {activeBusiness.legal_name || activeBusiness.businessName}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {activeBusiness.rut}
                      </p>
                    </div>
                  )}
                  
                  <div className="hidden sm:block text-right">
                    <p className="text-sm font-medium text-foreground">
                      {user.displayName || 'Usuario'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {userTypeDisplay}
                    </p>
                  </div>
                  
                  {/* Avatar del usuario */}
                  <Avatar
                    initials={userInitials}
                    userType={userType?.name}
                    size="md"
                  />
                  
                  {/* Botón de cerrar sesión */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={signOut}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Salir
                  </Button>
                </div>
              )}
              
              {/* Toggle de tema - Solo emoji */}
              <button
                onClick={() => {
                  const themes = ['light', 'dark', 'system'] as const;
                  const currentIndex = themes.indexOf(theme);
                  const nextTheme = themes[(currentIndex + 1) % themes.length];
                  setTheme(nextTheme);
                }}
                className="w-10 h-10 rounded-lg border border-border bg-background text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring flex items-center justify-center"
                aria-label="Cambiar tema"
                title={`Tema actual: ${theme === 'light' ? 'Claro' : theme === 'dark' ? 'Oscuro' : 'Sistema'}`}
              >
                <span className="text-lg">
                  {theme === 'light' ? '☀️' : theme === 'dark' ? '🌙' : '💻'}
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground">Encuesta de Estándares</h2>
          <p className="text-muted-foreground mt-1">
            Selecciona un estándar y completa la evaluación de acciones
          </p>
        </div>
      
      {loading && <p className="text-muted-foreground">Cargando...</p>}
      {error && <p className="text-error">{error}</p>}
      {!loading && !error && (
        <>
          {/* Selector de estándares y botón de envío */}
          <div className="mb-8 bg-card border border-border rounded-lg p-6 shadow-sm">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              {/* Listbox de estándares */}
              <div className="flex-1">
                <label htmlFor="standard-select" className="block text-sm font-medium text-foreground mb-2">
                  Selecciona un estándar para evaluar:
                </label>
                <select
                  id="standard-select"
                  value={selected?.id || ''}
                  onChange={(e) => {
                    const selectedStandard = standards.find(std => std.id === e.target.value);
                    setSelected(selectedStandard || null);
                  }}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                >
                  <option value="">-- Selecciona un estándar --</option>
                  {standards.map((std) => (
                    <option key={std.id} value={std.id}>
                      {std.description}
                    </option>
                  ))}
                </select>
              </div>

              {/* Botón de envío */}
              <div className="flex flex-col items-center gap-2">
                <Button
                  onClick={handleEnviarEncuesta}
                  disabled={!isEncuestaCompleta()}
                  className={`px-6 py-2 font-medium ${
                    isEncuestaCompleta() 
                      ? 'bg-success text-success-foreground hover:bg-success/90' 
                      : 'bg-muted text-muted-foreground cursor-not-allowed'
                  }`}
                >
                  {isEncuestaCompleta() ? '✓ Enviar Encuesta' : 'Completar Encuesta'}
                </Button>
                {selected && (
                  <p className="text-xs text-muted-foreground text-center">
                    {(() => {
                      const allActions = Object.values(getActionsByDimensionAndTheme(selected.actions))
                        .flatMap(themes => Object.values(themes))
                        .flat()
                        .filter(([, action]) => Array.isArray(action.valid_answers) && action.valid_answers.length > 0);
                      const completedActions = allActions.filter(([key]) => selectedAnswers[key] !== undefined);
                      return `${completedActions.length}/${allActions.length} acciones completadas`;
                    })()}
                  </p>
                )}
              </div>
            </div>
          </div>
          {selected && (
            <section className="bg-card p-4 rounded-lg border border-border shadow-sm">
              <h2 className="text-xl font-bold mb-4 text-primary">Acciones para: <span className="text-accent">{selected.description}</span></h2>
              
              {/* Tabs Component */}
              <Tabs
                tabs={createTabsFromActions(selected.actions)}
                defaultTab={activeDimension || undefined}
                defaultSubTab={activeTheme || undefined}
                variant="agricultural"
                sticky={true}
                onTabChange={handleTabChange}
              />
            </section>
          )}
        </>
      )}
      </main>
    </div>
  );
}

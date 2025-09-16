"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { collection, getDocs, db } from "@/lib/firebase/utils";
import { useAuth } from "@/lib/contexts/AuthContext";
import { Button } from "@/components/ui/Button";
import { Avatar } from "@/components/ui/Avatar";
import { USER_TYPE_DISPLAY_NAMES, USER_TYPES } from "@/lib/types/permissions";
import { useTheme } from "@/lib/contexts/ThemeContext";
import { EvidenceUpload, EvidenceList } from "@/components/evidence";
import { Tabs, type NestedTabItem } from "@/components/ui/Tabs";
import { useSurveyAutoSave } from "@/lib/hooks/useSurveyAutoSave";
import { SaveStatusIndicator, ProgressIndicator } from "@/components/survey/SaveStatusIndicator";
import { calculateProgress } from "@/lib/firebase/responses";
import { devLog } from "@/lib/utils/devLog";

// Helper para obtener progreso usando el mismo cálculo que el hook, pero adaptado al formato esperado
function getProgress(actions: [string, Action][], answers: Record<string, string | undefined>) {
  const allActionKeys = actions.map(([key]) => key);
  const answeredActionKeys = actions
    .filter(([key]) => answers[key] !== undefined && answers[key] !== '')
    .map(([key]) => key);
  
  const hookProgress = calculateProgress(allActionKeys, answeredActionKeys);
  
  // Adaptar al formato esperado por el componente Tabs
  return {
    total: hookProgress.totalQuestions,
    answered: hookProgress.answeredQuestions,
    percent: hookProgress.percentComplete
  };
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

// Componente que usa useSearchParams
function SurveyContent() {
  // Declaración única de todos los estados principales
  const { user, userType, activeBusiness, loading: authLoading, signOut } = useAuth();
  const { theme, setTheme, currentTheme, toggleTheme } = useTheme();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [standards, setStandards] = useState<Standard[]>([]);
  const [selected, setSelected] = useState<Standard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Detectar si está en modo debug por URL parameter
  const isDebugMode = searchParams.get('debug') === 'true';

  // Hook de auto-guardado - reemplaza selectedAnswers y lógica manual
  // Solo se activa cuando tenemos usuario autenticado, business activo y estándar seleccionado
  const {
    selectedAnswers,
    setSelectedAnswers,
    saveStatus,
    submitSurvey,
    isLoading: isSaving,
    progress,
    saveCurrentState,
    isCompleted,
    isReadonly
  } = useSurveyAutoSave({
    standardId: (selected?.id && activeBusiness?.rut && user?.uid) ? selected.id : '',
    standardActions: selected?.actions || {},
    enableAutoSave: !authLoading && !!activeBusiness?.rut && !!user?.uid,
    debounceMs: 1000 // Reducir a 1 segundo para mejor responsividad
  });

  // DEBUG: Log crítico para entender el problema del cambio
  devLog.debug('🎯 HOOK PARAMETERS DEBUG:', {
    'selected?.id': selected?.id,
    'activeBusiness?.rut': activeBusiness?.rut,  
    'user?.uid': user?.uid,
    'computed standardId': (selected?.id && activeBusiness?.rut && user?.uid) ? selected.id : '',
    'enableAutoSave': !authLoading && !!activeBusiness?.rut && !!user?.uid,
    'authLoading': authLoading
  });

  // Debug logs
  devLog.debug('Survey Page - Debug Info:', {
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
  const [evidenceRefreshTriggers, setEvidenceRefreshTriggers] = useState<Record<string, number>>({});
  
  // 🔧 NUEVO: Estado para trackear estándares completados
  const [completedStandards, setCompletedStandards] = useState<Set<string>>(new Set());

  // 🔧 NUEVO: Actualizar set de estándares completados cuando cambie isCompleted
  useEffect(() => {
    if (selected?.id) {
      setCompletedStandards(prev => {
        const newSet = new Set(prev);
        if (isCompleted) {
          newSet.add(selected.id);
        } else {
          newSet.delete(selected.id);
        }
        return newSet;
      });
    }
  }, [isCompleted, selected?.id]);

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

  // Guardar cuando la página pierde visibilidad (cambio de pestaña, etc.)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && selected && Object.keys(selectedAnswers).length > 0) {
        devLog.debug('👁️ Página oculta - guardando respuestas...');
        // Usar Promise.resolve para manejar async de forma más robusta
        Promise.resolve(saveCurrentState()).catch(error => {
          devLog.warn('⚠️ Error al guardar por cambio de visibilidad:', error);
        });
      }
    };

    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (selected && Object.keys(selectedAnswers).length > 0) {
        devLog.debug('🔄 Página cerrándose - intentando guardar respuestas...');
        
        // Para beforeunload, no podemos esperar promesas async
        // pero podemos usar navigator.sendBeacon si está disponible
        if (typeof navigator !== 'undefined' && 'sendBeacon' in navigator) {
          // Intentar guardado rápido usando beacon (mejor práctica para beforeunload)
          devLog.debug('📡 Using sendBeacon for emergency save');
          // Nota: Esto requeriría un endpoint específico, por ahora solo loggeamos
        }
        
        // Mostrar confirmación de salida si hay datos sin guardar
        if (saveStatus.status !== 'saved') {
          event.preventDefault();
          event.returnValue = 'Hay respuestas sin guardar. ¿Estás seguro de que quieres salir?';
          return event.returnValue;
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [selected, selectedAnswers, saveCurrentState, saveStatus.status]);

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
            const data: Standard[] = querySnapshot.docs.map((doc) => {
              const docData = doc.data();
              
              // Convertir actions de lista a objeto usando standard_code como clave
              let actionsObj: { [key: string]: Action } = {};
              if (Array.isArray(docData.actions)) {
                // Si actions es una lista, convertirla a objeto
                docData.actions.forEach((action: any) => {
                  if (action.standard_code) {
                    actionsObj[action.standard_code] = action;
                  }
                });
              } else if (docData.actions && typeof docData.actions === 'object') {
                // Si ya es un objeto, usarlo directamente
                actionsObj = docData.actions;
              }
              
              return {
                id: doc.id,
                description: docData.description,
                actions: actionsObj,
              };
            });
            
            devLog.debug('Standards loaded:', data.map(std => ({
              id: std.id,
              description: std.description,
              actionCount: Object.keys(std.actions).length,
              sampleActions: Object.keys(std.actions).slice(0, 3)
            })));
            
            setStandards(data);
            
            // Seleccionar el primer estándar por defecto
            if (data.length > 0 && !selected) {
              setSelected(data[0]);
            }
          } catch (err: any) {
            devLog.error('Error loading standards:', err);
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
                              <label 
                                key={idx} 
                                className={`inline-flex items-center gap-3 p-3 rounded-lg border-2 transition-all duration-200 ${
                                  selectedAnswers[key] === answer 
                                    ? isReadonly 
                                      ? 'bg-green-100 border-green-400 dark:bg-green-900/30 dark:border-green-600 shadow-sm' // Respuesta seleccionada en modo readonly
                                      : 'bg-primary/10 border-primary shadow-sm'
                                    : isReadonly
                                      ? 'bg-gray-50 border-gray-300 dark:bg-gray-800/50 dark:border-gray-500 opacity-70' // Respuestas no seleccionadas en modo readonly
                                      : 'bg-card border-border hover:border-primary/50 hover:bg-primary/5'
                                } ${
                                  isReadonly ? 'cursor-not-allowed' : 'cursor-pointer'
                                }`}
                              >
                                <input
                                  type="radio"
                                  name={`answer-${key}`}
                                  className={`form-radio text-primary focus:ring-ring ${
                                    isReadonly 
                                      ? 'opacity-70 cursor-not-allowed' 
                                      : 'disabled:opacity-50 disabled:cursor-not-allowed'
                                  }`}
                                  checked={selectedAnswers[key] === answer}
                                  disabled={isReadonly}
                                  onChange={() => {
                                    if (isReadonly || isCompleted) {
                                      devLog.debug('🚫 Input blocked - survey is completed or readonly');
                                      return;
                                    }
                                    devLog.debug(`🎯 Radio button changed - Key: ${key}, Answer: ${answer}`);
                                    devLog.debug(`🎯 Action data for key ${key}:`, action);
                                    devLog.debug(`🔍 Estado ANTES del cambio:`, {
                                      isSaving,
                                      isCompleted,
                                      isReadonly,
                                      saveStatus: saveStatus.status,
                                      selectedAnswersCount: Object.keys(selectedAnswers).length
                                    });
                                    
                                    setSelectedAnswers((prev) => {
                                      const newState = { ...prev, [key]: answer };
                                      devLog.debug(`🎯 New selectedAnswers state:`, newState);
                                      
                                      // Log asíncrono para ver el estado DESPUÉS del cambio
                                      setTimeout(() => {
                                        devLog.debug(`🔍 Estado DESPUÉS del cambio (${key}):`, {
                                          isSaving,
                                          isCompleted,
                                          isReadonly,
                                          saveStatus: saveStatus.status
                                        });
                                      }, 100);
                                      
                                      return newState;
                                    });
                                  }}
                                />
                                <span className={`text-sm font-medium ${
                                  selectedAnswers[key] === answer 
                                    ? isReadonly 
                                      ? 'text-green-900 dark:text-green-100' // Texto de respuesta seleccionada en modo readonly
                                      : 'text-primary'
                                    : isReadonly
                                      ? 'text-gray-600 dark:text-gray-300' // Texto de respuestas no seleccionadas en modo readonly
                                      : 'text-card-foreground'
                                }`}>
                                  {answer}
                                </span>
                                {/* Icono de respuesta seleccionada en modo readonly */}
                                {selectedAnswers[key] === answer && isReadonly && (
                                  <svg className="w-4 h-4 text-green-600 dark:text-green-400 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                )}
                              </label>
                            ))}
                          </div>
                          {action.verification_detail && (
                            <div className="mt-3 text-sm text-muted-foreground italic">Medio de verificación: {action.verification_detail}</div>
                          )}

                          {/* Componentes de Evidencia */}
                          {canUploadEvidence && !isReadonly && (
                            <EvidenceUpload
                              questionId={key}
                              standardId={selected?.id || ''}
                              onUploadComplete={() => handleEvidenceUploadComplete(key)}
                              disabled={isReadonly}
                            />
                          )}

                          {canViewEvidence && (
                            <EvidenceList
                              questionId={key}
                              standardId={selected?.id || ''}
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
    // NO limpiar selectedAnswers aquí - el hook se encarga de cargar los datos
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

  // Verificar si la encuesta está completamente respondida usando el progress del hook
  const isEncuestaCompleta = () => {
    return progress.percentComplete === 100;
  };

  const handleEnviarEncuesta = async () => {
    if (!isEncuestaCompleta()) return;
    
    try {
      await submitSurvey();
      alert('Encuesta enviada exitosamente');
    } catch (error) {
      devLog.error('Error enviando encuesta:', error);
      alert('Error al enviar la encuesta. Por favor, intenta de nuevo.');
    }
  };

  // DEBUG: Función para llenar la encuesta con valores aleatorios
  const handleFillRandomAnswers = () => {
    if (!selected || !selected.actions) {
      alert('Primero selecciona un estándar');
      return;
    }

    const randomAnswers: Record<string, string> = {};
    const actionEntries = Object.entries(selected.actions);
    let processedCount = 0;
    
    devLog.debug('🎲 Starting random fill process...');
    devLog.debug(`🎲 Total actions found: ${actionEntries.length}`);
    
    actionEntries.forEach(([key, action]) => {
      // Solo procesar acciones que tengan valid_answers
      if (Array.isArray(action.valid_answers) && action.valid_answers.length > 0) {
        // Seleccionar una respuesta aleatoria de las opciones válidas
        const randomIndex = Math.floor(Math.random() * action.valid_answers.length);
        const randomAnswer = action.valid_answers[randomIndex];
        randomAnswers[key] = randomAnswer;
        processedCount++;
        
        devLog.debug(`🎲 [${processedCount}] ${key}: "${randomAnswer}" (options: ${action.valid_answers.join(', ')})`);
      } else {
        devLog.debug(`⚠️ Skipped ${key}: no valid_answers (${typeof action.valid_answers}, length: ${action.valid_answers?.length})`);
      }
    });

    devLog.debug('🎲 Generated random answers:', randomAnswers);
    devLog.debug(`🎲 Summary: ${processedCount} actions filled out of ${actionEntries.length} total`);
    
    // Usar setSelectedAnswers para disparar el auto-guardado
    setSelectedAnswers(randomAnswers);
    
    // Mostrar resultado al usuario
    const message = `🎲 Llenado aleatorio completado!\n\n` +
      `✅ ${processedCount} acciones completadas\n` +
      `📊 Total disponibles: ${actionEntries.length}\n` +
      `🔄 Auto-guardado activado`;
      
    alert(message);
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
                <div className="flex items-center gap-2">
                  <p className="text-xs text-muted-foreground">
                    Encuesta de Estándares
                  </p>
                  {/* Indicador de modo debug */}
                  {isDebugMode && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
                      🔧 Debug
                    </span>
                  )}
                </div>
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
                onClick={toggleTheme}
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
          
          {/* 🔒 Banner de Encuesta Completada */}
          {isCompleted && selected && (
            <div className="mt-4 p-4 bg-green-100 dark:bg-green-900/30 border-2 border-green-400 dark:border-green-600 rounded-lg shadow-sm">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-green-900 dark:text-green-100">
                    Encuesta Completada y Enviada
                  </h3>
                  <p className="mt-1 text-sm font-medium text-green-800 dark:text-green-200">
                    Esta encuesta ha sido enviada exitosamente y ya no puede ser modificada. 
                    Los resultados están siendo revisados por el equipo de auditores.
                  </p>
                </div>
                <div className="flex-shrink-0 flex items-center gap-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    Solo Lectura
                  </span>
                  <Button
                    onClick={() => router.push('/stats')}
                    className="px-3 py-1.5 text-sm bg-blue-600 text-white hover:bg-blue-700 border border-blue-500 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    📊 Ver Resultados
                  </Button>
                </div>
              </div>
            </div>
          )}
          
          {/* Indicadores de guardado y progreso */}
          {selected && (
            <div className="mt-4 flex flex-col sm:flex-row sm:items-center gap-4">
              <SaveStatusIndicator saveStatus={saveStatus} />
              <ProgressIndicator progress={progress} className="flex-1" />
            </div>
          )}
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
                  disabled={isSaving} // Solo deshabilitar durante guardado, no por completitud
                  onChange={async (e) => {
                    // Evitar cambios durante guardado
                    if (isSaving) {
                      console.log('🚫 Cambio de estándar bloqueado - guardado en progreso');
                      return;
                    }

                    // 🔧 CAPTURAR VALOR INMEDIATAMENTE para evitar que el DOM lo modifique
                    const targetValue = e.target.value;
                    
                    // Guardar respuestas actuales antes de cambiar estándar
                    if (selected && Object.keys(selectedAnswers).length > 0) {
                      try {
                        console.log('💾 Guardando respuestas antes de cambiar estándar...');
                        await saveCurrentState();
                      } catch (error) {
                        console.warn('⚠️ Error al guardar antes del cambio:', error);
                      }
                    }
                    
                    // Buscar el estándar usando el valor capturado
                    const selectedStandard = standards.find(std => std.id === targetValue);
                    
                    if (!selectedStandard) {
                      console.error('❌ Standard not found for ID:', targetValue);
                      return;
                    }
                    
                    console.log('🔄 Cambiando a estándar:', selectedStandard.description);
                    setSelected(selectedStandard);
                  }}
                  className={`w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent ${
                    isSaving ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <option value="">-- Selecciona un estándar --</option>
                  {standards.map((std) => (
                    <option key={std.id} value={std.id}>
                      {completedStandards.has(std.id) ? '✅ ' : ''}{std.description}
                    </option>
                  ))}
                </select>
                {/* Indicador de estado del selector */}
                {isSaving && (
                  <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    <svg className="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Procesando cambio...
                  </p>
                )}
                {/* 🔧 NUEVO: Ayuda contextual */}
                {selected && isCompleted && (
                  <p className="text-xs text-green-700 dark:text-green-300 mt-1 flex items-center gap-1 font-medium">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                    </svg>
                    Este estándar está completado. Las respuestas están protegidas y no se pueden modificar.
                  </p>
                )}
              </div>

              {/* Botón de envío */}
              <div className="flex flex-col items-center gap-2">
                {/* 🎲 DEBUG: Botones para debugging - Solo con parámetro ?debug=true y si no está completada */}
                {isDebugMode && selected && !isCompleted && (
                  <div className="flex gap-2">
                    <Button
                      onClick={handleFillRandomAnswers}
                      disabled={isSaving || isReadonly}
                      className="px-3 py-1 text-xs bg-orange-500 text-white hover:bg-orange-600 border border-orange-400 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      🎲 Llenar Aleatoriamente
                    </Button>
                    <Button
                      onClick={() => {
                        if (isReadonly) return;
                        setSelectedAnswers({});
                        alert('🧹 Todas las respuestas han sido limpiadas');
                      }}
                      disabled={isSaving || isReadonly}
                      className="px-3 py-1 text-xs bg-gray-500 text-white hover:bg-gray-600 border border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      🧹 Limpiar Respuestas
                    </Button>
                  </div>
                )}
                
                {/* Botón principal - cambia según el estado */}
                {isCompleted ? (
                  <div className="text-center">
                    <Button
                      disabled
                      className="px-6 py-2 font-medium bg-green-100 text-green-800 cursor-not-allowed border border-green-300"
                    >
                      ✅ Encuesta Completada y Enviada
                    </Button>
                    <p className="text-xs text-muted-foreground mt-1">
                      Esta encuesta fue enviada el {saveStatus.lastSaved?.toLocaleDateString() || 'fecha desconocida'}
                    </p>
                  </div>
                ) : (
                  <Button
                    onClick={handleEnviarEncuesta}
                    disabled={!isEncuestaCompleta() || isSaving}
                    className={`px-6 py-2 font-medium ${
                      isEncuestaCompleta() 
                        ? 'bg-success text-success-foreground hover:bg-success/90' 
                        : 'bg-muted text-muted-foreground cursor-not-allowed'
                    }`}
                  >
                    {isSaving ? 'Enviando...' : isEncuestaCompleta() ? '✓ Enviar Encuesta' : 'Completar Encuesta'}
                  </Button>
                )}
                
                {selected && (
                  <p className="text-xs text-muted-foreground text-center">
                    {progress.answeredQuestions}/{progress.totalQuestions} acciones completadas
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

// Componente principal que envuelve SurveyContent en Suspense
export default function SurveyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando encuesta...</p>
        </div>
      </div>
    }>
      <SurveyContent />
    </Suspense>
  );
}

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { 
  saveOrUpdateResponse, 
  getResponseByBusinessAndStandard, 
  markResponseCompleted,
  calculateProgress,
  type ResponseDocument,
  type AnswerDocument 
} from '@/lib/firebase/responses';
import { devLog } from '@/lib/utils/devLog';

export interface SaveStatus {
  status: 'idle' | 'saving' | 'saved' | 'error';
  message?: string;
  lastSaved?: Date;
}

export interface UseSurveyAutoSaveOptions {
  standardId: string;
  standardActions?: { [key: string]: any };
  debounceMs?: number;
  enableAutoSave?: boolean;
}

export interface UseSurveyAutoSaveReturn {
  selectedAnswers: Record<string, string | undefined>;
  setSelectedAnswers: (answers: Record<string, string | undefined> | ((prev: Record<string, string | undefined>) => Record<string, string | undefined>)) => void;
  saveStatus: SaveStatus;
  currentResponseId: string | null;
  loadExistingResponses: () => Promise<void>;
  saveCurrentState: () => Promise<void>;
  submitSurvey: () => Promise<void>;
  isLoading: boolean;
  progress: { totalQuestions: number; answeredQuestions: number; percentComplete: number };
  isCompleted: boolean; // Nueva propiedad para indicar si la encuesta está completada
  isReadonly: boolean; // Nueva propiedad para indicar si la encuesta es de solo lectura
}

/**
 * Custom hook para manejar auto-guardado de respuestas de encuesta
 * Maneja la persistencia automática en Firestore y la carga de respuestas existentes
 */
export const useSurveyAutoSave = ({
  standardId,
  standardActions = {},
  debounceMs = 2000,
  enableAutoSave = true
}: UseSurveyAutoSaveOptions): UseSurveyAutoSaveReturn => {
  
  const { user, activeBusiness } = useAuth();
  
  // Estados principales
  const [selectedAnswers, setSelectedAnswersState] = useState<Record<string, string | undefined>>({});
  const [saveStatus, setSaveStatus] = useState<SaveStatus>({ status: 'idle' });
  const [currentResponseId, setCurrentResponseId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false); // Nuevo estado para evitar guardados concurrentes
  const [isCompleted, setIsCompletedState] = useState(false); // Nuevo estado para encuesta completada
  
  // Wrapper para rastrear cambios en isCompleted (solo en development)
  const setIsCompleted = useCallback((newValue: boolean, reason?: string) => {
    devLog.debug(`🔄 COMPLETITUD CHANGED: ${isCompleted} → ${newValue} | Reason: ${reason || 'not specified'} | StandardId: ${standardId}`);
    setIsCompletedState(newValue);
  }, [isCompleted, standardId]);
  
  // Referencias para debouncing
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastSaveDataRef = useRef<string>('');
  const isLoadingRef = useRef<boolean>(false); // Referencia para tracking de carga
  
  // Referencia para el estado actual de selectedAnswers
  const selectedAnswersRef = useRef<Record<string, string | undefined>>({});
  
  // Sincronizar la referencia con el estado
  useEffect(() => {
    selectedAnswersRef.current = selectedAnswers;
    devLog.debug('🔄 selectedAnswersRef updated:', selectedAnswersRef.current);
  }, [selectedAnswers]);

  // Calcular si la encuesta es de solo lectura (completada o status específico)
  const isReadonly = isCompleted;

  // Calcular progreso
  const allActionKeys = Object.keys(standardActions).filter(key => {
    const action = standardActions[key];
    return Array.isArray(action.valid_answers) && action.valid_answers.length > 0;
  });
  
  const answeredActionKeys = Object.keys(selectedAnswers).filter(key => 
    selectedAnswers[key] !== undefined && selectedAnswers[key] !== ''
  );
  
  const progress = calculateProgress(allActionKeys, answeredActionKeys);
  
  /**
   * Cargar respuestas existentes desde Firestore
   */
  const loadExistingResponses = useCallback(async () => {
    if (!activeBusiness?.rut || !standardId) {
      devLog.debug('🚫 No loading - missing data:', { 
        businessRut: activeBusiness?.rut, 
        standardId 
      });
      return;
    }

    // Evitar cargas concurrentes
    if (isLoadingRef.current) {
      devLog.debug('🚫 Already loading - skipping concurrent load');
      return;
    }
    
    devLog.debug('📥 Loading responses for:', { 
      businessRut: activeBusiness.rut, 
      standardId 
    });
    
    isLoadingRef.current = true;
    setIsLoading(true);
    try {
      const existingResponse = await getResponseByBusinessAndStandard(
        activeBusiness.rut,
        standardId
      );
      
      devLog.debug('📄 Found existing response:', existingResponse);
      
      if (existingResponse) {
        devLog.debug('📥 Loading existing response:', existingResponse.id);
        setCurrentResponseId(existingResponse.id!);
        
        // Verificar si la encuesta está completada
        const responseIsCompleted = existingResponse.is_completed || existingResponse.status === 'submitted';
        setIsCompleted(responseIsCompleted, `Loading existing response - is_completed: ${existingResponse.is_completed}, status: ${existingResponse.status}`);
        
        devLog.debug('📋 Response completion status:', {
          is_completed: existingResponse.is_completed,
          status: existingResponse.status,
          computed_isCompleted: responseIsCompleted
        });
        
        // Convertir answers array a selectedAnswers object
        const answersMap: Record<string, string> = {};
        existingResponse.answers?.forEach((answer: any) => {
          devLog.debug('🔄 Processing answer:', answer);
          
          // FIXED: Usar standard_code directamente
          const standardCode = answer.standard_code;
          
          if (standardCode && answer.answer_value) {
            answersMap[standardCode] = String(answer.answer_value);
            devLog.debug(`✅ Mapped ${standardCode} -> ${answer.answer_value}`);
          } else {
            devLog.debug('⚠️ Skipped answer - missing standard_code or value:', { 
              standard_code: standardCode, 
              answer_value: answer.answer_value 
            });
          }
        });
        
        devLog.debug('📋 Final answers map:', JSON.stringify(answersMap, null, 2));
        devLog.debug('📋 Final answers map keys:', Object.keys(answersMap));
        devLog.debug('📋 Final answers map values:', Object.values(answersMap));
        
        setSelectedAnswersState(answersMap);
        setSaveStatus({ 
          status: 'saved', 
          message: responseIsCompleted ? 'Encuesta completada' : 'Respuestas cargadas', 
          lastSaved: new Date() 
        });
      } else {
        devLog.debug('📄 No existing response found - resetting to clean state');
        setSelectedAnswersState({});
        setCurrentResponseId(null);
        setIsCompleted(false, 'No existing response found');
        setSaveStatus({ status: 'idle' });
      }
      
      devLog.debug('✅ Load completed for standard:', standardId, '- UI should now show new questions');
    } catch (error) {
      devLog.error('❌ Error loading responses:', error);
      setSaveStatus({ 
        status: 'error', 
        message: 'Error al cargar respuestas' 
      });
    } finally {
      setIsLoading(false);
      isLoadingRef.current = false;
      devLog.debug('🏁 loadExistingResponses COMPLETED for standardId:', standardId);
    }
  }, [activeBusiness?.rut, standardId]);

  /**
   * Guardar estado actual en Firestore
   */
  const saveCurrentState = useCallback(async () => {
    if (!activeBusiness?.rut || !standardId || !user?.uid) {
      devLog.debug('🚫 No saving - missing data:', { 
        businessRut: activeBusiness?.rut, 
        standardId, 
        userId: user?.uid 
      });
      return;
    }

    // Bloquear guardado si la encuesta ya está completada
    if (isCompleted) {
      devLog.debug('🚫 No saving - survey is already completed and readonly');
      return;
    }

    // Evitar guardados concurrentes
    if (isSaving) {
      devLog.debug('🚫 Already saving - skipping concurrent save');
      return;
    }

    // Usar la referencia en lugar del estado desfasado
    const currentSelectedAnswers = selectedAnswersRef.current;
    devLog.debug('🔧 Using selectedAnswersRef.current:', currentSelectedAnswers);

    // Verificar si hay cambios usando comparación más robusta
    const currentDataEntries = Object.entries(currentSelectedAnswers)
      .filter(([key, value]) => value !== undefined && value !== '')
      .sort(([a], [b]) => a.localeCompare(b));
    
    const currentDataString = JSON.stringify(currentDataEntries);
    
    devLog.debug('🔍 Change detection:', {
      currentDataString,
      lastSavedData: lastSaveDataRef.current,
      areEqual: currentDataString === lastSaveDataRef.current,
      selectedAnswersKeys: Object.keys(currentSelectedAnswers),
      filteredEntriesCount: currentDataEntries.length
    });
    
    if (currentDataString === lastSaveDataRef.current) {
      devLog.debug('🚫 No changes to save - data identical to last save');
      return;
    }

    devLog.debug('💾 Starting save process...', { 
      selectedAnswers: currentSelectedAnswers,
      businessRut: activeBusiness.rut,
      standardId 
    });

    setIsSaving(true);
    setSaveStatus({ status: 'saving' });
    
    try {
      // Convertir selectedAnswers a formato AnswerDocument
      devLog.debug('🔍 Raw selectedAnswers before filtering:', currentSelectedAnswers);
      devLog.debug('🔍 Object.entries before filtering:', Object.entries(currentSelectedAnswers));
      
      const filteredEntries = Object.entries(currentSelectedAnswers)
        .filter(([key, value]) => {
          const isValid = value !== undefined && value !== '' && value !== null;
          devLog.debug(`🔍 Filtering ${key}: "${value}" -> ${isValid ? 'KEEP' : 'REMOVE'}`);
          return isValid;
        });
      
      devLog.debug('🔍 Entries after filtering:', filteredEntries);
      devLog.debug('🔍 Filtered count:', filteredEntries.length, 'Original count:', Object.entries(currentSelectedAnswers).length);
      
      // Diagnóstico: Si no hay respuestas filtradas, mostrar detalles
      if (filteredEntries.length === 0) {
        devLog.debug('🚨 NO FILTERED ENTRIES - Diagnostic info:');
        devLog.debug('  - selectedAnswers keys:', Object.keys(currentSelectedAnswers));
        devLog.debug('  - selectedAnswers values:', Object.values(currentSelectedAnswers));
        devLog.debug('  - typeof values:', Object.values(currentSelectedAnswers).map(v => typeof v));
        devLog.debug('  - Raw entries:', Object.entries(currentSelectedAnswers));
      }
      
      const answers: AnswerDocument[] = filteredEntries
        .map(([actionKey, answerValue]) => {
          const actionData = standardActions[actionKey] || { action: actionKey };
          
          // Usar actionKey como standard_code para consistencia
          devLog.debug(`🔍 Processing ${actionKey}: ${answerValue} -> standard_code: ${actionKey}`);
          
          return {
            standard_code: actionKey,
            action: actionData,
            answer_value: answerValue!,
            answered_at: new Date().toISOString()
          };
        });

      devLog.debug('📝 Converted answers:', answers);
      devLog.debug('📝 Final answers count:', answers.length);

      const responseData: Omit<ResponseDocument, 'id' | 'createdAt' | 'updatedAt'> = {
        business_rut: activeBusiness.rut,
        standard_template: standardId,
        user_id: user.uid,
        is_completed: false,
        status: 'draft',
        date: new Date().toISOString(),
        answers,
        progress
      };

      devLog.debug('📦 Response data to save:', responseData);

      const responseId = await saveOrUpdateResponse(responseData);
      devLog.debug('🆔 Response saved with ID:', responseId);
      
      setCurrentResponseId(responseId);
      
      // Actualizar referencia con el mismo formato que usamos para detectar cambios
      const savedDataEntries = Object.entries(currentSelectedAnswers)
        .filter(([key, value]) => value !== undefined && value !== '')
        .sort(([a], [b]) => a.localeCompare(b));
      lastSaveDataRef.current = JSON.stringify(savedDataEntries);
      
      devLog.debug('📊 Setting save status to saved...');
      setSaveStatus({ 
        status: 'saved', 
        message: 'Guardado automáticamente', 
        lastSaved: new Date() 
      });

      devLog.debug('✅ Save completed successfully - status updated');
    } catch (error) {
      devLog.error('❌ Error saving response:', error);
      setSaveStatus({ 
        status: 'error', 
        message: 'Error al guardar' 
      });
      throw error;
    } finally {
      setIsSaving(false);
    }
  }, [activeBusiness?.rut, standardId, user?.uid, standardActions, progress, isSaving]);

  /**
   * Wrapper para setSelectedAnswers que dispara auto-guardado
   */
  const setSelectedAnswers = useCallback((
    answers: Record<string, string | undefined> | ((prev: Record<string, string | undefined>) => Record<string, string | undefined>)
  ) => {
    devLog.debug('🔄 setSelectedAnswers called with:', answers);
    
    // Bloquear cambios si la encuesta está completada
    if (isCompleted) {
      devLog.debug('🚫 Blocked setSelectedAnswers - survey is completed and readonly');
      return;
    }

    // Log del estado actual antes del cambio
    devLog.debug('🔍 Hook state ANTES de setSelectedAnswers:', {
      isLoading,
      isSaving,
      isCompleted,
      isReadonly,
      saveStatus: saveStatus.status,
      enableAutoSave
    });
    
    setSelectedAnswersState(answers);
    
    // Log del estado después del set (será visible en el próximo render)
    setTimeout(() => {
      devLog.debug('⏰ Selected answers after state update - setTimeout check');
    }, 0);
    
    // Disparar auto-guardado con debounce si está habilitado
    if (enableAutoSave && !isCompleted) {
      devLog.debug('⏰ Setting up auto-save timeout...');
      
      if (saveTimeoutRef.current) {
        devLog.debug('⏰ Clearing previous timeout');
        clearTimeout(saveTimeoutRef.current);
      }
      
      saveTimeoutRef.current = setTimeout(() => {
        devLog.debug('⏰ Debounce timeout fired - calling saveCurrentState');
        saveCurrentState();
      }, debounceMs);
      
      devLog.debug(`⏰ Auto-save scheduled for ${debounceMs}ms from now`);
    } else if (isCompleted) {
      devLog.debug('🚫 Auto-save blocked - survey is completed and readonly');
    } else {
      devLog.debug('🚫 Auto-save disabled, not scheduling save');
    }
  }, [saveCurrentState, enableAutoSave, debounceMs, isCompleted, isLoading, isSaving, saveStatus.status]);

  /**
   * Enviar encuesta completada
   */
  const submitSurvey = useCallback(async () => {
    if (!currentResponseId) {
      await saveCurrentState();
      return;
    }

    setSaveStatus({ status: 'saving' });
    
    try {
      await markResponseCompleted(currentResponseId);
      
      // Marcar la encuesta como completada localmente
      setIsCompleted(true, 'Survey submitted via submitSurvey');
      
      setSaveStatus({ 
        status: 'saved', 
        message: 'Encuesta enviada exitosamente', 
        lastSaved: new Date() 
      });
      
      devLog.debug('✅ Survey marked as completed - now in readonly mode');
    } catch (error) {
      devLog.error('❌ Error submitting survey:', error);
      setSaveStatus({ 
        status: 'error', 
        message: 'Error al enviar encuesta' 
      });
    }
  }, [currentResponseId, saveCurrentState]);

  // Limpiar timeout al desmontar
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  // Reset específico cuando cambia el standardId - debe ejecutarse ANTES de loadExistingResponses
  useEffect(() => {
    devLog.debug('🔥 RESET EFFECT TRIGGERED - standardId:', standardId);
    if (standardId) {
      devLog.debug('🔄 StandardId changed, resetting state for:', standardId);
      // Resetear completamente el estado al cambiar de estándar
      setIsCompleted(false, `StandardId changed from ${isCompleted ? 'completed' : 'incomplete'} to reset`);
      setCurrentResponseId(null);
      setSelectedAnswersState({});
      setSaveStatus({ status: 'idle' });
      // También resetear la referencia de datos guardados para evitar conflictos
      lastSaveDataRef.current = '';
      devLog.debug('✅ Estado reseteado completamente para:', standardId);
    } else {
      devLog.debug('📝 StandardId is empty, no reset needed');
    }
  }, [standardId]);

  // Auto-cargar respuestas cuando cambie el estándar o business
  useEffect(() => {
    devLog.debug('🔥 LOAD EFFECT TRIGGERED - Checking conditions:', {
      businessRut: !!activeBusiness?.rut,
      standardId: !!standardId,
      enableAutoSave,
      userId: !!user?.uid,
      actualStandardId: standardId,
      actualBusinessRut: activeBusiness?.rut
    });
    
    if (activeBusiness?.rut && standardId && enableAutoSave && user?.uid) {
      devLog.debug('✅ All conditions met - scheduling loadExistingResponses');
      
      // Aumentar delay para evitar condiciones de carrera con el reset
      const loadTimeout = setTimeout(() => {
        devLog.debug('⏰ Timeout fired - calling loadExistingResponses');
        loadExistingResponses();
      }, 200);
      
      return () => {
        devLog.debug('🧹 Cleaning up load timeout');
        clearTimeout(loadTimeout);
      };
    } else {
      devLog.debug('🚫 Skipping loadExistingResponses - missing requirements:', {
        businessRut: !!activeBusiness?.rut,
        standardId: !!standardId,
        enableAutoSave,
        userId: !!user?.uid
      });
    }
  }, [loadExistingResponses, activeBusiness?.rut, standardId, enableAutoSave, user?.uid]);

  return {
    selectedAnswers,
    setSelectedAnswers,
    saveStatus,
    currentResponseId,
    loadExistingResponses,
    saveCurrentState,
    submitSurvey,
    isLoading,
    progress,
    isCompleted,
    isReadonly
  };
};
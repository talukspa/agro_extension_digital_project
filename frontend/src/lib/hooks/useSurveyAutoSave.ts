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
  
  // Referencias para debouncing
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastSaveDataRef = useRef<string>('');
  const isLoadingRef = useRef<boolean>(false); // Referencia para tracking de carga

  // Calcular progreso
  const allActionKeys = Object.keys(standardActions).filter(key => {
    const action = standardActions[key];
    return Array.isArray(action.valid_answers) && action.valid_answers.length > 0;
  });
  
  const answeredActionKeys = Object.keys(selectedAnswers).filter(key => 
    selectedAnswers[key] !== undefined && selectedAnswers[key] !== ''
  );
  
  const progress = calculateProgress(allActionKeys, answeredActionKeys);
  
  // Debug logging para el progreso
  console.log('🎯 Progress - selectedAnswers keys:', Object.keys(selectedAnswers));
  console.log('🎯 Progress - selectedAnswers:', JSON.stringify(selectedAnswers, null, 2));
  console.log('🎯 Progress - answeredActionKeys:', answeredActionKeys);
  console.log('🎯 Progress - progress:', progress);

  /**
   * Cargar respuestas existentes desde Firestore
   */
  const loadExistingResponses = useCallback(async () => {
    if (!activeBusiness?.rut || !standardId) {
      console.log('🚫 No loading - missing data:', { 
        businessRut: activeBusiness?.rut, 
        standardId 
      });
      return;
    }

    // Evitar cargas concurrentes
    if (isLoadingRef.current) {
      console.log('🚫 Already loading - skipping concurrent load');
      return;
    }
    
    console.log('📥 Loading responses for:', { 
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
      
      console.log('📄 Found existing response:', existingResponse);
      
      if (existingResponse) {
        console.log('📥 Loading existing response:', existingResponse.id);
        setCurrentResponseId(existingResponse.id!);
        
        // Convertir answers array a selectedAnswers object
        const answersMap: Record<string, string> = {};
        existingResponse.answers?.forEach((answer: any) => {
          console.log('🔄 Processing answer:', answer);
          
          // FIXED: Usar standard_code directamente
          const standardCode = answer.standard_code;
          
          if (standardCode && answer.answer_value) {
            answersMap[standardCode] = String(answer.answer_value);
            console.log(`✅ Mapped ${standardCode} -> ${answer.answer_value}`);
          } else {
            console.log('⚠️ Skipped answer - missing standard_code or value:', { 
              standard_code: standardCode, 
              answer_value: answer.answer_value 
            });
          }
        });
        
        console.log('📋 Final answers map:', JSON.stringify(answersMap, null, 2));
        console.log('📋 Final answers map keys:', Object.keys(answersMap));
        console.log('📋 Final answers map values:', Object.values(answersMap));
        
        setSelectedAnswersState(answersMap);
        setSaveStatus({ 
          status: 'saved', 
          message: 'Respuestas cargadas', 
          lastSaved: new Date() 
        });
      } else {
        console.log('📄 No existing response found');
        setSelectedAnswersState({});
        setCurrentResponseId(null);
      }
    } catch (error) {
      console.error('❌ Error loading responses:', error);
      setSaveStatus({ 
        status: 'error', 
        message: 'Error al cargar respuestas' 
      });
    } finally {
      setIsLoading(false);
      isLoadingRef.current = false; // Siempre liberar el estado de carga
    }
  }, [activeBusiness?.rut, standardId]);

  /**
   * Guardar estado actual en Firestore
   */
  const saveCurrentState = useCallback(async () => {
    if (!activeBusiness?.rut || !standardId || !user?.uid) {
      console.log('🚫 No saving - missing data:', { 
        businessRut: activeBusiness?.rut, 
        standardId, 
        userId: user?.uid 
      });
      return;
    }

    // Evitar guardados concurrentes
    if (isSaving) {
      console.log('🚫 Already saving - skipping concurrent save');
      return;
    }

    // Verificar si hay cambios usando comparación más robusta
    const currentDataEntries = Object.entries(selectedAnswers)
      .filter(([key, value]) => value !== undefined && value !== '')
      .sort(([a], [b]) => a.localeCompare(b));
    
    const currentDataString = JSON.stringify(currentDataEntries);
    
    console.log('🔍 Change detection:', {
      currentDataString,
      lastSavedData: lastSaveDataRef.current,
      areEqual: currentDataString === lastSaveDataRef.current,
      selectedAnswersKeys: Object.keys(selectedAnswers),
      filteredEntriesCount: currentDataEntries.length
    });
    
    if (currentDataString === lastSaveDataRef.current) {
      console.log('🚫 No changes to save - data identical to last save');
      return;
    }

    console.log('💾 Starting save process...', { 
      selectedAnswers,
      businessRut: activeBusiness.rut,
      standardId 
    });

    setIsSaving(true);
    setSaveStatus({ status: 'saving' });
    
    try {
      // Convertir selectedAnswers a formato AnswerDocument
      console.log('🔍 Raw selectedAnswers before filtering:', selectedAnswers);
      console.log('🔍 Object.entries before filtering:', Object.entries(selectedAnswers));
      
      const filteredEntries = Object.entries(selectedAnswers)
        .filter(([key, value]) => {
          const isValid = value !== undefined && value !== '' && value !== null;
          console.log(`🔍 Filtering ${key}: "${value}" -> ${isValid ? 'KEEP' : 'REMOVE'}`);
          return isValid;
        });
      
      console.log('🔍 Entries after filtering:', filteredEntries);
      console.log('🔍 Filtered count:', filteredEntries.length, 'Original count:', Object.entries(selectedAnswers).length);
      
      // DIAGNÓSTICO: Si no hay respuestas filtradas, mostrar detalles
      if (filteredEntries.length === 0) {
        console.log('🚨 NO FILTERED ENTRIES - Diagnostic info:');
        console.log('  - selectedAnswers keys:', Object.keys(selectedAnswers));
        console.log('  - selectedAnswers values:', Object.values(selectedAnswers));
        console.log('  - typeof values:', Object.values(selectedAnswers).map(v => typeof v));
        console.log('  - Raw entries:', Object.entries(selectedAnswers));
      }
      
      const answers: AnswerDocument[] = filteredEntries
        .map(([actionKey, answerValue]) => {
          const actionData = standardActions[actionKey] || { action: actionKey };
          
          // CRÍTICO: Siempre usar actionKey como standard_code para consistencia
          // El actionKey ya ES el standard_code desde el frontend
          console.log(`🔍 Processing ${actionKey}: ${answerValue} -> standard_code: ${actionKey}`);
          
          return {
            // FIXED: Usar actionKey directamente como standard_code
            standard_code: actionKey,
            action: actionData, // snapshot del action completo
            answer_value: answerValue!,
            answered_at: new Date().toISOString()
          };
        });

      console.log('📝 Converted answers:', answers);
      console.log('📝 Final answers count:', answers.length);

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

      console.log('📦 Response data to save:', responseData);

      const responseId = await saveOrUpdateResponse(responseData);
      console.log('🆔 Response saved with ID:', responseId);
      
      setCurrentResponseId(responseId);
      
      // Actualizar referencia con el mismo formato que usamos para detectar cambios
      const savedDataEntries = Object.entries(selectedAnswers)
        .filter(([key, value]) => value !== undefined && value !== '')
        .sort(([a], [b]) => a.localeCompare(b));
      lastSaveDataRef.current = JSON.stringify(savedDataEntries);
      
      console.log('📊 Setting save status to saved...');
      setSaveStatus({ 
        status: 'saved', 
        message: 'Guardado automáticamente', 
        lastSaved: new Date() 
      });

      console.log('✅ Save completed successfully - status updated');
    } catch (error) {
      console.error('❌ Error saving response:', error);
      setSaveStatus({ 
        status: 'error', 
        message: 'Error al guardar' 
      });
      throw error; // Re-throw para que se pueda manejar arriba si es necesario
    } finally {
      setIsSaving(false); // Siempre liberar el estado de guardado
    }
  }, [selectedAnswers, activeBusiness?.rut, standardId, user?.uid, standardActions, progress, isSaving]);

  /**
   * Wrapper para setSelectedAnswers que dispara auto-guardado
   */
  const setSelectedAnswers = useCallback((
    answers: Record<string, string | undefined> | ((prev: Record<string, string | undefined>) => Record<string, string | undefined>)
  ) => {
    console.log('🔄 setSelectedAnswers called with:', answers);
    
    // Manejar tanto funciones como objetos
    const newAnswers = typeof answers === 'function' ? answers : answers;
    console.log('🔄 Setting new answers:', newAnswers);
    
    setSelectedAnswersState(answers);
    
    // Log del estado después del set (será visible en el próximo render)
    setTimeout(() => {
      console.log('⏰ Selected answers after state update - setTimeout check');
    }, 0);
    
    // Disparar auto-guardado con debounce si está habilitado
    if (enableAutoSave) {
      console.log('⏰ Setting up auto-save timeout...');
      
      if (saveTimeoutRef.current) {
        console.log('⏰ Clearing previous timeout');
        clearTimeout(saveTimeoutRef.current);
      }
      
      saveTimeoutRef.current = setTimeout(() => {
        console.log('⏰ Debounce timeout fired - calling saveCurrentState');
        saveCurrentState();
      }, debounceMs);
      
      console.log(`⏰ Auto-save scheduled for ${debounceMs}ms from now`);
    } else {
      console.log('🚫 Auto-save disabled, not scheduling save');
    }
  }, [saveCurrentState, enableAutoSave, debounceMs]);

  /**
   * Enviar encuesta completada
   */
  const submitSurvey = useCallback(async () => {
    if (!currentResponseId) {
      await saveCurrentState(); // Guardar primero si no hay ID
      return;
    }

    setSaveStatus({ status: 'saving' });
    
    try {
      await markResponseCompleted(currentResponseId);
      setSaveStatus({ 
        status: 'saved', 
        message: 'Encuesta enviada exitosamente', 
        lastSaved: new Date() 
      });
    } catch (error) {
      console.error('❌ Error submitting survey:', error);
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

  // Auto-cargar respuestas cuando cambie el estándar o business
  useEffect(() => {
    if (activeBusiness?.rut && standardId && enableAutoSave && user?.uid) {
      console.log('🔄 Triggering loadExistingResponses due to dependency change');
      
      // Pequeño delay para permitir que se complete cualquier guardado pendiente
      const loadTimeout = setTimeout(() => {
        loadExistingResponses();
      }, 100);
      
      return () => clearTimeout(loadTimeout);
    } else {
      console.log('🚫 Skipping loadExistingResponses - missing requirements:', {
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
    progress
  };
};
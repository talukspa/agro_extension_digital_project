import { 
  collection, 
  doc, 
  getDoc,
  getDocs,
  setDoc, 
  updateDoc,
  query,
  where,
  orderBy,
  serverTimestamp,
  addDoc
} from 'firebase/firestore';
import { validateDb, db } from './utils';
import { devLog } from '@/lib/utils/devLog';

// Types
export interface ResponseDocument {
  id?: string;
  business_rut: string;
  standard_template: string; // standard ID
  user_id?: string; // quien está llenando la encuesta
  auditor_id?: string;
  is_completed: boolean;
  date: string; // ISO string
  status: 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected';
  answers: AnswerDocument[];
  createdAt?: any; // Firestore Timestamp
  updatedAt?: any; // Firestore Timestamp
  progress?: {
    totalQuestions: number;
    answeredQuestions: number;
    percentComplete: number;
  };
}

export interface AnswerDocument {
  standard_code: string; // key from standard actions (era action_key)
  action: any; // snapshot of the action at time of response
  answer_value: string;
  answered_at?: any; // Firestore Timestamp
}

// ============================================
// RESPONSES OPERATIONS
// ============================================

/**
 * Create or update a response document for auto-save functionality
 * Uses business_rut + standard_template as composite key for upsert
 */
export const saveOrUpdateResponse = async (responseData: Omit<ResponseDocument, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> => {
  validateDb();
  
  try {
    // Look for existing response for this business + standard combination
    const existingResponse = await getResponseByBusinessAndStandard(responseData.business_rut, responseData.standard_template);
    
    const timestamp = serverTimestamp();
    const docData = {
      ...responseData,
      updatedAt: timestamp,
    };
    
    if (existingResponse) {
      // Update existing response
      const responseRef = doc(db, 'responses', existingResponse.id!);
      await updateDoc(responseRef, docData);
      devLog.debug('✅ Response updated:', existingResponse.id);
      return existingResponse.id!;
    } else {
      // Create new response
      const responseRef = await addDoc(collection(db, 'responses'), {
        ...docData,
        createdAt: timestamp
      });
      devLog.debug('✅ Response created:', responseRef.id);
      return responseRef.id;
    }
  } catch (error) {
    devLog.error('❌ Error saving response:', error);
    throw new Error('Failed to save response');
  }
};

/**
 * Get existing response by business RUT and standard template
 */
export const getResponseByBusinessAndStandard = async (
  businessRut: string, 
  standardTemplate: string
): Promise<ResponseDocument | null> => {
  validateDb();
  
  try {
    const responsesRef = collection(db, 'responses');
    const q = query(
      responsesRef, 
      where('business_rut', '==', businessRut),
      where('standard_template', '==', standardTemplate),
      orderBy('updatedAt', 'desc')
    );
    
    const querySnapshot = await getDocs(q);
    
    if (querySnapshot.empty) {
      return null;
    }
    
    // Get the most recent response
    const doc = querySnapshot.docs[0];
    return {
      id: doc.id,
      ...doc.data()
    } as ResponseDocument;
  } catch (error) {
    devLog.error('❌ Error fetching response:', error);
    return null;
  }
};

/**
 * Get all responses for a business
 */
export const getResponsesByBusiness = async (businessRut: string): Promise<ResponseDocument[]> => {
  validateDb();
  
  try {
    const responsesRef = collection(db, 'responses');
    const q = query(
      responsesRef, 
      where('business_rut', '==', businessRut),
      orderBy('updatedAt', 'desc')
    );
    
    const querySnapshot = await getDocs(q);
    
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    })) as ResponseDocument[];
  } catch (error) {
    devLog.error('❌ Error fetching business responses:', error);
    return [];
  }
};

/**
 * Mark response as completed
 */
export const markResponseCompleted = async (responseId: string): Promise<void> => {
  validateDb();
  
  try {
    const responseRef = doc(db, 'responses', responseId);
    await updateDoc(responseRef, {
      is_completed: true,
      status: 'submitted',
      updatedAt: serverTimestamp()
    });
    devLog.debug('✅ Response marked as completed:', responseId);
  } catch (error) {
    devLog.error('❌ Error marking response as completed:', error);
    throw new Error('Failed to mark response as completed');
  }
};

/**
 * Helper to calculate progress from answers
 */
export const calculateProgress = (
  allActionKeys: string[], 
  answeredActionKeys: string[]
): { totalQuestions: number; answeredQuestions: number; percentComplete: number } => {
  const totalQuestions = allActionKeys.length;
  const answeredQuestions = answeredActionKeys.length;
  const percentComplete = totalQuestions === 0 ? 0 : Math.round((answeredQuestions / totalQuestions) * 100);
  
  return {
    totalQuestions,
    answeredQuestions,
    percentComplete
  };
};
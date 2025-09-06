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
import { db } from './config';

// Helper function to clean undefined values from an object
export const cleanUndefinedValues = (obj: Record<string, any>): Record<string, any> => {
  const cleaned: Record<string, any> = {};
  
  for (const [key, value] of Object.entries(obj)) {
    if (value !== undefined && value !== null) {
      if (typeof value === 'object' && !Array.isArray(value) && value.constructor === Object) {
        // Recursively clean nested objects
        const cleanedNested = cleanUndefinedValues(value);
        if (Object.keys(cleanedNested).length > 0) {
          cleaned[key] = cleanedNested;
        }
      } else {
        cleaned[key] = value;
      }
    }
  }
  
  return cleaned;
};

// Helper function to validate database initialization
export const validateDb = () => {
  if (!db) {
    throw new Error('Firestore database instance is not initialized. Check Firebase configuration.');
  }
};

// Helper function to wait for Firebase to be ready
export const waitForFirestore = async (): Promise<boolean> => {
  let retries = 0;
  const maxRetries = 10;
  
  while (retries < maxRetries) {
    try {
      if (db) {
        // Try a simple operation to test if Firestore is ready
        return true;
      }
    } catch (error) {
      console.warn(`Firebase not ready, attempt ${retries + 1}/${maxRetries}`);
    }
    
    retries++;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  return false;
};

// Re-export Firebase functions for use in other modules
export {
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
  addDoc,
  db
};

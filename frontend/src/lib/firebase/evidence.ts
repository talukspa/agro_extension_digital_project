import { 
  collection, 
  doc, 
  addDoc, 
  getDocs, 
  deleteDoc, 
  query, 
  where, 
  orderBy,
  Timestamp,
  getDoc
} from 'firebase/firestore';
import { db } from './config';
import type { Evidence } from '@/lib/types/evidence';

export class EvidenceFirestoreService {
  private readonly collectionName = 'evidence';

  private convertEvidenceToFirestore(evidence: Evidence): any {
    return {
      ...evidence,
      uploadedAt: Timestamp.fromDate(evidence.uploadedAt)
    };
  }

  private convertEvidenceFromFirestore(data: any, id: string): Evidence {
    return {
      ...data,
      id,
      uploadedAt: data.uploadedAt?.toDate() || new Date()
    } as Evidence;
  }

  async saveEvidence(evidence: Evidence): Promise<string> {
    try {
      const evidenceData = this.convertEvidenceToFirestore(evidence);
      const evidenceRef = await addDoc(collection(db, this.collectionName), evidenceData);
      return evidenceRef.id;
    } catch (error) {
      console.error('Error saving evidence to Firestore:', error);
      throw new Error('Error al guardar los datos de la evidencia.');
    }
  }

  async getEvidenceForQuestion(businessId: string, questionId: string): Promise<Evidence[]> {
    try {
      const q = query(
        collection(db, this.collectionName),
        where('businessId', '==', businessId),
        where('questionId', '==', questionId),
        orderBy('uploadedAt', 'desc')
      );
      
      const querySnapshot = await getDocs(q);
      return querySnapshot.docs.map(doc => 
        this.convertEvidenceFromFirestore(doc.data(), doc.id)
      );
    } catch (error) {
      console.error('Error getting evidence from Firestore:', error);
      throw new Error('Error al obtener la evidencia.');
    }
  }

  async getEvidenceForBusiness(businessId: string): Promise<Evidence[]> {
    try {
      const q = query(
        collection(db, this.collectionName),
        where('businessId', '==', businessId),
        orderBy('uploadedAt', 'desc')
      );
      
      const querySnapshot = await getDocs(q);
      return querySnapshot.docs.map(doc => 
        this.convertEvidenceFromFirestore(doc.data(), doc.id)
      );
    } catch (error) {
      console.error('Error getting business evidence from Firestore:', error);
      throw new Error('Error al obtener la evidencia del negocio.');
    }
  }

  async deleteEvidence(evidenceId: string): Promise<void> {
    try {
      await deleteDoc(doc(db, this.collectionName, evidenceId));
    } catch (error) {
      console.error('Error deleting evidence from Firestore:', error);
      throw new Error('Error al eliminar los datos de la evidencia.');
    }
  }

  async getEvidenceById(evidenceId: string): Promise<Evidence | null> {
    try {
      const evidenceDocRef = doc(db, this.collectionName, evidenceId);
      const docSnapshot = await getDoc(evidenceDocRef);
      
      if (!docSnapshot.exists()) {
        return null;
      }
      
      return this.convertEvidenceFromFirestore(docSnapshot.data(), docSnapshot.id);
    } catch (error) {
      console.error('Error getting evidence by ID from Firestore:', error);
      return null;
    }
  }
}

export const evidenceFirestoreService = new EvidenceFirestoreService();
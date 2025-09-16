import { ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';
import { storage } from './config';
import type { Evidence, EvidenceUploadRequest } from '@/lib/types/evidence';
import { v4 as uuidv4 } from 'uuid';

export class EvidenceStorageService {
  private getStoragePath(businessId: string, standardId: string, questionId: string, fileName: string): string {
    return `businesses/${businessId}/evidence/${standardId}/${questionId}/${fileName}`;
  }

  async uploadEvidence(
    businessId: string, 
    standardId: string,
    uploadRequest: EvidenceUploadRequest,
    userId: string
  ): Promise<Evidence> {
    const { file, questionId, description, tags } = uploadRequest;
    
    // Generar nombre único para el archivo
    const fileExtension = file.name.split('.').pop() || '';
    const uniqueFileName = `${uuidv4()}.${fileExtension}`;
    const storagePath = this.getStoragePath(businessId, standardId, questionId, uniqueFileName);
    
    try {
      // Subir archivo a Firebase Storage
      const storageRef = ref(storage, storagePath);
      const snapshot = await uploadBytes(storageRef, file, {
        customMetadata: {
          userId,
          originalName: file.name,
          questionId,
          businessId,
          standardId
        }
      });
      
      const downloadURL = await getDownloadURL(snapshot.ref);

      // Crear objeto Evidence
      const evidence: Evidence = {
        id: uuidv4(),
        questionId,
        standardId,
        businessId,
        userId,
        fileName: file.name,
        storageFileName: uniqueFileName,
        fileUrl: downloadURL,
        fileType: file.type,
        fileSize: file.size,
        uploadedAt: new Date(),
        description: description || '', // Usar string vacío en lugar de undefined
        tags: tags || []
      };

      return evidence;
    } catch (error: any) {
      console.error('Upload error:', error);
      
      // Proporcionar mensajes de error más específicos
      if (error?.code === 'storage/unauthorized') {
        throw new Error('No tienes permisos para acceder a este archivo. Verifica que estés logueado correctamente.');
      } else if (error?.code === 'storage/retry-limit-exceeded') {
        throw new Error('Tiempo de espera agotado. Verifica tu conexión a internet y intenta de nuevo.');
      } else if (error?.code === 'storage/canceled') {
        throw new Error('La subida fue cancelada.');
      } else if (error?.code === 'storage/unknown') {
        throw new Error('Error desconocido en el servidor. Intenta de nuevo más tarde.');
      } else if (error?.code === 'storage/quota-exceeded') {
        throw new Error('Se excedió la cuota de almacenamiento del proyecto.');
      } else if (error?.code === 'storage/unauthenticated') {
        throw new Error('Necesitas estar autenticado para subir archivos.');
      }
      
      throw new Error('Error al subir el archivo. Por favor, intenta de nuevo.');
    }
  }

  async deleteEvidence(businessId: string, standardId: string, questionId: string, fileName: string): Promise<void> {
    const storagePath = this.getStoragePath(businessId, standardId, questionId, fileName);
    const storageRef = ref(storage, storagePath);
    
    try {
      await deleteObject(storageRef);
    } catch (error) {
      console.error('Error deleting evidence from Storage:', error);
      // No lanzar error si el archivo ya no existe
      if (error && typeof error === 'object' && 'code' in error && error.code !== 'storage/object-not-found') {
        throw new Error('Error al eliminar el archivo del almacenamiento.');
      }
    }
  }

  private extractFileNameFromUrl(fileUrl: string): string {
    try {
      const url = new URL(fileUrl);
      const pathSegments = url.pathname.split('/');
      const encodedFileName = pathSegments[pathSegments.length - 1];
      return decodeURIComponent(encodedFileName);
    } catch (error) {
      console.error('Error extracting filename from URL:', error);
      return '';
    }
  }
}

export const evidenceStorageService = new EvidenceStorageService();
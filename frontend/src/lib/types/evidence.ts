export interface Evidence {
  id: string;
  questionId: string;
  standardId: string;
  businessId: string;
  userId: string;
  fileName: string; // Nombre original del archivo
  storageFileName: string; // Nombre único usado en Firebase Storage
  fileUrl: string;
  fileType: string;
  fileSize: number;
  uploadedAt: Date;
  description: string; // Requerido, pero puede ser string vacío
  tags?: string[];
}

export interface EvidenceUploadRequest {
  file: File;
  questionId: string;
  description: string; // Requerido, pero puede ser string vacío
  tags?: string[];
}

export const ALLOWED_FILE_TYPES = {
  images: ['image/jpeg', 'image/png', 'image/webp'],
  documents: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ],
  get all() {
    return [...this.images, ...this.documents];
  }
};

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const FILE_TYPE_LABELS: Record<string, string> = {
  'image/jpeg': 'Imagen JPEG',
  'image/png': 'Imagen PNG',
  'image/webp': 'Imagen WebP',
  'application/pdf': 'Documento PDF',
  'application/msword': 'Documento Word',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Documento Word'
};
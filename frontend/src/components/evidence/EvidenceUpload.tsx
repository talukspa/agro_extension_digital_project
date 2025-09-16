'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { evidenceStorageService } from '@/lib/firebase/storage';
import { evidenceFirestoreService } from '@/lib/firebase/evidence';
import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE, type EvidenceUploadRequest } from '@/lib/types/evidence';
import { Upload, X, FileText, Image as ImageIcon, AlertCircle } from 'lucide-react';

interface EvidenceUploadProps {
  questionId: string;
  standardId: string;
  onUploadComplete: () => void;
  disabled?: boolean;
}

export default function EvidenceUpload({ 
  questionId, 
  standardId,
  onUploadComplete, 
  disabled = false 
}: EvidenceUploadProps) {
  const { user, activeBusiness } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');

  const validateFile = (file: File): { valid: boolean; error?: string } => {
    if (!ALLOWED_FILE_TYPES.all.includes(file.type)) {
      return {
        valid: false,
        error: 'Tipo de archivo no permitido. Solo se permiten imágenes (JPG, PNG, WEBP) y documentos (PDF, DOC, DOCX).'
      };
    }

    if (file.size > MAX_FILE_SIZE) {
      const maxSizeMB = Math.round(MAX_FILE_SIZE / (1024 * 1024));
      return {
        valid: false,
        error: `El archivo es demasiado grande. El tamaño máximo es ${maxSizeMB}MB.`
      };
    }

    return { valid: true };
  };

  const handleFileUpload = async (file: File) => {
    if (!user || !activeBusiness) {
      setError('Debes estar autenticado y tener un negocio seleccionado');
      return;
    }

    setError('');
    const validation = validateFile(file);
    if (!validation.valid) {
      setError(validation.error || 'Error de validación');
      return;
    }

    setUploading(true);

    try {
      const uploadRequest: EvidenceUploadRequest = {
        file,
        questionId,
        description: description.trim() || '' // Usar string vacío en lugar de undefined
      };

      const evidence = await evidenceStorageService.uploadEvidence(
        activeBusiness.id,
        standardId,
        uploadRequest,
        user.uid
      );

      await evidenceFirestoreService.saveEvidence(evidence);
      
      setDescription('');
      setError('');
      onUploadComplete();
      
    } catch (error) {
      console.error('Upload error:', error);
      setError(error instanceof Error ? error.message : 'Error al subir la evidencia. Por favor, intenta de nuevo.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (disabled || uploading) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const clearError = () => setError('');

  if (disabled) {
    return null;
  }

  return (
    <div className="mt-4 p-4 border border-border rounded-lg bg-muted/30">
      <h4 className="text-sm font-medium text-foreground mb-3 flex items-center">
        <Upload className="h-4 w-4 mr-2" />
        Subir Evidencia (Opcional)
      </h4>
      
      {/* Error Display */}
      {error && (
        <div className="mb-3 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-destructive mr-2" />
              <span className="text-sm text-destructive">{error}</span>
            </div>
            <button
              onClick={clearError}
              className="text-destructive hover:text-destructive/80"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
      
      {/* Description Input */}
      <div className="mb-3">
        <input
          type="text"
          placeholder="Descripción de la evidencia (opcional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={uploading}
          className="w-full px-3 py-2 border border-border rounded-md text-sm bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:bg-muted disabled:cursor-not-allowed"
        />
      </div>

      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          transition-all duration-200 bg-background
          ${dragActive 
            ? 'border-primary bg-primary/5' 
            : 'border-border hover:border-primary/50 hover:bg-muted/30'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => {
          if (!uploading && !disabled) {
            document.getElementById(`file-input-${questionId}`)?.click();
          }
        }}
      >
        <input
          id={`file-input-${questionId}`}
          type="file"
          className="hidden"
          accept={ALLOWED_FILE_TYPES.all.join(',')}
          onChange={handleFileInput}
          disabled={uploading}
        />

        {uploading ? (
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm text-muted-foreground">Subiendo archivo...</span>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex justify-center">
              <Upload className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground mb-1">
                Arrastra un archivo aquí o haz clic para seleccionar
              </p>
              <p className="text-xs text-muted-foreground">
                Imágenes (JPG, PNG, WEBP) o documentos (PDF, DOC, DOCX)
              </p>
              <p className="text-xs text-muted-foreground">
                Tamaño máximo: {Math.round(MAX_FILE_SIZE / (1024 * 1024))}MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Supported Formats */}
      <div className="mt-3 flex flex-wrap gap-2">
        <div className="flex items-center text-xs text-muted-foreground">
          <ImageIcon className="h-3 w-3 mr-1" />
          Imágenes
        </div>
        <div className="flex items-center text-xs text-muted-foreground">
          <FileText className="h-3 w-3 mr-1" />
          Documentos
        </div>
      </div>
    </div>
  );
}
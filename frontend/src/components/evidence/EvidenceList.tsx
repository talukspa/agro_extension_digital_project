'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { evidenceFirestoreService } from '@/lib/firebase/evidence';
import { evidenceStorageService } from '@/lib/firebase/storage';
import type { Evidence } from '@/lib/types/evidence';
import { File, Image as ImageIcon, Download, Trash2, Eye, FileText, AlertCircle } from 'lucide-react';
import { USER_TYPES } from '@/lib/types/permissions';

interface EvidenceListProps {
  questionId: string;
  refreshTrigger?: number;
}

export default function EvidenceList({ questionId, refreshTrigger }: EvidenceListProps) {
  const { user, activeBusiness, userType } = useAuth();
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());

  const canDelete = userType?.id === USER_TYPES.BUSINESS_USER || userType?.id === USER_TYPES.ADMIN;

  const loadEvidence = async () => {
    if (!activeBusiness) {
      setLoading(false);
      return;
    }

    try {
      setError('');
      const evidenceList = await evidenceFirestoreService.getEvidenceForQuestion(
        activeBusiness.id,
        questionId
      );
      setEvidence(evidenceList);
    } catch (error) {
      console.error('Error loading evidence:', error);
      setError('Error al cargar la evidencia');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvidence();
  }, [activeBusiness, questionId, refreshTrigger]);

  const handleDelete = async (evidenceItem: Evidence) => {
    if (!activeBusiness || !confirm('¿Estás seguro de que deseas eliminar esta evidencia?')) {
      return;
    }

    if (deletingIds.has(evidenceItem.id)) {
      return; // Ya se está eliminando
    }

    setDeletingIds(prev => new Set([...prev, evidenceItem.id]));

    try {
      // Eliminar de Storage primero
      const fileName = extractFileNameFromUrl(evidenceItem.fileUrl);
      if (fileName) {
        await evidenceStorageService.deleteEvidence(
          activeBusiness.id,
          questionId,
          fileName
        );
      }

      // Luego eliminar de Firestore
      await evidenceFirestoreService.deleteEvidence(evidenceItem.id);
      
      // Recargar lista
      await loadEvidence();
    } catch (error) {
      console.error('Error deleting evidence:', error);
      setError('Error al eliminar la evidencia');
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(evidenceItem.id);
        return newSet;
      });
    }
  };

  const extractFileNameFromUrl = (fileUrl: string): string => {
    try {
      const url = new URL(fileUrl);
      const pathSegments = url.pathname.split('/');
      // El formato es: /v0/b/{bucket}/o/businesses/{businessId}/evidence/{questionId}/{fileName}
      const encodedFileName = pathSegments[pathSegments.length - 1];
      return decodeURIComponent(encodedFileName);
    } catch (error) {
      console.error('Error extracting filename from URL:', error);
      return '';
    }
  };

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) {
      return <ImageIcon className="h-4 w-4 text-blue-500" />;
    }
    if (fileType === 'application/pdf') {
      return <FileText className="h-4 w-4 text-red-500" />;
    }
    return <File className="h-4 w-4 text-gray-500" />;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const handleView = (fileUrl: string) => {
    window.open(fileUrl, '_blank');
  };

  const handleDownload = (fileUrl: string, fileName: string) => {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = fileName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center justify-center py-4">
          <div className="w-5 h-5 border-2 border-gray-300 border-t-transparent rounded-full animate-spin mr-2"></div>
          <span className="text-sm text-gray-500">Cargando evidencia...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
        <div className="flex items-center">
          <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      </div>
    );
  }

  if (evidence.length === 0) {
    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500 text-center py-2">
          No hay evidencia adjuntada para esta pregunta
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
        <File className="h-4 w-4 mr-2" />
        Evidencia Adjuntada ({evidence.length})
      </h4>
      
      <div className="space-y-3">
        {evidence.map((item) => {
          const isDeleting = deletingIds.has(item.id);
          const canDeleteThisItem = canDelete && (item.userId === user?.uid || userType?.id === USER_TYPES.ADMIN);

          return (
            <div key={item.id} className={`
              flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200
              ${isDeleting ? 'opacity-50' : ''}
            `}>
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {getFileIcon(item.fileType)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {item.fileName}
                  </p>
                  {item.description && item.description.trim() && (
                    <p className="text-xs text-gray-600 truncate mt-1">
                      {item.description}
                    </p>
                  )}
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-400">
                      {formatFileSize(item.fileSize)}
                    </span>
                    <span className="text-xs text-gray-300">•</span>
                    <span className="text-xs text-gray-400">
                      {formatDate(item.uploadedAt)}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <button
                  onClick={() => handleView(item.fileUrl)}
                  className="p-2 text-gray-400 hover:text-blue-600 transition-colors rounded-md hover:bg-blue-50"
                  title="Ver archivo"
                  disabled={isDeleting}
                >
                  <Eye className="h-4 w-4" />
                </button>
                
                <button
                  onClick={() => handleDownload(item.fileUrl, item.fileName)}
                  className="p-2 text-gray-400 hover:text-green-600 transition-colors rounded-md hover:bg-green-50"
                  title="Descargar"
                  disabled={isDeleting}
                >
                  <Download className="h-4 w-4" />
                </button>
                
                {canDeleteThisItem && (
                  <button
                    onClick={() => handleDelete(item)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors rounded-md hover:bg-red-50 disabled:cursor-not-allowed"
                    title="Eliminar"
                    disabled={isDeleting}
                  >
                    {isDeleting ? (
                      <div className="w-4 h-4 border border-red-300 border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
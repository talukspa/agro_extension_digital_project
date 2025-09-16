import React from 'react';
import type { SaveStatus } from '@/lib/hooks/useSurveyAutoSave';

interface SaveStatusIndicatorProps {
  saveStatus: SaveStatus;
  className?: string;
}

export const SaveStatusIndicator: React.FC<SaveStatusIndicatorProps> = ({ 
  saveStatus, 
  className = "" 
}) => {
  const getStatusContent = () => {
    switch (saveStatus.status) {
      case 'saving':
        return {
          icon: (
            <svg className="animate-spin w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
          ),
          text: 'Guardando...',
          textColor: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200'
        };
      
      case 'saved':
        return {
          icon: (
            <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
            </svg>
          ),
          text: saveStatus.message || 'Guardado',
          textColor: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200'
        };
      
      case 'error':
        return {
          icon: (
            <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
            </svg>
          ),
          text: saveStatus.message || 'Error al guardar',
          textColor: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200'
        };
      
      default:
        return null;
    }
  };

  const statusContent = getStatusContent();
  
  if (!statusContent || saveStatus.status === 'idle') {
    return null;
  }

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md border ${statusContent.bgColor} ${statusContent.borderColor} ${className}`}>
      {statusContent.icon}
      <span className={`text-sm font-medium ${statusContent.textColor}`}>
        {statusContent.text}
      </span>
      {saveStatus.lastSaved && (
        <span className={`text-xs ${statusContent.textColor} opacity-70`}>
          {saveStatus.lastSaved.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
};

interface ProgressIndicatorProps {
  progress: {
    totalQuestions: number;
    answeredQuestions: number;
    percentComplete: number;
  };
  className?: string;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ 
  progress, 
  className = "" 
}) => {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Progress bar */}
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div 
          className="bg-green-500 h-2 rounded-full transition-all duration-300 ease-in-out"
          style={{ width: `${progress.percentComplete}%` }}
        />
      </div>
      
      {/* Progress text */}
      <div className="text-sm font-medium text-gray-600 whitespace-nowrap">
        {progress.answeredQuestions}/{progress.totalQuestions} ({progress.percentComplete}%)
      </div>
    </div>
  );
};
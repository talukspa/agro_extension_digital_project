'use client';

import { useState } from 'react';
import { storage } from '@/lib/firebase/config';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';

export default function FirebaseStorageTest() {
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<string>('');

  const testStorageConnection = async () => {
    setTesting(true);
    setResult('Iniciando prueba de Firebase Storage...\n');

    try {
      // Crear un archivo de prueba muy pequeño
      const testContent = new Blob(['test content'], { type: 'text/plain' });
      const testFile = new File([testContent], 'test.txt', { type: 'text/plain' });
      
      setResult(prev => prev + 'Archivo de prueba creado\n');

      // Intentar subir a Storage
      const testPath = `test/${Date.now()}/test.txt`;
      const storageRef = ref(storage, testPath);
      
      setResult(prev => prev + `Intentando subir a: ${testPath}\n`);

      const snapshot = await uploadBytes(storageRef, testFile);
      setResult(prev => prev + 'Upload exitoso!\n');

      const downloadURL = await getDownloadURL(snapshot.ref);
      setResult(prev => prev + `Download URL obtenida: ${downloadURL}\n`);
      
      setResult(prev => prev + '✅ Firebase Storage funciona correctamente!\n');

    } catch (error: any) {
      console.error('Storage test error:', error);
      setResult(prev => prev + `❌ Error: ${error.code || 'unknown'}\n`);
      setResult(prev => prev + `Mensaje: ${error.message}\n`);
      
      if (error.code === 'storage/retry-limit-exceeded') {
        setResult(prev => prev + '\n🔍 Posibles causas:\n');
        setResult(prev => prev + '- Problema de conectividad\n');
        setResult(prev => prev + '- Storage bucket incorrecto\n');
        setResult(prev => prev + '- Reglas de seguridad muy restrictivas\n');
        setResult(prev => prev + '- Proyecto Firebase mal configurado\n');
      }
    } finally {
      setTesting(false);
    }
  };

  const checkStorageConfig = () => {
    setResult('📋 Configuración actual:\n\n');
    setResult(prev => prev + `STORAGE_BUCKET: ${process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET}\n`);
    setResult(prev => prev + `PROJECT_ID: ${process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID}\n`);
    setResult(prev => prev + `AUTH_DOMAIN: ${process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN}\n\n`);
    
    // Verificar que las variables existan
    const missingVars: string[] = [];
    if (!process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET) missingVars.push('STORAGE_BUCKET');
    if (!process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID) missingVars.push('PROJECT_ID');
    if (!process.env.NEXT_PUBLIC_FIREBASE_API_KEY) missingVars.push('API_KEY');
    
    if (missingVars.length > 0) {
      setResult(prev => prev + `❌ Variables faltantes: ${missingVars.join(', ')}\n`);
    } else {
      setResult(prev => prev + '✅ Todas las variables están definidas\n');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          🔧 Diagnóstico Firebase Storage
        </h1>
        
        <div className="space-y-4 mb-6">
          <button
            onClick={checkStorageConfig}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            📋 Verificar Configuración
          </button>
          
          <button
            onClick={testStorageConnection}
            disabled={testing}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed ml-2"
          >
            {testing ? '🔄 Probando...' : '🧪 Probar Storage'}
          </button>
        </div>

        <div className="bg-gray-100 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-700 mb-2">Resultado:</h3>
          <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
            {result || 'Haz clic en un botón para empezar...'}
          </pre>
        </div>

        <div className="mt-6 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
          <h4 className="font-semibold text-yellow-800 mb-2">💡 Posibles soluciones:</h4>
          <ul className="text-sm text-yellow-700 space-y-1">
            <li>1. Verificar que Firebase Storage esté habilitado en la consola</li>
            <li>2. Revisar las reglas de seguridad de Storage</li>
            <li>3. Confirmar que el STORAGE_BUCKET sea correcto</li>
            <li>4. Verificar conectividad a internet</li>
            <li>5. Verificar cuota del proyecto Firebase</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
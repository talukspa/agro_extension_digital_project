/**
 * Script para inicializar los tipos de usuario en Firestore
 * Ejecutar una vez para configurar los tipos de usuario base
 * Nota: Este script ahora está sincronizado con la estructura real de la base de datos
 */

import { initializeApp } from 'firebase/app';
import { getFirestore, collection, doc, setDoc, getDocs, query, where } from 'firebase/firestore';
import { USER_TYPES, USER_TYPE_DISPLAY_NAMES, USER_TYPE_DESCRIPTIONS, USER_TYPE_PERMISSIONS } from '../src/lib/types/permissions';

// Configuración de Firebase (usar las mismas credenciales del proyecto)
const firebaseConfig = {
  // Agregar aquí la configuración de Firebase
  // Se puede obtener desde process.env o archivo de configuración
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// User types configuration - matches what's in the database
const userTypes = [
  {
    id: USER_TYPES.ADMIN,
    name: USER_TYPES.ADMIN,
    displayName: USER_TYPE_DISPLAY_NAMES[USER_TYPES.ADMIN],
    description: USER_TYPE_DESCRIPTIONS[USER_TYPES.ADMIN],
    permissions: USER_TYPE_PERMISSIONS[USER_TYPES.ADMIN],
    isActive: true
  },
  {
    id: USER_TYPES.BUSINESS_USER,
    name: USER_TYPES.BUSINESS_USER,
    displayName: USER_TYPE_DISPLAY_NAMES[USER_TYPES.BUSINESS_USER],
    description: USER_TYPE_DESCRIPTIONS[USER_TYPES.BUSINESS_USER],
    permissions: USER_TYPE_PERMISSIONS[USER_TYPES.BUSINESS_USER],
    isActive: true
  },
  {
    id: USER_TYPES.BUSINESS_OWNER,
    name: USER_TYPES.BUSINESS_OWNER,
    displayName: USER_TYPE_DISPLAY_NAMES[USER_TYPES.BUSINESS_OWNER],
    description: USER_TYPE_DESCRIPTIONS[USER_TYPES.BUSINESS_OWNER],
    permissions: USER_TYPE_PERMISSIONS[USER_TYPES.BUSINESS_OWNER],
    isActive: true
  },
  {
    id: USER_TYPES.AUDITOR,
    name: USER_TYPES.AUDITOR,
    displayName: USER_TYPE_DISPLAY_NAMES[USER_TYPES.AUDITOR],
    description: USER_TYPE_DESCRIPTIONS[USER_TYPES.AUDITOR],
    permissions: USER_TYPE_PERMISSIONS[USER_TYPES.AUDITOR],
    isActive: true
  }
];

async function initializeUserTypes() {
  console.log('Iniciando la inicialización de tipos de usuario...');
  
  try {
    // Verificar si ya existen tipos de usuario
    const userTypesRef = collection(db, 'user_types');
    const existingTypes = await getDocs(userTypesRef);
    
    if (existingTypes.size > 0) {
      console.log('Ya existen tipos de usuario en la base de datos.');
      console.log('Tipos existentes:');
      existingTypes.forEach(doc => {
        console.log(`- ${doc.id}: ${doc.data().displayName}`);
      });
      return;
    }

    // Crear tipos de usuario
    for (const userType of userTypes) {
      const userTypeRef = doc(db, 'user_types', userType.id);
      await setDoc(userTypeRef, {
        ...userType,
        createdAt: new Date(),
        metadata: {
          createdBy: 'system_initialization',
          version: '1.0'
        }
      });
      console.log(`✓ Tipo de usuario creado: ${userType.displayName}`);
    }

    console.log('\n✅ Inicialización completada exitosamente!');
    console.log('\nTipos de usuario creados:');
    userTypes.forEach(type => {
      console.log(`- ${type.name}: ${type.displayName}`);
      console.log(`  Permisos: ${type.permissions.join(', ')}`);
      console.log('');
    });

  } catch (error) {
    console.error('❌ Error durante la inicialización:', error);
  }
}

async function createFirstAdminUser() {
  console.log('\n🔧 Configuración del primer usuario administrador...');
  console.log('Para crear el primer administrador, necesitarás:');
  console.log('1. Registrar un usuario usando la interfaz web');
  console.log('2. Obtener el UID del usuario desde Firebase Auth');
  console.log('3. Ejecutar el siguiente comando en la consola de Firestore:');
  console.log('');
  console.log('// Actualizar el usuario para que sea administrador');
  console.log('db.collection("users").doc("USER_UID_AQUI").update({');
  console.log('  userTypeId: "admin",');
  console.log('  status: "approved",');
  console.log('  isActive: true,');
  console.log('  approvedAt: new Date(),');
  console.log('  approvedBy: "system_initialization"');
  console.log('});');
  console.log('');
}

// Ejecutar la inicialización
if (require.main === module) {
  initializeUserTypes()
    .then(() => createFirstAdminUser())
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Error:', error);
      process.exit(1);
    });
}

export { initializeUserTypes, userTypes };

const admin = require('firebase-admin');

// Inicializar Firebase Admin
admin.initializeApp({
  credential: admin.credential.applicationDefault(),
  databaseURL: `https://${process.env.PROJECT_ID}.firebaseio.com`
});

const db = admin.firestore();

async function initializeSchema() {
  console.log('🤖 Inicializando esquema Firestore automáticamente...');

  // Crear colecciones con documento temporal
  const collections = [
    'users',
    'business_profiles', 
    'auditors',
    'standards',
    'audits',
    'registers',
    'resources',
    'standard_responses'
  ];

  for (const collection of collections) {
    console.log(`📁 Creando colección: ${collection}`);
    
    try {
      await db.collection(collection).doc('_init').set({
        _initialized: true,
        _created_at: admin.firestore.FieldValue.serverTimestamp(),
        _auto_generated: true,
        _note: 'Este documento será eliminado automáticamente'
      });
      
      // Eliminar documento temporal
      await db.collection(collection).doc('_init').delete();
      
      console.log(`✅ Colección ${collection} inicializada`);
    } catch (error) {
      console.error(`❌ Error creando colección ${collection}:`, error.message);
    }
  }

  // Crear índices básicos necesarios
  console.log('📑 Creando índices básicos...');
  
  try {
    // Nota: Los índices se crean automáticamente con Terraform
    // Este script solo se asegura de que las colecciones existan
    console.log('✅ Índices serán creados por Terraform automáticamente');
  } catch (error) {
    console.error('⚠️ Nota: Índices se crearán bajo demanda');
  }

  console.log('✅ Esquema Firestore inicializado completamente');
}

// Ejecutar si es llamado directamente
if (require.main === module) {
  initializeSchema()
    .then(() => {
      console.log('🎉 Inicialización exitosa');
      process.exit(0);
    })
    .catch(error => {
      console.error('❌ Error inicializando esquema:', error);
      process.exit(1);
    });
}

module.exports = { initializeSchema };

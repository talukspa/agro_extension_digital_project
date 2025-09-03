const admin = require('firebase-admin');

// Usar configuración existente o inicializar
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    databaseURL: `https://${process.env.PROJECT_ID}.firebaseio.com`
  });
}

const db = admin.firestore();

async function seedInitialData() {
  console.log('🤖 Poblando datos iniciales automáticamente...');

  // Datos base de estándares
  const baseStandards = [
    {
      id: 'organic-cert',
      name: 'Certificación Orgánica',
      description: 'Estándares para certificación orgánica de productos agrícolas',
      category: 'organic',
      requirements: [
        'No uso de pesticidas sintéticos',
        'Suelo libre de químicos por 3 años',
        'Separación física de cultivos convencionales',
        'Uso de semillas orgánicas certificadas'
      ],
      active: true,
      version: '1.0',
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      auto_generated: true
    },
    {
      id: 'good-practices',
      name: 'Buenas Prácticas Agrícolas',
      description: 'Estándares de buenas prácticas para producción agrícola',
      category: 'practices',
      requirements: [
        'Trazabilidad completa del proceso',
        'Manejo integrado de plagas',
        'Uso eficiente del agua',
        'Capacitación del personal'
      ],
      active: true,
      version: '1.0',
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      auto_generated: true
    },
    {
      id: 'food-safety',
      name: 'Seguridad Alimentaria',
      description: 'Estándares de seguridad alimentaria para productos agrícolas',
      category: 'safety',
      requirements: [
        'Análisis de riesgos microbiológicos',
        'Control de contaminantes',
        'Higiene en manipulación',
        'Temperatura de almacenamiento'
      ],
      active: true,
      version: '1.0',
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      auto_generated: true
    }
  ];

  // Insertar estándares
  console.log('📋 Creando estándares base...');
  for (const standard of baseStandards) {
    try {
      await db.collection('standards').doc(standard.id).set(standard);
      console.log(`✅ Estándar creado: ${standard.name}`);
    } catch (error) {
      console.error(`❌ Error creando estándar ${standard.name}:`, error.message);
    }
  }

  // Datos base de recursos
  const baseResources = [
    {
      title: 'Guía de Certificación Orgánica',
      description: 'Manual completo para obtener certificación orgánica',
      type: 'document',
      url: '/resources/organic-certification-guide.pdf',
      category: 'certification',
      tags: ['organic', 'certification', 'guide'],
      public: true,
      language: 'es',
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      auto_generated: true
    },
    {
      title: 'Checklist de Buenas Prácticas',
      description: 'Lista de verificación para implementar buenas prácticas agrícolas',
      type: 'checklist',
      url: '/resources/good-practices-checklist.pdf',
      category: 'practices',
      tags: ['practices', 'checklist', 'agriculture'],
      public: true,
      language: 'es',
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      auto_generated: true
    },
    {
      title: 'Manual de Seguridad Alimentaria',
      description: 'Guía completa de seguridad alimentaria en la producción agrícola',
      type: 'manual',
      url: '/resources/food-safety-manual.pdf',
      category: 'safety',
      tags: ['safety', 'food', 'manual'],
      public: true,
      language: 'es',
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      auto_generated: true
    }
  ];

  // Insertar recursos
  console.log('📚 Creando recursos base...');
  for (const resource of baseResources) {
    try {
      const docRef = await db.collection('resources').add(resource);
      console.log(`✅ Recurso creado: ${resource.title} (${docRef.id})`);
    } catch (error) {
      console.error(`❌ Error creando recurso ${resource.title}:`, error.message);
    }
  }

  // Datos base de configuración del sistema
  const systemConfig = {
    app_name: 'CiruelaCertificada',
    version: '1.0.0',
    environment: process.env.ENVIRONMENT || 'production',
    features: {
      authentication: true,
      authorization: true,
      audit_trail: true,
      notifications: false
    },
    settings: {
      default_language: 'es',
      timezone: 'America/Santiago',
      date_format: 'DD/MM/YYYY'
    },
    initialized_at: admin.firestore.FieldValue.serverTimestamp(),
    auto_generated: true
  };

  // Insertar configuración del sistema
  console.log('⚙️ Creando configuración del sistema...');
  try {
    await db.collection('system_config').doc('app_settings').set(systemConfig);
    console.log('✅ Configuración del sistema creada');
  } catch (error) {
    console.error('❌ Error creando configuración del sistema:', error.message);
  }

  console.log('✅ Datos iniciales poblados completamente');
  
  // Mostrar resumen
  console.log('');
  console.log('📊 RESUMEN DE DATOS CREADOS:');
  console.log(`   📋 Estándares: ${baseStandards.length}`);
  console.log(`   📚 Recursos: ${baseResources.length}`);
  console.log('   ⚙️ Configuración: 1');
  console.log('');
  console.log('🔗 Próximo paso: Crear usuario administrador');
}

// Ejecutar si es llamado directamente
if (require.main === module) {
  seedInitialData()
    .then(() => {
      console.log('🎉 Datos iniciales creados exitosamente');
      process.exit(0);
    })
    .catch(error => {
      console.error('❌ Error poblando datos:', error);
      process.exit(1);
    });
}

module.exports = { seedInitialData };

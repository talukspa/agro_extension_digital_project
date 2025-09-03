const admin = require('firebase-admin');

// Usar configuración existente o inicializar
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    databaseURL: `https://${process.env.PROJECT_ID}.firebaseio.com`
  });
}

const auth = admin.auth();
const db = admin.firestore();

async function createAdminUser() {
  console.log('🤖 Creando usuario administrador automáticamente...');

  const adminEmail = process.env.ADMIN_EMAIL || 'admin@ciruelacertificada.cl';
  const adminPassword = process.env.ADMIN_PASSWORD || generateSecurePassword();
  const adminName = process.env.ADMIN_NAME || 'Administrador Sistema';

  try {
    // Verificar si el usuario ya existe
    let userRecord;
    try {
      userRecord = await auth.getUserByEmail(adminEmail);
      console.log(`👤 Usuario ya existe: ${adminEmail}`);
      
      // Actualizar claims si es necesario
      await auth.setCustomUserClaims(userRecord.uid, {
        role: 'admin',
        permissions: ['read', 'write', 'admin'],
        auto_generated: true
      });
      
      console.log('✅ Claims de administrador actualizados');
      
    } catch (error) {
      if (error.code === 'auth/user-not-found') {
        // Crear usuario nuevo
        console.log(`👤 Creando nuevo usuario auth: ${adminEmail}`);
        userRecord = await auth.createUser({
          email: adminEmail,
          password: adminPassword,
          displayName: adminName,
          emailVerified: true
        });

        console.log(`✅ Usuario creado con UID: ${userRecord.uid}`);
        
        // Establecer claims personalizados
        await auth.setCustomUserClaims(userRecord.uid, {
          role: 'admin',
          permissions: ['read', 'write', 'admin'],
          auto_generated: true
        });

        console.log('✅ Claims de administrador establecidos');
      } else {
        throw error;
      }
    }

    // Crear o actualizar documento en Firestore
    console.log('📄 Creando/actualizando documento usuario en Firestore...');
    await db.collection('users').doc(userRecord.uid).set({
      email: adminEmail,
      displayName: adminName,
      role: 'admin',
      permissions: ['read', 'write', 'admin'],
      active: true,
      profile: {
        firstName: 'Administrador',
        lastName: 'Sistema',
        phone: '',
        organization: 'CiruelaCertificada'
      },
      preferences: {
        language: 'es',
        timezone: 'America/Santiago',
        notifications: {
          email: true,
          push: false
        }
      },
      metadata: {
        created_at: admin.firestore.FieldValue.serverTimestamp(),
        updated_at: admin.firestore.FieldValue.serverTimestamp(),
        auto_generated: true,
        first_login: null,
        last_login: null
      }
    }, { merge: true });

    console.log('✅ Usuario administrador configurado exitosamente');
    console.log('');
    console.log('📋 INFORMACIÓN DEL ADMINISTRADOR:');
    console.log(`📧 Email: ${adminEmail}`);
    console.log(`👤 Nombre: ${adminName}`);
    console.log(`🆔 UID: ${userRecord.uid}`);
    console.log(`🔐 Password: ${adminPassword}`);
    console.log('');

    // Guardar credenciales en Secret Manager para proyecto nuevo
    if (process.env.SAVE_TO_SECRETS === 'true') {
      await saveAdminCredentials(adminEmail, adminPassword, userRecord.uid);
    }

    // Crear entrada de auditoría
    await createAuditEntry('admin_user_created', {
      user_id: userRecord.uid,
      email: adminEmail,
      auto_generated: true
    });

    return {
      uid: userRecord.uid,
      email: adminEmail,
      password: adminPassword
    };

  } catch (error) {
    console.error('❌ Error creando usuario admin:', error);
    throw error;
  }
}

function generateSecurePassword() {
  // Generar password seguro para proyecto nuevo
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
  let password = '';
  for (let i = 0; i < 16; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}

async function saveAdminCredentials(email, password, uid) {
  console.log('🔐 Guardando credenciales en Secret Manager...');
  
  try {
    const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');
    const client = new SecretManagerServiceClient();

    const projectId = process.env.PROJECT_ID;
    
    const adminCredentials = {
      email: email,
      password: password,
      uid: uid,
      created_at: new Date().toISOString(),
      type: 'admin_initial',
      note: 'Usuario administrador creado automáticamente'
    };

    // Crear secret si no existe
    try {
      await client.createSecret({
        parent: `projects/${projectId}`,
        secretId: 'admin-credentials',
        secret: {
          replication: {
            automatic: {},
          },
        },
      });
    } catch (error) {
      if (!error.message.includes('already exists')) {
        throw error;
      }
    }

    // Agregar versión del secret
    await client.addSecretVersion({
      parent: `projects/${projectId}/secrets/admin-credentials`,
      payload: {
        data: Buffer.from(JSON.stringify(adminCredentials, null, 2)),
      },
    });

    console.log('✅ Credenciales guardadas en Secret Manager');
  } catch (error) {
    console.error('⚠️ Error guardando credenciales en Secret Manager:', error.message);
    console.log('💡 Las credenciales están disponibles en la salida de este script');
  }
}

async function createAuditEntry(action, details) {
  try {
    await db.collection('audit_logs').add({
      action: action,
      details: details,
      timestamp: admin.firestore.FieldValue.serverTimestamp(),
      system_generated: true
    });
  } catch (error) {
    console.error('⚠️ Error creando entrada de auditoría:', error.message);
  }
}

// Ejecutar si es llamado directamente
if (require.main === module) {
  createAdminUser()
    .then((result) => {
      console.log('🎉 Usuario administrador creado exitosamente');
      console.log('');
      console.log('🔗 SIGUIENTE PASO:');
      console.log('   1. Acceder a la aplicación web');
      console.log('   2. Iniciar sesión con las credenciales mostradas');
      console.log('   3. Cambiar password en primer login');
      console.log('   4. Crear usuarios adicionales según necesidad');
      console.log('');
      process.exit(0);
    })
    .catch(error => {
      console.error('❌ Error creando admin:', error);
      process.exit(1);
    });
}

module.exports = { createAdminUser };

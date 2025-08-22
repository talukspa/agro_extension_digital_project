import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Optimización para Cloud Run - usamos standalone en lugar de export
  output: 'standalone',
  
  // Configuración de imágenes para dominio público
  images: {
    domains: ['agro-extension-digital-npe.firebaseapp.com'],
  },
  
  // Variables de entorno que serán expuestas al cliente
  env: {
    NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV,
  },
  
  // Configuración para producción
  poweredByHeader: false,
  compress: true,
};

export default nextConfig;

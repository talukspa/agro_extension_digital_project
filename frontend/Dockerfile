# Dockerfile for Next.js application - Cloud Run optimized

# Stage 1: Build the application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json pnpm-lock.yaml ./

# Install pnpm
RUN npm install -g pnpm

# Install all dependencies (including dev dependencies for build)
RUN pnpm install --frozen-lockfile

# Copy the rest of the application
COPY . .

# Build the application (this will compile TypeScript)
RUN pnpm run build

# Stage 2: Production image
FROM node:18-alpine

# Install pnpm in production image
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package files for production dependencies
COPY package*.json pnpm-lock.yaml ./

# Install only production dependencies
RUN pnpm install --prod --frozen-lockfile

# Copy the built application from the builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Copy next.config.js (compiled from TypeScript during build)
COPY --from=builder /app/next.config.js* ./

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose the port the app runs on (Cloud Run uses PORT env var)
EXPOSE 3000

# Set environment variable for production
ENV NODE_ENV production

# Start the application
CMD ["pnpm", "start"]

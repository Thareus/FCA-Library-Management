# ========== Development Stage ==========
FROM node:20 AS development

WORKDIR /app

# Copy package files
COPY ./frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY ./frontend /app

# Expose port
EXPOSE 5173

# Set environment variables for development
ENV VITE_API_URL=/api
ENV VITE_USE_PROXY=true
ENV VITE_API_SERVER_URL=http://backend:8000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ========== Production Build Stage ==========
FROM node:20 AS builder

WORKDIR /app

# Copy package files
COPY ./frontend/package*.json ./

# Install dependencies including devDependencies for build
RUN npm ci

# Copy the rest of the application
COPY ./frontend /app

# Build the application
RUN npm run build

# Clean up devDependencies after build
RUN npm prune --production

# ========== Production Stage ==========
FROM nginx:alpine AS production

# Set working directory
WORKDIR /app

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config with proper routing
COPY ./docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Set environment variables for production
ENV VITE_API_URL=/api
ENV VITE_USE_PROXY=false
COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Create necessary directories and set permissions
RUN mkdir -p /usr/share/nginx/html/assets && \
    chmod -R 755 /usr/share/nginx/html

# Expose port
EXPOSE 5173

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
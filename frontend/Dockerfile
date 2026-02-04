# Frontend Dockerfile for Silver Land Properties
FROM node:20-alpine

# Set work directory
WORKDIR /app

# Install dependencies first (for better caching)
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Default command for development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Frontend Dockerfile
FROM node:20-alpine

# Set Working Directory
WORKDIR /app

# Copy Package Files and Install Dependencies
COPY package*.json ./
RUN npm install

# Copy Application Code
COPY . .

# Build the Frontend
RUN npm run build

# Expose Frontend Port
EXPOSE 3000

# Start the Frontend
CMD ["npm", "start"]
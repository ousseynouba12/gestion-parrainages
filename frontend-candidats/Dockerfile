# Étape de construction
FROM node:20-alpine AS build
WORKDIR /app

# Copie des fichiers de configuration
COPY package*.json ./
COPY angular.json ./
COPY tsconfig*.json ./

# Installation des dépendances
RUN npm ci

# Copie du code source
COPY src ./src
COPY public ./public

# Construction de l'application en mode production
RUN npm run build

# Étape de production avec nginx
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Copie de la configuration nginx personnalisée si nécessaire
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers générés lors de l'étape de construction
COPY --from=build /app/dist/frontend-candidats/browser .

# Exposition du port 80
EXPOSE 80

# Commande de démarrage
CMD ["nginx", "-g", "daemon off;"]

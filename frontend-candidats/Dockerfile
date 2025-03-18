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
COPY . .

# Construction de l'application en mode production
RUN npm run build

# Étape de production
FROM node:20-alpine
WORKDIR /app

# Copie des fichiers générés et des dépendances
COPY --from=build /app/dist /app/dist
COPY --from=build /app/package*.json ./

# Installation des dépendances de production uniquement
RUN npm ci --omit=dev

# Exposition du port (3000 est généralement le port par défaut pour Express)
EXPOSE 3000

# Commande de démarrage du serveur SSR
CMD ["node", "dist/frontend-candidats/server/server.mjs"]
